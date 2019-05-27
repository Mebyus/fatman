import botchecks

import discord
import pafy

from discord.ext import commands

if not discord.opus.is_loaded():
    print("[FAILED] Opus library")

_ffmpeg = r".\bin\ffmpeg.exe"
_ffmpeg_before = r"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
_default_volume = 0.2
_default_max_song_length = 600


class SongEntry:
    def __init__(self, request):
        self.request = request
        yt_video = pafy.new(request)
        self.title = yt_video.title
        self.length = yt_video.length
        self.audio_stream_url = yt_video.getbestaudio().url


class PlayerState:
    def __init__(self, bot, client, channel, volume = _default_volume):
        self.client = client
        self.channel = channel
        self.volume = volume
        self.bot = bot
        self.current_song = None
        self.stream = None
        self.songs = []  # basically a songs queue in a player
    
    def play_next(self, error):
        if self.songs:
            if self.stream:
                self.stream.cleanup()
            self.current_song = self.songs.pop(0)
            self.stream = discord.FFmpegPCMAudio(next_song.audio_stream_url, executable = _ffmpeg, pipe = True,
                                                 isurl = True, before_options = _ffmpeg_before, options = None)
            self.stream = discord.PCMVolumeTransformer(self.stream, self.volume)
            self.bot.loop.create_task(self.channel.send("Now playing: " + self.current_song.title +
                                                        "\nSong length: " + str(self.current_song.length)))
            self.client.play(self.stream, after = self.play_next)
        else:
            self.bot.loop.create_task(self.channel.send("There is nothing more to play. Queue is empty"))


class Music(commands.Cog):
    """
    Voice related commands.
    Works in multiple guilds at once.
    """

    def __init__(self, bot):
        self.bot = bot
        self.players = {}  # dictionary of {guild_id: player_state} pairs
        self.max_song_length = _default_max_song_length
    
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
        elif not ctx.guild.voice_client and ctx.guild.id not in self.players:
            new_client = await ctx.author.voice.channel.connect()
            self.players[ctx.guild.id] = PlayerState(self.bot, new_client, ctx.channel)
        elif not ctx.guild.voice_client:
            self.players[ctx.guild.id].client = await ctx.author.voice.channel.connect()
            self.players[ctx.guild.id].channel = ctx.channel
        elif ctx.guild.id not in self.players:
            self.players[ctx.guild.id] = PlayerState(self.bot, ctx.guild.voice_client, ctx.channel)
        elif ctx.guild.voice_client.channel == ctx.author.voice.channel:
            await ctx.send("What's wrong with you!? I'm already here")
        else:
            self.players[ctx.guild.id].channel = ctx.channel
            await ctx.guild.voice_client.move_to(ctx.author.voice.channel)
    
    @commands.command(name = "quit", aliases = ["q", "d", "disconnect", "leave"])
    @botchecks.in_same_voice()
    @commands.guild_only()
    async def quit(self, ctx):
        client = ctx.guild.voice_client
        await client.disconnect()

    @commands.command(name = "play", aliases = ["p"])
    @botchecks.in_same_voice()
    @commands.guild_only()
    async def play(self, ctx, *args):
        """
        Plays a song.
        If there is a song currently in the queue, then it is queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        """
        client = ctx.guild.voice_client
        player = self.players[ctx.guild.id]

        if args:
            url = args[0]
            new_song = SongEntry(url)
            if new_song.length <= self.max_song_length:
                player.songs.append(new_song)
                self.bot.loop.create_task(player.channel.send(new_song.title + " added to queue"))
            else:
                await ctx.send("This song is too long. I will ignore it")
                return
        if not (client.is_playing() or client.is_paused()):
            player.play_next(None)

    @commands.command(name = "list", aliases = ["l", "queue"])
    @botchecks.in_same_voice()
    @commands.guild_only()
    async def list(self, ctx):
        player = self.players[ctx.guild.id]
        client = ctx.guild.voice_client
        for song in player.songs:
            await ctx.send(song.title)

    @commands.command(name = "skip", aliases = ["s", "n", "next"])
    @botchecks.in_same_voice()
    @commands.guild_only()
    async def skip(self, ctx):
        client = ctx.guild.voice_client
        if not client.is_playing():
            pass
        else:
            client.stop()

    @commands.command(name = "pause", aliases = ["w", "wait"])
    @botchecks.in_same_voice()
    @commands.guild_only()
    async def pause(self, ctx):
        client = ctx.guild.voice_client
        if not client.is_playing():
            pass
        else:
            client.pause()

    @commands.command(name = "resume", aliases = ["r", "continue"])
    @botchecks.in_same_voice()
    @commands.guild_only()
    async def resume(self, ctx):
        client = ctx.guild.voice_client
        if not client.is_paused():
            pass
        else:
            client.resume()

    @commands.command(name = "volume", aliases = ["v"])
    @botchecks.in_same_voice()
    @commands.guild_only()
    async def volume(self, ctx, *, volume: str):
        client = ctx.guild.voice_client
        player = self.players[ctx.guild.id]
        try:
            new_volume = int(volume)
            if 0 <= new_volume <= 100:
                player.volume = new_volume / 100
            else:
                player.volume = _default_volume
                await ctx.send("Value \"" + volume + "\" is out of scope. Must be between 1 and 100\n "
                                                     "Volume is set to default = " + str(int(100 * _default_volume)))
        except ValueError:
            await ctx.send("Unable to convert value \"" + volume + "\" to an integer")

    @commands.command(name = "save")
    @botchecks.in_same_voice()
    @commands.guild_only()
    async def save(self, ctx):
        client = ctx.guild.voice_client
        player = self.players[ctx.guild.id]
        try:
            with open("queue.txt", "w") as save_file:
                for song in player.songs:
                    save_file.write(song.request + "\n")
        except FileNotFoundError:
            print("No save file")

    @commands.command(name = "load")
    @botchecks.in_same_voice()
    @commands.guild_only()
    async def load(self, ctx):
        client = ctx.guild.voice_client
        player = self.players[ctx.guild.id]
        try:
            with open("queue.txt", "r") as save_file:
                requests = save_file.read().split(sep = "\n")
            for request in requests[:-1]:  # TODO fix EOF
                new_song = SongEntry(request)
                player.songs.append(new_song)
        except FileNotFoundError:
            print("No save file")

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
        dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
        if isinstance(error, (botchecks.AuthorNotInVoice, botchecks.BotNotInVoice)):
            dm_channel.send(error)

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)
        dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
        if isinstance(error, botchecks.AuthorNotInVoice):
            await dm_channel.send(error)
        if isinstance(error, botchecks.BotNotInVoice):
            await ctx.send("Sorry, but I have nowhere to play")

    @skip.error
    async def stop_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)
        dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
        if isinstance(error, (botchecks.AuthorNotInVoice, botchecks.BotNotInVoice)):
            await dm_channel.send(error)

    @pause.error
    async def pause_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)
        dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
        if isinstance(error, (botchecks.AuthorNotInVoice, botchecks.BotNotInVoice)):
            await dm_channel.send(error)

    @resume.error
    async def resume_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)
        dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
        if isinstance(error, (botchecks.AuthorNotInVoice, botchecks.BotNotInVoice)):
            await dm_channel.send(error)

    @volume.error
    async def volume_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)
        dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
        if isinstance(error, (botchecks.AuthorNotInVoice, botchecks.BotNotInVoice)):
            await dm_channel.send(error)


def setup(bot):
    """
    Extension entry point
    """
    bot.add_cog(Music(bot))
    print("Music extension loaded")