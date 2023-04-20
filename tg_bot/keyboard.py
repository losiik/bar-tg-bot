from aiogram import types

keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_menu = types.KeyboardButton(text="Меню")
button_promo = types.KeyboardButton(text="Акции")
button_bonus = types.KeyboardButton(text="Бонусная система")
button_review = types.KeyboardButton(text="Оставить отзыв")

keyboard_main.add(button_menu, button_promo)
keyboard_main.add(button_bonus, button_review)

pay_keyboard = types.InlineKeyboardMarkup()
button_pay = types.InlineKeyboardButton('Оплатить заказ', callback_data="pay")
button_use_bonus = types.InlineKeyboardButton('Использовать бонусы', callback_data="use_bonus")
pay_keyboard.add(button_pay, button_use_bonus)