import discord
from discord.ext import commands
import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor
import os
from youtubesearchpython import VideosSearch

class MyLogger:
    def debug(self, msg):
        if msg.startswith('[debug]'):
            pass
        else:
            self.info(msg)
    
    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    @staticmethod
    def error(msg):
        print(msg)


class MyCustomPP(PostProcessor):
    def run(self, info):
        self.to_screen('Doing stuff')
        return [], info


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting...')


client = commands.Bot(command_prefix="-")


@client.command(name="play", aliases=["p"])
async def play(ctx, *args):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Песня не закончилась, Пёс. Стопни или слушай")
        return

    voice_channel = discord.utils.get(ctx.guild.voice_channels, name='Music')

    try:
        await voice_channel.connect()
    except discord.errors.ClientException:
        pass

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    ydl_opts = {
            'format': '140',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }],
            #'logger': MyLogger(),
            #'progress_hooks': [my_hook],
            }
    url = ''
    if not args[0].startswith('http'):
        url = ' '.join(args)
        videos_search = VideosSearch(url)
        url = videos_search.result()['result'][0]['id']
        await ctx.send(videos_search.result()['result'][0]['link'])
    else:
        url = args[0]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")

    if voice.is_playing():
        voice.stop()
        voice.play(discord.FFmpegPCMAudio("song.mp3"))
    else:
        voice.play(discord.FFmpegPCMAudio("song.mp3"))


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    await voice.disconnect()
    os.remove("song.mp3")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Ниче не играет")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Ниче не на паузе")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


@client.command()
async def h(ctx):
    await ctx.send('Какроче в двух словах как работает бот\n-play [ссылку на видос с ютуба или название песни]\n' +
                   'Песня будет останавливать текущую и сразу играть\nТак как очереди на данный момент нет')

client.run('ODk1Mzc4MTUwOTM3MjA2ODc0.YV3r4g.xCOO6PFY-SuXnaRsLdfhQiJpo_w')
