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
import datetime
import hashlib
from datetime import datetime, timedelta
from typing import Literal


#Fill in particuliar info here.
BOT_TOKEN = '' #The Bot Token from Discord. Enclosed in ''
AUTHORIZED_USER_ID = #The ID of the user that should have access to admin commands.
ANNOUNCEMENT_CHANNEL_ID = #The Channel ID where announcements (Minted Green Tokens, Milestones, Lottery, etc..)
SERVER_ID = #ID of the server that the bot should be in.
GREEN_TOKEN_CHANCE = 1000 #The chance that a Green Token will be minted when a user sends a message.
LOTTERY_TICKET_PRICE = 10 #The price of a single lottery ticket
GAMBLE_WIN_PROBABILITY = 50 #The chance that a user wins when gambling through the gamble command. 1/x
GAMBLING_GIF = ["https://tenor.com/bUqTI.gif", "https://tenor.com/qilXWf0scHP.gif", "https://tenor.com/b1Uy2.gif", "https://tenor.com/bKBOs.gif", "https://tenor.com/inlvw8b43pB.gif", "https://tenor.com/vdvl.gif"]


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
        user_green_token_balance.setdefault(user_id, 0)
        message_multiplier.setdefault(user_id, 1)
        user_balance[user_id] += (1 * message_multiplier[user_id])
        global dollar_minted_amount
        dollar_minted_amount += (1 * message_multiplier[user_id])
        save_user_balance()
        save_dollar_minted_amount()
        
        if random.randint(1, GREEN_TOKEN_CHANCE) == GREEN_TOKEN_CHANCE:
            user_green_token_balance[user_id] += 1
            announcement_channel = client.get_channel(ANNOUNCEMENT_CHANNEL_ID)
            if announcement_channel:
                await announcement_channel.send(f"🎉 <@{user_id}> has minted a Green Token!")
                save_user_green_token_balance()
        await update_status()

#Update Bot Status
async def update_status():
    status_message = f'TD${dollar_minted_amount}'
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=status_message))
    
#COMMANDS:
    
#/leaderboard command
@tree.command(
    name="leaderboard",
    description="Displays a Leaderboard, ranking users from highest to lowest TD$ balance.",
    guild=discord.Object(id=SERVER_ID)
)
async def leaderboard(interaction: discord.Interaction):
    sorted_users = sorted(user_balance.items(), key=lambda item: (item[1], user_green_token_balance.get(item[0], 0)), reverse=True)
    leaderboard_text = "**Leaderboard**\n"
    position = 1
    guild = client.get_guild(SERVER_ID)
    for user_id, balance in sorted_users:
        user = guild.get_member(int(user_id))
        if user:
            leaderboard_text += f"{position}. {user.display_name} - TD${balance}\n"
            position += 1
    await interaction.response.send_message(leaderboard_text, ephemeral=True)

