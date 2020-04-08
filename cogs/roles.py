from discord.ext import commands
import discord

class Roles(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command(name='colour')
    async def colour(self, context: commands.Context, arg1: str, member: discord.Member = None) -> None:
        """
        Model function for role management.
        Handles mutually exclusive roles such as colour.           
        """
        role_type = 'colour'
        role_name = f'{role_type}_{arg1}'
        if not member:          #apply role to self if no member given
            member = context.author
        try:
            new_role = await context.guild.create_role(
                    name=role_name, 
                    colour=discord.Colour(int(arg1, base=16))
                    )
            await context.send('Granted.')
        except ValueError:
            await context.send(f'{arg1} is not a valid hex you retard!')
            return None
        
        for i in member.roles:
            if str(i).split('_')[0] == role_type:
                await member.remove_roles(i)
        await member.add_roles(new_role)



def setup(client: commands.Bot) -> None:
    client.add_cog(Roles(client))
    
