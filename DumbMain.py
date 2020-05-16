from os import getenv      
from discord.ext import commands      
from dotenv import load_dotenv      
import discord
from cogs.sup import checks
      
load_dotenv()      
TOKEN = getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix=';')

all_cogs = getenv('ALL_COGS') 

@client.event      
async def on_ready():      
    print(f'{client.user} connected!') 

@client.check
async def bot_banned(context: commands.Context) -> bool:
    #return 'bot_banned' not in [i.name for i in context.author.roles]
    return context.author.id in [607614577412145172, 266052628427964417]

@client.command(name='load')
@commands.is_owner()
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
            raise

@client.command(name='unload')
@commands.is_owner()
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
            raise

@client.command(name='reload')
@commands.is_owner()
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
            await context.send(f'Could not reload {name.title()}!')
            raise

client.run(TOKEN)
