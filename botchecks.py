from discord.ext import commands


def author_in_voice():
    def predicate(ctx: commands.context.Context) -> bool:
        return bool(ctx.author.voice)
    return commands.check(predicate)


def bot_in_voice():
    def predicate(ctx: commands.context.Context) -> bool:
        return bool(ctx.guild.voice_client)
    return commands.check(predicate)