import os

def rename_files(directory, old_phrase, new_phrase):
    """
    Renames files in the given directory by replacing old_phrase with new_phrase.
    
    :param directory: The directory to scan for files.
    :param old_phrase: The phrase in the filenames to be replaced.
    :param new_phrase: The new phrase to replace the old_phrase.
    """
    # Check if the directory exists
    if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist.")
        return

    # Rename files
    for filename in os.listdir(directory):
        if old_phrase in filename:
            new_filename = filename.replace(old_phrase, new_phrase)
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
            print(f"Renamed '{filename}' to '{new_filename}'")

# Example usage
directory_path = "C:\\path\\to\\your\\directory"  # Replace with your directory path
rename_files(directory_path, 'XX', 'YY')

fp='C:\\Users\\zdune\\Downloads\\music'
s1='[SPOTIFY-DOWNLOADER.COM] '
s2=''
rename_files(fp,s1,s2)
