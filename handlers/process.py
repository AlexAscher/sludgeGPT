

# ...existing code...


from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from services.downloader import download_video
from services.video_edit import randomize_metadata
from services.photo_edit import randomize_exif
from services.tools_edit import autocrop_photo, autocrop_video, video_to_gif
import mimetypes
import aiohttp
import os
from config import TEMP_DIR


router = Router()

# Импорт autocaption_video и регистрация caption_handler строго после router

# Autocrop callback

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("autocrop_handler")

@router.callback_query(F.data == "autocrop")
async def autocrop_handler(callback: CallbackQuery):
    try:
        logger.info(f"Autocrop called. Message: {callback.message}")
        # Определяем тип медиа
        if callback.message.photo:
            logger.info("Detected photo. Getting file_id...")
            file_id = callback.message.photo[-1].file_id
            logger.info(f"Photo file_id: {file_id}")
            file = await callback.bot.get_file(file_id)
            file_path = file.file_path
            logger.info(f"Telegram file_path: {file_path}")
            dest_path = os.path.join(TEMP_DIR, f"{file_id}.jpg")
            logger.info(f"Downloading photo to {dest_path}")
            await callback.bot.download_file(file_path, dest_path)
            logger.info(f"Downloaded photo exists: {os.path.exists(dest_path)} size: {os.path.getsize(dest_path) if os.path.exists(dest_path) else 'N/A'}")
            output_file = autocrop_photo(dest_path)
            logger.info(f"Photo autocropped. Output: {output_file}")
            logger.info(f"Autocropped photo exists: {os.path.exists(output_file)} size: {os.path.getsize(output_file) if os.path.exists(output_file) else 'N/A'}")
            # Сначала отправляем как новое сообщение, чтобы получить file_id
            try:
                sent = await callback.message.answer_photo(types.FSInputFile(output_file), caption="✅ Cropped to square!")
                logger.info(f"Sent photo message: {sent}")
            except Exception as e:
                logger.exception(f"Failed to send autocropped photo: {e}")
                await callback.answer(f"Failed to send cropped photo: {e}", show_alert=True)
                return
            photo_file_id = sent.photo[-1].file_id if sent.photo else None
            logger.info(f"photo_file_id: {photo_file_id}")
            if photo_file_id:
                try:
                    await callback.message.edit_media(
                        types.InputMediaPhoto(media=photo_file_id, caption="✅ Cropped to square!"),
                        reply_markup=callback.message.reply_markup
                    )
                    logger.info("edit_media for photo successful")
                    await sent.delete()
                except Exception as e:
                    logger.exception(f"edit_media for photo failed: {e}")
                    await callback.answer(f"edit_media failed: {e}", show_alert=True)
            else:
                logger.warning("Failed to get file_id from sent photo.")
                await callback.answer("Failed to upload cropped photo.", show_alert=True)
        elif callback.message.video:
            logger.info("Detected video. Getting file_id...")
            file_id = callback.message.video.file_id
            logger.info(f"Video file_id: {file_id}")
            file = await callback.bot.get_file(file_id)
            file_path = file.file_path
            logger.info(f"Telegram file_path: {file_path}")
            ext = os.path.splitext(file_path)[1] or ".mp4"
            dest_path = os.path.join(TEMP_DIR, f"{file_id}{ext}")
            logger.info(f"Downloading video to {dest_path}")
            await callback.bot.download_file(file_path, dest_path)
            logger.info(f"Downloaded video exists: {os.path.exists(dest_path)} size: {os.path.getsize(dest_path) if os.path.exists(dest_path) else 'N/A'}")
            output_file = autocrop_video(dest_path)
            logger.info(f"Video autocropped. Output: {output_file}")
            logger.info(f"Autocropped video exists: {os.path.exists(output_file)} size: {os.path.getsize(output_file) if os.path.exists(output_file) else 'N/A'}")
            if not os.path.exists(output_file):
                logger.error(f"Autocropped video file not found: {output_file}")
                await callback.answer(f"Autocropped video file not found: {output_file}", show_alert=True)
                return
            # Сначала отправляем как новое сообщение, чтобы получить file_id
            try:
                sent = await callback.message.answer_video(types.FSInputFile(output_file), caption="✅ Cropped to square!")
                logger.info(f"Sent video message: {sent}")
            except Exception as e:
                logger.exception(f"Failed to send autocropped video: {e}")
                await callback.answer(f"Failed to send cropped video: {e}", show_alert=True)
                return
            video_file_id = sent.video.file_id if sent.video else None
            logger.info(f"video_file_id: {video_file_id}")
            if video_file_id:
                try:
                    await callback.message.edit_media(
                        types.InputMediaVideo(media=video_file_id, caption="✅ Cropped to square!"),
                        reply_markup=callback.message.reply_markup
                    )
                    logger.info("edit_media for video successful")
                    await sent.delete()
                except Exception as e:
                    logger.exception(f"edit_media for video failed: {e}")
                    await callback.answer(f"edit_media failed: {e}", show_alert=True)
            else:
                logger.warning("Failed to get file_id from sent video.")
                await callback.answer("Failed to upload cropped video.", show_alert=True)
        else:
            logger.warning("No photo or video detected in message.")
            await callback.answer("Only works for photo or video!", show_alert=True)
    except Exception as e:
        logger.exception(f"Autocrop failed: {e}")
        await callback.answer(f"Autocrop failed: {e}", show_alert=True)

