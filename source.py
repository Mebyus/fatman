import discord
import pafy
from discord.ext import commands

_token = "NTc3NDUwNjI4ODA5NDkwNDMy.XNlUvg.LsNqYfSCfZRwX0mGt-3enKTzUPg"
_prefix = "-"
_mp3ex = "file_example_MP3_700KB.mp3"
_ytex = "https://www.youtube.com/watch?v=9bZkp7q19f0"
_ffmpeg = ".\\bin\\ffmpeg.exe"

print("Discord API version:", discord.__version__)
print("Opus library is", "loaded" if discord.opus.is_loaded() else "not loaded. Voice API will be unavailable.")

def get_voice_client(self, channel: discord.VoiceChannel) -> discord.VoiceClient:
    """
    Gets a voice client connected to a given channel
    """
    for voice_client in self.voice_clients:
        if voice_client.channel == channel:
            return voice_client
    return None

commands.Bot.get_voice_client = get_voice_client
bot = commands.Bot(command_prefix = _prefix)

# Checks section

# Events section

@bot.event
async def on_ready():
    print("Started working.")
    await bot.change_presence(activity = discord.Game(name = "Making a bot"))

# Commands section

# class Main_Commands():
#     def __init__(self, bot):
#         self.bot = bot


@bot.command(name = "hello")
async def _hello(ctx):
    await ctx.send("Hi, I'm fatman.")

@bot.command(name = "shutdown")
@commands.is_owner()
async def _shutdown(ctx):
    print("Shutting down...")
    await ctx.send("You almost killed me. Taking a timeout to prepare revenge.")
    for voice_client in bot.voice_clients:
        # if voice_client.is_playing():
        #     voice_client.stop()
        await voice_client.disconnect()
    await bot.close()

@bot.command(name = "connect")
async def _connect(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
    else:
        await ctx.send("Where are you? Join voice channel first.")

@bot.command(name = "disconnect")
async def _disconnect(ctx):
    if ctx.author.voice:
        voice_client = bot.get_voice_client(ctx.author.voice.channel)
        if voice_client:
            await voice_client.disconnect()
        else:
            pass
    else:
        pass

@bot.command(name = "play")
async def _play(ctx, *arg):
    if ctx.author.voice:
        voice_client = bot.get_voice_client(ctx.author.voice.channel)
        if not voice_client:
            pass
        elif voice_client.is_playing():
            await ctx.send("Don't you hear? I'm already playing!")
        else:
            if arg:
                url = arg[0]
                video = pafy.new(url)
                audio_stream = video.getbestaudio()
                _exaudio = discord.FFmpegPCMAudio(audio_stream.url, executable = _ffmpeg, pipe = True, isurl = True)
            else:
                _exaudio = discord.FFmpegPCMAudio(_mp3ex, executable = _ffmpeg)

            voice_client.play(_exaudio)
    else:
        pass

@bot.command(name = "pause")
async def _pause(ctx):
    if ctx.author.voice:
        voice_client = bot.get_voice_client(ctx.author.voice.channel)
        if voice_client:
            voice_client.pause()
        else:
            pass
    else:
        pass

@bot.command(name = "resume")
async def _pause(ctx):
    if ctx.author.voice:
        voice_client = bot.get_voice_client(ctx.author.voice.channel)
        if voice_client:
            voice_client.resume()
        else:
            pass
    else:
        pass

@bot.command(name = "stop")
async def _pause(ctx):
    if ctx.author.voice:
        voice_client = bot.get_voice_client(ctx.author.voice.channel)
        if voice_client:
            voice_client.stop()
        else:
            pass
    else:
        pass

@bot.command(name = "dsid")
async def _dsid(ctx):
    dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
    await dm_channel.send(ctx.author.id)

    # if ctx.author.dm_channel:
    #     ctx.author.dm_channel.send(ctx.author.id)
    # else:
    #     ctx.author.create_dm().send(ctx.author.id)

print("Initializing...")
# bot.load_extension("Music")
bot.run(_token)
print("Finished at ???")