import logging
import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from fetcher import fetch_all_data, filter_and_sort, format_coin_data

# Logging config
logging.basicConfig(level=logging.INFO)

# Load token dari .env
load_dotenv()
BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")

bot = Bot(token=BOT_API_TOKEN)
router = Router()


@router.message(Command("cheapest100"))
async def cheapest100_handler(message: types.Message):
    try:
        logging.info("Memulai proses /cheapest100")
        all_coins = await fetch_all_data()
        logging.info(f"Total coin yang diambil: {len(all_coins)}")

        filtered = filter_and_sort(all_coins)
        logging.info(f"Total coin setelah filter: {len(filtered)}")

        top = filtered[:100]
        if top:
            formatted = format_coin_data(top)
            await message.answer(
                f"🔥 <b>Coin Termurah (Uptrend di Semua Timeframe)</b>\n\n{formatted}",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.answer("⚠️ Tidak ada koin yang memenuhi kriteria.")

    except Exception as e:
        logging.error(f"Terjadi error di /cheapest100: {e}")
        await message.answer(f"❌ Terjadi kesalahan: <code>{e}</code>", parse_mode=ParseMode.HTML)


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
