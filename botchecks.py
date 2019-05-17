from discord.ext import commands


class AuthorNotInVoice(commands.CheckFailure):
    def __init__(self, message = None):
        super().__init__(message or 'You must be in a voice channel to use this command')


class BotNotInVoice(commands.CheckFailure):
    def __init__(self, message = None):
        super().__init__(message or 'I need to be in a voice channel to perform this')


def author_in_voice():
    def predicate(ctx: commands.context.Context) -> bool:
        if not ctx.author.voice:
            raise AuthorNotInVoice()
        return True
    return commands.check(predicate)


def bot_in_voice():
    def predicate(ctx: commands.context.Context) -> bool:
        if not ctx.guild.voice_client:
            raise BotNotInVoice()
        return True
    return commands.check(predicate)