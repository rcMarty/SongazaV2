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


class RemindMe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lock = threading.Lock()

        # we will see what is best format or smthng
        self.reminders = list(defaultdict(
            lambda: {"date": datetime.now(), "message": "something you wanted to remember"}))
        # Struct:
        #     "(user id, guild id)": [
        #     {
        #        "date": "08.05.2023",
        #        "message": "something you wanted to remember"
        #                                                       # maybe stuff like channel where sould it remind or only dm
        #     }, and so on
        # ]

        # once per time save
        x = datetime.today()
        y = x.replace(day=x.day, hour=1, minute=0, second=0,
                      microsecond=0) + timedelta(days=1)
        delta_t = y - x
        secs = delta_t.total_seconds()

        t = Timer(secs, self.save)
        t.start()

    async def spam_protection(self, ctx: commands.Context):

        global author_msg_counts

        author_id = ctx.author.id
        curr_time = datetime.now().timestamp() * 1000  # current time

        self.author_msg_times[author_id].append(curr_time)

        # Find the beginning of our time window.
        expr_time = curr_time - self.time_window_milliseconds

        # remove old messages
        expired_msgs = [
            msg_time for msg_time in self.author_msg_times[author_id] if msg_time < expr_time]
        for msg_time in expired_msgs:
            self.author_msg_times[author_id].remove(msg_time)

        if len(self.author_msg_times[author_id]) > self.max_msg_per_window:
            await ctx.send("only one rep per user per hour")
            return True
        return False

    @commands.Cog.listener()
    async def on_ready(self):
        self.load()
        print('RemindMe loaded.')

    def save(self):
        self.lock.acquire()
        save = self.reps.copy()
        save = {str(k): v for k, v in save.items()}

        with open("data/reps.json", "w") as f:
            json.dump(save, f)
        self.lock.release()

    def load(self):

        self.lock.acquire()
        print("loading reps")
        try:
            with open("data/reps.json", "r") as f:
                print("F", f.errors)
                tmp = json.load(f)
                self.reps = {eval(k): v for k, v in tmp.items()}
                print(self.reps)
        except Exception as e:
            print("error loading reps: ", e)
        self.lock.release()

    @commands.hybrid_command(name="saverep", description="save reputation")
    @commands.is_owner()
    async def saverep(self, ctx: commands.Context):
        threading.Thread(target=self.save).start()
        await ctx.send("Reputation saved")


async def setup(bot):
    await bot.add_cog(RemindMe(bot))
