import threading
from telethon import TelegramClient, events, Button
from datetime import datetime
import asyncio
import logging
import os
import sqlite3
import json
import re

# get stasera.json
import get_stasera
get_stasera.main()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Database connection
conn = sqlite3.connect('./data/users.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    notify_time TEXT DEFAULT "14:00",
    notified BOOLEAN DEFAULT 0,
    blacklist TEXT DEFAULT "[]"
)
''')
conn.commit()

# Your API ID and hash from my.telegram.org
BOT_TOKEN = os.environ.get('BOT_TOKEN')
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')

# Create the client and connect
client = TelegramClient("./data/bot.session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Poll and selected responses
user_selections = {}

# Add a user in the database
def add_user(user_id: int):
    cursor.execute("INSERT INTO users (user_id) VALUES (?) ON CONFLICT(user_id) DO NOTHING", (user_id,))
    conn.commit()

# Update user notify_time in the database
def update_notify_time(user_id, notify_time):
    assert re.match(r"([0-1]\d|[2][0-3]){1}:([0-5]\d){1}", notify_time) or notify_time == "-1", "Notify time must be in 'HH:MM' format" 
    cursor.execute("UPDATE users SET notify_time=? WHERE user_id=?", (notify_time, user_id))
    conn.commit()

# Update user blacklist in the database
def update_blacklist(user_id, blacklist: list):
    blacklist = json.dumps(sorted(blacklist))
    cursor.execute("UPDATE users SET blacklist=? WHERE user_id=?", (blacklist, user_id))
    conn.commit()

# Update user notified in the database
def update_notified(user_id, notified):
    print(f"{notified = }")
    cursor.execute("UPDATE users SET notified=? WHERE user_id=?", (str(int(notified)), user_id))
    conn.commit()

def reset_notified_all():
    cursor.execute("UPDATE users SET notified=0")
    conn.commit()

# Get all users from the database
def get_users():
    cursor.execute("SELECT * FROM users WHERE notify_time != '-1'")
    return cursor.fetchall()

# Get a specific user from the database
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

# Get the blacklist of a user
def get_user_blacklist(user_id):
    return json.loads(get_user(user_id)[3])

# Get the notify time of a user
def get_user_notify_time(user_id):
    return get_user(user_id)[1]

# Delete a user from the database
def delete_user(user_id):
    cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()



@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    add_user(event.sender_id)
    await event.respond("Ciao uagliò! Ti romperò i coglioni tutti i giorni alle 14:00!\nMi raccomando aggiusta la blacklist dei canali che non vuoi vedere se no ti arriva un sacco di merda.")
    await help(event)
    logging.info(f'Start command received from {event.sender_id}')
    

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    help_text = (
        "Con questi sei tu che rompi i coglioni a me:\n\n"
        "`/cambio <ora>:<minuto>`  cambia la rottura di coglioni\n"
        "`/rottura`  a che ora rompo i coglioni?\n"
        "`/avast`  non ti romperò più i coglioni\n"
        "`/riattiva`  ti rompo di nuovo i coglioni\n"
        "`/canale <numero>`  mostra il programma del canale selezionato\n"
        "`/set_blacklist`  definisce i canali che non vuoi essere rotto i coglioni\n"
        "`/help`  sono io"
    )
    await event.respond(help_text)
    logging.info(f'Help command received from {event.sender_id}')


async def send_tv_program(user_id):
    try:
        with open("./data/stasera.json", "r") as f:
            stasera = json.load(f)
        
        for canale in get_user_blacklist(user_id):
            del stasera['highlights'][str(canale)]
        
        for canale, info in stasera['highlights'].items():
            caption = f"**{info['channel']}** - canale {canale}\n\n**{info['title']}**\n{info['description'][:500]}{'...' if len(info['description']) > 510 else ''}"
            
            buttons = []
            if info.get('info') or len(info['description']) > 510:
                buttons.append(Button.inline('Info', f"info_{canale}"))
            
            if info.get('trailer'):
                buttons.append(Button.url('Trailer', info['trailer']))

            with open(f'./data/images/{canale}.jpg', 'rb') as image:
                await client.send_file(user_id, image, caption=caption, buttons=buttons if buttons.__len__() > 0 else None)
    except Exception as e:
        logging.error(f"Error sending TV program to {user_id}: {e}")
    update_notified(user_id, True)


@client.on(events.CallbackQuery(pattern=r"info_\d+"))
async def callbackInfo(event):
    canale = event.data.decode().split("_")[1]  # Estrai il canale
    await send_program_info(event.sender_id, canale)
    await event.answer()


async def send_program_info(user_id, canale):
    with open("./data/stasera.json", "r") as f:
        stasera = json.load(f)
    info: dict = stasera['highlights'].get(canale, None)
    assert info, f"Canale \"{canale}\" non trovato"

    caption = f"**{info['channel']}** - canale {canale}\n\n**{info['title']}**\n{info['description']}"

    buttons = []
    if info.get('trailer'):
        buttons.append(Button.url('Trailer', info['trailer']))

    with open(f'./data/images/{canale}.jpg', 'rb') as image:
        await client.send_file(user_id, image)
        if info.get('info'):
            await client.send_message(user_id, caption)
            await client.send_message(user_id, info['info'], buttons=buttons if buttons.__len__() > 0 else None)
        else:
            await client.send_message(user_id, caption, buttons=buttons if buttons.__len__() > 0 else None)

@client.on(events.NewMessage(pattern='/cambio'))
async def cambio(event):
    try:
        _, notify_time = event.raw_text.split(' ', 1)
        update_notify_time(event.sender_id, notify_time)
        update_notified(event.sender_id, False)
        await event.respond(f"Ora di rottura cambiata a {notify_time}")
    except (AssertionError, ValueError) as e:
        await event.respond("Devi specificare l'ora in formato 'HH:MM'")
    logging.info(f'Change time command received from {event.sender_id}')


@client.on(events.NewMessage(pattern='/rottura'))
async def rottura(event):
    time = get_user_notify_time(event.sender_id)
    await event.respond(f"Ti rompo le palle tutti i giorni alle {time}" if time != '-1' else "Ma che cazzo vuoi.")


@client.on(events.NewMessage(pattern='/canale'))
async def canale(event):
    try:
        _, canale = event.raw_text.split(' ', 1)
        await send_program_info(event.sender_id, canale)
    except AssertionError as e:
        await event.respond(str(e))
    except ValueError:
        await event.respond(f"Devi specificare il numero del canale cazzo: /canale <numero>")
    logging.info(f'Channel info command received from {event.sender_id}')


@client.on(events.NewMessage(pattern='/avast'))
async def avast(event):
    update_notify_time(event.sender_id, notify_time="-1")
    await event.respond("Non ti romperò più le palle 🖕")
    logging.info(f'Unsubscribe command received from {event.sender_id}')


@client.on(events.NewMessage(pattern='/riattiva'))
async def riattiva(event):
    update_notify_time(event.sender_id, '14:00')
    await event.respond("Da oggi ti romperò di nuovo le palle tutti i giorni alle 14:00 😌🖕")
    logging.info(f'Resubscribe command received from {event.sender_id}')


def generate_poll(user_id):
    """Crea il poll per la blacklist e restituisce il messaggio e i buttons."""
    selections = user_selections.get(user_id, [])
    buttons = []
    for channel, channel_name in get_all_channels():
        status = "❌" if channel in selections else "✔️"
        buttons.append([Button.inline(f"{status} {channel_name} - canale {channel}", f"toggle_{channel}".encode())])
    buttons.append([Button.inline("✅ Conferma", b"confirm")])
    return "Seleziona i canali da escludere dalla rottura di coglioni e poi conferma", buttons


@client.on(events.NewMessage(pattern='/set_blacklist'))
async def set_blacklist(event):
    user_id = event.sender_id
    user_selections[user_id] = get_user_blacklist(user_id)

    text, buttons = generate_poll(user_id)
    await event.reply(text, buttons=buttons)

    logging.info(f'Set blacklist command received from {user_id}')


@client.on(events.CallbackQuery(pattern=r"toggle_\d+"))
async def toggle_option(event):
    """Gestisce la selezione/deselezione di un'opzione della blacklist."""
    user_id = event.sender_id
    canale = int(event.data.decode().split("_")[1])  # Estrai il canale

    # Aggiorna le selezioni
    if user_id not in user_selections:
        user_selections[user_id] = []
    if canale in user_selections[user_id]:
        user_selections[user_id].remove(canale)  # Deseleziona
    else:
        user_selections[user_id].append(canale)  # Seleziona

    # Aggiorna il messaggio del sondaggio
    _, buttons = generate_poll(user_id)
    await event.edit(buttons=buttons)
    await event.answer()


@client.on(events.CallbackQuery(pattern=r"confirm"))
async def confirm_poll(event):
    """Gestisce la conferma della blacklist."""
    user_id = event.sender_id
    update_blacklist(user_id, user_selections[user_id])

    # Invia un messaggio di conferma
    await event.edit("Apposto!", buttons=None)
    await event.answer()


def get_all_channels():
    with open("./data/stasera.json", "r") as f:
        stasera: dict = json.load(f)

    return zip((int(i) for i in stasera['highlights'].keys()), (info['channel'] for info in stasera['highlights'].values()))


# Semaphore to limit the number of threads
semaphore = threading.Semaphore(10)

def send_message(loop, user_id):
    """Send a message to a user and update the last sent time."""
    with semaphore:  # Ensure no more than 10 threads are active
        asyncio.run_coroutine_threadsafe(send_tv_program(user_id), loop)

async def schedule_notifications():
    """
    Schedule a task to run at a specific time.
    :param target_time: Target time in 'HH:MM' 24-hour format.
    """
    loop = asyncio.get_event_loop()
    while True:
        now = datetime.now()
        for user_id, target_time, notified, _ in get_users():
            target_hour, target_minute = map(int, target_time.split(':'))

            if now.hour == target_hour and target_minute <= now.minute < target_minute + 10 and not notified:
                thread = threading.Thread(target=send_message, args=(loop, user_id))
                thread.start()

        # Aspetta 60 secondi prima di ricontrollare il programma
        await asyncio.sleep(60)


async def reset_notified():
    while True:
        await asyncio.sleep(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() + 86400 - datetime.now().timestamp())
        reset_notified_all()


async def main():
    await asyncio.gather(client.run_until_disconnected(), schedule_notifications(), reset_notified())


if __name__ == '__main__':
    client.loop.run_until_complete(main())