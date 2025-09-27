import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from aiogram.client.default import DefaultBotProperties
from handlers import start, help, process

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    # регистрируем хендлеры
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(process.router)

    print("🤖 Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
