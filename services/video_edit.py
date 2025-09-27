import os
import shutil
import subprocess
from config import TEMP_DIR, OUTPUT_DIR


def remux_file(input_file: str) -> str:
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


def randomize_metadata(input_file: str, output_file: str = None) -> str:
    """Меняет метаданные видео (заглушка: пока просто копируем файл)."""
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, os.path.basename(input_file))
    shutil.copy(input_file, output_file)
    return output_file
