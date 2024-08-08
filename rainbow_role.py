import discord
import random
import asyncio
import os

ROLE_ID = 1270742938191659028
GUILD_ID = 1193262535168753824

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def generate_random_color():
    return discord.Color(random.randint(0, 0xFFFFFF))

@client.event
async def on_disconnect():
    print("The bot has been disconnected.")

@client.event
async def on_resumed():
    print("The bot has resumed the session.")

@client.event
async def on_ready():
    print(f'Bot connected as {client.user} et prêt.')
    
@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')
    guild = client.get_guild(GUILD_ID)
    role = guild.get_role(ROLE_ID)
    
    while True:
        try:
            new_color = generate_random_color()
            await role.edit(color=new_color)
            print(f'Role color changed to {new_color}')
            await asyncio.sleep(60)
        except discord.DiscordException as e:
            print(f'An error occurred: {e}')
            await asyncio.sleep(5)  # wait a bit before retrying

client.run(os.getenv('DISCORD_TOKEN'))
