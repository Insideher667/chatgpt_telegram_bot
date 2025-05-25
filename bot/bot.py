import io
import logging
import asyncio
import traceback
import html
import json
from datetime import datetime
import openai
import telegram
from telegram import (
    Update,
    User,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    AIORateLimiter,
    filters,
    ContextTypes
)
import config
import database
import openai_utils
import base64
import os
import nest_asyncio

# Avvio automatico del loop asyncio per compatibilità con ambienti come Jupyter o Render
nest_asyncio.apply()

# Logger setup
logger = logging.getLogger(__name__)

# Database instance
db = database.Database()

# Funzione di inizializzazione post costruttore
async def post_init(application):
    print("✅ Bot inizializzato correttamente.")

# ✅ Handler di test per il comando /start
async def start_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ Comando /start ricevuto")
    await update.message.reply_text("Ciao! Il bot è attivo e funzionante ✅")

# Funzione principale che costruisce e avvia il bot
def run_bot():
    application = (
        ApplicationBuilder()
        .token(config.telegram_token)
        .concurrent_updates(True)
        .rate_limiter(AIORateLimiter(max_retries=5))
        .http_version("1.1")
        .get_updates_http_version("1.1")
        .post_init(post_init)
        .build()
    )

    # Imposta filtri utenti se configurati
    user_filter = filters.ALL
    if config.allowed_telegram_usernames:
        usernames = [x for x in config.allowed_telegram_usernames if isinstance(x, str)]
        any_ids = [x for x in config.allowed_telegram_usernames if isinstance(x, int)]
        user_ids = [x for x in any_ids if x > 0]
        group_ids = [x for x in any_ids if x < 0]
        user_filter = (
            filters.User(username=usernames)
            | filters.User(user_id=user_ids)
            | filters.Chat(chat_id=group_ids)
        )

    # ✅ Handler per il comando /start (puoi aggiungere gli altri in seguito)
    application.add_handler(CommandHandler("start", start_handle, filters=user_filter))

    # Esegui il webhook (Render richiede HTTP in ingresso)
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url="https://chatgpt-telegram-bot-7n4o.onrender.com"
    )

# Avvia il bot
async def main():
    run_bot()

if __name__ == "__main__":
    asyncio.run(main())
