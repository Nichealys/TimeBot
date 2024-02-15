#Initialize the bot, let's get some of these gorgeous libraries going.
import discord
import discord from discord.ext import commands
from discord import app_commands
import json
import asyncio
import io
import os
import random
import time
import hashlib

#Fill in particuliar info here.
BOT_TOKEN = '' #The Bot Token from Discord. Enclosed in ''
AUTHORIZED_USER_ID = #The ID of the user that should have access to admin commands.
ANNOUNCEMENT_CHANNEL_ID = #The Channel ID where announcements (Minted Green Tokens, Milestones, Lottery, etc..)
SERVER_ID = #ID of the server that the bot should be in.

#Set up bot, receive all intents.
intents = discord.Intents.all() 
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

#Connect to Discord, display a ready message.
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=SERVER_ID))
    print("The bot has connected to Discord succefully!")

client.run(BOT_TOKEN)
