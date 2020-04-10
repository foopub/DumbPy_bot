from discord.ext import commands
import discord
from cogs import checks 
import functools
class Roles(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    def give_role(
        
            _funct=None,
            role_type: str=None, 
            cleanup: str=None,      #'hard' deletes role globally 
            perms: set={'manage_roles'}, 
            roles: set={'Mod'}
            ) -> None:

        def funct_wrapper(role_function):

            async def wrapper(
                context: commands.Context,
                role_name: str,
                member: checks.Member=None,
                ) -> None:

                if not member:      #make author target if none specified
                    member = await checks.Member(context.author)
                    if await member.self_check(perms, roles): 
                        #can author do this to themselves?
                        pass
                elif await member.targer_check(context.author, perms, roles): 
                    #can author do this to others?
                    pass
                else:
                    await context.send("You're not allowed to do this >:(")
                    return None
                
                new_role = await role_function(context, role_name, member)

                if cleanup:
                    for role in member.roles:
                        if str(role).split('_')[0] == role_type:
                            await member.remove_roles(role)
                            if cleanup == 'hard' and not role.members:
                                await role.delete(reason='Role replaced')
                    await member.add_roles(new_role)

        if _funct is None:
            return funct_wrapper
        else:
            return funct_wrapper(_funct)

    @commands.command(name='colour')
    @give_role(cleanup='hard',role_type='colour')
    async def colour(
            self,
            context: commands.Context, 
            colour_hex: str, 
            member: discord.Member=None
            ) -> discord.Role:
        
        role_name = f'colour_{colour_hex}'

        try:
            new_role = await context.guild.create_role(
                    name=role_name, 
                    colour=discord.Colour(int(colour_hex, base=16))
                    )
            await context.send('Swag granted.')
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
    
