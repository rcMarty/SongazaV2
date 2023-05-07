import asyncio
import discord
from discord.ext import commands
import configparser


# from sqlalchemy.dialects.sqlite import aiosqlite


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)
    return config


# conn = None
# def create_connection(db_file):
#     """ create a database connection to a SQLite database """
#     conn = None
#     try:
#         conn = aiosqlite.connect(db_file)
#     except Exception as e:
#         print(e)
#     finally:
#         if conn:
#             conn.close()


bot = commands.Bot(command_prefix=';', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Ready")
    for guild in bot.guilds:
        print("guild:", guild)
        print("guild id:", guild.id)


@bot.hybrid_command(name="command", description="Test command")
async def command(ctx: commands.Context):
    print(ctx)
    print(ctx.guild.id)
    await ctx.send("STFU")


@bot.hybrid_command(name="sync", description="Synchronization command")
@commands.is_owner()
async def sync(ctx):
    print("trying to sync")
    fmt = await ctx.bot.tree.sync()  # guild=discord.Object(id=829658812138520576))  # todo sync for only one guild
    await ctx.send(f"Synced {len(fmt)} commands to the guild.")
    print(fmt)


@bot.hybrid_command(name="shutdown", description="*windows xp logoff sound*")
@commands.is_owner()
async def shutdown(ctx):
    await bot.close()


async def load():
    await bot.load_extension("cogs.reputationcog")
    await bot.load_extension("cogs.musiccog")


async def main():
    await load()
    config = load_config("config.ini")
    await bot.start(config["DISCORD"]["DISCORD_TOKEN"])


if __name__ == "__main__":
    asyncio.run(main())
