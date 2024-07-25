import asyncio, logging, config
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router, set_bot, setup_handlers
from db import UsersDataBase, HomeWorkBase


async def main():
    global bot, dp
    bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(router)
    db = UsersDataBase()
    db_work = HomeWorkBase()
    set_bot(bot)
    setup_handlers()
    await db.create_table()
    await db_work.create_table()
    await bot.delete_webhook(drop_pending_updates=True)
    tasks = [dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())]
    await asyncio.gather(*tasks)


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
