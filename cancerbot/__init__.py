import os
import sys
import logging

import discord

class CustomFormatter(logging.Formatter):
    LEVEL_MAP = {logging.FATAL: 'F', logging.ERROR: 'E', logging.WARN: 'W', logging.INFO: 'I', logging.DEBUG: 'D'}

    def format(self, record):
        record.levelletter = self.LEVEL_MAP[record.levelno]
        return super(CustomFormatter, self).format(record)


def init_logging():
    fmt = '%(levelletter)s%(asctime)s.%(msecs).03d %(process)d %(filename)s:%(lineno)d] %(message)s'
    datefmt = '%m%d %H:%M:%S'
    formatter = CustomFormatter(fmt, datefmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(console_handler)

    # Explicitly tell these libraries to shut up
    logging.getLogger('discord').setLevel(logging.WARN)
    logging.getLogger('websockets').setLevel(logging.WARN)

    return logging.getLogger(__name__)


client = discord.Client()
logger = init_logging()


@client.event
async def on_message(message: discord.Message):
    if message.content.startswith('test'):
        await client.send_message(message.channel, 'TESTING')