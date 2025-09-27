from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()

# keyboard
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📥 Download")],
        [KeyboardButton(text="🖼 Add Overlay")],
        [KeyboardButton(text="🧠 Retention Filter")],
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "❓ <b>SLUDGE AI FAQ</b> ❓\n\n"
        "Welcome 🚀\n\n"
        "👀 Send me a link to a video or a profile, then choose an option:\n"
        "📥 Download\n🖼 Overlay\n🧠 Retention Filter",
        reply_markup=main_kb
    )
