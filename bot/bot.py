import asyncio
import logging
import os
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    AIORateLimiter,
)

# Applichiamo nest_asyncio per Render
nest_asyncio.apply()

# Logging base
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Funzione chiamata dopo l'avvio
async def post_init(application):
    print("✅ Bot inizializzato correttamente.")

# Comando /start
async def start_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ Comando /start ricevuto")
    await update.message.reply_text("Ciao! Il bot è attivo e funzionante ✅")

# Avvio del bot
def run_bot():
    application = (
        ApplicationBuilder()
        .token(os.getenv("TELEGRAM_BOT_TOKEN"))
        .concurrent_updates(True)
        .rate_limiter(AIORateLimiter(max_retries=5))
        .post_init(post_init)
        .http_version("1.1")
        .get_updates_http_version("1.1")
        .build()
    )

    # Aggiunge l'handler /start (senza filtri)
    application.add_handler(CommandHandler("start", start_handle))

    # Avvio in modalità webhook per Render
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=os.environ.get("WEBHOOK_URL")  # da specificare in Render
    )

# Punto d'ingresso
async def main():
    run_bot()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
