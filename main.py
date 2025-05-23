# --- Block 1 Start ---
# Don't Remove Credit Tg - @Tushar0125
# Ask Doubt on telegram @Tushar0125

import os
import re
import sys
import json
import time
import m3u8
import aiohttp
import asyncio
import requests
import subprocess
import urllib.parse
import cloudscraper
import datetime
import random
import ffmpeg
import logging
import yt_dlp
from subprocess import getstatusoutput
from aiohttp import web
# Ensure 'core' exists and contains necessary definitions like 'helper'
# from core import * # Consider importing specific functions/classes from core to avoid namespace pollution
import core as helper # Assuming core is a module with helper functions
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL
import yt_dlp as youtube_dl # Already imported as YoutubeDL, this is redundant
import cloudscraper # Already imported
import m3u8 # Already imported
# from core import * # Duplicative import, removed. Assuming 'core as helper' is sufficient.
from utils import progress_bar # Ensure progress_bar is defined in utils
from vars import API_ID, API_HASH, BOT_TOKEN # Make sure vars.py is present
from aiohttp import ClientSession # Already imported
from pyromod import listen
from subprocess import getstatusoutput # Already imported
from pytube import YouTube, Playlist # Playlist was imported later, now moved up

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# For the web server part
from fastapi import FastAPI
import uvicorn
import threading


# --- Configuration and Global Variables ---
cookies_file_path = os.getenv("COOKIES_FILE_PATH", "youtube_cookies.txt")

cpimg = "https://graph.org/file/5ed50675df0faf833efef-e102210eb72c1d5a17.jpg"

# Define the owner's user ID
OWNER_ID = 6221765779 # Replace with the actual owner's user ID

# List of sudo users (initially empty or pre-populated)
SUDO_USERS = [6221765779, 7856557198, 6303334633]

AUTH_CHANNEL = -1002281845928 # This usually implies a channel ID, ensure it's correct if used for auth

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__) # Use a logger instance
# --- Block 1 End ---
# --- Block 2 Start ---
# --- Utility Functions ---

async def show_random_emojis(message):
    emojis = ['🎊', '🔮', '😎', '⚡️', '🚀', '✨', '💥', '🎉', '🥂', '🍾', '🦠', '🤖', '❤️‍🔥', '🕊️', '💃', '🥳', '🐅', '🦁']
    emoji_message = await message.reply_text(' '.join(random.choices(emojis, k=1)))
    return emoji_message

def is_authorized(user_id: int) -> bool:
    """Function to check if a user is authorized."""
    return user_id == OWNER_ID or user_id in SUDO_USERS or user_id == AUTH_CHANNEL

def sanitize_filename(name):
    """Sanitizes a string to create a valid filename."""
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')

