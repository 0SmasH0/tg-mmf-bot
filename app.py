import schedule
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeAllPrivateChats

from function.download_data import download_menu_food, download_schedule, download_subgroups
from function.render_image_menu import render
from function.work_with_date import get_number_week, check_saturday_sunday

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from handlers.user_private import user_private_router
from common.bot_commands_list import private

ALLOWED_UPDATES = ['message', 'edited_message']

bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

dp.include_router(user_private_router)


async def downloads_files():
    while True:
        if not check_saturday_sunday():
            schedule.every().day.at("19:00").do(download_schedule)
            schedule.every().day.at("08:00").do(download_menu_food)
            schedule.every().day.at("08:10").do(render)

        schedule.every().day.at("18:00").do(get_number_week)
        schedule.run_pending()
        await asyncio.sleep(30)


async def tg_bot():
    await bot.delete_webhook(drop_pending_updates=True)  # не отвечает на сообщения,когда бот был офлайн
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


async def main():
    await asyncio.gather(tg_bot(), downloads_files())


if __name__ == "__main__":
    asyncio.run(main())
