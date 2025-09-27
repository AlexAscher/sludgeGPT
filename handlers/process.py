from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from services.downloader import download_video
from services.video_edit import randomize_metadata

router = Router()


# 1️⃣ Обработка ссылки
@router.message(F.text.startswith("http"))
async def handle_link(message: Message):
    url = message.text.strip()
    await message.answer(f"🔗 Got link: {url}\n⏳ Downloading...")

    try:
        filepath = download_video(url)
        await message.answer(
            f"✅ Video saved: {filepath}\n\nNow choose an action:",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="📥 Download (randomize metadata)", callback_data="download")]
            ])
        )
    except Exception as e:
        await message.answer(f"❌ Failed to download video: {e}")


# 2️⃣ Обработка кнопки
@router.callback_query(F.data == "download")
async def process_download(callback: CallbackQuery):
    await callback.message.answer("⏳ Processing (Download mode)...")

    try:
        input_file = "data/temp/7338086447637105925.mp4"  # пока статично
        output_file = randomize_metadata(input_file)
        await callback.message.answer(f"✅ Done! File saved: {output_file}")
    except Exception as e:
        await callback.message.answer(f"❌ Error: {e}")
