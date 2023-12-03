from pathlib import Path
from openai import OpenAI
import dotenv
import utils 
import datetime
dotenv.load_dotenv()
client = OpenAI()






def curate(text):
    text.replace('<Joe>', '').replace('<Adam>', '').replace('<Sarah>', '')
    return text 


def talk(text,voice_map,fp='./speeches/',fname=None):
    # check which voice to use 
    first_word=text.split(' ')[0]
    voice=voice_map[first_word.strip()]

    
    if fname is None:
        # make name as current timestamp up to seconds 
        now = datetime.datetime.now()
        fname=now.strftime("%Y%m%d-%H%M%S")+'.mp3'

    
    speech_file_path = fp +  fname
    response = client.audio.speech.create(
      model="tts-1",
      voice=voice,
      input=curate(text)
    )
    response.stream_to_file(speech_file_path)


    
    



fp='./speeches/'
utils.clear_dir(fp=fp)

voices=['alloy','echo','fable']
voice_map={'<Joe>':'fable','<Adam>':'echo','<Sarah>':'alloy'}


# open pass3.txt and read it
with open('./data/pass3.txt','r',encoding="utf-8") as f:
    out=f.readlines()


for line in out:
    talk(line,voice_map)