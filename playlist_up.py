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

# Liste des URLs des playlists
PLAYLIST_URLS = [
    "https://youtube.com/playlist?list=PL-ZXraMeHBPLA1JOBRLDLUN9C6dGTbSZH&si=MwoV5Gp-SWdjxvbT",
    "https://youtube.com/playlist?list=PL-ZXraMeHBPJHXBhrNowJaQslyqtUg-tZ&si=M07imAq2-HCz1VPS",
    "https://youtube.com/playlist?list=PL-ZXraMeHBPIEQ71rP-EtFoUIy8dVqam7&si=Ya-Lhymc-cDpFHx8"
]

# Stocker le contenu précédent pour détecter les mises à jour
previous_playlists = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_playlists_update.start()

@tasks.loop(seconds=3600)  # Vérifier toutes les heures
async def check_playlists_update():
    global previous_playlists

    for playlist_url in PLAYLIST_URLS:
        # Extraire l'ID de la playlist à partir du lien
        playlist_id = playlist_url.split("list=")[-1]

        current_playlist = await get_playlist_content(playlist_id)
        if current_playlist is None:
            continue  # Erreur lors de la récupération du contenu, ignorer cette playlist

        # Vérifier si la playlist a été mise à jour
        if playlist_id in previous_playlists and current_playlist != previous_playlists[playlist_id]:
            diff = get_diff(previous_playlists[playlist_id], current_playlist)
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                await channel.send(f'The playlist `{playlist_id}` has been updated! Check it here: {playlist_url}\nChanges:\n{diff}\n\n<@&1246455610963394672>')
            else:
                print(f"Channel with ID {CHANNEL_ID} not found")

        # Mettre à jour le contenu précédent
        previous_playlists[playlist_id] = current_playlist

async def get_playlist_content(playlist_id):
    videos = []
    page_token = ''
    while True:
        url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={YOUTUBE_API_KEY}&pageToken={page_token}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f'Error fetching playlist content for playlist {playlist_id}: {response.status}')
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
