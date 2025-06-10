FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libwebp-dev \  # For WebP support
    libopenjp2-7 \ # For PNG support
    libtiff5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
