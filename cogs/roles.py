from discord.ext import commands
import discord
from cogs import checks 
import functools

def give_role(
    
        _funct=None,
        role_type: str=None, 
        cleanup: str=None,      #'hard' deletes role globally 
        perms: set={'manage_roles'}, 
        roles: set={'Mod'}
        ) -> None:

    def funct_wrapper(role_function):
        @functools.wraps(role_function)
        async def my_wrapper(
            self,
            context: commands.Context,
            role_name: str,
            member: discord.Member=None,
            ) -> None:
            if not member:      #make author target if none specified
                member = context.author
                if checks.self_check(member, perms, roles): 
                    #can author do this to themselves?
                    pass
            elif checks.target_check(member, context.author, perms, roles): 
                #can author do this to others?
                pass
            else:
                await context.send("You're not allowed to do this >:(")
                return None
            
            print('\nIside wrapper', self, context, role_name, member)
            new_role = await role_function(self, context, role_name, member)

            if cleanup:
                for role in member.roles:
                    if str(role).split('_')[0] == role_type:
                        await member.remove_roles(role)
                        if cleanup == 'hard' and not role.members:
                            await role.delete(reason='Role replaced')
                await member.add_roles(new_role)
        return my_wrapper 
    if _funct is None:
        return funct_wrapper
    else:
        return funct_wrapper(_funct)

class Roles(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command(name='colour')
    @give_role(cleanup='hard',role_type='colour')
    async def colour(
            self,
            context: commands.Context, 
            colour_hex: str, 
            member: discord.Member=None
            ) -> discord.Role:
        
        print('\nInside colour', self, context, colour_hex, member)
        role_name = f'colour_{colour_hex}'

        try:
            new_role = await context.guild.create_role(
                    name=role_name, 
                    colour=discord.Colour(int(colour_hex, base=16))
                    )
        except ValueError:
            await context.send(f"{colour_hex} isn't a valid hex you retard!")
        return new_role       

    @commands.command(name='clean_roles')
    async def clean_roles(self, context: commands.Context) -> None:
        for role in context.guild.roles:
            if not role.members:
                await role.delete(reason='Redundant role deleted')

def setup(client: commands.Bot) -> None:
    client.add_cog(Roles(client))
    
