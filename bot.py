import logging
from telethon import TelegramClient, events
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

# Your API ID and hash from my.telegram.org
BOT_TOKEN = os.environ.get('BOT_TOKEN')
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')

# Create the client and connect
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    start_text = (
        "Ciao uagliò! Ti romperò i coglioni tutti i giorni alle 14:00!\n"
        "Fai il comando /help per vedere che cazzo puoi farmi."
    )
    await event.respond(start_text)
    logging.info(f'Start command received from {event.sender_id}')


@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    help_text = (
        "Con questi sei tu che rompi i coglioni a me:\n\n"
        "`/cambio <ora>:<minuto>`  cambia la rottura di coglioni\n"
        "`/chiarimenti`  a che ora rompo i coglioni?\n"
        "`/canale <numero>`  mostra il programma del canale selezionato\n"
        "`/rottura`  mostra la rottura qunado vuoi\n"
        "`/blacklist <num1> <num2> ...`  definisce i canali che non vuoi essere rotto i coglioni\n"
        "`/add_blacklist <num1> <num2> ...`  aggiunge i canali alla blacklist\n"
        "`/rem_blacklist <num1> <num2> ...`  toglie i canali dalla blacklist\n"
        "`/get_blacklist`  mostra la blacklist\n"
        "`/help`  sono io"
    )
    await event.respond(help_text)
    logging.info(f'Help command received from {event.sender_id}')


@client.on(events.NewMessage(pattern='/info'))
async def info(event):
    await event.respond('This bot is created using Telethon in Python. It can respond to various commands and messages.')
    logging.info(f'Info command received from {event.sender_id}')


# Start the client
client.start()
client.run_until_disconnected()
