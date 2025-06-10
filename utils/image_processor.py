from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np
import cv2
from moviepy.editor import ImageSequenceClip
from telegram import Bot
from io import BytesIO

async def process_sticker(file_id: str, bot: Bot):
    """Download and process sticker"""
    sticker_file = await bot.get_file(file_id)
    sticker_bytes = await sticker_file.download_as_bytearray()
    
    # Save to temp file
    temp_path = f"data/stickers/{file_id}.webp"
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    
    with open(temp_path, 'wb') as f:
        f.write(sticker_bytes)
    
    return temp_path

async def create_meme(file_id: str, top_text: str, bottom_text: str, bot: Bot):
    """Create meme from sticker with text"""
    sticker_path = await process_sticker(file_id, bot)
    
    # Open image
    img = Image.open(sticker_path)
    draw = ImageDraw.Draw(img)
    
    # Use a meme font
    try:
        font = ImageFont.truetype("impact.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Calculate text positions
    width, height = img.size
    top_pos = (width/2, 10)
    bottom_pos = (width/2, height - 50)
    
    # Draw text with outline
    def draw_text_with_outline(text, position):
        x, y = position
        # Outline
        for adj in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            draw.text((x+adj[0], y+adj[1]), text, font=font, fill="black", 
                     anchor="mm", stroke_width=2)
        # Main text
        draw.text((x, y), text, font=font, fill="white", anchor="mm")
    
    draw_text_with_outline(top_text.upper(), top_pos)
    draw_text_with_outline(bottom_text.upper(), bottom_pos)
    
    # Save meme
    meme_path = f"data/memes/{file_id}_meme.webp"
    img.save(meme_path, "WEBP")
    
    return meme_path

async def create_quote_sticker(text: str, author: str):
    """Create quote sticker from text"""
    # Create blank image
    img = Image.new("RGB", (512, 512), color=(29, 29, 29))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 32)
        author_font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
        author_font = ImageFont.load_default()
    
    # Split text into lines
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if draw.textlength(test_line, font=font) < 450:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw text
    y_position = 100
    for line in lines:
        draw.text((256, y_position), line, font=font, fill="white", anchor="mm")
        y_position += 40
    
    # Draw author
    draw.text((400, 450), f"— {author}", font=author_font, fill="white")
    
    # Save quote
    quote_path = f"data/quotes/quote_{hash(text)}.webp"
    img.save(quote_path, "WEBP")
    
    return quote_path
