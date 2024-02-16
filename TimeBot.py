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
    user_id = interaction.user.id
    balances = get_user_balance(user_id)
    message = f"Your balance: {balances['dollar_balance']} dollars, {balances['green_token_balance']} green tokens."
    await interaction.response.send_message(message, ephemeral=True)




''' FUNCTIONS AND VARIABLE FOR MANAGING USER BALANCES AND INVENTORY SPACE
    ALL VERY VERY VERYVERY VERY VERY VERY VERY VERY VERY VERY VERY VERY VERY
    IMPORTANT: This is a very basic function that will be used to manage user balances and inventory space.'''

USER_BALANCES_FILE = "user_balances.json"  

# Initialize user balances file
if not os.path.exists(USER_BALANCES_FILE):
    with open(USER_BALANCES_FILE, 'w') as file:
        json.dump({}, file)

# Function for reading user balances.
def read_user_balances():
    with open(USER_BALANCES_FILE, 'r') as file:
        return json.load(file)
    
# Function for updating user balances
def update_user_balances(user_id, dollar_balance=None, green_token_balance=None, lottery_tickets=None):
    balances = read_user_balances()
    if str(user_id) not in balances:
        balances[str(user_id)] = {"dollar_balance": 0, "green_token_balance": 0, "lottery_tickets": 0}

        if str(user_id) not in balances:
            balances[str(user_id)] = {"dollar_balance": 0, "green_token_balance": 0}
    
        if dollar_balance is not None:
            balances[str(user_id)]['dollar_balance'] = dollar_balance
    
        if green_token_balance is not None:
            balances[str(user_id)]['green_token_balance'] = green_token_balance

        if green_token_balance is not None:
            balances[str(user_id)]['lottery_tickets'] = lottery_tickets
    
        with open(USER_BALANCES_FILE, 'w') as file:
            json.dump(balances, file, indent=4)

#Function to get the balance of a user.
def get_user_balance(user_id):
    balances = read_user_balances()
    return balances.get(str(user_id), {"dollar_balance": 0, "green_token_balance": 0, "lottery_tickets": 0})

client.run(BOT_TOKEN)
