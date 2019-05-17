import botchecks

import discord
import pafy

from discord.ext import commands

if not discord.opus.is_loaded():
    print("[FAILED] Opus library")

_ffmpeg = r".\bin\ffmpeg.exe"
_default_volume = 0.2


class SongEntry:
    def __init__(self, request):
        self.request = request
        yt_video = pafy.new(request)
        self.title = yt_video.title
        self.length = yt_video.length
        self.audio_stream_url = yt_video.getbestaudio().url


class PlayerState:
    def __init__(self, client, channel, volume = _default_volume):
        self.client = client
        self.channel = channel
        self.volume = volume
        self.songs = []  # basically a songs queue in a player
    
    def play_next(self, error):
        if self.songs:
            new_entry = self.songs.pop(0)
            print(new_entry.length)
            audio_stream = discord.FFmpegPCMAudio(new_entry.audio_stream_url, executable = _ffmpeg, pipe = True, isurl = True)
            audio_stream = discord.PCMVolumeTransformer(audio_stream, 0.2)
            # self.channel.send("Now playing: " + new_entry.title)
            self.client.play(audio_stream, after = self.play_next)
        else:
            pass
            # await self.channel.send("Bad news! Queue has ended")


class Music(commands.Cog):
    """
    Voice related commands.
    Works in multiple guilds at once.
    """

    def __init__(self, bot):
        self.bot = bot
        self.states = {}  # dictionary of {guild_id: player_state} pairs 
    
    # Commands section

    @commands.command(name = "join", aliases = ["j", "c", "summon", "connect"])
    @commands.guild_only()
    @commands.cooldown(3, 60, type = commands.BucketType.guild)
    async def join(self, ctx):
        """
        Joins a voice channel, which is used by author of the command
        """
        if not ctx.author.voice:
            await ctx.send("Where are you? Join voice channel first.")
        elif not ctx.guild.voice_client and ctx.guild.id not in self.states:
            self.states[ctx.guild.id] = PlayerState(await ctx.author.voice.channel.connect(), ctx.channel)
        elif not ctx.guild.voice_client:
            self.states[ctx.guild.id].client = await ctx.author.voice.channel.connect()
            self.states[ctx.guild.id].channel = ctx.channel
        elif ctx.guild.id not in self.states:
            self.states[ctx.guild.id] = PlayerState(ctx.guild.voice_client, ctx.channel)
        elif ctx.guild.voice_client.channel == ctx.author.voice.channel:
            await ctx.send("What's wrong with you!? I'm already here")
        else:
            self.states[ctx.guild.id].channel = ctx.channel
            await ctx.guild.voice_client.move_to(ctx.author.voice.channel)
    
    @commands.command(name = "quit", aliases = ["q", "d", "l", "disconnect", "leave"])
    @commands.guild_only()
    async def quit(self, ctx):
        if not ctx.author.voice:
            pass
        elif not ctx.guild.voice_client:
            pass
        elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
            pass
        else:
            await ctx.guild.voice_client.disconnect()

    @commands.command(name = "play", aliases = ["p"])
    @commands.guild_only()
    async def play(self, ctx, *, url: str):
        """
        Plays a song.
        If there is a song currently in the queue, then it is queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        """
        if not ctx.author.voice:
            pass
        elif not ctx.guild.voice_client:
            await ctx.send("Sorry, but I have nowhere to play")
        elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
            pass
        elif ctx.guild.voice_client.is_playing() or ctx.guild.voice_client.is_paused():
            self.states[ctx.guild.id].songs.append(SongEntry(url))
            await ctx.send("Your song has been added to queue")
        else:
            new_entry = SongEntry(url)
            print(new_entry.length)
            audio_stream = discord.FFmpegPCMAudio(new_entry.audio_stream_url, executable = _ffmpeg, pipe = True, isurl = True, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
            audio_stream = discord.PCMVolumeTransformer(audio_stream, self.states[ctx.guild.id].volume)
            await ctx.send("Now playing: " + new_entry.title)
            ctx.guild.voice_client.play(audio_stream, after = self.states[ctx.guild.id].play_next)

    @commands.command(name = "skip", aliases = ["s", "n", "next"])
    @commands.guild_only()
    async def skip(self, ctx):
        if not ctx.author.voice:
            pass
        elif not ctx.guild.voice_client:
            pass
        elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
            pass
        elif not ctx.guild.voice_client.is_playing():
            pass
        else:
            ctx.guild.voice_client.stop()

    @commands.command(name = "pause", aliases = ["w", "wait"])
    @botchecks.author_in_voice()
    @botchecks.bot_in_voice()
    @commands.guild_only()
    async def pause(self, ctx):
        if not ctx.author.voice:
            pass
        elif not ctx.guild.voice_client:
            pass
        elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
            pass
        elif not ctx.guild.voice_client.is_playing():
            pass
        else:
            ctx.guild.voice_client.pause()

    @commands.command(name = "resume", aliases = ["r", "continue"])
    @commands.guild_only()
    async def resume(self, ctx):
        if not ctx.author.voice:
            pass
        elif not ctx.guild.voice_client:
            pass
        elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
            pass
        elif not ctx.guild.voice_client.is_paused():
            pass
        else:
            ctx.guild.voice_client.resume()

    @commands.command(name = "volume", aliases = ["v"])
    @commands.guild_only()
    async def volume(self, ctx, *, volume: str):
        if not ctx.author.voice:
            pass
        elif not ctx.guild.voice_client:
            pass
        elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
            pass
        else:
            try:
                new_volume = int(volume)
                if 0 <= new_volume <= 100:
                    self.states[ctx.guild.id].volume = new_volume / 100
                else:
                    self.states[ctx.guild.id].volume = _default_volume
                    await ctx.send("Value \"" + volume + "\" is out of scope. Must be between 1 and 100\n Volume is set to default = " + str(int(100 * _default_volume)))
            except ValueError:
                await ctx.send("Unable to convert value \"" + volume + "\" to an integer")

    # Error handling section

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(error)

    @quit.error
    async def quit_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)

    @skip.error
    async def stop_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)

    @pause.error
    async def pause_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)

    @resume.error
    async def resume_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)

    @volume.error
    async def volume_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)


def setup(bot):
    """
    Extension entry point
    """
    bot.add_cog(Music(bot))