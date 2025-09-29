import os
import subprocess
from PIL import Image
from config import TEMP_DIR, OUTPUT_DIR

def autocrop_photo(input_file: str, output_file: str = None) -> str:
    """Обрезает фото по центру до квадрата."""
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, os.path.basename(input_file))
    img = Image.open(input_file)
    w, h = img.size
    min_side = min(w, h)
    left = (w - min_side) // 2
    top = (h - min_side) // 2
    right = left + min_side
    bottom = top + min_side
    img_cropped = img.crop((left, top, right, bottom))
    img_cropped.save(output_file, format='JPEG', quality=95)
    return output_file

def autocrop_video(input_file: str, output_file: str = None) -> str:
    """Обрезает видео по центру до квадрата через ffmpeg."""
    if output_file is None:
        base = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(OUTPUT_DIR, f"{base}_autocrop.mp4")
    # Получаем размеры видео через ffprobe
    import json
    import subprocess
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height", "-of", "json", input_file
    ], capture_output=True, text=True)
    info = json.loads(probe.stdout)
    w = info['streams'][0]['width']
    h = info['streams'][0]['height']
    min_side = min(w, h)
    x = (w - min_side) // 2
    y = (h - min_side) // 2
    crop_filter = f"crop={min_side}:{min_side}:{x}:{y}"
    cmd = [
        "ffmpeg", "-i", input_file, "-vf", crop_filter, "-c:a", "copy", output_file, "-y"
    ]
    subprocess.run(cmd, check=True)
    return output_file

def video_to_gif(input_file: str, output_file: str = None) -> str:
    """Конвертирует видео в GIF через ffmpeg."""
    if output_file is None:
        base = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(OUTPUT_DIR, f"{base}.gif")
    cmd = [
        "ffmpeg", "-i", input_file, "-vf", "fps=15,scale=320:-1:flags=lanczos", "-t", "15", output_file, "-y"
    ]
    subprocess.run(cmd, check=True)
    return output_file
