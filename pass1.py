from openai import OpenAI
from utils import * 
import json 
import dotenv 
dotenv.load_dotenv()
client = OpenAI()
model="gpt-3.5-turbo"
model="gpt-4"



pass1_sys_prompt= f"""
You are an assistant turning content of provided text into a discussion between Joe, Adam, and Sarah.
Joe asking questions and keeping conversation going, Adam being technical expert and Sarah being a general expert.
To denote who is talkins use tags <Joe> <Adam> <Sarah>
Continue the conversation without any opening or closing remarks such as "thank you for discussion".
"""
pass1_sys_prompt_fun= lambda x: f"""    (for better context, this is previous statement from the discussion: "{x}" do not include it in output.)"""
pass1_get_context_fun= lambda x: x[-1] # get last statement from the discussion


    # makes system prompt with additional info that can be added on the go
def make_sys_prompt(sys_prompt,sys_prompt_fun,*args):
    f=sys_prompt_fun
    if args is not None: # if there was something added on the go add it to the sys prompt packed in above lambda function 
        a='\n'.join(args) 
        a=f(a)
        
    sys_prompt= sys_prompt+f"{a}" 
    return sys_prompt


# loops through text list and generates output from GPT-3
def completion_loop(text_list,out_filename,sys_prompt_template,sys_prompt_fun,sys_prompt_context,get_context_fun  ):
    mode='w'
    for t  in text_list:
        sys_prompt=make_sys_prompt(sys_prompt_template,sys_prompt_fun,sys_prompt_context )
        completion = client.chat.completions.create(
          model=model,
          messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": t}
          ]
        )
        out = completion.choices[0].message 
        d=json.loads(out.model_dump_json())
        text=d['content']
        text=clean_gpt_output(text)   # cleanup string 
        content_list=mywritelines('./data/tmp1.txt',text.split('\n'),mode='w') # dump to file
        mywritelines(f'./data/{out_filename}.txt',content_list,mode=mode)
        
        sys_prompt_context=get_context_fun(content_list)
        print(sys_prompt)
        input('wait')
        mode='a'

# make pass1 
d=pdf_to_chunks(nchunk=2,N=2500,pdf_path='./data/bitcoin.pdf',delim='. ',dump_res=True)
text_list=[ d[f'chunks_{i}']['mixed_chunk'] for i in range(0,len(d)) ]
init_context='<Joe> Hey Sarah and Adam, thanks for joining me today i want to talk about bitcoin ! '
sys_prompt=make_sys_prompt(pass1_sys_prompt,pass1_sys_prompt_fun,init_context)

completion_loop(text_list,out_filename='pass1'
                ,sys_prompt_template=pass1_sys_prompt
                ,sys_prompt_fun=pass1_sys_prompt_fun
                ,sys_prompt_context=init_context
                ,get_context_fun=pass1_get_context_fun
                )
###
# make pass2 
###pass2_sys_prompt= f"""
###Please adjust a discussion fragment from the user (middle fragment) so it fits coherently in between following two fragments:
###"""
###pass2_sys_prompt_fun= lambda x,y: f"""top fragment: "{x}" bottom fragmet: "{y}" """




text_list=read_chunks('./data/pass1.txt')

