import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, BotCommand

from Planning_the_day import Calendar, Event, Day

dp = Dispatcher()

storage = Calendar()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    # message - объект контекста для работы с сообщениями
    await message.answer(
        f"Привет, <b>{message.from_user.full_name}</b>! \n"
        f"Здесь ты можешь планировать свои дни "
    )


@dp.message(Command('create'))
async def command_start_handler(message: Message) -> None:
    args = message.text.split(maxsplit=3)

    date = args[1]
    time = args[2]
    description = args[3]

    event = Event(time, description)

    # Создаем объект Day с указанной датой
    day = Day(date)
    day.create_event(event)

    # Сохраняем день в хранилище
    storage.create_day_event(day)

    await message.answer(f"Событие добавлено: {event.event_time} - {event.description}")


@dp.message(Command('delete'))
async def command_start_handler(message: Message) -> None:
    args = message.text.split(maxsplit=3)

    date = args[1]
    time = args[2]

    storage.delete_day_event(date, time)

    await message.answer(f"Событие удалено")


@dp.message(Command('update'))
async def command_start_handler(message: Message) -> None:
    args = message.text.split(maxsplit=3)

    date = args[1]
    time = args[2]
    description = args[3]

    # Сохраняем день в хранилище
    storage.update_day_event(date, time, description)

    await message.answer(f"Событие исправлено")

@dp.message(Command('read'))
async def command_start_handler(message: Message) -> None:
    args = message.text.split(maxsplit=3)

    date = args[1]

    all_events = storage.read_day_event(date)
    events_list = "\n".join(all_events)
    await message.answer(f"События на {date}:\n{events_list}")


async def main() -> None:
    TOKEN = getenv("BOT_TOKEN")

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands([
        BotCommand(command='/start', description='Начало работы'),
        BotCommand(command='/create', description='Добавить событие'),
        BotCommand(command='/delete', description='Удалить событие'),
        BotCommand(command='/update', description='Редактировать событие'),
        BotCommand(command='/read', description='Посмотреть события за день'),

    ])

    # запускаем диспетчер
    await dp.start_polling(bot)


if __name__ == "__main__":
    # установка логов
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    # запуск asyncio (про асинхронность кратко https://blog.skillfactory.ru/glossary/asinhronnoe-programmirovanie/)
    asyncio.run(main())
