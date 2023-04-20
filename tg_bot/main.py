import datetime

from aiogram import types
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiohttp

import ast

from keyboard import keyboard_main, pay_keyboard


bot = Bot(token="5996297773:AAHvc2w7_JynE5bqq8aZSvEUojG06MlX4hk")
# Диспетчер
dp = Dispatcher(bot, storage=MemoryStorage())


class Review(StatesGroup):
    review_content = State()


orders = {}


async def check_data(chat_id):
    text = 'Чек:\n\n'
    total_price = 0

    for key in orders[chat_id]['order']['data'].keys():
        text += key
        text += ':'
        text += f" {orders[chat_id]['order']['data'][key][1]}"
        text += f" x{orders[chat_id]['order']['data'][key][0]}"
        text += '\n'

        total_price += orders[chat_id]['order']['data'][key][1] * orders[chat_id]['order']['data'][key][0]
    text += '\n'
    text += f'Итог: {total_price}'
    return text


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Hello! " + message.from_user.first_name, reply_markup=keyboard_main)


@dp.message_handler(text="Меню")
async def get_menu(message: types.Message):
    menu_text = ''
    category = {
        'ALCO': 'Алкогольные напитки',
        'NONALCO': 'Безалкогольные напитки',
        'SNACK': 'Закуски',
        'MAIN': 'Основные блюда',
    }

    units = {
        'N': '-',
        'G': 'гр.',
        'M': 'мл.',
    }

    url = 'http://127.0.0.1:8000/api/menu/'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            menu_response = await resp.read()

    menu_response = ast.literal_eval(menu_response.decode('utf-8'))
    menu = menu_response['menu']
    menu_sorted = sorted(menu, key=lambda d: d['category'])

    category_type = category[menu_sorted[0]['category']]
    await bot.send_message(message.from_user.id, text=f'*{category_type}*', parse_mode="Markdown")

    for menu_param in menu_sorted:
        if category[menu_param['category']] != category_type:
            category_type = category[menu_param['category']]
            await bot.send_message(message.from_user.id, text=f'*{category_type}*', parse_mode="Markdown")

        menu_text += f"*{menu_param['title']}*" + '\n'
        menu_text += menu_param['weight_volume'] + ' ' + units[menu_param['units']] + '\n'
        menu_text += menu_param['energy_value'] + ' кКл' + '\n'
        menu_text += menu_param['price'] + ' руб.' + '\n'
        menu_text += f"*Подробное описание:*" + '\n'
        menu_text += menu_param['description'] + '\n'
        photo = open(f"../{menu_param['photo']}", 'rb')

        add_to_order = types.InlineKeyboardMarkup()
        add_to_order_btn_add = types.InlineKeyboardButton('+', callback_data=f"add_{menu_param['title']}")
        add_to_order_btn_amount = types.InlineKeyboardButton('0', callback_data=f"amount_{menu_param['title']}")
        add_to_order_btn_del = types.InlineKeyboardButton('-', callback_data=f"del_{menu_param['title']}")
        add_to_order.add(add_to_order_btn_add, add_to_order_btn_amount, add_to_order_btn_del)

        await bot.send_photo(message.from_user.id,
                             photo=photo,
                             caption=menu_text,
                             parse_mode="Markdown",
                             reply_markup=add_to_order)
        menu_text = ''

    check_msg = await bot.send_message(message.from_user.id, 'Чек:', reply_markup=pay_keyboard)
    orders[check_msg['chat']['id']] = {'order': {'message_id': check_msg['message_id'], 'data': {}}}
    print(orders)


@dp.message_handler(text="Акции")
async def get_promo(message: types.Message):
    promo_text = ''

    url = 'http://127.0.0.1:8000/api/promo/'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            promo_response = await resp.read()

    promo_data = ast.literal_eval(promo_response.decode('utf-8'))

    for promo in promo_data['promo']:
        promo_text += f"*{promo['title']}*" + '\n'
        promo_text += promo['description'] + '\n' + '\n'

    await message.answer(promo_text, parse_mode="Markdown")


@dp.message_handler(text="Оставить отзыв")
async def start_review(message: types.Message):
    await message.answer("Напишите отзыв")
    await Review.review_content.set()


@dp.message_handler(content_types=['text'], state=Review.review_content)
async def create_review(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['review'] = message.text
        await state.finish()

    review = await state.get_data()
    review = review['review']

    url = 'http://127.0.0.1:8000/api/review/'

    review_data = {
        'from_username': message.from_user.first_name,
        'review_content': review,
        'data': datetime.datetime.now()
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=review_data) as resp:
            review_response = await resp.read()

    review_response = review_response.decode("utf-8")

    if review_response == '"review saved successful"':
        await message.answer('Ваш отзыв сохранен успешно')
    else:
        await message.answer('Во время записи отзыва произошла ошибка. Попробуйте еще раз')


@dp.callback_query_handler(lambda call: True)
async def create_order(callback_query: types.CallbackQuery):
    position_data = callback_query.values['message']['caption']
    position_data = position_data.split('\n')
    name = position_data[0]
    price = float(position_data[3].split(' ')[0])
    chat_id = callback_query['from']['id']
    inline_buttons_data = callback_query.values['message']['reply_markup']['inline_keyboard'][0]
    amount = int(inline_buttons_data[1]['text'])
    if 'add_' in callback_query.data:
        amount += 1
    if 'del' in callback_query.data and amount > 0:
        amount -= 1

    orders[chat_id]['order']['data'][name] = [amount, price]
    add_to_order = types.InlineKeyboardMarkup()
    add_to_order_btn_add = types.InlineKeyboardButton('+',
                                                      callback_data=inline_buttons_data[0]['callback_data'])
    add_to_order_btn_amount = types.InlineKeyboardButton(f'{amount}',
                                                         callback_data=inline_buttons_data[1]['callback_data'])
    add_to_order_btn_del = types.InlineKeyboardButton('-',
                                                      callback_data=inline_buttons_data[2]['callback_data'])
    add_to_order.add(add_to_order_btn_add, add_to_order_btn_amount, add_to_order_btn_del)
    await callback_query.message.edit_reply_markup(add_to_order)

    await bot.edit_message_text(chat_id=chat_id,
                                message_id=orders[chat_id]['order']['message_id'],
                                text=await check_data(chat_id),
                                reply_markup=pay_keyboard)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)