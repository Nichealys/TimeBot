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
        message_multiplier.setdefault(user_id, 1)
        user_balance[user_id] += (1 * message_multiplier[user_id])
        save_user_balance()
    
#COMMANDS

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
async def balance(interaction: discord.Interaction, user: discord.User):
    user_id = str(user.id)
    balance = user_balance.get(user_id, 0)
    await interaction.response.send_message(f"{user.nick}'s Balance: ${balance}", ephemeral=True)
    print(user)

#/pay command
@tree.command(
    name="pay",
    description="Transfer money from your inventory to someone else's inventory.",
    guild=discord.Object(id=SERVER_ID)
)
async def pay(interaction: discord.Interaction, recipient: discord.User, amount: int):
    user_id = str(interaction.user.id)
    recipient_id = str(recipient.id)
    if amount <= 0:
        await interaction.response.send_message("Please provide a valid positive amount to transfer.", ephemeral=True)
        return
    if user_id not in user_balance or user_balance[user_id] < amount:
        await interaction.response.send_message("You don't have enough to transfer that amount.", ephemeral=True)
        return
    user_balance[user_id] -= amount
    user_balance[recipient_id] = user_balance.get(recipient_id, 0) + amount
    save_user_balance()
    await interaction.response.send_message(f"${amount} transferred succesfully to {recipient.nick}.", ephemeral=True)
    

#USER DATA STORAGE

user_balance_file = 'user_balances.json'
user_green_token_file = 'user_green_token_balances.json'
message_multiplier_file = 'message_multiplier.json'
lottery_state_file = 'lottery_state.json'
lottery_tickets_file = 'lottery_tickets.json'

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

#Function to load the green token balance file.
def load_user_green_token_balance():
    try:
        with open(user_green_token_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
#Function to save green token balance to the balance file.
def save_user_green_token_balance():
    try:
        with open(user_green_token_balance_file, 'w') as file:
            json.dump(user_balance, file)
    except FileNotFoundError:
        return {}

#Function to load the lottery state.
def load_lottery_state():
    try:
        with open(lottery_state_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'is_active': False, 'pot': 0}

#Function to save the lottery state
def save_lottery_state(state):
    with open(lottery_state_file, 'w') as file:
        json.dump(state, file)
    except FileNotFoundError:
        return {}

#Function to load lottery ticket balances
def load_lottery_tickets():
    try:
        with open(lottery_tickets_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

#Function to save the lottery ticket balances
def save_lottery_tickets(tickets):
    with open(lottery_tickets_file, 'w') as file:
        json.dump(tickets, file)
    except FileNotFoundError:
        return {}


user_balance = load_user_balance()
user_green_token_balance = load_user_green_token_balance()
message_multiplier = load_message_multiplier()
lottery_state = load_lottery_state()
lottery_tickets = load_lottery_tickets()


client.run(BOT_TOKEN)
