import discord
import os
from discord.ext import tasks

intents = discord.Intents.default()
intents.presences = True  # Enable presences to monitor user status
intents.members = True  # Enable members to get server members

bot = discord.Client(intents=intents)

TARGET_USER_ID = 123456789012345678  # Replace with the target user's ID
CHANNEL_ID = 987654321098765432  # Replace with the channel ID to send messages

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_user_status.start()

@tasks.loop(seconds=10)
async def check_user_status():
    guild = discord.utils.get(bot.guilds)
    member = guild.get_member(TARGET_USER_ID)
    
    if member:
        if str(member.status) == 'online':
            channel = bot.get_channel(CHANNEL_ID)
            await channel.send(f'{member.name} is online!')
        
        for activity in member.activities:
            if isinstance(activity, discord.Game):  # Check if the activity is a game
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f'{member.name} started {activity.name}!')

bot.run(os.getenv('DISCORD_TOKEN'))
