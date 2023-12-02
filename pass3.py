from openai import OpenAI
from utils import * 
import json 
import dotenv 
dotenv.load_dotenv()
client = OpenAI()
model="gpt-3.5-turbo"
model="gpt-4"


chunks=read_chunks('./data/pass2.txt')
sys_prompt="""Make the conversation provided by user less formal and a little bit less dense by adding additional dialogoue between Joe, Adam, and Sarah. Dont add any meta commentary such as [Laughs] or [Sighs] or [Pause] etc"""
mode='w'

dic={}
for no,chunk in enumerate(chunks):
  
  completion = client.chat.completions.create(
    model=model,
    messages=[
      {"role": "system", "content": sys_prompt},
      {"role": "user", "content": chunk}
    ]
  )
  out = completion.choices[0].message 
  d=json.loads(out.model_dump_json())
  text=d['content']
  text=clean_gpt_output(text)   # cleanup string 

  ###text=chunk.upper()
  ###chunks[no]=text
  
  dic[f'{no}']={'gpttext':text,'sys_prompt':sys_prompt,'original_text':chunk}
  chunks[no]=text
  with open('./data/pass3_json.json', 'w') as f:
    json.dump(dic, f,indent=4)
  mywritelines(f'./data/pass3.txt',text.split('\n'),mode=mode,add_end_line=False)
  mode='a'

exit(1)


    # makes system prompt with additional info that can be added on the go
def make_sys_prompt(sys_prompt,sys_prompt_fun,*args):
    f=sys_prompt_fun
    if args is not None: # if there was something added on the go add it to the sys prompt packed in above lambda function 
        a=f(args[0],args[1])
        
    sys_prompt= sys_prompt+f"{a}" 
    return sys_prompt





# loops through text list and generates output from GPT-3
def completion_loop(text_list,out_filename,sys_prompt_template,sys_prompt_fun,top_chunk,bot_chunk,get_context_fun  ):
    mode='w'
    dic={}
    for no,t  in enumerate(text_list):
        sys_prompt=make_sys_prompt(pass_sys_prompt,pass_sys_prompt_fun,top_chunk,bot_chunk)
        

        ###completion = client.chat.completions.create(
        ###  model=model,
        ###  messages=[
        ###    {"role": "system", "content": sys_prompt},
        ###    {"role": "user", "content": t}
        ###  ]
        ###)
        ###out = completion.choices[0].message 
        ###d=json.loads(out.model_dump_json())
        ###text=d['content']
        ###text=clean_gpt_output(text)   # cleanup string 
        text=t
        content_list=mywritelines('./data/tmp1.txt',text.split('\n'),mode='w') # dump to file
        mywritelines(f'./data/{out_filename}.txt',text.split('\n'),mode=mode)
        
        
        top_chunk=' '.join(content_list[-2:])
        try:
          bot_chunk=' '.join(text_list[no+2].split('\n')[:2])
        except IndexError:
          bot_chunk=''
                
        print(sys_prompt)
        
        dic[f'{no}']={'top_chunk':top_chunk,'bot_chunk':bot_chunk,'text':text,sys_prompt:sys_prompt}
        # dump json 
        with open('./data/pass2_json.json', 'w') as f:
            json.dump(dic, f,indent=4)
        
        print(text[:30])
        print('------------------------------')
        #input('wait')
        mode='a'

# make pass 

pass_sys_prompt= f"""
Please adjust a discussion fragment from the user (middle fragment) so it fits coherently in between following two fragments:
"""
pass_sys_prompt=""" """
pass_sys_prompt_fun= lambda x,y: f"""top fragment: "{x}"
bottom fragmet: "{y}" 
adjust user inputs so it fits to top and bottom fragments provided above, do not include top and bottom fragments in your answer
"""
pass_get_context_fun=lambda l,n : l[n]
chunks=read_chunks('./data/pass1.txt')



top_chunk=''
this_chunk=chunks[0]
bot_chunk=''.join(chunks[1].split('\n')[0:2])
sys_prompt=make_sys_prompt(pass_sys_prompt,pass_sys_prompt_fun,top_chunk,bot_chunk)


completion_loop(chunks,out_filename='pass2'
                ,sys_prompt_template=pass_sys_prompt
                ,sys_prompt_fun=pass_sys_prompt_fun
                ,top_chunk=top_chunk
                ,bot_chunk=bot_chunk
                ,get_context_fun=pass_get_context_fun
                )
###
# make pass 




