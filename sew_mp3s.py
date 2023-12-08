import os 
import subprocess

# sews mp3s together from speeches fir 
def main(tmp_file_path='./data/tmp.txt',
         sounds_fp='./data/sounds_tmp/'
         ,out_mp3_path='./files/podcast.mp3'):
    this_path=os.path.dirname(os.path.realpath(__file__))
    #intro_fp=this_path+'/data/sounds_inputs/gpt_intro_with_background_music_v3.mp3'
    files=  os.listdir(sounds_fp)
    mode='w'
    for no, file in enumerate(files):
        file_path=this_path+sounds_fp.replace('.','')+file
        with open(tmp_file_path,mode) as f:
            f.write(f"file '{file_path}'\n")
        mode='a'
        #print(file_path)
        #input('wait')
    command = f"ffmpeg -y -f concat -safe 0 -i {tmp_file_path} -c copy {out_mp3_path}"
    subprocess.run(command, shell=True)

def add_intro(intro_fp='/data/sounds_inputs/gpt_intro_with_background_music_v3.mp3'
              ,podcast_fp='./files/podcast.mp3'
              ,tmp_file_path='./data/tmp.txt'
              ,out_podcast_path='./files/podcast_with_intro.mp3'
              ):
    this_path=os.path.dirname(os.path.realpath(__file__))
    intro_fp=this_path+intro_fp
    podcast_fp=this_path+podcast_fp
    with open(tmp_file_path,'w') as f:
        f.write(f"file '{intro_fp}'\n")
        f.write(f"file '{podcast_fp}'\n")
    command = f"ffmpeg -y -f concat -safe 0 -i {tmp_file_path} -c copy {out_podcast_path}"
    subprocess.run(command, shell=True)
    


#sew_speeches()
#exit(1)
#sew_speeches()
#exit(1)
###def sew_mp3_files(tmp_file_path='./tmp.txt',mode='w',out_mp3_path='./tmp.mp3'):
###    f1='/files/01_bitcoin_experience.mp3'
###    f2='/files/gpt_intro_with_background_music.mp3'
###    this_path=os.path.dirname(os.path.realpath(__file__))
###    
###    files=[this_path+f2,this_path+f1]
###    
###    for file in files:
###        print(file)
###        with open(tmp_file_path,mode) as f:
###            f.write(f"file '{file}'\n")
###        mode='a'
###    command = f"ffmpeg -y -f concat -safe 0 -i {tmp_file_path} -c copy {out_mp3_path}"
###    subprocess.run(command, shell=True)
###    
###sew_mp3_files()
###exit(1)
###    
###
###l= lambda input : f'ffmpeg -i ./intro_tmp/{input}.mp3 -q:a 0 ./intro_tmp/intermediate_{input}.mp3'
###
###fs=['01_check_it_out','silent','02_gpt_experience_robo','03_code_by_day']
###
###for f in fs:
###    command=l(f)
###    subprocess.run(command, shell=True)
###



#command=f"ffmpeg -f lavfi -i anullsrc -t 1 -q:a 9 -acodec libmp3lame silent.mp3"
#subprocess.run(command, shell=True)