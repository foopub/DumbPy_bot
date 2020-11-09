from discord.ext import commands
import discord
from typing import Optional, List
import itertools as itt
from datetime import datetime, timedelta
import pyparsing as pp
from discord.errors import Forbidden
import random 

async def webhooksay(message: discord.Message, 
        channel: discord.TextChannel,
        content: Optional[str]=None,
        delete: bool=False) -> None:
    """
    Quotes a message using a webhook.
    """
    if content is None:
        content = message.content
    webhooks = await channel.webhooks()
    atts = message.attachments
    bundle = []
    for att in atts:
        file = await att.to_file()
        bundle.append(file)
    wmessage = {'content': content,
            'files': bundle,
            'avatar_url': message.author.avatar_url,
            'username': str(message.author)}

    await webhooks[0].send(**wmessage)
    if delete:
        await message.delete()

attrs = discord.Message.__slots__
flag = pp.Word('-') + pp.Word(pp.alphas, max=1)
phrase = pp.Literal('"').suppress() + pp.Word(pp.alphanums+" _")\
        + pp.Literal('"').suppress()
pair = pp.Group(pp.oneOf(attrs) + pp.Literal(':').suppress()\
        + (pp.Word(pp.alphanums) ^ phrase))
fdict = flag + pp.ZeroOrMore(pp.Dict(pp.OneOrMore(pair)))
args = pp.OneOrMore(fdict)


class Basic(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @commands.command(name='ping')
    async def ping(self, context: commands.Context) -> None:       
        """
        Basic ping.
        """          
        await context.send(f'Ping is {self.client.latency*1000} ms')

    @commands.command(name='echo',aliases=['say'])
    async def echo(self, context: commands.Context,
            channel: Optional[discord.TextChannel]=None,
            *, content) -> None:
        """
        Say something using a webhook.
        """
        if channel is None:
            channel = context.channel
        
        await webhooksay(context.message,channel,content,True)

    @commands.command(name='sarcasm',aliases=['s'])
    async def sarcasm(self, context: commands.Context,
            *, message: str) -> None:
        """
        Say something sarcastically.
        """
        channel = context.channel 
        message = ''.join([i.upper() if random.choice([0,1])\
                else i.lower() for i in list(message)])
        await webhooksay(context.message,channel,message,True)

    @commands.command(name='quote')
    async def quote(self, context: commands.Context,
            message: discord.Message) -> None:
        """
        Quote message by ID or URL. If quoting from another channel 
        you need both channel ID and message ID (easier to use url tbh).

        Examples:
        .quote 701500480941064252           #message ID only, same channel
        .quote 696759845638111246-701500480941064252    #channel ID added
        .quote https://discordapp.com/channels/696759845159698455/696759845638111246/701500480941064252
        """
        await webhooksay(message, context.channel)

    @commands.command(name='seppuku')
    async def seppuku(self, context: commands.Context,
            channels: commands.Greedy[discord.TextChannel],
            member: Optional[discord.Member],
            *, flags: str='-n') -> None:
        """
        Purge messages in channels, defaults to all.

        Flagsa:

        -f  dict{attr: value}   filter by attribute value (partial)
        -v                      verbose
        """
        opts = args.parseString(flags).asDict()

        if not member:
            member = context.author

        #print(opts,'123')

        log = ""
        def options(message: discord.Message) -> bool:
            i = 1
            for key in opts:
                if opts[key] == "any":
                    i*=bool(getattr(message,key))
                else:
                    i*=(opts[key] in str(getattr(message,key)))
            return all([message.author == member,i])
        
        if not channels:
            channels = context.guild.text_channels

        date = datetime.now()-timedelta(days=14)        
        failled = []
        for channel in channels:
            try:
                log += "\n" 
                log += str(channel)
                deleted = await channel.purge(
                        after = date,
                        limit = None,
                        check = options)
                #print(len(deleted))
            except Forbidden:
                failled.append(str(channel))
        #print(log)
        if failled and "-v" in flags:
            await context.send(f"Missing access for: {', '.join(failled)}")

def setup(client: commands.Bot) -> None:
    client.add_cog(Basic(client))
    
