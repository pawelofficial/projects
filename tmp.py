

import subprocess

def cut_audio_segment(input_file, output_file, start_time, end_time):
    """
    Cuts a segment from an audio file using FFmpeg.

    :param input_file: Path to the input MP3 file.
    :param output_file: Path for the output MP3 file.
    :param start_time: Start time of the segment in seconds.
    :param end_time: End time of the segment in seconds.
    """
    # Construct the FFmpeg command
    ffmpeg_cmd = ['ffmpeg', '-i', input_file, '-ss', str(start_time), '-to', str(end_time), '-c', 'copy', output_file]

    # Execute the command
    subprocess.run(ffmpeg_cmd)

# Example usage
#cut_audio_segment('./files/synthwave.mp3', './files/short_synthwave.mp3', 15, 30)
#exit(1)



from gtts import gTTS
import os

def text_to_speech(text, output_file):
    """
    Converts text to speech and saves it as an MP3 file.

    :param text: The text to convert to speech.
    :param output_file: The output MP3 file name.
    """
    # Initialize gTTS object
    tts = gTTS(text, lang='en')  # You can change the language here

    # Save the speech to a file
    tts.save(output_file)
    print(f"Speech saved to {output_file}")

# Example usage
#text_to_speech("The G P T Experience", "output.mp3")


from pydub import AudioSegment
def concatenate_audios(file_paths, output_path):
    """
    Concatenates multiple MP3 files into a single file.

    :param file_paths: List of file paths to concatenate.
    :param output_path: Path for the output MP3 file.
    """
    combined = AudioSegment.empty()

    for file_path in file_paths:
        audio = AudioSegment.from_mp3(file_path)
        combined += audio

    combined.export(output_path, format="mp3")

#1. combine excerpts to make podcast intro 
# Example usage
### make gpt intro 
###l=['silent.mp3','silent.mp3'
###    ,'01_check_it_out.mp3'
###   ,'silent.mp3'
###   ,'02_gpt_experience_robo.mp3'
###   ,'silent.mp3'
###   ,'03_code_by_day.mp3'
###   ,'silent.mp3'
###   ,'silent.mp3'
###   ]
###
###fps=[f'./intro_tmp/{f}' for f in l]
###concatenate_audios(fps, 'combined.mp3')
###exit(1)
#3.  combine podcast with intro with music 
f1='./files/podcast.mp3'
f2='./files/gpt_intro_with_background_music_v3.mp3'
fps=[f2,f1]
concatenate_audios(fps, './files/01_bitcoin_experience.mp3')
exit(1)

from pydub import AudioSegment

def overlay_background(main_audio_path, background_audio_path, output_path, background_volume=-20.0):
    """
    Overlays a background audio on a main audio.

    :param main_audio_path: Path to the main audio file.
    :param background_audio_path: Path to the background audio file.
    :param output_path: Path for the output audio file.
    :param background_volume: Volume adjustment for background audio in dB.
    """
    # Load the main audio and background audio
    main_audio = AudioSegment.from_mp3(main_audio_path)
    background_audio = AudioSegment.from_mp3(background_audio_path)

    # Adjust the volume of the background audio
    background_audio = background_audio - background_volume

    # If the background audio is shorter, loop it
    if len(background_audio) < len(main_audio):
        background_audio = background_audio.loop(times=int(len(main_audio)/len(background_audio)))

    # Overlay the background audio onto the main audio
    combined = main_audio.overlay(background_audio)

    # Export the combined audio
    combined.export(output_path, format='mp3')

# Example usage
# 2. combine podcast intro with music background 
main_audio='./files/gpt_podcast_intro_v3.mp3'
background_audio='./files/short_synthwave.mp3'

command=f"""ffmpeg -y -i {main_audio} -i {background_audio} -filter_complex "[1:a]volume=0.1[a1];[0:a][a1]amerge=inputs=2[aout]" -map "[aout]" -ac 2 output.mp3
"""
#command=f"""ffmpeg -y -i {main_audio} -i {background_audio} -filter_complex "[0:a][1:a]amix=inputs=2:duration=longest" output.mp3"""

os.system(command)

#overlay_background('./files/gpt_podcast_intro.mp3', './files/short_synthwave.mp3', 'combined.mp3')