def get_videos_with_ytdlp(url):
    """
    Retrieves video titles and URLs using `yt-dlp`.
    If a title is not available, only the URL is saved.
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            if 'entries' in result:
                title = result.get('title', 'Unknown Title')
                videos = {}
                for entry in result['entries']:
                    video_url = entry.get('url', None)
                    video_title = entry.get('title', None)
                    if video_url:
                        videos[video_title if video_title else "Unknown Title"] = video_url
                return title, videos
            return None, None
    except Exception as e:
        logger.error(f"Error retrieving videos with yt-dlp: {e}")
        return None, None

def save_to_file(videos, name):
    """
    Saves video titles and URLs to a .txt file.
    If a title is unavailable, only the URL is saved.
    """
    filename = f"{sanitize_filename(name)}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        for title, url in videos.items():
            if title == "Unknown Title":
                file.write(f"{url}\n")
            else:
                file.write(f"{title}: {url}\n")
    return filename
# --- Block 2 End ---
# --- Block 3 Start ---
# --- Pyrogram Bot Client Initialization ---
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- FastAPI Web Server Setup ---
app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Telegram Bot is running and healthy!"}

def start_web_server():
    """Starts the FastAPI web server for health checks."""
    # Koyeb injects the PORT environment variable
    port = int(os.environ.get("PORT", 8000)) # Default to 8000 for local testing
    logger.info(f"Starting web server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
# --- Block 3 End ---
# --- Block 4 Start ---
# --- Telegram Bot Handlers ---

# Inline keyboard for start command
keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🇮🇳ʙᴏᴛ ᴍᴀᴅᴇ ʙʏ🇮🇳", url=f"https://t.me/Tushar0125")],
        [InlineKeyboardButton("🔔ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ🔔", url="https://t.me/TxtToVideoUpdateChannel")],
        [InlineKeyboardButton("🦋ғᴏʟʟᴏᴡ ᴜs🦋", url="https://t.me/TxtToVideoUpdateChannel")]
    ]
)

# Image URLs for the random image feature
image_urls = [
    "https://graph.org/file/996d4fc24564509244988-a7d93d020c96973ba8.jpg",
    "https://graph.org/file/96d25730136a3ea7e48de-b0a87a529feb485c8f.jpg",
    "https://graph.org/file/6593f76ddd8c735ae3ce2-ede9fa2df40079b8a0.jpg",
    "https://graph.org/file/a5dcdc33020aa7a488590-79e02b5a397172cc35.jpg",
    "https://graph.org/file/0346106a432049e391181-7560294e8652f9d49d.jpg",
    "https://graph.org/file/ba49ebe9a8e387addbcdc-be34c4cd4432616699.jpg",
    "https://graph.org/file/26f98dec8b3966687051f-557a430bf36b660e24.jpg",
    "https://graph.org/file/2ae78907fa4bbf3160ffa-2d69cd23fa75cb0c3a.jpg",
    "https://graph.org/file/05ef9478729f165809dd7-3df2f053d2842ed098.jpg",
    "https://graph.org/file/b1330861fed21c4d7275c-0f95cca72c531382c1.jpg",
    "https://graph.org/file/0ebb95807047b062e402a-9e670a0821d74e3306.jpg",
    "https://graph.org/file/b4e5cfd4932d154ad6178-7559c5266426c0a399.jpg",
    "https://graph.org/file/44ffab363c1a2647989bc-00e22c1e36a9fd4156.jpg",
    "https://graph.org/file/5f0980969b54bb13f2a8a-a3e131c00c81c19582.jpg",
    "https://graph.org/file/6341c0aa94c803f94cdb5-225b2999a89ff87e39.jpg",
    "https://graph.org/file/90c9f79ec52e08e5a3025-f9b73e9d17f3da5040.jpg",
    "https://graph.org/file/1aaf27a49b6bd81692064-30016c0a382f9ae22b.jpg",
    "https://graph.org/file/702aa31236364e4ebb2be-3f88759834a4b164a0.jpg",
    "https://graph.org/file/d0c6b9f6566a564cd7456-27fb594d26761d3dc0.jpg",
    # Add more image URLs as needed
]

# Start command handler
@bot.on_message(filters.command(["start"]))
async def start_command(bot: Client, message: Message):
    random_image_url = random.choice(image_urls)
    caption = (
        "**ʜᴇʟʟᴏ👋**\n\n"
        "➠ **ɪ ᴀᴍ ᴛxᴛ ᴛᴏ ᴠɪᴅᴇᴏ ᴜᴘʟᴏᴀᴅᴇʀ ʙᴏᴛ.**\n"
        "➠ **ғᴏʀ ᴜsᴇ ᴍᴇ sᴇɴᴅ /tushar.\n"
        "➠ **ғᴏʀ ɢᴜɪᴅᴇ sᴇ𝗻𝗱 /help."
    )
    await bot.send_photo(chat_id=message.chat.id, photo=random_image_url, caption=caption, reply_markup=keyboard)

# Stop command handler
@bot.on_message(filters.command("stop"))
async def stop_handler(_, m: Message):
    await m.reply_text("**𝗦𝘁𝗼𝗽𝗽𝗲𝗱**🚦", True)
    # This will exit the process and Koyeb will restart it
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command("restart"))
async def restart_handler(_, m: Message):
    if not is_authorized(m.from_user.id):
        await m.reply_text("**🚫 You are not authorized to use this command.**")
        return
    await m.reply_text("🔮Restarted🔮", True)
    # This will exit the process and Koyeb will restart it
    os.execl(sys.executable, sys.executable, *sys.argv)


@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    if not is_authorized(m.from_user.id):
        await m.reply_text("🚫 You are not authorized to use this command.")
        return
    """
    Command: /cookies
    Allows authorized users to upload a cookies file dynamically.
    """
    await m.reply_text(
        "𝗣𝗹𝗲𝗮𝘀𝗲 𝗨𝗽𝗹𝗼𝗮𝗱 𝗧𝗵𝗲 𝗖𝗼𝗼𝗸𝗶𝗲𝘀 𝗙𝗶𝗹𝗲 (.𝘁𝘅𝘁 𝗳𝗼𝗿𝗺𝗮𝘁).",
        quote=True
    )

    try:
        # Wait for the user to send the cookies file
        input_message: Message = await client.listen(m.chat.id)

        # Validate the uploaded file
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        # Download the cookies file
        downloaded_path = await input_message.download()

        # Read the content of the uploaded file
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        # Replace the content of the target cookies file
        with open(cookies_file_path, "w") as target_file: # Use the global cookies_file_path
            target_file.write(cookies_content)

        await input_message.reply_text(
            "✅ 𝗖𝗼𝗼𝗸𝗶𝗲𝘀 𝗨𝗽𝗱𝗮𝘁𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆.\n\𝗻📂 𝗦𝗮𝘃𝗲𝗱 𝗜𝗻 youtube_cookies.txt."
        )
        os.remove(downloaded_path) # Clean up the downloaded temp file

    except Exception as e:
        logger.error(f"Error in cookies_handler: {e}")
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")
# --- Block 4 End ---
# --- Block 5 Start ---
# Define paths for uploaded file and processed file
# IMPORTANT: CHANGE THIS TO A WRITABLE DIRECTORY IN YOUR DEPLOYMENT ENVIRONMENT
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/uploads") # Using /tmp for Koyeb

@bot.on_message(filters.command('e2t'))
async def edit_txt(client, message: Message):
    # Ensure UPLOAD_FOLDER exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Prompt the user to upload the .txt file
    await message.reply_text(
        "🎉 **Welcome to the .txt File Editor!**\n\n"
        "Please send your `.txt` file containing subjects, links, and topics."
    )

    # Wait for the user to upload the file
    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.document:
        await message.reply_text("🚨 **Error**: Please upload a valid `.txt` file.")
        return

    # Get the file name
    file_name = input_message.document.file_name.lower()

    # Define the path where the file will be saved
    uploaded_file_path = os.path.join(UPLOAD_FOLDER, file_name)

    # Download the file
    try:
        uploaded_file = await input_message.download(uploaded_file_path)
    except Exception as e:
        logger.error(f"Error downloading file for e2t: {e}")
        await message.reply_text(f"🚨 **Error**: Unable to download the file.\n\nDetails: {e}")
        return

    # After uploading the file, prompt the user for the file name or 'd' for default
    await message.reply_text(
        "🔄 **Send your .txt file name, or type 'd' for the default file name.**"
    )

    # Wait for the user's response
    user_response: Message = await bot.listen(message.chat.id)
    final_file_name = file_name # Default to the uploaded file name
    if user_response.text:
        user_response_text = user_response.text.strip().lower()
        if user_response_text != 'd':
            final_file_name = user_response_text + '.txt'


    # Read and process the uploaded file
    try:
        with open(uploaded_file, 'r', encoding='utf-8') as f:
            content = f.readlines()
    except Exception as e:
        logger.error(f"Error reading uploaded file for e2t: {e}")
        await message.reply_text(f"🚨 **Error**: Unable to read the file.\n\nDetails: {e}")
        return

    # Parse the content into subjects with links and topics
    subjects = {}
    current_subject = None
    for line in content:
        line = line.strip()
        if line and ":" in line:
            # Split the line by the first ":" to separate title and URL
            title, url = line.split(":", 1)
            title, url = title.strip(), url.strip()

            # Add the title and URL to the dictionary
            if title in subjects:
                subjects[title]["links"].append(url)
            else:
                subjects[title] = {"links": [url], "topics": []}

            # Set the current subject
            current_subject = title
        elif line.startswith("-") and current_subject:
            # Add topics under the current subject
            subjects[current_subject]["topics"].append(line.strip("- ").strip())

    # Sort the subjects alphabetically and topics within each subject
    sorted_subjects = sorted(subjects.items())
    for title, data in sorted_subjects:
        data["topics"].sort()

    # Save the edited file to the defined path with the final file name
    try:
        final_file_path = os.path.join(UPLOAD_FOLDER, final_file_name)
        with open(final_file_path, 'w', encoding='utf-8') as f:
            for title, data in sorted_subjects:
                # Write title and its links
                for link in data["links"]:
                    f.write(f"{title}:{link}\n")
                # Write topics under the title
                for topic in data["topics"]:
                    f.write(f"- {topic}\n")
    except Exception as e:
        logger.error(f"Error writing edited file for e2t: {e}")
        await message.reply_text(f"🚨 **Error**: Unable to write the edited file.\n\nDetails: {e}")
        return

    # Send the sorted and edited file back to the user
    try:
        await message.reply_document(
            document=final_file_path,
            caption="📥**𝗘𝗱𝗶𝘁𝗲𝗱 𝗕𝘆 ➤ 𝗧𝘂𝘀𝗵𝗮𝗿**"
        )
    except Exception as e:
        logger.error(f"Error sending edited file for e2t: {e}")
        await message.reply_text(f"🚨 **Error**: Unable to send the file.\n\nDetails: {e}")
    finally:
        # Clean up the temporary files
        if os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path)
        if os.path.exists(final_file_path):
            os.remove(final_file_path)


@bot.on_message(filters.command('yt2txt'))
async def ytplaylist_to_txt(client: Client, message: Message):
    """
    Handles the extraction of YouTube playlist/channel videos and sends a .txt file.
    """
    user_id = message.chat.id
    if user_id != OWNER_ID:
        await message.reply_text("**🚫 You are not authorized to use this command.\n\n🫠 This Command is only for owner.**")
        return

    # Request YouTube URL
    await message.delete()
    editable = await message.reply_text("📥 **Please enter the YouTube Playlist Url :**")
    input_msg = await client.listen(editable.chat.id)
    youtube_url = input_msg.text
    await input_msg.delete()
    await editable.delete()

    # Process the URL
    title, videos = get_videos_with_ytdlp(youtube_url)
    if videos:
        file_name = save_to_file(videos, title)
        await message.reply_document(
            document=file_name,
            caption=f"`{title}`\n\n📥 𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗕𝘆 ➤ 𝗧𝘂𝘀𝗵𝗮𝗿"
        )
        os.remove(file_name)
    else:
        await message.reply_text("⚠️ **Unable to retrieve videos. Please check the URL.**")
# --- Block 5 End ---
# --- Block 6 Start ---
# List users command
@bot.on_message(filters.command("userlist") & filters.user(SUDO_USERS))
async def list_users(client: Client, msg: Message):
    if SUDO_USERS:
        users_list = "\n".join([f"User ID : `{user_id}`" for user_id in SUDO_USERS])
        await msg.reply_text(f"SUDO_USERS :\n{users_list}")
    else:
        await msg.reply_text("No sudo users.")


# Help command
@bot.on_message(filters.command("help"))
async def help_command(client: Client, msg: Message):
    help_text = (
        "`/start` - Start the bot⚡\n\n"
        "`/tushar` - Download and upload files (sudo)🎬\n\n"
        "`/restart` - Restart the bot🔮\n\n"
        "`/stop` - Stop ongoing process🛑\n\n"
        "`/cookies` - Upload cookies file🍪\n\n"
        "`/e2t` - Edit txt file📝\n\n"
        "`/yt2txt` - Create txt of yt playlist (owner)🗃️\n\n"
        "`/sudo add` - Add user or group or channel (owner)🎊\n\n"
        "`/sudo remove` - Remove user or group or channel (owner)❌\n\n"
        "`/userlist` - List of sudo user or group or channel📜\n\n"

    )
    await msg.reply_text(help_text)

# Upload command handler
@bot.on_message(filters.command(["tushar"]))
async def upload(bot: Client, m: Message):
    if not is_authorized(m.chat.id):
        await m.reply_text("**🚫You are not authorized to use this bot.**")
        return

    editable = await m.reply_text(f"⚡𝗦𝗘𝗡𝗗 𝗧𝗫𝗧 𝗙𝗜𝗟𝗘⚡")
    input_file_msg: Message = await bot.listen(editable.chat.id)
    x = await input_file_msg.download()
    await input_file_msg.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))
    pdf_count = 0
    img_count = 0
    zip_count = 0
    video_count = 0

    try:
        with open(x, "r") as f:
            content = f.read()
        content_lines = content.split("\n")

        links = []
        for i in content_lines:
            if "://" in i:
                # Assuming the format is "title:url" or just "url"
                parts = i.split("://", 1)
                full_url = i
                # If there's a title part, the URL is the second element
                if len(parts) > 1:
                    full_url = parts[0] + "://" + parts[1] # Reconstruct full URL with protocol
                links.append(full_url) # Append the full URL or line

                if ".pdf" in full_url:
                    pdf_count += 1
                elif full_url.endswith((".png", ".jpeg", ".jpg", ".gif", ".bmp", ".tiff")): # Added more image extensions
                    img_count += 1
                elif ".zip" in full_url or ".rar" in full_url or ".7z" in full_url: # Added more archive extensions
                    zip_count += 1
                else: # This else covers video files if not pdf, img, or zip
                    video_count += 1
        os.remove(x) # Remove the uploaded file after processing
    except Exception as e:
        logger.error(f"Error processing input file for /tushar: {e}")
        await m.reply_text(f"😶𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗙𝗶𝗹𝗲 𝗜𝗻𝗽𝘂𝘁😶 or Error processing file: {e}")
        if os.path.exists(x):
            os.remove(x)
        return

    await editable.edit(f"`𝗧𝗼𝘁𝗮𝗹 🔗 𝗟𝗶𝗻𝗸𝘀 𝗙𝗼𝘂𝗻𝗱 𝗔𝗿𝗲 {len(links)}\n\n🔹Img : {img_count}  🔹Pdf : {pdf_count}\n🔹Zip : {zip_count}  🔹Video : {video_count}\n\n𝗦𝗲𝗻𝗱 𝗙𝗿𝗼𝗺 𝗪𝗵𝗲𝗿𝗲 𝗬𝗼𝘂 𝗪𝗮𝗻𝘁 𝗧𝗼 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱.`")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
    try:
        arg = int(raw_text)
    except ValueError: # Catch specific ValueError for int conversion
        arg = 1 # Default to 1 if not a valid number

    await editable.edit("📚 𝗘𝗻𝘁𝗲𝗿 𝗬𝗼𝘂𝗿 𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 📚\n\n🦠 𝗦𝗲𝗻𝗱 `1` 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗗𝗲𝗳𝗮𝘂𝗹𝘁 🦠")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == '1':
        b_name = file_name
    else:
        b_name = raw_text0

    await editable.edit("**📸 𝗘𝗻𝘁𝗲𝗿 𝗥𝗲𝘀𝗼𝗹𝘂𝘁𝗶𝗼𝗻 📸**\n➤ `144`\n➤ `240`\n➤ `360`\n➤ `480`\n➤ `720`\n➤ `1080`")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080"
        else:
            res = "UN" # 'UN' likely means unknown/unsupported resolution
    except Exception: # Catch any other potential errors
        res = "UN"

    await editable.edit("📛 𝗘𝗻𝘁𝗲𝗿 𝗬𝗼𝘂𝗿 𝗡𝗮𝗺𝗲 📛\n\n🐥 𝗦𝗲𝗻𝗱 `1` 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗗𝗲𝗳𝗮𝘂𝗹𝘁 🐥")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)

    if raw_text3 == '1':
        CR = '[𝗧𝘂𝘀𝗵𝗮𝗿](https://t.me/Tushar0125)'
    elif raw_text3: # This checks if raw_text3 is not empty
        try:
            # Use split with maxsplit=1 to handle only the first comma,
            # in case the user's name or link contains commas.
            text, link = raw_text3.split(',', 1)
            CR = f'[{text.strip()}]({link.strip()})'
        except ValueError:
            # If split fails (i.e., no comma found), use the raw text as is.
            CR = raw_text3.strip()
    else:
        # This 'else' handles cases where raw_text3 is empty or None.
        CR = '[𝗧𝘂𝘀𝗵𝗮𝗿](https://t.me/Tushar0125)' # Default value if input is empty or just spaces

    # --- Continue the /tushar command logic from here ---
    # This part was missing in your original snippet, but based on the context,
    # it's where the actual downloading and uploading would begin.
    # You will need to implement the core logic here, calling functions from 'core' and 'utils'.
    # For example:

    await editable.edit(f"Starting download and upload process for {len(links)} links...\n"
                        f"Batch Name: `{b_name}`\n"
                        f"Resolution: `{res}`\n"
                        f"Credit: {CR}\n"
                        f"Starting from link: `{arg}`")

    # Example placeholder for your actual download/upload loop
    # This section is crucial and needs to be implemented based on your 'core' and 'utils' modules.
    # The 'links' list now contains full URLs.
    for i, full_url_string in enumerate(links):
        if i + 1 >= arg:
            try:
                # Assuming 'helper.download_and_upload' is a function in your core.py
                # that handles the actual downloading and uploading of each link.
                # You need to pass the appropriate arguments to it.
                # Example:
                status_message = await editable.edit(f"Processing link {i+1}/{len(links)}: {full_url_string}")

                # THIS IS A PLACEHOLDER. You need to call your actual download/upload logic here.
                # e.g., await helper.download_file_and_upload_to_telegram(
                #     bot, m, full_url_string, b_name, res, CR, status_message
                # )
                logger.info(f"Attempting to process URL: {full_url_string}")
                await asyncio.sleep(5) # Simulate work for demonstration
                await status_message.edit_text(f"✅ Finished link {i+1}/{len(links)}")

            except Exception as e:
                logger.error(f"Error processing link {full_url_string}: {e}")
                await m.reply_text(f"⚠️ Error processing link {full_url_string}: {e}")
                await asyncio.sleep(5) # Wait before continuing to next link
        else:
            logger.info(f"Skipping link {i+1} as it's before the starting argument.")


    await m.reply_text("All links processed. Task completed! 🎉")
    # Clean up the downloaded file if it wasn't removed inside the loop (depends on your helper functions)
    # If files are temporarily saved in UPLOAD_FOLDER during download, ensure they are cleaned up.


# --- Main execution block ---
if __name__ == "__main__":
    # Ensure UPLOAD_FOLDER exists at startup
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    logger.info(f"UPLOAD_FOLDER set to: {UPLOAD_FOLDER}")

    # Start the FastAPI web server in a separate thread for health checks
    web_server_thread = threading.Thread(target=start_web_server)
    web_server_thread.daemon = True # Allow the main program to exit even if this thread is running
    web_server_thread.start()
    logger.info("Web server thread started.")

    # Start the Pyrogram bot (this will block the main thread)
    logger.info("Starting Telegram bot...")
    bot.run() # This line should be at the very end to keep the bot alive
# --- Block 6 End ---
