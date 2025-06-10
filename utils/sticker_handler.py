async def kang_sticker(update: Update, context: CallbackContext, sticker_data: dict):
    user = update.effective_user
    file_id = sticker_data['file_id']
    
    try:
        # Get sticker file
        sticker_file = await context.bot.get_file(file_id)
        sticker_bytes = await sticker_file.download_as_bytearray()
        
        # Convert to BytesIO and verify
        with BytesIO(sticker_bytes) as sticker_io:
            try:
                # Try to open the image to verify it's valid
                with Image.open(sticker_io) as img:
                    img.verify()  # Verify it's a valid image
                    sticker_io.seek(0)  # Reset pointer after verification
                    
                    # Determine if animated
                    is_animated = hasattr(img, 'is_animated') and img.is_animated
                    
                    # Convert to PNG if static and not already PNG
                    if not is_animated and img.format != 'PNG':
                        png_io = BytesIO()
                        img.save(png_io, 'PNG')
                        sticker_bytes = png_io.getvalue()
            except Exception as img_error:
                raise ValueError(f"Invalid image file: {str(img_error)}")

        # Rest of your kang logic...
        pack_name = f"{user.id}_by_{context.bot.username}"
        
        if is_animated:
            await context.bot.create_new_sticker_set(
                user_id=user.id,
                name=pack_name,
                title=f"@{user.username}'s Pack" if user.username else f"{user.first_name}'s Pack",
                stickers=[InputSticker(
                    sticker=BytesIO(sticker_bytes),
                    emoji_list=["🤖"]
                )],
                sticker_format="animated"
            )
        else:
            await context.bot.create_new_sticker_set(
                user_id=user.id,
                name=pack_name,
                title=f"@{user.username}'s Pack" if user.username else f"{user.first_name}'s Pack",
                stickers=[InputSticker(
                    sticker=BytesIO(sticker_bytes),
                    emoji_list=["🤖"]
                )],
                sticker_format="static"
            )
            
        await update.message.reply_text(
            f"Sticker added! [View Pack](t.me/addstickers/{pack_name})",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logging.error(f"Kang failed: {str(e)}", exc_info=True)
        await update.message.reply_text(
            f"Failed to kang sticker: {str(e)}\n"
            f"Supported formats: PNG, static WebP, animated stickers"
        )
