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


class Reputation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reps = defaultdict(lambda: {"count": 0, "log": list()})  # todo mby sqlite database

        self.lock = threading.Lock()

        x = datetime.today()
        y = x.replace(day=x.day, hour=1, minute=0, second=0, microsecond=0) + timedelta(days=1)
        delta_t = y - x
        secs = delta_t.total_seconds()

        t = Timer(secs, self.save)
        t.start()

    @commands.Cog.listener()
    async def on_ready(self):
        self.load()
        print('REP loaded.')

    @commands.hybrid_command(name="rep", description="Give reputation to a user")
    async def rep(self, ctx: commands.Context, direction: typing.Optional[Literal['++', '--']], user: str, notes: typing.Optional[str] = "Idk why just because"):
        print("before user: ", user)
        print("direction: ", direction)
        userconverter = UserConverter()
        try:
            user = await userconverter.convert(ctx, user)
        except:
            await ctx.send("Pepega jsi a nikdo takový tu není")
            return

        if user == ctx.author:
            await ctx.send("Nemůžeš měnit reputaci sobě Pepego")
            return

        today = datetime.date.today()

        if direction == "++":
            self.reps[(user.id, ctx.guild.id)]["count"] += 1
            self.reps[(user.id, ctx.guild.id)]["log"].append({"from": user.id, "action": "+rep", "reason": notes, "timestamp": today.strftime("%d.%m.%Y")})
            await ctx.send(f"+rep {user}")
        elif direction == "--":
            self.reps[(user.id, ctx.guild.id)]["count"] -= 1
            self.reps[(user.id, ctx.guild.id)]["log"].append({"from": user.id, "action": "-rep", "reason": notes, "timestamp": today.strftime("%d.%m.%Y")})
            await ctx.send(f"-rep {user}")
        elif direction is None:
            tmp = self.reps[(user.id, ctx.guild.id)]["count"]
            await ctx.send(f"{user} has {tmp} reps")

    @commands.hybrid_command(name="replog", description="Show reputation log")
    async def replog(self, ctx: commands.Context, user: str):
        userconverter = UserConverter()
        try:
            user = await userconverter.convert(ctx, user)
        except:
            await ctx.send("Pepega jsi a nikdo takový tu není")
            return

        embed = discord.Embed(title=f"Reputace pro {user}", description=f"Reputace pro {user} je {self.reps[(user.id, ctx.guild.id)]['count']}")
        for i in self.reps[(user.id, ctx.guild.id)]["log"]:
            embed.add_field(name=i["timestamp"], value=f"{i['action']} pro \"{i['reason']}\"", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="represet", description="Reset reputation")
    @commands.is_owner()
    async def represet(self, ctx: commands.Context, user: str):
        userconverter = UserConverter()
        try:
            user = await userconverter.convert(ctx, user)
        except:
            await ctx.send("Pepega jsi a nikdo takový tu není")
            return

        self.reps[(user.id, ctx.guild.id)]["count"] = 0
        self.reps[(user.id, ctx.guild.id)]["log"] = list()
        await ctx.send(f"Reputace pro {user} resetována")

    # on message event
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.content.startswith("+rep") or message.content.startswith("-rep"):
            mess = message.content.split(" ", 2)
            # s.split('mango', 1)[1]
            if len(mess) != 3:
                await message.channel.send("format is +rep/--rep @user reason")
                return
            # ctx = await self.bot.get_context(message)
            # get ctx from message
            ctx = await self.bot.get_context(message)
            await self.rep(ctx, "++" if mess[0] == "+rep" else "--", mess[1], mess[2])

            return

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
        await ctx.send("Reputace uložena")


async def setup(bot):
    await bot.add_cog(Reputation(bot))
