import discord
import os
import aiohttp
from discord.ext import tasks
from hashlib import md5
from bs4 import BeautifulSoup
import difflib
import asyncio

intents = discord.Intents.default()

bot = discord.Client(intents=intents)

CHANNEL_ID = 1243967560647577710  # Replace with the ID of the channel where messages should be sent
TARGET_WEBSITE_URL = "https://dafuqboom.shop"  # Replace with the URL you want to monitor

# Store the previous content to detect updates
previous_content = None

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='dafuqboom.shop'))
    print(f'Logged in as {bot.user}')
    check_website_update.start()

@tasks.loop(seconds=10)
async def check_website_update():
    global previous_content

    current_content = await get_website_content(TARGET_WEBSITE_URL)
    if current_content is None:
        return  # Error fetching content, skip this loop

    if previous_content is not None and current_content != previous_content:
        diff = get_diff(previous_content, current_content)
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(f'The {TARGET_WEBSITE_URL} has been updated! Changes:\n{diff}\n\n<@&1269734191923462194>')

    previous_content = current_content

async def get_website_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f'Error fetching website content: {response.status}')
                return None
            content = await response.text()
            # Clean the HTML to eliminate non-significant changes
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            return text

def get_diff(old_content, new_content):
    diff = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        lineterm='',
        fromfile='previous',
        tofile='current'
    )
    return '\n'.join(diff)

bot.run(os.getenv('DISCORD_TOKEN'))
