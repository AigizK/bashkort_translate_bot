import logging

from telethon import TelegramClient
import config


class Bot(TelegramClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.me = None


bot = Bot('bot', config.API_ID, config.API_HASH)
bot.parse_mode = 'HTML'
logging.basicConfig(level=logging.INFO)

import app.handlers


async def start():
    await bot.connect()
    bot.me = await bot.sign_in(bot_token=config.BOT_TOKEN)
    await bot.run_until_disconnected()


def run():
    bot.loop.run_until_complete(start())