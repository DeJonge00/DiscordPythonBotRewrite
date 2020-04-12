FROM python:3.8.2-slim-buster

WORKDIR /usr/src/PythonBot

COPY requirements.txt .

RUN pip install requests && \
    pip install --no-cache-dir -r requirements.txt && \
    apt update && apt install -y ffmpeg

CMD [ "python", "-u", "./PythonBot.py" ]
