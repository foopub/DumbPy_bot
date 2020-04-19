from discord.ext import commands
import discord

class Music(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.group()
    async def mu(self, context: commands.Context):
        pass

    @mu.command()
    async def play(self, context: commands.Context):
        self.vclient = await context.author.voice.channel.connect()
        pass

    @mu.command()
    async def leave(self, context: command.Context):
        await self.vclient.disconnect()

def setup(client: commands.Bot) -> None:
    client.add_cog(Music(client))
    
