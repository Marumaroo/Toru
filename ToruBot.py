import discord
import asyncio
import config
import requests
from functions import readFile, writeFile
from discord.ext import commands

BOT_PREFIX = ('$','!')
blacklistw = readFile('blacklist.txt')
client = commands.Bot(command_prefix = BOT_PREFIX)

@client.event
async def on_ready():
    print('logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-------')

@client.command()
async def bitcoin():
    url = 'http://api.coinmarketcap.com/v1/ticker/bitcoin/'
    json = requests.get(url).json()
    await client.say('The price of Bitcoin is $%s' % round(float(json[0]['price_usd']),2))

@client.command()
async def blacklist(word):
    word = word.lower()
    if word not in blacklistw:
        blacklistw.append(word)
        writeFile('blacklist.txt', blacklistw)
        await client.say('The word %s has been blacklisted' % word)
    else:
        await client.say('The word %s has already been blacklisted' % word)

@client.event
async def on_message(message):
    if client.user.id != message.author.id:
        msg = message.content.lower().split(' ')
        print(msg)
        if bool(set(blacklistw).intersection(msg)) and not message.content.startswith(BOT_PREFIX):
            await client.delete_message(message)
            await client.send_message(message.channel, 'Your message has been deleted as it contains a blacklisted word')
    await client.process_commands(message)

client.run(config.TOKEN)