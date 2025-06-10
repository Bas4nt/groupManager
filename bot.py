from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import os
import logging
from app.utils import image_processor, sticker_handler

# Render-specific setup
IS_RENDER = os.getenv('RENDER', False)
PORT = int(os.environ.get('PORT', 8443))

async def post_init(application):
    if IS_RENDER:
        await application.bot.set_webhook(f"https://your-render-url.onrender.com/{application.bot.token}")

def main():
    app = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).post_init(post_init).build()
    
    # Add handlers (same as before)
    app.add_handler(CommandHandler("start", start))
    # ... other handlers ...

    if IS_RENDER:
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            secret_token='WEBHOOK_SECRET',
            webhook_url=f"https://your-render-url.onrender.com"
        )
    else:
        app.run_polling()

if __name__ == '__main__':
    main()
