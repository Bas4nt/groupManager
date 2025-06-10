import os
from telegram import Update, InputSticker, StickerSet
from telegram.ext import CallbackContext
from PIL import Image
from io import BytesIO

async def kang_sticker(update: Update, context: CallbackContext, sticker_data: dict):
    user = update.effective_user
    file_id = sticker_data['file_id']
    file_unique_id = sticker_data['file_unique_id']
    
    try:
        # Get sticker file
        sticker_file = await context.bot.get_file(file_id)
        sticker_bytes = await sticker_file.download_as_bytearray()
        
        # Create pack name
        pack_name = f"{user.id}_by_{context.bot.username}"
        pack_title = f"@{user.username}'s Pack" if user.username else f"{user.first_name}'s Pack"
        
        # Check if pack exists
        try:
            await context.bot.get_sticker_set(pack_name)
            mode = "add"
        except:
            mode = "create"
        
        # Convert to PNG if needed (Telegram requires PNG for new packs)
        with BytesIO(sticker_bytes) as bio:
            img = Image.open(bio)
            
            if img.format != "PNG" and mode == "create":
                png_bio = BytesIO()
                img.save(png_bio, "PNG")
                png_bio.seek(0)
                sticker_bytes = png_bio.read()
        
        # Prepare sticker
        sticker = InputSticker(
            sticker=BytesIO(sticker_bytes),
            emoji_list=["🤖"]  # Default emoji
        )
        
        # Add to pack
        if mode == "create":
            await context.bot.create_new_sticker_set(
                user_id=user.id,
                name=pack_name,
                title=pack_title,
                stickers=[sticker],
                sticker_format="static" if not sticker_file.is_animated else "animated"
            )
            message = f"Created new pack! [View Pack](t.me/addstickers/{pack_name})"
        else:
            await context.bot.add_sticker_to_set(
                user_id=user.id,
                name=pack_name,
                sticker=sticker
            )
            message = f"Added to your pack! [View Pack](t.me/addstickers/{pack_name})"
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_to_message_id=update.message.message_id
        )
    
    except Exception as e:
        await update.message.reply_text(f"Failed to kang sticker: {str(e)}")
