from discord.ext import commands
import discord



class Reactions(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        Model emoji report function using predefined emojis.
        Message is deleted and sent to a review channel if it contains
        images (embeds or attachments).
        """
        review_channel = 697153058559492178
        report_emoji = '💩'
        report_treshold = 2
        attachments = reaction.message.attachments
        conditions = all([
                (reaction.count >= report_treshold),
                (reaction.emoji == report_emoji),
                any([reaction.message.embeds, 
                    attachments,
                    ])
                ])
        if conditions:          #conditions can be edited.
            channel = self.client.get_channel(review_channel)
            bundle = []         #create empty list for attachments
            if attachments:
                for attachment in attachments:
                    file = await attachment.to_file()
                    bundle.append(file)
            await channel.send(\
                f'Message by {reaction.message.author}:\n',
                {reaction.message.content}, files=bundle)
            await reaction.message.delete()



def setup(client: commands.Bot) -> None:
    client.add_cog(Reactions(client))

