import os
import shutil
import subprocess
from config import TEMP_DIR, OUTPUT_DIR


def randomize_exif(input_file: str) -> str:
    """Перепаковывает видео в mp4, чтобы исправить битые moov atom."""
    output_file = os.path.join(TEMP_DIR, "remuxed.mp4")
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c", "copy",
        output_file,
        "-y"
    ]
    subprocess.run(cmd, check=True)
    return output_file


import random
import string

def random_string(n=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def randomize_metadata(input_file: str, output_file: str = None) -> str:
    """Меняет метаданные видео (title, artist, comment) через ffmpeg."""
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, os.path.basename(input_file))
    title = random_string(10)
    artist = random_string(10)
    comment = random_string(16)
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-metadata", f"title={title}",
        "-metadata", f"artist={artist}",
        "-metadata", f"comment={comment}",
        "-c", "copy",
        output_file,
        "-y"
    ]
    subprocess.run(cmd, check=True)
    return output_file
