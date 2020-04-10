from discord.ext import commands
import discord

class Basic(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @commands.command(name='ping')
    async def ping(self, context: commands.Context) -> None:       
        """
        Basic ping.
        """          
        await context.send(f'Ping is {self.client.latency*1000} ms')

def setup(client: commands.Bot) -> None:
    client.add_cog(Basic(client))
    
