from openai import OpenAI
from utils import * 
import json 
import dotenv 
dotenv.load_dotenv()
client = OpenAI()
model="gpt-3.5-turbo"
model="gpt-4"
sys_prompt="""Turn provided text into a podcast style discussion format with following personas:
     Joe ( Podcast host ) - asks questions, keeps the conversation going, provides overview
     Adam ( Guest One ) - talks about technical details of each subject 
     Sarah ( Guest Two)  - talks about high level concepts and general ideas behind each subject 
     Embed personas statements in tags corresponding to their names <Joe>  <Adam> <Sarah> 
     Do not include closing opening or closing statements such as "Hello, welcome to the podcast" or "Thanks for listening", just a conversation 
     """

lc='<Joe> Hey Sarah and Adam, thanks for joining me today i want to talk about bitcoin ! '
def make_sys_prompt(lc):
    sys_prompt=  f"""
        You are an assistant turning content of provided text into a discussion between Joe, Adam, and Sarah.
        Joe asking questions and keeping conversation going, Adam being technical expert and Sarah being a general expert.
        To denote who is talkins use tags <Joe> <Adam> <Sarah>
        For your context - previous message of discussion is following <<< {lc} >>> do not include it in output
        Continue the conversation without any opening or closing remarks such as "thank you for discussion".
    """
    return sys_prompt
sys_prompt=make_sys_prompt(lc)
#sys_prompt='youre a helpful assistant '

texts=pdf_to_text('./data/bitcoin.pdf')
mode='w'
previous_statement='<Joe> Hi Adam and Sarah How are you ? wanna talk about bitcoin ? <Adam> Of course !'
for t  in texts:
    
    #t=texts[0]
    #t='hi i like pizza '


    completion = client.chat.completions.create(
      model=model,
      messages=[
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": t}
      ]
    )

    out = completion.choices[0].message
    d=json.loads(out.model_dump_json())
    out=d['content']
    out=out.replace('<Joe>', '<Joe>').replace('<Adam>', '<Adam>').replace('<Sarah>', '<Sarah>')
    out=out.replace('"', '')

    # dump output 
    with open('./data/out.txt', mode,encoding="utf-8") as f:
        f.write(out)
        #f.writelines('\n--------------------------\n')
    # get previous to last line from out file 
    with open('./data/out.txt', 'r',encoding="utf-8") as f:
        out2=[ i.strip() for i in  f.readlines() if i.strip()!='' ]
        previous_statement=out2[-1]
        

    print(previous_statement)
    sys_prompt=make_sys_prompt(previous_statement)
    print(sys_prompt)
#    input('wait')
         
    mode='a'