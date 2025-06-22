#=========================================================================
# [AutoDelete - Telegram bot to delete messages after specific time]
# Copyright (C) 2022 Arunkumar Shibu
# License: AGPL-3.0
#=========================================================================

from time import time
from utils.info import *  # Should define SESSION, BOT_TOKEN, CHATS, etc.
from utils.database import save_message
from subprocess import Popen
from pyrogram import Client, filters
from pyrogram import utils as pyroutils
import asyncio

pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

# Initialize User and Bot Clients
User = Client("auto-delete-user", session_string=SESSION)
Bot = Client("auto-delete-bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Common delete handler
@User.on_message(filters.chat(CHATS))
async def delete_handler_user(client, message):
    try:
        if WHITE_LIST and message.from_user and message.from_user.id in WHITE_LIST:
            return
        if BLACK_LIST and message.from_user and message.from_user.id not in BLACK_LIST:
            return
        _time = int(time()) + TIME
        save_message(message, _time)
    except Exception as e:
        print(f"Error in user handler: {e}")

@Bot.on_message(filters.chat(CHATS))
async def delete_handler_bot(client, message):
    try:
        if WHITE_LIST and message.from_user and message.from_user.id in WHITE_LIST:
            return
        if BLACK_LIST and message.from_user and message.from_user.id not in BLACK_LIST:
            return
        _time = int(time()) + TIME
        save_message(message, _time)
    except Exception as e:
        print(f"Error in bot handler: {e}")

User.add_handler(filters.chat(CHATS), delete_handler)
Bot.add_handler(filters.chat(CHATS), delete_handler)

# Start handler only for bot
@Bot.on_message(filters.command("start") & filters.private)
async def start(bot, message):
    await message.reply("Hi, I'm alive!")

# Launch web server and deletion worker
Popen(f"gunicorn utils.server:app --bind 0.0.0.0:{PORT}", shell=True)
Popen("python3 -m utils.delete", shell=True)

# Run both clients
async def main():
    await asyncio.gather(
        User.start(),
        Bot.start(),
        idle_loop()
    )

async def idle_loop():
    from pyrogram.idle import idle
    await idle()
    await User.stop()
    await Bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
