import logging
import os
from random import choice

from emoji import emojize
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler

import config
from image_get import color_image, what_is

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', level=logging.INFO, filename='bot.log')


def get_smile():
    smile = emojize(choice(config.EMOJI_LIST), use_aliases=True)
    return smile


def talking(bot, update):
    smile = get_smile()
    user_text = "Привет, {}! Ты можешь колоризовать своё черно-белое фото или же с помощью нейросети распознать" \
                " что же находится на фото. Для начала работы просто отправь фотографию! {} ".format(
                                                                        update.message.chat.first_name, smile)
    logging.info(user_text)
    update.message.reply_text(user_text, reply_markup=ReplyKeyboardRemove())


def download_photo(bot, update):
    os.makedirs('downloads', exist_ok=True)
    input_photo = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', '{}.jpg'.format(input_photo.file_id))
    input_photo.download(filename)
    return filename


def send_photo(bot, update, url, user_data):
    chat_id = user_data['chat_id']
    bot.send_photo(chat_id, url)


def photo_reply1(bot, update, user_data):
    chat_id = update.message.chat.id
    filename = download_photo(bot, update)
    image_file = open(filename, 'rb')
    url = color_image(image_file)
    send_photo(bot, update, url, user_data)
    what = what_is(filename)
    bot.send_message(chat_id, what)


def photo_reply(bot, update, user_data):
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Колоризация', callback_data='color')],
            [InlineKeyboardButton(text='Распознавание', callback_data='what')],
            [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
        ],
    )
    update.message.reply_text("Выберите что именно вы хотите сделать с фото?", reply_markup=inline_buttons)
    filename = download_photo(bot, update)
    chat_id = update.message.chat.id
    user_data['filename'] = filename
    user_data['chat_id'] = chat_id


def photo_final(bot, update, user_data):
    update.callback_query.answer()
    choose = update.callback_query.data
    filename = user_data['filename']
    chat_id = user_data['chat_id']
    if choose == 'color':
        smile = get_smile()
        bot.send_message(chat_id, '{} Обрабатываю фото...'.format(smile))
        image_file = open(filename, 'rb')
        url = color_image(image_file)
        send_photo(bot, update, url, user_data)
    if choose == 'what':
        smile = get_smile()
        bot.send_message(chat_id, '{} Обрабатываю фото...'.format(smile))
        what = what_is(filename)
        bot.send_message(chat_id, what)
    if choose == 'cancel':
        bot.send_message(chat_id, 'Отменено.')
        return


def main():
    my_bot = Updater(config.API_KEY)
    dispatcher = my_bot.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text, talking))
    dispatcher.add_handler(MessageHandler(Filters.photo, photo_reply, pass_user_data=True))
    dispatcher.add_handler(CallbackQueryHandler(photo_final, pass_user_data=True))
    my_bot.start_polling()
    my_bot.idle()


if __name__ == "__main__":
    main()
