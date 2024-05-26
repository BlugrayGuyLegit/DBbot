import discord
import os
import aiohttp
from discord.ext import tasks

intents = discord.Intents.default()
intents.presences = True  # Enable presences to monitor user status
intents.members = True  # Enable members to get server members

bot = discord.Client(intents=intents)

TARGET_USER_ID = 1158064576722641028  # Replace with the target user's ID
CHANNEL_ID = 1243967560647577710  # Replace with the channel ID to send messages

STEAM_API_KEY = os.getenv('STEAM_API_KEY')
STEAM_ID = '76561198041196864'  # Replace with the target user's Steam ID

# Store previous status and activity to avoid spamming
previous_discord_status = None
previous_discord_activity_name = None
previous_steam_status = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_user_status.start()

@tasks.loop(seconds=10)
async def check_user_status():
    global previous_discord_status, previous_discord_activity_name, previous_steam_status

    guild = bot.guilds[0]  # Assuming the bot is in a single guild
    member = guild.get_member(TARGET_USER_ID)
    
    if member:
        current_discord_status = str(member.status)
        current_discord_activity = next((activity for activity in member.activities if isinstance(activity, discord.Game)), None)
        current_discord_activity_name = current_discord_activity.name if current_discord_activity else None
        
        # Check if Discord status has changed
        if current_discord_status != previous_discord_status:
            previous_discord_status = current_discord_status
            if current_discord_status == 'online':
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f'{member.name} is online!')

        # Check if Discord activity has changed
        if current_discord_activity_name != previous_discord_activity_name:
            if previous_discord_activity_name and not current_discord_activity_name:
                # User stopped playing a game
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f'{member.name} stopped playing {previous_discord_activity_name}!')
            previous_discord_activity_name = current_discord_activity_name
            if current_discord_activity_name:
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f'{member.name} started {current_discord_activity_name}!')

    # Check Steam status
    steam_status = await get_steam_status(STEAM_ID)
    if steam_status != previous_steam_status:
        previous_steam_status = steam_status
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(f'Steam user is now {steam_status}!')

async def get_steam_status(steam_id):
    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if 'response' in data and 'players' in data['response'] and len(data['response']['players']) > 0:
                player = data['response']['players'][0]
                steam_status = player.get('personastate', 0)
                return {
                    0: 'offline',
                    1: 'online',
                    2: 'busy',
                    3: 'away',
                    4: 'snooze',
                    5: 'looking to trade',
                    6: 'looking to play'
                }.get(steam_status, 'unknown')
    return 'unknown'

bot.run(os.getenv('DISCORD_TOKEN'))
