import discord
import os
import aiohttp
from discord.ext import tasks
from hashlib import md5
import difflib

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

CHANNEL_ID = 1243967560647577710  # Remplacez par l'ID du canal où envoyer les messages
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')  # Clé API YouTube
PLAYLIST_URL = "https://youtube.com/playlist?list=PLOSCes_ANHgg9xPLAofLUEBDLZFlGGyNU&si=bkDfC0qfcgESbd4Y"  # Lien vers la playlist YouTube

# Stocker le contenu précédent pour détecter les mises à jour
previous_playlist = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_playlist_update.start()

@tasks.loop(seconds=3600)  # Vérifier toutes les heures
async def check_playlist_update():
    global previous_playlist

    # Extraire l'ID de la playlist à partir du lien
    playlist_id = PLAYLIST_URL.split("list=")[-1]

    current_playlist = await get_playlist_content(playlist_id)
    if current_playlist is None:
        return  # Erreur lors de la récupération du contenu, ignorer cette boucle

    if previous_playlist is not None and current_playlist != previous_playlist:
        diff = get_diff(previous_playlist, current_playlist)
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f'The playlist has been updated! Check it here: {PLAYLIST_URL}\nChanges:\n{diff}\n\n<@&1246455610963394672>')
        else:
            print(f"Channel with ID {CHANNEL_ID} not found")

    previous_playlist = current_playlist

async def get_playlist_content(playlist_id):
    videos = []
    page_token = ''
    while True:
        url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={YOUTUBE_API_KEY}&pageToken={page_token}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f'Error fetching playlist content: {response.status}')
                    return None
                data = await response.json()
                videos.extend([(item['snippet']['title'], item['snippet']['resourceId']['videoId'], item['snippet']['publishedAt']) for item in data.get('items', [])])
                page_token = data.get('nextPageToken')
                if not page_token:
                    break
    return videos

def get_diff(old_content, new_content):
    old_lines = format_playlist(old_content)
    new_lines = format_playlist(new_content)
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        lineterm='',
        fromfile='previous',
        tofile='current'
    )
    return '\n'.join(diff)

def format_playlist(playlist):
    # Convertir une liste de vidéos en lignes de texte
    lines = [f"{title} (ID: {video_id}, Published: {published_at})" for title, video_id, published_at in playlist]
    return lines

bot.run(os.getenv('DISCORD_TOKEN'))
