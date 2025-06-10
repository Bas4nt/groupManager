import os
import logging
from dotenv import load_dotenv
from telegram import Update, Sticker
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)

# Import utils
from utils.image_processor import process_sticker, create_meme, create_quote_sticker
from utils.sticker_handler import kang_sticker
from utils.text_utils import parse_quote_text

# Load environment
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🤖 Hi! I'm your sticker bot!\n\n"
        "Commands:\n"
        "/kang - Kang a sticker\n"
        "/mmf 'top text' 'bottom text' - Create meme\n"
        "/quote - Reply to a message to make it a sticker"
    )

async def handle_sticker(update: Update, context: CallbackContext):
    """Handle incoming stickers"""
    if not update.message.sticker:
        return
    
    sticker = update.message.sticker
    file_id = sticker.file_id
    file_unique_id = sticker.file_unique_id
    
    # Save sticker to kang later
    context.user_data['last_sticker'] = {
        'file_id': file_id,
        'file_unique_id': file_unique_id
    }
    
    await update.message.reply_text(
        "Sticker received! Use /kang to add to your pack",
        reply_to_message_id=update.message.message_id
    )

async def kang_command(update: Update, context: CallbackContext):
    """Kang a sticker"""
    if 'last_sticker' not in context.user_data:
        await update.message.reply_text("No sticker to kang! Send me a sticker first.")
        return
    
    sticker_data = context.user_data['last_sticker']
    await kang_sticker(update, context, sticker_data)

async def meme_command(update: Update, context: CallbackContext):
    """Create meme from sticker"""
    try:
        # Expecting format: /mmf "top text" "bottom text"
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Usage: /mmf 'top text' 'bottom text'")
            return
        
        if 'last_sticker' not in context.user_data:
            await update.message.reply_text("No sticker to meme! Send me a sticker first.")
            return
        
        sticker_data = context.user_data['last_sticker']
        top_text = args[0].strip('"\'')
        bottom_text = args[1].strip('"\'')
        
        meme_path = await create_meme(
            sticker_data['file_id'],
            top_text,
            bottom_text,
            context.bot
        )
        
        with open(meme_path, 'rb') as meme_file:
            await update.message.reply_sticker(meme_file)
        
        os.remove(meme_path)
        
    except Exception as e:
        logging.error(f"Meme creation error: {e}")
        await update.message.reply_text("Failed to create meme 😢")

async def quote_command(update: Update, context: CallbackContext):
    """Create quote sticker from replied message"""
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to quote it!")
        return
    
    replied_message = update.message.reply_to_message
    quote_text = replied_message.text or replied_message.caption
    
    if not quote_text:
        await update.message.reply_text("The message has no text to quote!")
        return
    
    # Create quote sticker
    author = replied_message.from_user.first_name
    quote_sticker = await create_quote_sticker(quote_text, author)
    
    with open(quote_sticker, 'rb') as sticker_file:
        await update.message.reply_sticker(sticker_file)
    
    os.remove(quote_sticker)

def main():
    # Create application
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("kang", kang_command))
    application.add_handler(CommandHandler("mmf", meme_command))
    application.add_handler(CommandHandler("quote", quote_command))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
