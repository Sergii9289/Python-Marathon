from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from dotenv import load_dotenv
import os

from gpt import *
from util import *

load_dotenv(dotenv_path='config.env')
TOKEN = os.getenv('TG_TOKEN')


async def start(update, context):
    # await send_photo(update, context, name='avatar_main')
    # await send_text(update, context, text='Привіт користувач')
    msg = load_message('main')
    await send_text(update, context, msg)


async def hello(update, context):
    # await send_text(update, context, text='Hello ' + update.message.text)
    await send_text_buttons(update, context, 'Hello ' + update.message.text, buttons={
        'start': 'START',
        'stop': 'STOP'
    })


async def buttons_handler(update, context):
    query = update.callback_query.data
    if query == 'start':
        await send_text(update, context, text='Started')
    elif query == 'stop':
        await send_text(update, context, text='Stopped')


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
    app.add_handler(CallbackQueryHandler(buttons_handler))
    app.run_polling()
