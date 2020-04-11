from discord.ext import commands
import discord
from cogs import checks as ch 
import functools
from typing import Callable, List
from cogs.sup import settings as st

def role_wrap(
    
        _funct=None,
        role_type: str=None, 
        cleanup: str=None,      #'hard' deletes role globally
        perms: set={'manage_roles'}, 
        roles: set={'Mod'},
        message: str='Granted!'
        ) -> Callable:
    """
    Wrapper for quick role command creation.
    Main functionality is to check perms, assign the role, and clean up.
    Useful for colours, levels, types, etc. 
    """
    def funct_wrapper(role_function: Callable) -> Callable:
        @functools.wraps(role_function)
        async def my_wrapper(
            self,
            context: commands.Context,
            role_name: str,
            members: commands.Greedy[discord.Member]=None,
            ) -> None:

            if not members:      #make author target if none specified
                members = context.author
                if not ch.author(members, perms, roles):
                    await context.send(
                            "You're not allowed to do this to yourself")
                    return None

            for member in members:
                if not ch.target(context.author, member, perms, roles):
                    await context.send(
                        "You're not allowed to do this to {member} >:(")
                    continue
                
                new_role, cleanup_rule = await role_function(
                        self, context, role_name, member)

                if cleanup:
                    for role in member.roles:
                        if cleanup_rule(role):
                            await member.remove_roles(role)
                            if cleanup == 'hard' and not role.members:
                                await role.delete(reason='Role replaced')
                await member.add_roles(new_role)
            await context.send(message)
        return my_wrapper 
    if _funct is None:
        return funct_wrapper
    else:
        return funct_wrapper(_funct)

class Roles(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command(name='colour')
    @role_wrap(cleanup='hard',role_type='colour',message='Swag granted!')
    async def colour(
            self,
            context: commands.Context, 
            colour_hex: str, 
            member: commands.Greedy[discord.Member]=None
            ) -> (discord.Role, Callable):
        """
        Creates and gives colour role from hex, then cleans up. 
        Usage:
        .colour 1234                #applies role to author
        .colour 1234  @someone      #give role to someone else
        .colour 1233  @alice @bob   #works for both alice and bob 
        """
        role_name = f'colour_{colour_hex}'

        try:
            colour_role = await context.guild.create_role(
                    name=role_name, 
                    colour=discord.Colour(int(colour_hex, base=16))
                    )
        except ValueError:
            await context.send(f"{colour_hex} isn't a valid hex you retard!")

        return colour_role, lambda x: str(x.name).split('_')[0]=='colour'

    @commands.command(name='mod')
    @role_wrap(cleanup=None, role_type='mod', 
            message='With great power comes great responsibility.')
    async def mod(
            self,
            context: commands.Context, 
            rank: str, 
            member: commands.Greedy[discord.Member]=None
            ) -> discord.Role:
        """
        This command does nothing lol.
        """
        pass

    @commands.command(name='clean_roles')
    async def clean_roles(self, context: commands.Context) -> None:
        """
        Delete all redundant roles that aren't saved.
        """
        for role in context.guild.roles:
            if not any([role.members, role.name in st.saved_roles]):
                await role.delete(reason='Redundant role deleted')
    
    @commands.command(name='save_role', aliases=['save_roles'])
    async def save_role(
            self,
            context: commands.Context, 
            roles: commands.Greedy[discord.Role],
            all_roles: str=None
            ) -> None:
        role_names = [i.name for i in roles]
        if all_roles == 'all':
            role_names = [i.name for i in context.guild.roles]
        await context.send(f'Saving roles: {role_names[1:]}')

def setup(client: commands.Bot) -> None:
    client.add_cog(Roles(client))
    