#/gamble command
@tree.command(
    name="gamble",
    description="Gamble TD$ or Green Tokens.",
    guild=discord.Object(id=SERVER_ID)
)
async def gamble(interaction: discord.Interaction, amount: int, type: Literal["Green Tokens", "Dollars"]):
    user_id = str(interaction.user.id)
    if type == "Dollars":
        balance = user_balance.get(user_id, 0)
    if type == "Green Tokens":
        balance = user_green_token_balance.get(user_id, 0)


    if balance < amount:
        await interaction.response.send_message("You do not have enough balance to gamble.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("Please provide a valid positive amount to gamble.", ephemeral=True)
        return
    
    if type == "Dollars":
        user_balance[user_id] -= amount
        save_user_balance()
    if type == "Green Tokens":
        user_green_token_balance[user_id] -= amount
        save_user_green_token_balance()
    
    win = random.randint(1, 100) <= GAMBLE_WIN_PROBABILITY
    await interaction.response.send_message(GAMBLING_GIF[random.randint(0, (len(GAMBLING_GIF) - 1))], ephemeral=True)
    await asyncio.sleep(1)
    if win:
        if type == "Dollars":
            user_balance[user_id] += amount * 2
            save_user_balance()
            msg = f"You won TD${amount * 2}!"
            await interaction.followup.send(msg, ephemeral=True)
        if type == "Green Tokens":
            user_green_token_balance[user_id] += amount * 2
            save_user_green_token_balance()
            msg = f"You won {amount * 2} Green Tokens!"
            await interaction.followup.send(msg, ephemeral=True)
    else:
        msg = f"You lost... :["
        await interaction.followup.send(msg, ephemeral=True)

    

#/buytickets command
@tree.command(
    name="buytickets",
    description="Buy lottery tickets.",
    guild=discord.Object(id=SERVER_ID)
)
async def buytickets(interaction: discord.Interaction, amount: int):
    global lottery_state, user_balance, lottery_tickets
    if not lottery_state['is_active']:
        await interaction.response.send_message("There is no active lottery at the moment.", ephemeral=True)
        return
    user_id = str(interaction.user.id)
    global LOTTERY_TICKET_PRICE
    total_cost = amount * LOTTERY_TICKET_PRICE
    if user_balance.get(user_id, 0) < total_cost:
        await interaction.response.send_message("You do not have enough balance to buy these tickets.", ephemeral=True)
        return
    user_balance[user_id] -= total_cost
    lottery_state['pot'] += total_cost
    lottery_tickets[user_id] = lottery_tickets.get(user_id, 0) + amount
    save_user_balance()
    save_lottery_state(lottery_state)
    save_lottery_tickets(lottery_tickets)
    if lottery_state['pot'] % 100 == 0:
        announcement_channel = client.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        if announcement_channel:
            await announcement_channel.send(f"# 🎉 The lottery pot has reached TD${lottery_state['pot']}!")
    await interaction.response.send_message(f"You have successfully purchased {amount} tickets for **TD${total_cost}**!", ephemeral=True)


#/startlottery command
@tree.command(
    name="startlottery",
    description="Starts the lottery.",
    guild=discord.Object(id=SERVER_ID)
)
async def start_lottery(interaction: discord.Interaction):
    global lottery_state, lottery_tickets, LOTTERY_TICKET_PRICE
    user_id = str(interaction.user.id)
    if user_id != str(AUTHORIZED_USER_ID):
        await interaction.response.send_message("You are not authorized to start the lottery.", ephemeral=True)
        return
    if lottery_state['is_active']:
        await interaction.response.send_message("A lottery is already active!", ephemeral=True)
        return
    lottery_state = {'is_active': True, 'pot': 0}
    lottery_tickets = {}
    save_lottery_state(lottery_state)
    save_lottery_tickets(lottery_tickets)
    await interaction.response.send_message("The lottery has started!", ephemeral=True)
    announcement_channel = client.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    if announcement_channel:
        await announcement_channel.send(f"# 🎉 The lottery has started!\nBuy your tickets now for TD${LOTTERY_TICKET_PRICE} per ticket using the /buytickets command! 💳")


#/stoplottery command
@tree.command(
    name="stoplottery",
    description="Stops the lottery and picks a winner.",
    guild=discord.Object(id=SERVER_ID)
)
async def stop_lottery(interaction: discord.Interaction):
    global lottery_state, user_balance, lottery_tickets
    user_id = str(interaction.user.id)
    if user_id != str(AUTHORIZED_USER_ID):
        await interaction.response.send_message("You are not authorized to stop the lottery.", ephemeral=True)
        return
    if not lottery_state['is_active']:
        await interaction.response.send_message("There is no active lottery to stop.", ephemeral=True)
        return
    # Selecting a winner
    tickets_pool = [(user_id, ticket_count) for user_id, ticket_count in lottery_tickets.items() for _ in range(ticket_count)]
    if not tickets_pool:
        await interaction.response.send_message("No tickets were sold, lottery cannot be concluded.", ephemeral=True)
        lottery_state = {'is_active': False, 'pot': 0}
        save_lottery_state(lottery_state)
        return
    winner_id, _ = random.choice(tickets_pool)
    winner_amount = lottery_state['pot']
    user_balance[winner_id] = user_balance.get(winner_id, 0) + winner_amount
    lottery_state = {'is_active': False, 'pot': 0}
    lottery_tickets = {}
    save_user_balance()
    save_lottery_state(lottery_state)
    save_lottery_tickets(lottery_tickets)
    announcement_channel = client.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    if announcement_channel:
        await announcement_channel.send(f"# 🎉 The lottery draw has concluded!\n💵 The winner is <@{winner_id}> with a prize of TD${winner_amount}!")
    await interaction.response.send_message("The lottery has been stopped and the winner has been chosen.", ephemeral=True)



#/ping command
@tree.command(
    name="ping",
    description="Returns the latency of the bot.",
    guild=discord.Object(id=SERVER_ID)
)
async def ping(interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(client.latency * 1000)}ms", ephemeral=True)

@tree.command(
    name="inventory",
    description="Shows a user's inventory.",
    guild=discord.Object(id=SERVER_ID)
)
async def inventory(interaction: discord.Interaction, user: discord.User):
    user_id = str(user.id)
    dollarbalance = user_balance.get(user_id, 0)
    greentokenbalance = user_green_token_balance.get(user_id, 0)
    lotteryticketbalance = lottery_tickets.get(user_id, 0)
    await interaction.response.send_message(f"**{user.display_name}**\nTD${dollarbalance}\nGreen Tokens: {greentokenbalance}\nLottery Tickets: {lotteryticketbalance}", ephemeral=True)

#/transfer command
@tree.command(
    name="transfer",
    description="Transfer TD$ or Green Tokens to someone else's inventory.",
    guild=discord.Object(id=SERVER_ID)
)
async def transfer(interaction: discord.Interaction, amount: int, type: Literal["Dollars", "Green Tokens"], recipient: discord.User):
    user_id = str(interaction.user.id)
    recipient_id = str(recipient.id)
    if type == "Dollars":
        if amount <= 0:
            await interaction.response.send_message("Please provide a valid positive amount to transfer.", ephemeral=True)
            return
        if user_id not in user_balance or user_balance[user_id] < amount:
            await interaction.response.send_message("You don't have enough to transfer that amount.", ephemeral=True)
            return
        user_balance[user_id] -= amount
        user_balance[recipient_id] = user_balance.get(recipient_id, 0) + amount
        save_user_balance()
        await interaction.response.send_message(f"TD${amount} transferred succesfully to {recipient.display_name}.", ephemeral=True)
    if type == "Green Tokens":
        if amount <= 0:
            await interaction.response.send_message("Please provide a valid positive amount to transfer.", ephemeral=True)
            return
        if user_id not in user_green_token_balance or user_green_token_balance[user_id] < amount:
            await interaction.response.send_message("You don't have enough to transfer that amount.", ephemeral=True)
            return
        user_green_token_balance[user_id] -= amount
        user_green_token_balance[recipient_id] = user_green_token_balance.get(recipient_id, 0) + amount
        save_user_green_token_balance()
        await interaction.response.send_message(f"{amount} Green Tokens transferred succesfully to {recipient.display_name}.", ephemeral=True)

#USER DATA STORAGE

user_balance_file = 'user_balances.json'
user_green_token_file = 'user_green_token_balances.json'
message_multiplier_file = 'message_multiplier.json'
lottery_state_file = 'lottery_state.json'
lottery_tickets_file = 'lottery_tickets.json'
dollar_minted_amount_file = 'dollar_minted_amount.json'



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
        with open(user_green_token_file, 'w') as file:
            json.dump(user_green_token_balance, file)
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

#Function to load the minted amount of dollars
def load_dollar_minted_amount():
    try:
        with open(dollar_minted_amount_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

#Function to save the minted amount of dollars
def save_dollar_minted_amount():
    try:
        with open(dollar_minted_amount_file, 'w') as file:
            json.dump(dollar_minted_amount, file)
    except FileNotFoundError:
        return {}
    
dollar_minted_amount = load_dollar_minted_amount()
user_balance = load_user_balance()
user_green_token_balance = load_user_green_token_balance()
message_multiplier = load_message_multiplier()
lottery_state = load_lottery_state()
lottery_tickets = load_lottery_tickets()



client.run(BOT_TOKEN)
