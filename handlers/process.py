

# ...existing code...


from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from services.downloader import download_video
from services.video_edit import randomize_metadata
from services.photo_edit import randomize_exif
import mimetypes
import aiohttp
import os
import uuid
import boto3
from config import TEMP_DIR, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME, S3_REGION, S3_ENDPOINT


router = Router()

file_cache = {}

# S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=S3_REGION,
    endpoint_url=S3_ENDPOINT
)

# Импорт autocaption_video и регистрация caption_handler строго после router

# Autocrop callback

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger_caption = logging.getLogger("caption_handler")




## Удалено дублирование импортов и router = Router()


# Tools menu callback (edit message)

@router.callback_query(F.data == "tools")
async def show_tools_menu(callback: CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⬅️ Go Back", callback_data="back")],
    ])
    # Если сообщение с медиа — используем edit_caption, иначе edit_text
    try:
        if callback.message.photo or callback.message.video:
            await callback.message.edit_caption(caption="Select a template option:", reply_markup=keyboard)
        else:
            await callback.message.edit_text("Select a template option:", reply_markup=keyboard)
    except Exception as e:
        await callback.answer("Failed to open tools menu.", show_alert=True)


# Go Back button handler (restore previous menu)
@router.callback_query(F.data == "back")
async def go_back_menu(callback: CallbackQuery):
    # Определяем, к какому типу файла возвращаться (фото или видео)
    # Пробуем получить caption и media type
    caption = callback.message.caption or callback.message.text or ""
    # Определяем, что было отправлено: фото или видео
    is_photo = callback.message.photo is not None
    is_video = callback.message.video is not None
    # Клавиатура как после обработки фото/видео
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Download", callback_data="download_photo" if is_photo else "download_video")],
        [types.InlineKeyboardButton(text="Templates", callback_data="templates"), types.InlineKeyboardButton(text="Tools", callback_data="tools")],
        [types.InlineKeyboardButton(text="Bulk Templates", callback_data="bulk_templates"), types.InlineKeyboardButton(text="Bulk Randomize", callback_data="bulk_randomize")],
        [types.InlineKeyboardButton(text="Get Paid to Post 💰", callback_data="get_paid")],
        [types.InlineKeyboardButton(text="Monthly Subscription", callback_data="monthly_sub")],
        [types.InlineKeyboardButton(text="Annual Subscription (3 months free)", callback_data="annual_sub")],
    ])
    # Обновляем только reply_markup и caption, не отправляем новое сообщение
    try:
        if is_photo:
            await callback.message.edit_caption(caption="✅ Done! Here is your photo with new metadata.", reply_markup=keyboard)
        elif is_video:
            await callback.message.edit_caption(caption="✅ Done! Here is your video with new metadata.", reply_markup=keyboard)
        else:
            # Если не фото и не видео, просто обновим reply_markup
            await callback.message.edit_reply_markup(reply_markup=keyboard)
    except Exception as e:
        await callback.answer("Failed to go back.", show_alert=True)


# Обработка фото от пользователя
@router.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_path = file.file_path
    dest_path = os.path.join(TEMP_DIR, f"{photo.file_id}.jpg")
    await message.bot.download_file(file_path, dest_path)
    # Сохраняем в кэш
    file_uuid = str(uuid.uuid4())
    file_cache[file_uuid] = dest_path
    # Вместо обработки, отправляем сообщение с выбором количества копий
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="5", callback_data=f"copies|5|{file_uuid}|photo"),
            types.InlineKeyboardButton(text="10", callback_data=f"copies|10|{file_uuid}|photo"),
            types.InlineKeyboardButton(text="20", callback_data=f"copies|20|{file_uuid}|photo"),
            types.InlineKeyboardButton(text="30", callback_data=f"copies|30|{file_uuid}|photo"),
        ],
        [
            types.InlineKeyboardButton(text="40", callback_data=f"copies|40|{file_uuid}|photo"),
            types.InlineKeyboardButton(text="50", callback_data=f"copies|50|{file_uuid}|photo"),
            types.InlineKeyboardButton(text="75", callback_data=f"copies|75|{file_uuid}|photo"),
            types.InlineKeyboardButton(text="100", callback_data=f"copies|100|{file_uuid}|photo"),
        ],
        [
            types.InlineKeyboardButton(text="120", callback_data=f"copies|120|{file_uuid}|photo"),
        ]
    ])
    await message.answer("Detected post. How many copies do you want to make?", reply_markup=keyboard)

