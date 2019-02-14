FROM python:3.6-alpine
ARG TOKEN
ENV DISCORD_BOT_TOKEN=$TOKEN
COPY . /discord-cancer-bot
WORKDIR /discord-cancer-bot/requirements
RUN pip install -r base.txt
WORKDIR /discord-cancer-bot
CMD ["python3", "bot.py"]
RUN echo "Token Set: $TOKEN"