# Convert to GIF callback
@router.callback_query(F.data == "convert_gif")
async def convert_gif_handler(callback: CallbackQuery):
    try:
        if callback.message.video:
            file_id = callback.message.video.file_id
            file = await callback.bot.get_file(file_id)
            file_path = file.file_path
            ext = os.path.splitext(file_path)[1] or ".mp4"
            dest_path = os.path.join(TEMP_DIR, f"{file_id}{ext}")
            await callback.bot.download_file(file_path, dest_path)
            output_file = video_to_gif(dest_path)
            # Сначала отправляем GIF как новое сообщение, чтобы получить file_id
            sent = await callback.message.answer_animation(types.FSInputFile(output_file), caption="✅ Converted to GIF!")
            gif_file_id = sent.animation.file_id if sent.animation else None
            if gif_file_id:
                await callback.message.edit_media(
                    types.InputMediaAnimation(media=gif_file_id, caption="✅ Converted to GIF!"),
                    reply_markup=callback.message.reply_markup
                )
                await sent.delete()
            else:
                await callback.answer("Failed to upload GIF.", show_alert=True)
        else:
            await callback.answer("Only works for video!", show_alert=True)
    except Exception as e:
        await callback.answer(f"Convert to GIF failed: {e}", show_alert=True)




## Удалено дублирование импортов и router = Router()


# Tools menu callback (edit message)

@router.callback_query(F.data == "tools")
async def show_tools_menu(callback: CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Convert to GIF", callback_data="convert_gif")],
        [types.InlineKeyboardButton(text="Autocrop", callback_data="autocrop")],
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
    output_file = randomize_exif(dest_path)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Download", callback_data="download_photo")],
        [types.InlineKeyboardButton(text="Templates", callback_data="templates"), types.InlineKeyboardButton(text="Tools", callback_data="tools")],
        [types.InlineKeyboardButton(text="Bulk Templates", callback_data="bulk_templates"), types.InlineKeyboardButton(text="Bulk Randomize", callback_data="bulk_randomize")],
        [types.InlineKeyboardButton(text="Get Paid to Post 💰", callback_data="get_paid")],
        [types.InlineKeyboardButton(text="Monthly Subscription", callback_data="monthly_sub")],
        [types.InlineKeyboardButton(text="Annual Subscription (3 months free)", callback_data="annual_sub")],
    ])
    await message.answer_photo(types.FSInputFile(output_file), caption="✅ Done! Here is your photo with new metadata.", reply_markup=keyboard)

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
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Download", callback_data="download_video")],
        [types.InlineKeyboardButton(text="Templates", callback_data="templates"), types.InlineKeyboardButton(text="Tools", callback_data="tools")],
        [types.InlineKeyboardButton(text="Bulk Templates", callback_data="bulk_templates"), types.InlineKeyboardButton(text="Bulk Randomize", callback_data="bulk_randomize")],
        [types.InlineKeyboardButton(text="Get Paid to Post 💰", callback_data="get_paid")],
        [types.InlineKeyboardButton(text="Monthly Subscription", callback_data="monthly_sub")],
        [types.InlineKeyboardButton(text="Annual Subscription (3 months free)", callback_data="annual_sub")],
    ])
    await message.answer_video(types.FSInputFile(output_file), caption="✅ Done! Here is your video with new metadata.", reply_markup=keyboard)




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
        await message.answer(
            f"✅ File saved: {filepath}\n\nChoose an action:",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="📥 Download (randomize metadata)", callback_data=f"download|{filepath}")]
            ])
        )
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
