import asyncio
import logging
import sys
from os import getenv

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, BotCommand

from Planning_the_day import Calendar, Event, Day
from Checking_the_data import Checking_the_data

dp = Dispatcher()

storage: Calendar = Calendar() #БД дней
checking: Checking_the_data = Checking_the_data()#для проверки данных

HOLIDAY_API_URL: str = 'https://calendarific.com/api/v2/holidays' #api сайта про праздники


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, <b>{message.from_user.full_name}</b>! \n"
        f"Здесь ты можешь планировать свои дни \n"
        f"У нас есть такие функции:"
        f"- /create YYYY-MM-DD HH:MM Описание - создать пометку о событии\n"
        f"- /delete YYYY-MM-DD HH:MM - удалить пометку о событии\n"
        f"- /update YYYY-MM-DD HH:MM Описание - редактирование пометки и событии\n"
        f"- /read YYYY-MM-DD - показать все запланированные событие на эту дату\n"
    )


@dp.message(Command('create'))
async def command_start_handler(message: Message) -> None:
    args: str = message.text.split(maxsplit=3)

    if len(args) < 4:
        await message.answer(
            "Пожалуйста, укажите дату, время и описание события в формате:\n/create YYYY-MM-DD HH:MM Описание")
        return

    date: str = args[1].strip()  # Удаляем лишние пробелы
    time: str = args[2].strip()
    description: str = args[3].strip()

    if checking.checking_the_data(date, time):
        event: Event = Event(time, description)

        # Проверяем наличие дня с такой датой
        day_exists: bool = False
        event_exists: bool = False
        existing_day = None #type Day

        for day in storage.days:
            if day.date == date:
                day_exists = True
                existing_day = day
                for ev in day.events:
                    if ev.event_time == time:
                        event_exists = True
                        break
                break

        if event_exists:
            await message.answer(f"На это время событие уже было добавлено.")
        elif day_exists:
            # Если день существует, добавляем событие к нему
            existing_day.create_event(event)
            await message.answer(f"Событие добавлено: {event.event_time} - {event.description}")
        else:
            # Если дня нет, создаем новый день и добавляем событие
            day: Day = Day(date)
            day.create_event(event)
            storage.create_day_event(day)
            await message.answer(f"Событие добавлено: {event.event_time} - {event.description}")

    else:
        await message.answer(
            "Дата или время указанно не правильно, пожалуйста, повторите попытку")


@dp.message(Command('delete'))
async def command_start_handler(message: Message) -> None:
    args: str = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.answer(
            "Пожалуйста, укажите дату и время события в формате:\n/delete YYYY-MM-DD HH:MM ")
        return

    event_found: bool = False
    date: str = args[1]
    time: str = args[2]

    if checking.checking_the_data(date, time):
        for day in storage.days:
            if day.date == date:
                for ev in day.events:
                    if ev.event_time == time:
                        # Удаляем событие
                        storage.delete_day_event(date, time)
                        await message.answer(f"Событие удалено")
                        event_found = True
                        break  # Выходим из внутреннего цикла

                if event_found:
                    break  # Выходим из внешнего цикла, если событие было найдено и удалено

        if not event_found:
            await message.answer(f"На эту дату и время ничего не запланировано.")
    else:
        await message.answer(
            "Дата или время указанно не правильно, пожалуйста, повторите попытку")


@dp.message(Command('update'))
async def command_start_handler(message: Message) -> None:
    args: str = message.text.split(maxsplit=3)

    if len(args) < 4:
        await message.answer(
            "Пожалуйста, укажите дату, время и описание события в формате:\n/update YYYY-MM-DD HH:MM Описание ")
        return

    event_found: bool = False
    date: str = args[1]
    time: str = args[2]
    description: str = args[3]

    if checking.checking_the_data(date, time):
        for day in storage.days:
            if day.date == date:
                for ev in day.events:
                    if ev.event_time == time:
                        storage.update_day_event(date, time, description)
                        await message.answer(f"Событие изменено")
                        event_found = True
                        break

                if event_found:
                    break

        if not event_found:
            await message.answer(f"На эту дату и время ничего не запланировано.")
    else:
        await message.answer(
            "Дата или время указанно не правильно, пожалуйста, повторите попытку")


@dp.message(Command('read'))
async def command_start_handler(message: Message) -> None:
    args: str = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            "Пожалуйста, укажите дату в формате:\n/update YYYY-MM-DD ")
        return

    date: str = args[1]

    if checking.checking_the_date(date):
        url: str = f"{HOLIDAY_API_URL}?api_key=GefRUHUFs4vxFE1bhoUEwIkCAJE8OSBJ&country=RU&year={date[:4]}"

        all_events: list[str] = storage.read_day_event(date)
        events_list: str = "\n".join(all_events) if all_events else "Нет локальных событий."
        await message.answer(f"События на {date}:\n{events_list}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    holidays = data.get('response', {}).get('holidays', [])

                    # Фильтруем праздники по указанной дате
                    matching_holidays: list = [
                        holiday for holiday in holidays if holiday['date']['iso'].split('T')[0] == date
                    ]

                    if not matching_holidays:
                        await message.answer(f"Нет праздников на {date}.")
                    else:
                        # Формируем список названий праздников
                        holidays_list: str = "\n".join(
                            [f"{holiday['name']} - {holiday['description']}" for holiday in matching_holidays]
                        )
                        await message.answer(f"Праздники на {date}:\n{holidays_list}")
                else:
                    await message.answer(f"Ошибка при получении данных о праздниках. Код ошибки: {response.status}")
    else:
        await message.answer(
            "Дата указанна не правильно, пожалуйста, повторите попытку")


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
    asyncio.run(main())
