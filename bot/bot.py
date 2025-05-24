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
    Application,
    CallbackContext,
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
import http.server
import os
import socketserver
import nest_asyncio

# Avvio automatico del loop asyncio per compatibilità con ambienti come Jupyter o Render
nest_asyncio.apply()

# Logger setup
logger = logging.getLogger(__name__)

# Database instance
db = database.Database()

# Placeholder per run_bot (da implementare sopra con handler)
async def post_init(application):
    print("Bot inizializzato correttamente.")
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

    user_filter = filters.ALL
    if config.allowed_telegram_usernames:
        usernames = [x for x in config.allowed_telegram_usernames if isinstance(x, str)]
        any_ids = [x for x in config.allowed_telegram_usernames if isinstance(x, int)]
        user_ids = [x for x in any_ids if x > 0]
        group_ids = [x for x in any_ids if x < 0]
        user_filter = filters.User(username=usernames) | filters.User(user_id=user_ids) | filters.Chat(chat_id=group_ids)

    application.add_handler(CommandHandler("start", start_handle, filters=user_filter))
    application.add_handler(CommandHandler("help", help_handle, filters=user_filter))
    application.add_handler(CommandHandler("help_group_chat", help_group_chat_handle, filters=user_filter))
    application.add_handler(CommandHandler("gender", set_gender, filters=user_filter))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, message_handle))
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND & user_filter, message_handle))
    application.add_handler(MessageHandler(filters.VIDEO & ~filters.COMMAND & user_filter, unsupport_message_handle))
    application.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND & user_filter, unsupport_message_handle))
    application.add_handler(CommandHandler("retry", retry_handle, filters=user_filter))
    application.add_handler(CommandHandler("new", new_dialog_handle, filters=user_filter))
    application.add_handler(CommandHandler("cancel", cancel_handle, filters=user_filter))
    application.add_handler(MessageHandler(filters.VOICE & user_filter, voice_message_handle))
    application.add_handler(CommandHandler("mode", show_chat_modes_handle, filters=user_filter))
    application.add_handler(CallbackQueryHandler(show_chat_modes_callback_handle, pattern="^show_chat_modes"))
    application.add_handler(CallbackQueryHandler(set_chat_mode_handle, pattern="^set_chat_mode"))
    application.add_handler(CommandHandler("settings", settings_handle, filters=user_filter))
    application.add_handler(CallbackQueryHandler(set_settings_handle, pattern="^set_settings"))
    application.add_handler(CommandHandler("balance", show_balance_handle, filters=user_filter))
    application.add_error_handler(error_handler)

    application.run_polling()

# HTTP server dummy (necessario per Render)
async def start_http_server():
    PORT = int(os.environ.get("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving dummy HTTP on port {PORT}")
        httpd.serve_forever()

# Funzione principale che avvia il bot e il server HTTP
async def main():
    loop = asyncio.get_event_loop()
    bot_task = loop.run_in_executor(None, run_bot)
    http_task = loop.run_in_executor(None, start_http_server)
    await asyncio.gather(bot_task, http_task)

if __name__ == "__main__":
    asyncio.run(main())
