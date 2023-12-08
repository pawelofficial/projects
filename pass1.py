from openai import OpenAI
from utils import *
import json
import dotenv

def make_sys_prompt(sys_prompt, sys_prompt_fun, *args):
    f = sys_prompt_fun
    if args is not None:
        a = '\n'.join(args)
        a = f(a)
    sys_prompt = sys_prompt + f"{a}"
    return sys_prompt

def completion_loop(text_list, out_filename, sys_prompt_template, sys_prompt_fun, sys_prompt_context, get_context_fun, client, model):
    mode = 'w'
    for t in text_list:
        sys_prompt = make_sys_prompt(sys_prompt_template, sys_prompt_fun, sys_prompt_context)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": t}
            ]
        )
        out = completion.choices[0].message
        d = json.loads(out.model_dump_json())
        text = d['content']
        text = clean_gpt_output(text)
        content_list = mywritelines('./data/tmp1.txt', text.split('\n'), mode='w')
        mywritelines(f'./data/{out_filename}.txt', content_list, mode=mode)
        sys_prompt_context = get_context_fun(content_list)
        print(sys_prompt)
        mode = 'a'

def main(nchunk=2,N=1500,pdf_path='./data/bitcoin.pdf',delim='. ',dump_res=True):
    dotenv.load_dotenv()
    client = OpenAI()
    model = "gpt-4"

#    d = pdf_to_chunks(nchunk=2, N=1500, pdf_path='./data/bitcoin.pdf', delim='. ', dump_res=True)
    d=pdf_to_chunks(nchunk=N, pdf_path=pdf_path, delim=delim, dump_res=dump_res)
    
    text_list = [d[f'chunks_{i}']['mixed_chunk'] for i in range(0, len(d))]
    init_context = '<Joe> Hey Sarah and Adam, thanks for joining me today I want to talk about bitcoin!'

    pass1_sys_prompt = f"""
    You are an assistant turning content of provided text into a discussion between Joe, Adam, and Sarah.
    Joe asking questions and keeping conversation going, Adam being technical expert and Sarah being a general expert.
    To denote who is talking use tags <Joe> <Adam> <Sarah>
    Continue the conversation without any opening or closing remarks such as "thank you for discussion".
    """
    pass1_sys_prompt_fun = lambda x: f"""    (for better context, this is previous statement from the discussion: "{x}" do not include it in output.)"""
    pass1_get_context_fun = lambda x: x[-1]  # get last statement from the discussion


    completion_loop(text_list, out_filename='pass1',
                    sys_prompt_template=pass1_sys_prompt,
                    sys_prompt_fun=pass1_sys_prompt_fun,
                    sys_prompt_context=init_context,
                    get_context_fun=pass1_get_context_fun,
                    client=client, model=model)

if __name__ == "__main__":
    main()
