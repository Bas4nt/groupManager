def parse_quote_text(text: str, max_length=200):
    """Format text for quote sticker"""
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    return text
