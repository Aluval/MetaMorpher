# ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24

# Use latest stable Python version
FROM python:3.12-slim

WORKDIR /app
COPY . /app/

# Install system packages + FFmpeg + Mediainfo
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        git \
        wget \
        pv \
        jq \
        python3-dev \
        mediainfo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start bot
CMD ["python", "bot.py"]

# TG: @Sunrises_24
