import discord
from discord.ext import commands
from discord.ext.commands import UserConverter

from collections import defaultdict
import json
import threading
import typing
from typing import Literal

from datetime import datetime, timedelta
from threading import Timer


class Reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        print('Reminders loaded.')


async def setup(bot):
    await bot.add_cog(Reminder(bot))
