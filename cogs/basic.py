from discord.ext import commands
import discord
from typing import Optional

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


def setup(client: commands.Bot) -> None:
    client.add_cog(Basic(client))
    
