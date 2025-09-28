
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from services.downloader import download_video
from services.video_edit import randomize_metadata
from services.photo_edit import randomize_exif
import mimetypes
import aiohttp
import os
from config import TEMP_DIR

router = Router()


# Обработка фото от пользователя
@router.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_path = file.file_path
    dest_path = os.path.join(TEMP_DIR, f"{photo.file_id}.jpg")
    await message.bot.download_file(file_path, dest_path)
    output_file = randomize_exif(dest_path)
    await message.answer_photo(types.FSInputFile(output_file), caption="✅ Готово! Вот ваше фото с новыми метаданными.")

# Обработка видео от пользователя
@router.message(F.video)
async def handle_video(message: Message):
    video = message.video
    file = await message.bot.get_file(video.file_id)
    file_path = file.file_path
    ext = os.path.splitext(file_path)[1] or ".mp4"
    dest_path = os.path.join(TEMP_DIR, f"{video.file_id}{ext}")
    await message.bot.download_file(file_path, dest_path)
    output_file = randomize_metadata(dest_path)
    await message.answer_video(types.FSInputFile(output_file), caption="✅ Готово! Вот ваше видео с новыми метаданными.")




# Универсальное определение типа файла по ссылке
def guess_file_type(url: str) -> str:
    ext = os.path.splitext(url)[1].lower()
    if ext in {'.mp4', '.mov', '.avi', '.webm'}:
        return 'video'
    if ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}:
        return 'photo'
    # Проверка по домену для популярных видеохостингов
    video_domains = [
        'youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com', 'vk.com', 'twitter.com', 'x.com', 'facebook.com', 'vimeo.com', 'dailymotion.com'
    ]
    for domain in video_domains:
        if domain in url:
            return 'video-hosting'
    return 'unknown'

# Универсальное скачивание файла (фото/видео)
async def download_file(url: str) -> str:
    filename = os.path.basename(url.split('?')[0])
    if not filename:
        filename = 'file'
    filepath = os.path.join(TEMP_DIR, filename)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filepath, 'wb') as f:
                    f.write(await resp.read())
                return filepath
            else:
                raise Exception(f"HTTP {resp.status}")

@router.message(F.text.startswith("http"))
async def handle_link(message: Message):
    url = message.text.strip()
    await message.answer(f"🔗 Получена ссылка: {url}\n⏳ Скачивание...")

    filetype = guess_file_type(url)
    try:
        if filetype in ('video', 'video-hosting'):
            filepath = await download_video(url)
            if not filepath:
                raise Exception("Не удалось скачать видео. Возможно, оно недоступно или удалено.")
        elif filetype == 'photo':
            filepath = await download_file(url)
        else:
            # Попробуем скачать как есть, но проверим content-type
            filepath = await download_file(url)
            # Проверка: если скачали html, а не файл
            with open(filepath, 'rb') as f:
                head = f.read(512)
                if b'<html' in head.lower():
                    raise Exception("Ссылка не ведёт на файл, а на веб-страницу")
        if not filepath:
            raise Exception("Файл не был скачан")
        await message.answer(
            f"✅ Файл сохранён: {filepath}\n\nВыберите действие:",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="📥 Скачать (заменить метаданные)", callback_data=f"download|{filepath}")]
            ])
        )
    except Exception as e:
        await message.answer(f"❌ Не удалось скачать файл: {e}")

# 2️⃣ Обработка кнопки (с путём к файлу)
@router.callback_query(F.data.startswith("download|"))
async def process_download(callback: CallbackQuery):
    await callback.message.answer("⏳ Обработка файла...")

    try:
        _, input_file = callback.data.split("|", 1)
        ext = os.path.splitext(input_file)[1].lower()
        if ext in {'.jpg', '.jpeg', '.png', '.webp'}:
            output_file = randomize_exif(input_file)
            await callback.message.answer_photo(types.FSInputFile(output_file), caption="✅ Готово! Вот ваш файл с новыми метаданными.")
        elif ext in {'.mp4', '.mov', '.avi', '.webm'}:
            output_file = randomize_metadata(input_file)
            await callback.message.answer_video(types.FSInputFile(output_file), caption="✅ Готово! Вот ваш файл с новыми метаданными.")
        else:
            output_file = randomize_metadata(input_file)
            await callback.message.answer_document(types.FSInputFile(output_file), caption="✅ Готово! Вот ваш файл с новыми метаданными.")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")
