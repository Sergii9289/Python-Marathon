from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from dotenv import load_dotenv
import os

from gpt import *
from util import *

load_dotenv(dotenv_path='config.env')
TG_TOKEN = os.getenv('TG_TOKEN')
AI_TOKEN = os.getenv('AI_TOKEN')

dialog = Dialog()  # створюємо екземпляр порожнього класу Dialog
dialog.mode = 'main'  # Додаємо новий атрибут mode до об'єкту dialog та призначаємо йому значення 'main' as default
dialog.list = []  # порожній список для накопичування повідомлень

chatgpt = ChatGptService(token=AI_TOKEN)


async def start(update, context):
    dialog.mode = 'main'
    msg = load_message('main')  # завантажуємо вміст файлу main у змінну msg
    await send_photo(update, context, name='main')
    await send_text(update, context, msg)  # виводимо текст
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'profile': 'Генерація Tinder-профілю \uD83D\uDE0E',  # коди емоджи (смайлики)
        'opener': 'Повідомлення для знайомства \uD83E\uDD70',
        'message': 'Спілкування з зірками \uD83D\uDD25',
        'gpt': 'Задати питання ChatGPT \uD83E\uDDE0',
    })


async def gpt(update, context):
    dialog.mode = 'gpt'  # змінюємо значення атрибута на 'gpt'
    await send_photo(update, context, name='gpt')
    msg = load_message('gpt')  # завантажуємо вміст файлу gpt у змінну msg
    await send_text(update, context, msg)


async def gpt_dialog(update, context):
    text = update.message.text  # отримуємо текст із запросу (те, що пишуть в командній строці боту)
    prompt = load_prompt('gpt')  # підтягуємо вміст файлу /prompts/gpt.txt для створення промпту
    # prompt - це коротка інструкція для запиту штучному інтелекту.
    answer = await chatgpt.send_question(prompt_text=prompt, message_text=text)  # зберігаємо відповідь ШІ у змінну
    await send_text(update, context, answer)


async def date(update, context):
    dialog.mode = 'date'
    msg = load_message('date')  # завантажуємо вміст файлу /messages/date.txt у змінну msg
    await send_photo(update, context, name='date')  # надсилаємо файл /resources/images/date.jpg
    await send_text_buttons(update, context, msg, buttons={
        'date_grande': 'Аріана Гранде',
        'date_robbie': 'Марго Роббі',
        'date_zendaya': 'Зендея',
        'date_gosling': 'Райан Гослінг',
        'date_hardy': 'Том Харді',
    })


async def date_button(update, context):
    query = update.callback_query.data  # отримуємо 'name' кнопки (date_grande, date_hardy)
    # назви співпадають з назвами файлів jpg (date_grande.jpg, date_hardy.jpg)
    await update.callback_query.answer()  # повідомляє бота, що кнопка натиснута (щоб не блимала)
    await send_photo(update, context, query)  # надсилаємо фото {query}.jpg
    await send_text(update, context, text='Гарний вибір.\uD83D\uDE05 Ваша задача запросити дівчину/хлопця '
                                          'на побачення за 5 повідомлень! ♥\uFE0F')
    prompt = load_prompt(query)  # завантажуємо /prompts/{query}.txt
    chatgpt.set_prompt(prompt)  # prompt автоматом передається в date_dialog() в змінну answer


async def date_dialog(update, context):
    text = update.message.text  # отримуємо текст з update
    my_message = await send_text(update, context, text='набирає повідомлення...')
    # що буде бачити юзер, поки ШІ думає
    answer = await chatgpt.add_message(text)  # prompt підтягує з date_button()
    await my_message.edit_text(answer)  # показує текст my_message до моменту відповіді ШІ


async def message(update, context):
    dialog.mode = 'message'
    msg = load_message('message')
    await send_photo(update, context, name='message')
    await send_text_buttons(update, context, msg, buttons={
        'message_next': 'Написати повідомлення',
        'message_date': 'Запросити на побачення',
    })
    dialog.list.clear()


async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)


async def message_button(update, context):
    query = update.callback_query.data  # отримуємо 'name' кнопки з message()
    # (message_next, message_date)
    await update.callback_query.answer()

    prompt = load_prompt(query)  # завантажуємо /prompts/{query}.txt
    user_chat_history = '\n\n'.join(dialog.list)

    my_message = await send_text(update, context, text='думаю над варіантами...')
    answer = await chatgpt.send_question(prompt_text=prompt, message_text=user_chat_history)
    await my_message.edit_text(answer)  # показує текст my_message до моменту відповіді ШІ


async def hello(update, context):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == 'main':
        await send_text(update, context, 'Hello ' + update.message.text)
    elif dialog.mode == 'date':
        await date_dialog(update, context)
    elif dialog.mode == 'message':
        await message_dialog(update, context)


if __name__ == '__main__':
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler('start', start))  # обробник команди /start
    app.add_handler(CommandHandler('gpt', gpt))  # обробник команди /gpt
    app.add_handler(CommandHandler('date', date))  # обробник команди /date
    app.add_handler(CommandHandler('message', message))  # обробник команди /message
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))  # обробник
    # всіх текстів з командної строки
    app.add_handler(CallbackQueryHandler(date_button, pattern='^date_.*'))  # обробник запитів з кнопок
    # '^date_.*' - якщо з кнопки приходить з початку строки '^' 'date_' + будь-які символи '.'
    # необмежену кількість раз '*'
    app.add_handler(CallbackQueryHandler(message_button, pattern='^message_.*'))
    app.run_polling()
