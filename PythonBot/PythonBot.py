from core.setup import create_bot
from secret.secrets import bot_token

if __name__ == '__main__':
    bot = create_bot()
    bot.run(bot_token, bot=True, reconnect=True)
