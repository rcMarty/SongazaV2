import discord
from discord.ext import commands
from discord.ext.commands import UserConverter

from discord.voice_client import VoiceClient
from collections import defaultdict
import json
import datetime
import threading
import typing
import asyncio
import yt_dlp
from typing import Literal


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        
        self.queue = defaultdict(list) # todo more bots and queues per guild so there can be like 3 separate bots playing music in 3 separate channels
        self.bot = bot
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'auto'}
        self.encoder_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

         #all the music related stuff
        self.is_playing = False
        self.is_paused = False
        self.voice_clients = defaultdict(lambda: None)
        
    def search_yt(self,  search: str):
        ytdl = yt_dlp.YoutubeDL(self.ydl_opts)
        url = search # todo search by string or url (now by default)
        info = ytdl.extract_info(url, download=False)
        return info["url"]
            
    async def play_music(self, ctx: commands.Context):
        print("play_music")
        if len(self.queue[ctx.guild.id]) > 0:
            self.is_playing = True
            print("playing queue:", self.queue[ctx.guild.id])
            m_url = self.queue[ctx.guild.id][0]
            channel = ctx.author.voice.channel
            a = self.voice_clients[ctx.guild.id]
            print("channel:", channel)
            
            #try to connect to voice channel if you are not already connected
            if self.voice_clients[ctx.guild.id] == None :
                print("connecting to voice channel")
                self.voice_clients[ctx.guild.id] = await channel.connect()
                #in case we fail to connect
                if self.voice_clients[ctx.guild.id] == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            
            #remove the first element as you are currently playing it
            print("removing first element from queue")
            self.queue[ctx.guild.id].pop(0)

            self.voice_clients[ctx.guild.id].play(discord.FFmpegPCMAudio(m_url, **self.encoder_options), after=lambda e: self.play_next(ctx=ctx, voice_client=self.voice_clients[ctx.guild.id]))
        else:
            self.is_playing = False
            print("queue is empty")


    def play_next(self, ctx: commands.Context, voice_client: discord.VoiceClient):
        print("play_next")
        if len(self.queue[ctx.guild.id]) > 0:
            self.is_playing = True
            audio_url = self.queue[ctx.guild.id][0]
            self.queue[ctx.guild.id].pop(0)
            voice_client.play(discord.FFmpegPCMAudio(audio_url), after=lambda e: self.play_next(ctx, voice_client))
        else:
            self.is_playing = False
            print("queue is empty")


    @commands.Cog.listener()
    async def on_ready(self):
        print('MUSIC loaded.')

    @commands.hybrid_command(name="play", description="play any song from yt")
    async def play(self, ctx: commands.Context, url: typing.Optional[str] = None):
        voice_channel = ctx.author.voice.channel

        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
            return

        if self.is_paused:
            self.voice_clients[ctx.guild.id].resume()
            await ctx.send("Song resumed")
            self.search_yt(url)
            return
        
        if url is None:
            await ctx.send("No url provided")
            return
        
        song = self.search_yt(url)
    
        await ctx.send("Song added to the queue")
        print("song added to queue")
        self.queue[ctx.guild.id].append(song)
        print("queue:", self.queue[ctx.guild.id])
        if self.is_playing == False:
            print("playing")
            await self.play_music(ctx)

    @commands.hybrid_command(name="queue", description="add song to queue")
    async def add_to_queue(self, ctx: commands.Context, url: str, position: typing.Optional[int] = None):
        ytdl = yt_dlp.YoutubeDL(self.ydl_opts)
        info = ytdl.extract_info(url, download=False)
        audio_url = info["url"]
        if position is None:
            self.queue[ctx.guild.id].append(audio_url)
            await ctx.send(f"added {url} to queue")
            return
        
        if position < len(self.queue[ctx.guild.id]):
            self.queue[ctx.guild.id].insert(position, audio_url)
            await ctx.send(f"added {url} to queue at position {position}")
        else:
            self.queue[ctx.guild.id].append(audio_url)
            await ctx.send(f"added {url} to queue at last position")
            
    

    @commands.hybrid_command(name="skip", description="skip current song")
    async def skip(self, ctx: commands.Context):
        if self.is_playing:
            self.voice_clients[ctx.guild.id].stop()
            await ctx.send("Song skipped")
            return
        else:
            await ctx.send("No song playing")
            return
        
    @commands.hybrid_command(name="pause", description="pause current song")
    async def pause(self, ctx: commands.Context):
        if self.is_playing:
            self.voice_clients[ctx.guild.id].pause()
            self.is_paused = True
            await ctx.send("Song paused")
            return
        else:
            await ctx.send("No song playing")
            return

    # on disconnecting from voice channel
    #@bot.event
    @commands.Cog.listener()
    async def on_voice_state_update(self,member, before, after):
        print("on_voice_state_update")
        if before.channel is not None and after.channel is None and member.bot == True:
            print("bot left voice channel")
            guildid=member.guild.id
            
            self.is_playing = False
            self.is_paused = False
            # await self.voice_clients[guildid].disconnect()
            self.voice_clients[guildid] = None
            self.queue[guildid] = []

    

        

    

async def setup(bot):
    await bot.add_cog(Music(bot))
