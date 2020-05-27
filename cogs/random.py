from discord.ext import commands
import discord

class Random(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.group()
    async def get(self, context: commands.Context) -> None:
        pass

    @get.command()
    async def help(self, context: commands.Context,
            members: commands.Greedy[discord.Member]) -> None:
        """
        Get people the help they need.
        """
        if not members:
            await context.send("Who are you talking to?")
        else:
            members_str = [str(i) for i in members]
            await context.send(f"{', '.join(members_str)} have received "
                    "help. Thank you for your kindness.")

    @get.command()
    async def attributes(self, context: commands.Context, obj: str) -> None:
        obj = obj.capitalize()
        attrs = ', '.join(getattr(discord, obj).__slots__)
        await context.send(f"```Attributes of {obj}:\n{attrs}```")
        

def setup(client: commands.Bot) -> None:
    client.add_cog(Random(client))
    
