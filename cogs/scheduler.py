from discord.ext import commands
import discord
from typing import Optional

class Scheduler(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.events = {}

    @commands.command(name='remind')
    async def remind(self, context: commands.Context,
            member: Optional[discord.Member]):
        """
        Model scheduler function.
        """

        pass
   
    @commands.group(name='event', alias='events')
    async def event(self, context: commands.Context):
        """
        Schedule a command to be executed at a given time.
        """
        pass

    @event.command(name='add')
    async def add(self, context: commands.Context):
        pass
    
    @event.command(name='edit')
    async def edit(self, context: commands.Context):
        pass

    @event.command(name='list')
    async def list(self, context: commands.Context):
        pass

    @event.command(name='remove')
    async def remove(self, context: commands.Context):
        pass

def setup(client: commands.Bot) -> None:
    client.add_cog(Scheduler(client))
    
