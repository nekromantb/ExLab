from collector import get_data
from aiogram import Bot, Dispatcher, executor, types
from auth_data import token
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hlink
import json


def tg_bot():
    bot = Bot(token, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)

    @dp.message_handler(commands="start")
    async def start(message: types.Message):
        start_buttons = ["1 room", "2 rooms", "3 rooms", "Search"]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*start_buttons)

        await message.answer("New offers for renting apartments in Minsk", reply_markup=keyboard)

    num_for_output = 3
    room_count = []

    @dp.message_handler(Text(equals="1 room"))
    async def get_room_count1(message: types.Message):
        if '1' not in room_count:
            room_count.append('1')
            output = "Now searching: " + "_room ".join(room_count)+"_room." if room_count else ""
            await message.answer("You choose 1 room apartments for searching. " + output)
        else:
            room_count.remove('1')
            output = "Now searching: " + "_room ".join(room_count)+"_room." if room_count else ""
            await message.answer("You deleted 1 room apartments from searching. " + output)

    @dp.message_handler(Text(equals="2 rooms"))
    async def get_room_count2(message: types.Message):
        if '2' not in room_count:
            room_count.append('2')
            output = "Now searching: " + "_room ".join(room_count)+"_room." if room_count else ""
            await message.answer("You choose 2 room apartments for searching. " + output)
        else:
            room_count.remove('2')
            output = "Now searching: " + "_room ".join(room_count)+"_room." if room_count else ""
            await message.answer("You deleted 2 room apartments from searching. " + output)

    @dp.message_handler(Text(equals="3 rooms"))
    async def get_room_count3(message: types.Message):
        if '3' not in room_count:
            room_count.append('3')
            output = "Now searching: " + "_room ".join(room_count)+"_room." if room_count else ""
            await message.answer("You choose 3 room apartments for searching. " + output)
        else:
            room_count.remove('3')
            output = "Now searching: " + "_room ".join(room_count)+"_room." if room_count else ""
            await message.answer("You deleted 3 room apartments from searching. " + output)

    @dp.message_handler(Text(equals="Search"))
    async def get_search(message: types.Message):
        await message.answer("Searching...")

        get_data(num_for_output, room_count)

        with open('data/1_data.json') as file:
            data = json.load(file)

        for apartment in data:
            card = f'{hlink(apartment.get("address"), apartment.get("url"))}\n'\
                   f'{hbold("Description: ")}{apartment.get("description")}\n'\
                   f'{hbold("Phone: ")}{apartment.get("phone_number")}'

            await message.answer(card)

    executor.start_polling(dp)
