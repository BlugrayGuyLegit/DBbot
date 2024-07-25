import discord
import os
import aiohttp
from discord.ext import tasks
from hashlib import md5
from bs4 import BeautifulSoup
import difflib

intents = discord.Intents.default()

bot = discord.Client(intents=intents)

CHANNEL_ID = 1243967560647577710  # Remplacez par l'ID du canal où envoyer les messages
TARGET_WEBSITE_URL = "https://dafuqboom.shop"  # Remplacez par l'URL que vous souhaitez surveiller

# Stocker le contenu précédent pour détecter les mises à jour
previous_content = None

@bot.event
    async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='dafuqboom.shop'))
    print(f'Logged in as {bot.user}')
    check_website_update.start()

@tasks.loop(seconds=10)
async def check_website_update():
    global previous_content

    current_content = await get_website_content(TARGET_WEBSITE_URL)
    if current_content is None:
        return  # Erreur lors de la récupération du contenu, ignorer cette boucle

    if previous_content is not None and current_content != previous_content:
        diff = get_diff(previous_content, current_content)
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(f'The {TARGET_WEBSITE_URL} has been updated! Changes:\n{diff}')

    previous_content = current_content

async def get_website_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f'Error fetching website content: {response.status}')
                return None
            content = await response.text()
            # Nettoyer le HTML pour éliminer les changements non significatifs
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
