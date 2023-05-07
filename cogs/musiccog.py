import discord
from discord.ext import commands
import random
from discord.ext.commands import Bot
from dotenv import load_dotenv
import os
from requests import get
import openai
from discord.ext.commands import MemberConverter
import json
import requests
import yt_dlp
from discord.voice_client import VoiceClient
from pydub import AudioSegment
import asyncio
from collections import defaultdict


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.voice_clients = []
        self.bot = bot
        self.is_playing = False
        self.paused = False
        self.queue = defaultdict(list)
        self.ydl_opts = {'format': 'bestaudio/best'}
        self.ffmpeg_options = {'options': '-vn', "executable": "usr/bin/ffmpeg"}

    @commands.Cog.listener()
    async def on_ready(self):
        print('MUSIC loaded.')

    @commands.hybrid_command(name="play", description="play any song from yt")
    async def play(self, ctx: commands.Context, url: str):
        # print("play")
        # try:
        #     # send message to auhthor to channel where he wrote that message
        #     await ctx.send("trying to play something")
        #     # voice_client = await ctx.author.voice.channel.connect()  # here it should return voice_client but never returns
        #     # self.voice_clients[voice_client.guild.id] = voice_client
        #     # print("connected to", ctx.author.voice.channel)
        #
        # except Exception as err:
        #     print("exeption:", err)
        #
        # try:
        #     print("trying to play something")
        #     loop = asyncio.get_event_loop()
        #     ytdl = youtube_dl.YoutubeDL(self.ydl_opts)
        #     data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        #     print("song:", data['url'])
        #     song = data['url']
        #     player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options)
        #
        #     # self.voice_clients[ctx.guild.id].play(player)
        #
        # except Exception as err:
        #     print("exeption:", err)
        # # print(url)
        # # channel = ctx.author.voice.channel
        # # print(channel)
        # #
        # # voice_client = await channel.connect()
        # #
        # # print("connected")
        # # # self.voice_clients[ctx.guild.id] = voice_client
        # #
        # # loop = asyncio.get_event_loop()
        # # print("generated loop")
        # # ytdl = youtube_dl.YoutubeDL(self.ydl_opts)
        # # try:
        # #     data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        # #     print("extracted info")
        # #     song = data[url]
        # # except Exception as e:
        # #     print(e)
        # #     return
        # #
        # # print(data)
        # # player = discord.FFmpegPCMAudio(song, **{'options': '-vn'}, executable="usr/bin/ffmpeg")
        # # voice_client.play(player)
        # # print("playing")

        try:
            print("trying to connect")
            voice_client = await ctx.author.voice.channel.connect()
            print("connected")
            voice_client.encoder_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            ytdl = yt_dlp.YoutubeDL(self.ydl_opts)
            info = ytdl.extract_info(url, download=False)
            print(info)
            audio_url = info["url"]
            print(audio_url)
            voice_client.play(discord.FFmpegPCMAudio(audio_url))
            if voice_client is None:
                voice_client = ctx.voice_client
                await voice_client.disconnect()

        except discord.errors.ClientException:
            await voice_client.disconnect()
        except AttributeError:
            await ctx.send(f"johin a voice channel")
        pass

    @commands.hybrid_command(name="stop", description="stop playing")
    async def stop(self, ctx: commands.Context):
        pass


async def setup(bot):
    await bot.add_cog(Music(bot))
