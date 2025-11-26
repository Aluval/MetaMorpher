#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
FROM python:3.10
WORKDIR /app
COPY . /app/
# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg
RUN apt -qq update && apt -qq install -y git wget pv jq wget python3-dev ffmpeg mediainfo
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
#TG:@Sunrises_24
