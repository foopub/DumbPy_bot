from discord.ext import commands
import discord
from typing import Optional, List
import itertools as itt
from datetime import datetime, timedelta

async def webhooksay(message: discord.Message, 
        channel: discord.TextChannel,
        content: Optional[str]=None) -> None:
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
    message = {'content': content,
            'files': bundle,
            'avatar_url': message.author.avatar_url,
            'username': str(message.author)}

    await webhooks[0].send(**message)


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
        
        await webhooksay(context.message,channel,content)

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
            *args: List[str]) -> None:
        """
        Purge messages in channels, defaults to all.

        Flags to implement:
        -t  text
        -a  attachments
        -l  links
        -c  channels [channels] defaults to current
        -w  contains [word]
        """

        if not member:
            member = context.author
        def is_author(message: discord.Message):
            return message.author == member
        
        if not channels:
            channels = context.guild.text_channels

        date = datetime.now()-timedelta(days=14)        
        failled = []
        for channel in channels:
            print(channel)
            try:
                deleted = await channel.purge(
                        after = date,
                        limit = 10000,
                        check = is_author)
                print(len(deleted))
            except:
                failled.append(str(channel))
        if failled:
            await context.send(f"Failled channels: {', '.join(failled)}")
    """
    @commands.command(name='harakiri')
    async def harakiri(self, context: commands.Context):
    """
        #Delete messages using the delete_messages method.
    """
        messages_list = await context.channel.history().flatten()
        print(len(messages_list))
        messages_iter = iter(messages_list)
        count = 0
        while messages := list(itt.islice(messages_iter,100)):
            count += 1
            if count == 5:
                break
    """


        
        


def setup(client: commands.Bot) -> None:
    client.add_cog(Basic(client))
    
