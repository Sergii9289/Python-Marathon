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


async def hello(update, context):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == 'main':
        await send_text(update, context, 'Hello ' + update.message.text)


if __name__ == '__main__':
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler('start', start))  # обробник команди /start
    app.add_handler(CommandHandler('gpt', gpt))  # обробник команди /gpt
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))  # обробник
    # всіх текстів з командної строки
    # app.add_handler(CallbackQueryHandler(buttons_handler))
    app.run_polling()
