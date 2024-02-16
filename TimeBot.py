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

#Set up bot, receive all intents PLEASE.
intents = discord.Intents.all() 
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


#Connect to Discord, display a ready message.
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=SERVER_ID))
    print(f'Logged in as {client.user.name} succesfully!')

#Minting Event (On Message)
@client.event
async def on_message(message):
    if message.author.bot:
        return
    user_id = str(message.author.id)
    if message.guild:
        user_balance.setdefault(user_id, 0)
        user_balance[user_id] += (1 * message_multiplier[user_id])
        save_user_balance()
    

#/ping command
@tree.command(
    name="ping",
    description="Returns the latency of the bot.",
    guild=discord.Object(id=SERVER_ID)
)
async def ping(interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(client.latency * 1000)}ms", ephemeral=True)

#/balance command
@tree.command(
    name="balance",
    description="Shows your balance.",
    guild=discord.Object(id=SERVER_ID)
)
async def balance(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    balance = user_balance.get(user_id, 0)
    await interaction.response.send_message(f"Your balance: ${balance}", ephemeral=True)


#Literally just got rid of all of the new fancy balance code, rome wasn't built in a day D:

user_balance_file = 'user_balances.json'
message_multiplier_file = 'message_multiplier.json'

#Function to load the user balance file.
def load_user_balance():
    try:
        with open(user_balance_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
#Function to save user balance to the balance file.
def save_user_balance():
    try:
        with open(user_balance_file, 'w') as file:
            json.dump(user_balance, file)
    except FileNotFoundError:
        return {}

#Function to load the message multiplier file.
def load_message_multiplier():
    try:
        with open(message_multiplier_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

#Function to save message multiplier to the multiplier file.
def save_message_multiplier():
    try:
        with open(message_multiplier_file, 'w') as file:
            json.dump(message_multiplier, file)
    except FileNotFoundError:
        return {}
    
user_balance = load_user_balance()
message_multiplier = load_message_multiplier()


client.run(BOT_TOKEN)
