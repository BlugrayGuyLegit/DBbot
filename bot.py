import discord
import os
from discord.ext import tasks

intents = discord.Intents.default()
intents.presences = True  # Enable presences to monitor user status
intents.members = True  # Enable members to get server members

bot = discord.Client(intents=intents)

TARGET_USER_ID = 1158064576722641028  # Replace with the target user's ID
CHANNEL_ID = 1243967560647577710  # Replace with the channel ID to send messages

# Store previous status and activity to avoid spamming
previous_status = None
previous_activity_name = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_user_status.start()

@tasks.loop(seconds=10)
async def check_user_status():
    global previous_status, previous_activity_name

    guild = bot.guilds[0]  # Assuming the bot is in a single guild
    member = guild.get_member(TARGET_USER_ID)
    
    if member:
        current_status = str(member.status)
        current_activity = next((activity for activity in member.activities if isinstance(activity, discord.Game)), None)
        current_activity_name = current_activity.name if current_activity else None
        
        # Log the current status and activity for debugging purposes
        print(f'Current status: {current_status}')
        print(f'Current activity: {current_activity_name}')
        
        # Check if status has changed
        if current_status != previous_status:
            previous_status = current_status
            if current_status == 'online':
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f'{member.name} is online!')

        # Check if activity has changed
        if current_activity_name != previous_activity_name:
            previous_activity_name = current_activity_name
            if current_activity_name:
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f'{member.name} started {current_activity_name}!')
            elif previous_activity_name:  # Activity ended
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f'{member.name} stopped playing {previous_activity_name}!')

bot.run(os.getenv('DISCORD_TOKEN'))
