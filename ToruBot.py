import discord
import asyncio
import config
import requests
import youtube_dl
from functions import readFile, writeFile
from discord.ext import commands

BOT_PREFIX = ('$','!')
blacklistw = readFile('blacklist.txt')
client = commands.Bot(command_prefix = BOT_PREFIX)
players = {}
queue = []

def check_queue(id):
    queue.pop(0)
    if queue:
        players[id] = queue[0]
        queue[0].start()
        client.say('Now playing: %s' % queue[0].title)

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

@client.command()
async def whitelist(word):
    word = word.lower()
    if word in blacklistw:
        blacklistw.remove(word)
        writeFile('blacklist.txt', blacklistw)
        await client.say('The word %s has been removed from the blacklist' % word)
    else:
        await client.say('The word %s has not been blacklisted' % word)

@client.command(pass_context=True)
async def clear(ctx, amount=100):
    channel = ctx.message.channel
    messages = []
    async for message in client.logs_from(channel, limit=int(amount)+1):
        messages.append(message)
    await client.delete_messages(messages)
    await client.say('%s messages have been deleted' % amount)

@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()

@client.command(pass_context=True)
async def play(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
    if queue:
        queue.append(player)
        await client.say("%s queued: [%s of %s]" % (player.title, queue.index(player),len(queue)-1))
    else:
        queue.append(player)
        players[server.id] = player
        player.start()
        await client.say('Now playing: %s' % player.title)

@client.command(pass_context=True) 
async def playlist(ctx, url): #broken
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    ydl = youtube_dl.YoutubeDL()
    
    with ydl:
        r = ydl.extract_info(url, download=False)
        for video in r['entries']:
            player = await voice_client.create_ytdl_player('https://www.youtube.com/watch?v=%s' % video['id'], after=lambda: check_queue(server.id))
            queue.append(player)
            await client.say('%s queued: [%s of %s]' % (player.title, queue.index(player)+1, len(queue)))
    
    player = queue[0]
    player.start()
    await client.say('Now Playing: %s' % player.title)
    
@client.command(pass_context=True)
async def skip(ctx):
    id = ctx.message.server.id
    players[id].pause()
    check_queue(id)

@client.command(pass_context=True)
async def pause(ctx):
    id = ctx.message.server.id
    players[id].pause()

@client.command(pass_context=True)
async def stop(ctx):
    id = ctx.message.server.id
    players[id].stop()

@client.command(pass_context=True)
async def resume(ctx):
    id = ctx.message.server.id
    players[id].resume()

@client.command()
async def error():
    await client.say('OOPSIE WOOPSIE!! Uwu We make a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!')

@client.event
async def on_message(message):
    if client.user.id != message.author.id:
        msg = message.content.lower().split(' ')
        if bool(set(blacklistw).intersection(msg)) and not message.content.startswith(BOT_PREFIX):
            await client.delete_message(message)
            await client.send_message(message.channel, 'Your message has been deleted as it contains a blacklisted word')
    await client.process_commands(message)

client.run(config.TOKEN)