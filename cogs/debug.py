from discord.ext import commands
import discord
from aioconsole import ainput

class Debug(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @commands.command(name='speak')
    async def debug(self, context: commands.Context) -> None:
        """      
        This is used to take control of the bot from the console.      
        There's probably better ways.      
        """                       
        await context.send('*Ignore this...*')
        while True:
            line = await ainput("(ainupt):")
            if line == "close interpreter": 
                break
            try:
                exec(line)
            except Exception as e:
                print(e)

def setup(client: commands.Bot) -> None:
    client.add_cog(Debug(client))
    
