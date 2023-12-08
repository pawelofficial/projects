
import subprocess
import os

def create_video_from_image_and_audio(image_path, audio_path, output_path, duration=None):
    """
    Creates a video from a single image and an audio file using FFmpeg.
    
    :param image_path: Path to the image file.
    :param audio_path: Path to the audio file.
    :param output_path: Path for the output video file.
    :param duration: Duration of the video in seconds. If None, it's set to the length of the audio.
    """
    # Construct the FFmpeg command
    ffmpeg_cmd = ['ffmpeg', '-loop', '1', '-i', image_path, '-i', audio_path, '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '192k', '-pix_fmt', 'yuv420p', '-shortest', output_path]

    # If a specific duration is provided
    if duration:
        ffmpeg_cmd.insert(-2, '-t')
        ffmpeg_cmd.insert(-2, str(duration))

    # Execute the command
    subprocess.run(ffmpeg_cmd)

# Example usage
create_video_from_image_and_audio('./files/gptexperience.png', './files/01_bitcoin_experience.mp3', './files/01_bitcoin_experience.mp4')
