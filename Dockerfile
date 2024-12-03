
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt update && apt upgrade -y && apt install -y git python3-pip ffmpeg

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

USER myuser  # Run as a non-root user for better security

CMD ["python3", "bot.py"]
