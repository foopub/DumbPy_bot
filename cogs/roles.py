from discord.ext import commands
import discord
from cogs import checks as ch 
import functools
from typing import Callable, List, Union
from cogs.sup import settings as st

def role_wrap(
    
        _funct=None,
        role_type: str=None, 
        cleanup: str=None,      #'hard' deletes role globally
        perms: set={'manage_roles'}, 
        roles: set={'Mod'},
        message: str='All good!'
        ) -> Callable:
    """
    Wrapper for quick role command creation.
    Main functionality is to check perms, assign the role, and clean up.
    Useful for mutually exclusive roles - colours, levels, types, etc. 
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
                members = [context.author]
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
            members: commands.Greedy[discord.Member]=None
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
            await context.send(f"{colour_hex} isn't a valid hex, silly!")

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
        Delete all redundant roles which aren't saved.
        Roles can be saved using the save_role command.
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
        """
        Save roles to prevent deletion with "clean_roles".
        Roles need to be mentioned, not just named!
        Usage:
        .save_role @my_role @other_role     #saves mentioned roles
        .save_role all                      #saves all roles 
        (doesn't work yet lol)
        """
        role_names = [i.name for i in roles]
        if all_roles == 'all':
            role_names = [i.name for i in context.guild.roles]
        await context.send(f'Saving roles: {role_names[1:]}')

    @commands.command(name='make_help')
    async def make_help(
            self,
            context: commands.Context, 
            role_name: str,
            permissions: commands.Greedy[int]=None,
            colour: str='000',
            position: Union[int, str]=0,
            hoist: bool=False,
            mention: bool=False,
            override_permissions: commands.Greedy[int]=None,
            override_text_ch: commands.Greedy[discord.TextChannel]=None,
            *vc_categories: str
            ) -> None:
        """
        Global arguments 

        Role Name: use "" quotes if it contains spaces
        Colour: hex code or name (if common)
        Position: number or name of role to be placed under
        Hoist: yes or no (show members separately)
        Mentionable: y/n

        Permissions

        Some permissions are global (i.e. ban) while others are channel
        specific. Default value for all global permissions is False.
        Channel specific permissions overwrite global permissions, and
        their default value is None, meaning unchanged.

        Now to get a list of all permissions use:
        .make_role list_permissions
        or to see some examples of common usage:
        .make_role show_examples
        """
        if role_name == 'list_permissions':
            await context.send(
        """```
        T and V indicate channel specific options, * means 2FA may be
        required. Add permissions by listing leftmost numbers, or giving
        the total hexadecimal sum.

         1 create_instant_invite 00000001 T, V
         2 kick_members          00000002 *,
         3 ban_members           00000004 *,
         4 administrator         00000008 *,
         5 manage_channels       00000010 *, T, V
         6 manage_guild          00000020 *,
         7 add_reactions         00000040 T
         8 view_audit_log        00000080
         9 view_channel          00000400 T, V
        10 send_messages         00000800 T
        11 send_tts_messages     00001000 T
        12 manage_messages       00002000 *, T
        13 embed_links           00004000 T
        14 attach_files          00008000 T
        15 read_message_history  00010000 T
        16 mention_everyone      00020000 T
        17 use_external_emojis   00040000 T
        18 view_guild_insights   00080000
        19 connect               00100000 V
        20 speak                 00200000 V
        21 mute_members          00400000 V
        22 deafen_members        00800000 V
        23 move_members          01000000 V
        24 use_vad               02000000 V
        25 priority_speaker      00000100 V
        26 stream                00000200 V
        27 change_nickname       04000000
        28 manage_nicknames      08000000
        29 manage_roles          10000000 *, T, V
        30 manage_webhooks       20000000 *, T, V
        31 manage_emojis         40000000 *,
        ```""") 
            await context.send(
        """```
        You can give one set of permission overrides for all channels
        and categories following. You can also give multiple sets of 
        permissions where the first N sets will apply to the first N
        channels and cattegories, after which the last permission set 
        will be applied to all the remaining.

        Different permission sets should each be separated by a 0 if
        naming the permissions by number. If using hexadecimal, a space
        will suffice.
        ```"""
        )
        elif role_name == 'show_examples':
            await context.send('examples here')
        pass
    
    @commands.command(name='make_role')
    async def make_role(
            self,
            context: commands.Context, 
            role_name: str,
            permissions: commands.Greedy[int]=None,
            colour: str='000',
            position: Union[int, str]=0,
            hoist: bool=False,
            mention: bool=False,
            override_permissions: commands.Greedy[int]=None,
            override_text_ch: commands.Greedy[discord.TextChannel]=None,
            *vc_categories: str
            ) -> None:

        """
        This is an advanced function, use make_help for info.
        """


def setup(client: commands.Bot) -> None:
    client.add_cog(Roles(client))
    
