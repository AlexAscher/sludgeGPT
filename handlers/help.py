from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 <b>Help</b>\n\n"
        "1️⃣ Send a link to a video or profile.\n"
        "2️⃣ Choose an option: download, overlay, filter.\n"
        "3️⃣ Get your unique video 🎬\n\n"
        "❗ If the bot freezes — clear chat and restart."
    )
