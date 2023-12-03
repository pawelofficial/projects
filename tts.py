from pathlib import Path
from openai import OpenAI
import dotenv
import utils 
import datetime
dotenv.load_dotenv()
client = OpenAI()






def curate(text):
    text.replace('<Joe>', '').replace('<Adam>', '').replace('<Sarah>', '')
    text = text.replace('[Joe]', '').replace('[Adam]', '').replace('[Sarah]', '')
    return text 


def talk(text,voice_map,speeches_dir,fname=None):
    # check which voice to use 
    first_word=text.split(' ')[0]
    voice=voice_map[first_word.strip()]

    
    if fname is None:
        # make name as current timestamp up to seconds 
        now = datetime.datetime.now()
        fname=now.strftime("%Y%m%d-%H%M%S")+'.mp3'

    
    speech_file_path = speeches_dir +  fname
    response = client.audio.speech.create(
      model="tts-1",
      voice=voice,
      input=curate(text)
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path


    
def main(transcript_fp='./data/pass3.txt'
         ,speeches_dir='./data/sounds_tmp/'
         ):
    
    with open(transcript_fp,'r',encoding="utf-8") as f:
        out=f.readlines()
    
    utils.clear_dir(fp=speeches_dir)     # remove tmp mp3 files     
    voices=['alloy','echo','fable']
    voice_map={'<Joe>':'fable','<Adam>':'echo','<Sarah>':'alloy'}    

    output_fps=[]
    for line in out:
        output_fps.append(talk(line,voice_map,speeches_dir))
        #input('wait')
    
    return output_fps