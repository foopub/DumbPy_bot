from discord.ext import commands
import discord
from typing import Optional
import time
import dateparser as dtp
import schedule as sch 

class Scheduler(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.events = {}

    @commands.command(name='remind')
    async def remind(self, context: commands.Context,
            member: Optional[discord.Member],
            message: str,
            *, time: str):
        """
        Schedule a reminder, message must be enclosed in "". 
        This function uses the dateparser python module to convert natural
        language times to a valid datetime.

        """
        if not member:
            member = context.author
        
        def job():
            context.send('Reminder')

        sch.every()
        

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
    
