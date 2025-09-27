import asyncio
import os
from yt_dlp import YoutubeDL
from config import TEMP_DIR

async def download_video(url: str) -> str | None:
    """
    Download video with yt-dlp and return file path.
    Works for TikTok/YouTube. (Instagram requires cookies).
    """
    outtmpl = os.path.join(TEMP_DIR, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": outtmpl,
        "quiet": True,
        "nocheckcertificate": True,
        "merge_output_format": "mp4",
        "fragment_retries": 10,
        "noplaylist": True,
        "ignoreerrors": True,
        "retries": 5,
    }

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            lambda: YoutubeDL(ydl_opts).extract_info(url, download=True)
        )

        file_path = os.path.join(TEMP_DIR, f"{info['id']}.mp4")

        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"[downloader] File saved: {file_path} ({size/1024/1024:.2f} MB)")
            return file_path
        else:
            print("[downloader] File not found after download")
            return None

    except Exception as e:
        print("Download error:", e)
        return None
