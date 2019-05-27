from discord.ext import commands


class AuthorNotInVoice(commands.CheckFailure):
    def __init__(self, message = None):
        super().__init__(message or "You must be in a voice channel to use this command")


class BotNotInVoice(commands.CheckFailure):
    def __init__(self, message = None):
        super().__init__(message or "I need to be in a voice channel to perform this")


class NotInSameVoice(commands.CheckFailure):
    def __init__(self, message = None):
        super().__init__(message or "You need to be in the same voice channel as I to issue this command")


def author_in_voice(): # compatibility, remove later
    def predicate(ctx: commands.context.Context) -> bool:
        if not ctx.author.voice:
            raise AuthorNotInVoice()
        return True
    return commands.check(predicate)


def bot_in_voice():  # compatibility, remove later
    def predicate(ctx: commands.context.Context) -> bool:
        if not ctx.guild.voice_client:
            raise BotNotInVoice()
        return True
    return commands.check(predicate)


def in_same_voice():
    def predicate(ctx: commands.context.Context) -> bool:
        if not ctx.author.voice:
            raise AuthorNotInVoice()
        elif not ctx.guild.voice_client:
            raise BotNotInVoice()
        elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
            raise NotInSameVoice()
        else:
            return True

    return commands.check(predicate)