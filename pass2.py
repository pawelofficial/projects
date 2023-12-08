from openai import OpenAI
from utils import *
import json
import dotenv

def make_sys_prompt(sys_prompt, sys_prompt_fun, *args):
    f = sys_prompt_fun
    if args is not None:
        a = f(args[0], args[1])
    sys_prompt = sys_prompt + f"{a}" 
    return sys_prompt

def main(input_file='./data/pass1.txt', output_file_json='./data/pass2_json.json', output_file_txt='./data/pass2.txt'):
    dotenv.load_dotenv()
    client = OpenAI()
    model = "gpt-4"

    chunks = read_chunks(input_file)

    pass_sys_prompt = """ """
    pass_sys_prompt_fun = lambda x, y: f"""top fragment: "{x}"
bottom fragment: "{y}" 
Make sure users input ( which is a middle fragment of the discussion ) blends well with top and bottom fragments provided above.
Remove any closing remarks from users input such as "thank you for discussion" or "goodbye" etc.
Do not shorten the output with respect to users input.
"""

    mode = 'w'
    dic = {}

    for no, chunk in enumerate(chunks):
        top_chunk = ''.join(chunks[no - 1].split('\n')[-2:]) if no != 0 else ''
        bot_chunk = ''.join(chunks[no + 1].split('\n')[0:2]) if no + 1 < len(chunks) else ''
        
        sys_prompt = make_sys_prompt(pass_sys_prompt, pass_sys_prompt_fun, top_chunk, bot_chunk)

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": chunk}
            ]
        )
        out = completion.choices[0].message
        d = json.loads(out.model_dump_json())
        text = d['content']
        text = clean_gpt_output(text)  # cleanup string

        dic[f'{no}'] = {'top_chunk': top_chunk
                        , 'bot_chunk': bot_chunk
                        , 'gpttext': text
                        , 'sys_prompt': sys_prompt
                        , 'original_text': chunk
                        ,'orignal_len': len(chunk)
                        ,'gpt_len': len(text)
                        }
        chunks[no] = text
        with open(output_file_json, 'w') as f:
            json.dump(dic, f, indent=4)
        mywritelines(output_file_txt, text.split('\n'), mode=mode)
        mode = 'a'

if __name__ == "__main__":
    main()