# Обработка видео от пользователя
@router.message(F.video)
async def handle_video(message: Message):
    video = message.video
    file = await message.bot.get_file(video.file_id)
    file_path = file.file_path
    ext = os.path.splitext(file_path)[1] or ".mp4"
    dest_path = os.path.join(TEMP_DIR, f"{video.file_id}{ext}")
    await message.bot.download_file(file_path, dest_path)
    # Сохраняем в кэш
    file_uuid = str(uuid.uuid4())
    file_cache[file_uuid] = dest_path
    # Вместо обработки, отправляем сообщение с выбором количества копий
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="5", callback_data=f"copies|5|{file_uuid}|video"),
            types.InlineKeyboardButton(text="10", callback_data=f"copies|10|{file_uuid}|video"),
            types.InlineKeyboardButton(text="20", callback_data=f"copies|20|{file_uuid}|video"),
            types.InlineKeyboardButton(text="30", callback_data=f"copies|30|{file_uuid}|video"),
        ],
        [
            types.InlineKeyboardButton(text="40", callback_data=f"copies|40|{file_uuid}|video"),
            types.InlineKeyboardButton(text="50", callback_data=f"copies|50|{file_uuid}|video"),
            types.InlineKeyboardButton(text="75", callback_data=f"copies|75|{file_uuid}|video"),
            types.InlineKeyboardButton(text="100", callback_data=f"copies|100|{file_uuid}|video"),
        ],
        [
            types.InlineKeyboardButton(text="120", callback_data=f"copies|120|{file_uuid}|video"),
        ]
    ])
    await message.answer("Detected post. How many copies do you want to make?", reply_markup=keyboard)




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
    await message.answer(f"🔗 Link received: {url}\n⏳ Downloading...")

    filetype = guess_file_type(url)
    try:
        if filetype in ('video', 'video-hosting'):
            filepath = await download_video(url)
            if not filepath:
                raise Exception("Failed to download video. It may be unavailable or deleted.")
        elif filetype == 'photo':
            filepath = await download_file(url)
        else:
            # Попробуем скачать как есть, но проверим content-type
            filepath = await download_file(url)
            # Check: if we downloaded html, not a file
            with open(filepath, 'rb') as f:
                head = f.read(512)
                if b'<html' in head.lower():
                    raise Exception("The link does not point to a file, but to a web page.")
        if not filepath:
            raise Exception("File was not downloaded")
        # Сохраняем в кэш
        file_uuid = str(uuid.uuid4())
        file_cache[file_uuid] = filepath
        # Вместо кнопки download, отправляем сообщение с выбором количества копий
        ext = os.path.splitext(filepath)[1].lower()
        media_type = "photo" if ext in {'.jpg', '.jpeg', '.png', '.webp'} else "video" if ext in {'.mp4', '.mov', '.avi', '.webm'} else "document"
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="5", callback_data=f"copies|5|{file_uuid}|{media_type}"),
                types.InlineKeyboardButton(text="10", callback_data=f"copies|10|{file_uuid}|{media_type}"),
                types.InlineKeyboardButton(text="20", callback_data=f"copies|20|{file_uuid}|{media_type}"),
                types.InlineKeyboardButton(text="30", callback_data=f"copies|30|{file_uuid}|{media_type}"),
            ],
            [
                types.InlineKeyboardButton(text="40", callback_data=f"copies|40|{file_uuid}|{media_type}"),
                types.InlineKeyboardButton(text="50", callback_data=f"copies|50|{file_uuid}|{media_type}"),
                types.InlineKeyboardButton(text="75", callback_data=f"copies|75|{file_uuid}|{media_type}"),
                types.InlineKeyboardButton(text="100", callback_data=f"copies|100|{file_uuid}|{media_type}"),
            ],
            [
                types.InlineKeyboardButton(text="120", callback_data=f"copies|120|{file_uuid}|{media_type}"),
            ]
        ])
        await message.answer("Detected post. How many copies do you want to make?", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"❌ Failed to download file: {e}")

