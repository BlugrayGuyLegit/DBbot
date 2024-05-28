import discord
import os
import aiohttp
from discord.ext import tasks
from hashlib import md5

intents = discord.Intents.default()

bot = discord.Client(intents=intents)

CHANNEL_ID = 1243967560647577710  # Replace with the channel ID to send messages
TARGET_WEBSITE_URL = "https://dafuqboom.shop"  # Replace with the URL you want to monitor

# Store the hash of the previous content to detect updates
previous_content_hash = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_website_update.start()

@tasks.loop(seconds=10)
async def check_website_update():
    global previous_content_hash

    current_content_hash = await get_website_content_hash(TARGET_WEBSITE_URL)
    if current_content_hash != previous_content_hash:
        previous_content_hash = current_content_hash
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(f'The {TARGET_WEBSITE_URL} has been updated!')

async def get_website_content_hash(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f'Error fetching website content: {response.status}')
                return None
            content = await response.text()
            # Calculate the MD5 hash of the content
            return md5(content.encode('utf-8')).hexdigest()

bot.run(os.getenv('DISCORD_TOKEN'))
