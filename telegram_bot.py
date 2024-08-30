import os
import logging

from dotenv import load_dotenv
from datetime import time, datetime
from pylatexenc.latex2text import LatexNodes2Text
from uuid import uuid4
from html import escape

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent
)

from telegram.ext import (
    Application, 
    ContextTypes, 
    CommandHandler,
    InlineQueryHandler
)

from peewee import *

from database import db, ArxivUpdate

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") 
THUMBNAIL_URL = os.getenv("THUMBNAIL_URL")

channels = {"math.CT": "@arkeiftest", "math.QA": "@arkeiftest2"}

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi!")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    if not query:
        return
    results = list()
    db_arxiv_updates = ArxivUpdate.select().where(ArxivUpdate.abstract.contains(query))
    for u in db_arxiv_updates:
        abstract = LatexNodes2Text().latex_to_text(u.abstract[10:100])
        result = InlineQueryResultArticle(
            id=str(uuid4()),
            title=u.title,
            input_message_content=InputTextMessageContent(f"{u.link}"),
            description=abstract,
            thumbnail_url=THUMBNAIL_URL,
        )
        results.append(result)
    await update.inline_query.answer(results)


async def dispatch_updates(context: ContextTypes.DEFAULT_TYPE) -> None:
    ''' sends the updates their dedicated tg-channel '''
    keyboard = [[InlineKeyboardButton("Oh! Interesting!", callback_data="1")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    db.connect()
    todays_updates = ArxivUpdate.select().where(ArxivUpdate.date == datetime.today().strftime('%Y-%m-%d'))
    db.close()
    if todays_updates: 
        for update in todays_updates:
            topic = update.topic
            title = update.title
            authors = update.authors
            abstract = update.abstract
            link = update.link
            update = LatexNodes2Text().latex_to_text(f"<b>{title}</b>\n<i>{authors}</i>\n\n{abstract}\n\n{link}")
            await context.bot.send_message(
                chat_id=channels[topic],
                text=update,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=reply_markup
                )
    else:
        logger.info("No updates available today.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(InlineQueryHandler(inline_query))
    job_queue = app.job_queue
    job_queue.run_daily(dispatch_updates, time=time(9,49), days=(0, 1, 2, 4, 5, 6))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()


                