# 2️⃣ Обработка кнопки (с путём к файлу)
@router.callback_query(F.data.startswith("download|"))
async def process_download(callback: CallbackQuery):
    await callback.message.answer("⏳ Processing file...")

    try:
        _, input_file = callback.data.split("|", 1)
        ext = os.path.splitext(input_file)[1].lower()
        if ext in {'.jpg', '.jpeg', '.png', '.webp'}:
            output_file = randomize_exif(input_file)
            await callback.message.answer_photo(types.FSInputFile(output_file), caption="✅ Done! Here is your file with new metadata.")
        elif ext in {'.mp4', '.mov', '.avi', '.webm'}:
            output_file = randomize_metadata(input_file)
            await callback.message.answer_video(types.FSInputFile(output_file), caption="✅ Done! Here is your file with new metadata.")
        else:
            output_file = randomize_metadata(input_file)
            await callback.message.answer_document(types.FSInputFile(output_file), caption="✅ Done! Here is your file with new metadata.")
    except Exception as e:
        await callback.message.answer(f"❌ Error: {e}")

# Обработка выбора количества копий
@router.callback_query(F.data.startswith("copies|"))
async def process_copies(callback: CallbackQuery):
    try:
        parts = callback.data.split("|")
        if len(parts) != 4:
            await callback.answer("Invalid data", show_alert=True)
            return
        _, count_str, file_uuid, media_type = parts
        count = int(count_str)
        if count < 1 or count > 120:
            await callback.answer("Invalid count", show_alert=True)
            return
        filepath = file_cache.get(file_uuid)
        if not filepath:
            await callback.answer("File not found", show_alert=True)
            return
        await callback.message.answer(f"⏳ Creating {count} copies...")

        session_id = str(uuid.uuid4())
        download_links = []

        for i in range(count):
            try:
                if media_type == "photo":
                    output_file = randomize_exif(filepath)
                elif media_type == "video":
                    output_file = randomize_metadata(filepath)
                else:
                    output_file = randomize_metadata(filepath)

                # Загружаем на S3
                key = f"{session_id}/copy_{i+1}{os.path.splitext(output_file)[1]}"
                s3_client.upload_file(output_file, S3_BUCKET_NAME, key)

                # Получаем presigned URL
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
                    ExpiresIn=3600  # 1 час
                )
                download_links.append(f"Copy {i+1}: {url}")

            except Exception as e:
                await callback.message.answer(f"❌ Error creating copy {i+1}: {e}")

        # Генерируем HTML-страницу с presigned URLs
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your File Copies</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .file-list {{ list-style: none; padding: 0; }}
        .file-list li {{ margin: 10px 0; }}
        .file-list a {{ color: #007bff; text-decoration: none; }}
        .file-list a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Your File Copies</h1>
    <p>Here are your {count} processed copies. Click to download (links valid for 1 hour):</p>
    <ul class="file-list">
"""

        for i, url in enumerate(download_links, 1):
            html_content += f'        <li><a href="{url}" download>Copy {i}</a></li>\n'

        html_content += """    </ul>
</body>
</html>"""

        # Загружаем HTML в S3
        html_key = f"{session_id}/index.html"
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=html_key, Body=html_content, ContentType='text/html')

        # Получаем presigned URL для HTML
        page_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': html_key},
            ExpiresIn=3600
        )

        await callback.message.answer(f"✅ Your copies are ready! View and download them here: {page_url}")

    except Exception as e:
        await callback.answer(f"❌ Error: {e}", show_alert=True)
