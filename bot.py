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

# URL of the website to monitor
TARGET_WEBSITE_URL = "https://steamcommunity.com/id/dafuqboom"  # Replace with the URL you want to monitor

# Store previous status and activity to avoid spamming
previous_discord_status = None
previous_discord_activity_name = None
previous_website_status = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_user_status.start()

@tasks.loop(seconds=10)
async def check_user_status():
    global previous_discord_status, previous_discord_activity_name, previous_website_status

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

    # Check website status
    website_status = await get_website_status(TARGET_WEBSITE_URL)
    if website_status != previous_website_status:
        previous_website_status = website_status
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(f'DaFuq!?Boom! is now `online/offline` on steam!')

async def get_website_status(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f'Error fetching website status: {response.status}')
                return 'unknown'
            content = await response.text()
            # Check for a specific keyword or element in the webpage content
            if "User is online" in content:
                return 'online'
            elif "User is offline" in content:
                return 'offline'
            return 'unknown'

bot.run(os.getenv('DISCORD_TOKEN'))
