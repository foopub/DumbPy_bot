from discord.ext import commands
import discord

class Roles(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @commands.command(name='speak')
    async def speak(self, context: commands.Context) -> None:
        """      
        This is used to take control of the bot from the console.      
        There's probably better ways.      
        """                       
        await context.send('I cannot :(')      
        while True:      
            x = input('Say something: ')      
            if x == 'stop':                                              
                break      
            try:      
                print(eval(x))      
            except:      
                await context.send(x)

def setup(client: commands.Bot) -> None:
    client.add_cog(Roles(client))
    
