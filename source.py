import discord

from discord.ext import commands

_token = r"NTc3NDUwNjI4ODA5NDkwNDMy.XNlUvg.LsNqYfSCfZRwX0mGt-3enKTzUPg"
_prefix = "-"

print("Discord API version:", discord.__version__)

bot = commands.Bot(command_prefix = _prefix)

# Checks section

# Events section


@bot.event
async def on_ready():
    print("Started working")
    await bot.change_presence(activity = discord.Game(name = "Making a bot"))

# Commands section


@bot.command(name = "hello", aliases = ["hi"])
async def hello(ctx):
    await ctx.send("Hi, I'm fatman.")


@bot.command(name = "shutdown")
@commands.is_owner()
async def shutdown(ctx):
    print("Shutting down...")
    await ctx.send("You almost killed me. Taking a timeout to prepare revenge.")
    for voice_client in bot.voice_clients:
        await voice_client.disconnect()
    await bot.close()


@bot.command(name = "dsid")
async def dsid(ctx):
    dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
    await dm_channel.send(ctx.author.id)

# Errors section


@shutdown.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        ctx.send(error)

print("Initializing...")
bot.load_extension("music")
bot.run(_token)
print("Finished at ???")