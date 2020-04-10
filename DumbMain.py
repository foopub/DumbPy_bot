from os import getenv      
from discord.ext import commands      
from dotenv import load_dotenv      
import discord      
      
load_dotenv()      
TOKEN = getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='.')

all_cogs = getenv('ALL_COGS') 
@client.event      
async def on_ready():      
    print(f'{client.user} connected!') 

@client.command()
async def load(context: commands.Context, *, names: str) -> None:
    """
    Load modules. Names separated by a single space.
    Example usage: 
    .load One two THREE     #case insensitive
    .load all               #'all' to load all modules
    """
    if names.lower() == 'all': names = all_cogs
    for name in names.split(' '):
        try:
        client.load_extension(f'cogs.{name.lower()}')
            await context.send(f'Module {name.title()} loaded!')
        except:
            await context.send(f'Could not load {name.title()}!')

@client.command()
async def unload(context: commands.Context, *, names: str) -> None:
    """
    Unload modules. Names separated by a single space.
    Example usage: 
    .unload One two THREE     #case insensitive
    .unload all               #'all' to load all modules
    """
    if names.lower() == 'all': names = all_cogs
    for name in names.split(' '):
        try:
            client.unload_extension(f'cogs.{name.lower()}')
            await context.send(f'Module {name.title()} unloaded!')
        except:
            await context.send(f'Could not unload {name.title()}!')

@client.command()
async def reload(context: commands.Context, *, names: str) -> None:
    """
    Reload modules. Names separated by a single space.
    Example usage: 
    .reload One two THREE     #case insensitive
    .reload all               #'all' to load all modules
    """
    if names.lower() == 'all': names = all_cogs
    for name in names.split(' '):
        try:
            client.unload_extension(f'cogs.{name.lower()}')
            client.load_extension(f'cogs.{name.lower()}')
            await context.send(f'Module {name.title()} reloaded!')
        except:
            await context.send('Could not reload {name.title()}!')

client.run(TOKEN)
