import discord
from discord.ext import commands
import random
from discord.ext.commands import Bot
import os
from requests import get
from discord.ext.commands import MemberConverter
import json
import requests
import yt_dlp
from discord.voice_client import VoiceClient
import discord.voice_client
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
        self.ffmpeg_options = {'options': '-vn',
                               "executable": "usr/bin/ffmpeg"}

    @commands.Cog.listener()
    async def on_ready(self):
        print('MUSIC loaded.')

    @commands.hybrid_command(name="play", description="play any song from yt")
    async def play(self, ctx: commands.Context, url: str):
        print("play")
        try:

            await ctx.send("trying to play something")
            # here it should return voice_client but never returns
            voice_client = await ctx.author.voice.channel.connect()
            self.voice_clients[voice_client.guild.id] = voice_client
            print("connected to", ctx.author.voice.channel)

        except Exception as err:
            print("exeption:", err)

        try:
            print("trying to play something")
            loop = asyncio.get_event_loop()
            ytdl = yt_dlp.YoutubeDL(self.ydl_opts)
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            print("song:", data['url'])
            song = data['url']
            player = discord.FFmpegPCMAudio(song, **self.ffmpeg_options)

            self.voice_clients[ctx.guild.id].play(player)

        except Exception as err:
            print("exeption:", err)

    @commands.hybrid_command(name="stop", description="stop playing")
    async def stop(self, ctx: commands.Context):
        pass


async def setup(bot):
    await bot.add_cog(Music(bot))
