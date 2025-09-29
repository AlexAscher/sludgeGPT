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


from PIL import Image
import piexif

def rand_str(n=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def randomize_exif(input_file: str, output_file: str = None) -> str:
    """Меняет EXIF-метаданные у фото (Artist, Copyright, ImageDescription, Software, DateTime)."""
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, os.path.basename(input_file))
    img = Image.open(input_file)
    exif_bytes = img.info.get('exif', None)
    try:
        exif_dict = piexif.load(exif_bytes) if exif_bytes else {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    # Случайные значения для разных EXIF-полей
    exif_dict['0th'][piexif.ImageIFD.Artist] = rand_str(8).encode()
    exif_dict['0th'][piexif.ImageIFD.Copyright] = rand_str(12).encode()
    exif_dict['0th'][piexif.ImageIFD.ImageDescription] = rand_str(16).encode()
    exif_dict['0th'][piexif.ImageIFD.Software] = rand_str(10).encode()
    exif_dict['0th'][piexif.ImageIFD.DateTime] = f"20{random.randint(10,29):02d}:{random.randint(1,12):02d}:{random.randint(1,28):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}".encode()
    exif_bytes = piexif.dump(exif_dict)
    img.convert('RGB').save(output_file, format='JPEG', exif=exif_bytes, quality=95)
    return output_file
