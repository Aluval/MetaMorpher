#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
FROM python:3.10

WORKDIR /app
COPY . /app/

# ----------------------------
# Install dependencies
# ----------------------------
RUN apt-get update && \
    apt-get install -y ffmpeg mediainfo git wget curl jq python3-dev

# Install Node.js + NPM (required for webtorrent-hybrid)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install WebTorrent HYBRID (supports WebRTC + TCP + UDP)
RUN npm install -g webtorrent-hybrid

# Python requirements
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
#TG:@Sunrises_24
