import os
import logging
import redis

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from requests_to_moltin import (
    show_shop_products, get_product, get_url_photo,
    add_product_to_cart, show_cart, calculate_price,
    delete_product_to_cart, add_contact
)


logger = logging.getLogger(__name__)

_database = None


def start(bot, update):
    products = show_shop_products()
    products_name = []
    for product in products:
        keyboard = [
            InlineKeyboardButton(product['name'], callback_data=product['id']),
        ]
        products_name.append(keyboard)
    products_name.append(
        [InlineKeyboardButton('Корзина', callback_data='Корзина')]
    )
    reply_markup = InlineKeyboardMarkup(products_name)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_menu(bot, update):
    query = update.callback_query
    product = get_product(query.data)
    text = f"{product['name']}\n\n{product['meta']['display_price']['with_tax']['formatted']} per kg\n{product['weight']['kg']} kg on stock\n\n{product['description']}"
    photo_url = get_url_photo(
        product['relationships']['main_image']['data']['id']
    )
    keyboard = [
        [
            InlineKeyboardButton('Назад', callback_data='Назад')
        ],
        [
            InlineKeyboardButton(
                '1 kg', callback_data=f"1 {query.data} {product['name']}"
            ),
            InlineKeyboardButton(
                '5 kg', callback_data=f"5 {query.data} {product['name']}"
            ),
            InlineKeyboardButton(
                '10 kg', callback_data=f"10 {query.data} {product['name']}"
            ),
        ],
        [
            InlineKeyboardButton('Корзина', callback_data='Корзина')
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_photo(
        chat_id=query.message.chat_id, photo=photo_url,
        caption=text, reply_markup=reply_markup
    )
    bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )
    return 'HANDLE_DESCRIPTION'


def handle_description(bot, update):
    user_reply = update.callback_query.data
    chat_id = update.callback_query.message.chat_id
    query = update.callback_query
    if user_reply == 'Оплатить':
        bot.send_message(chat_id=chat_id, text='Пожалуйста, пришлите ваш email')
        return 'WAITING_EMAIL'

    if user_reply == 'Назад' or user_reply == 'Меню':
        bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        return 'HANDLE_MENU'

    if 'Убрать' in user_reply:
        quantity, product_id, product_name = user_reply.split()
        delete_product_to_cart(chat_id, product_id)
        update.callback_query.answer(
            f" Продукт {product_name} удален из корзины!", show_alert=True
        )
        bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        return 'HANDLE_DESCRIPTION'

    if set(user_reply.split()) & {'1', '5', '10'}:
        quantity, product_id, product_name = user_reply.split()
        add_product_to_cart(chat_id, product_id, quantity)
        update.callback_query.answer(
            f"{product_name} в размере {quantity}кг успешно добавлен в корзину!",
            show_alert=True
        )
    return 'HANDLE_DESCRIPTION'


def handle_cart(bot, update):
    query = update.callback_query
    chat_id = update.callback_query.message.chat_id
    products = show_cart(chat_id)
    total_sum = calculate_price(chat_id)
    description_cart = ''
    products_name = []
    for product in products['data']:
        text = f"{product['name']}\n{product['description']}\n{product['meta']['display_price']['with_tax']['unit']['formatted']} per kg\n{product['quantity']} kg in cart for {product['meta']['display_price']['with_tax']['value']['formatted']}\n\n"
        description_cart += text
        keyboard = [
            InlineKeyboardButton(
                f"Убрать из корзины {product['name']}",
                callback_data=f"Убрать {product['id']} {product['name']}"
            )
        ]
        products_name.append(keyboard)
    description_cart += total_sum
    products_name.append([InlineKeyboardButton('В меню', callback_data='Меню')])
    products_name.append([InlineKeyboardButton('Оплатить', callback_data='Оплатить')])
    reply_markup = InlineKeyboardMarkup(products_name)
    bot.send_message(
        chat_id=chat_id, text=description_cart,
        reply_markup=reply_markup
    )
    bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )
    return 'HANDLE_DESCRIPTION'


def waiting_email(bot, update):
    email = update.message.text
    chat_id = update.message.chat_id
    update.message.reply_text(text=f"Ваш email: {email}")
    add_contact(chat_id, email)
    return 'START'


def handle_users_reply(bot, update):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    elif user_reply == 'Корзина':
        user_state = 'HANDLE_CART'
    else:
        user_state = db.get(chat_id).decode('utf-8')

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email,
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv('REDIS_DATABASE_PASSWORD')
        database_host = os.getenv('REDIS_HOST')
        database_port = os.getenv('REDIS_PORT')
        _database = redis.Redis(
            host=database_host, port=database_port,
            password=database_password
        )
    return _database


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('TG_BOT_TOKEN')
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(logging.DEBUG)

    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()