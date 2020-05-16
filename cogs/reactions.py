from discord.ext import commands
import discord
import cogs.sup.settings as st



class Reactions(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user):
        """
        Model emoji report function using predefined emojis.
        Message is deleted and sent to a review channel if it contains
        images (embeds or attachments).
        """
        if reaction.emoji not in st.reactions:
            return None
        
        guild_id = reaction.message.guild.id
        attachments = reaction.message.attachments
        
        emoji = st.reactions[reaction.emoji]
        if reaction.count >= emoji[2][guild_id][1] and eval(emoji[0]):
            channel = emoji[2][guild_id][0]
        else:
            return None

        channel = self.client.get_channel(channel)
        bundle = []         #create empty list for attachments
        if attachments:
            for attachment in attachments:
                file = await attachment.to_file()
                bundle.append(file)
        await channel.send(\
            f'Message by {reaction.message.author}:\n'
            f'{reaction.message.content}', files=bundle)

        if emoji[1]:
            await reaction.message.delete()

def setup(client: commands.Bot) -> None:
    client.add_cog(Reactions(client))

