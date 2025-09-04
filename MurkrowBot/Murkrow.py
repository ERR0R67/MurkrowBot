import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from datetime import datetime
import os

# Load Token and target user (it just targets porygon but I added the variable for testing)
TOKEN = 'WouldntYouLikeToKnowWeatherboy'
Target_users = 204255221017214977 # This is YAGPDB's user ID
GuildID = 610951535526019112      # This is the server ID number for FLMG

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True
Client = commands.Bot(command_prefix='/', intents=intents)

# Syncing slash command
@Client.event
async def on_ready():
    await Client.wait_until_ready()
    try:
        guild = discord.Object(id=GuildID)
        synced = await Client.tree.sync(guild=guild)
        print(f'Synced Command')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

# Defining /gift
@app_commands.command(name='gift', description='Scrape Porygon messages from two channels after a given date')
@app_commands.guilds(discord.Object(id=GuildID))
@app_commands.describe(
    channel1="First channel to find shiny things",
    channel2="Second channel to find shiny things",
    start_time="Start time of finding shiny things YYYY-MM-DD HH:MM:SS"
)

# Command for pulling messages into text file
#@Client.tree.command(name='gift') I don't remember why I commented this or exactly what it does but the bot works without it so whatever
async def gift(interaction: discord.Interaction, channel1: discord.TextChannel, channel2: discord.TextChannel, start_time: str):
    # Make input date a usable time format
    try:
        Start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    
    #Exception for when the date is wrong because try needs an exception
    except ValueError:
        await interaction.response.send_message('Invalid time, use YYYY-MM-DD HH:MM:SS')
        return
    #The main exception is if you get literally anything else wrong it just doesn't do anything and I have no clue how to throw that exception in client
        
    # Defining the channel the bot is pulling from
    channels = [channel1, channel2]
    
    # Context message
    await interaction.response.send_message(f'Pulling Porygon messages in {channel1} and {channel2} from {Start}')

    # Create text file to append messages
    filename = f'porygon_commands.txt'

    # initializing message count for reporting (I wanna make the command pretty, sue me)
    commandcount = 0
    
    try:
        # Open file for appending, I don't know why encoding is necessary but every similar command I can find uses it so I'm using it
        with open(filename, 'w', encoding='utf-8') as f:
            for channel in channels:   
                async for msg in channel.history(after=Start, oldest_first=True, limit=None):
                    if msg.author.id == Target_users:  # The above loops just target all messages from target user in both selected channels
                        embed = msg.embeds[0]          # Making embeds readable because Chou put effort into the embeds

                        # Title contains username and scavenge line, skips all cooldown notifs
                        title = embed.title or ""
                        activity = ['went scavenging', 'shook the berry tree']
                        matching_phrase = next((phrase for phrase in activity if phrase in title), None)
                        if not matching_phrase:
                            continue

                        # Extract username from message
                        scavenger = title.split(matching_phrase)[0].strip()

                        # Description extracts items from message
                        description = embed.description or ""
                        lines = description.splitlines()

                        # This loop pulls each item line from the description and formats the data into a usable unbelievaboat command
                        for line in lines:
                            openings = ['You got a ', 'You found a ']
                            for opening in openings:
                                if line.startswith(opening):
                                    itemname = line.removeprefix(opening).rstrip('!').strip()
                                    command = f'/item-give member:@{scavenger} item:{itemname}'
                                    f.write(command + '\n')
                                    commandcount += 1
                                    break

        # Send generated text file in discord
        completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await interaction.followup.send(content=f'Complete at {completion_time}, {commandcount} commands attached below. Caw',
                       file=discord.File(filename))
        
    except Exception as e:
        await interaction.followup.send(f'Error: {str(e)}')

# Start Bot
Client.tree.add_command(gift)
Client.run(token=TOKEN)
