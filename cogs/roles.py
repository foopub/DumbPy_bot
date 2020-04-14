from discord.ext import commands
from commands import BadArgument
import itertools as itt
import discord
from cogs import checks as ch 
import functools
from typing import Callable, List, Union, Optional
from cogs.sup import settings as st
from cogs.sup import role_settings as rs
from math import copysign

total_perms = sum(rs.perms[i][1] for i in rs.perms)

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

class Hex_Oct_Bin(commands.Converter):
    """
    Useful converter for alternative number formats.
    """
    async def convert(self, context, name: str):
        d = {'x': 16,'o': 8,'b': 2}
        try:
            return int(name, base=d[name[1]])
        except:
            raise BadArgument

class Valid_Str(commands.Converter):
    """
    Potentially useful, avoid interpreting hex/oct/bin int as str. 
    """
    async def convert(self, context, name: str):
        try:
            Hex_Oct_Bin.convert(None,None,name)
            raise BadArgument
        except KeyError or TypeError:
            return name

class Permission(commands.Converter):
    """
    Check if valid permission hex/oct/bin/int value.
    """
    async def convert(self, context, name: str):
        try:
            value = Hex_Oct_Bin.convert(None,None,name)
            if value < total_perms:
                return value
            raise
        except:
            return copysign(rs.perms[name][1],int(name))
        except:
            raise BadArgument

def sum_perms(extra: List[int],start=0): 
    for i in extra:
        value = copysign(rs.perms[abs(i)][1],i)
        if -value < start: #always allow positive, but check negatives
            start+=value
    return int(start)

class Roles(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command(name='colour')
    @role_wrap(cleanup='hard',role_type='colour',message='Swag granted!')
    async def colour(
            self,
            context: commands.Context, 
            colour: discord.Colour, 
            members: commands.Greedy[discord.Member]=None
            ) -> (discord.Role, Callable):
        """
        Creates and gives colour role from hex, then cleans up. 
        Usage:
        .colour 1234                #applies role to author
        .colour 1234  @someone      #give role to someone else
        .colour 1233  @alice @bob   #works for both alice and bob 
        .colour blue                #discord default colours 
        """
        role_name = f'colour_{colour}'

        try:
            colour_role = await context.guild.create_role(
                    name=role_name, 
                    colour=colour
                    )
        except ValueError:
            await context.send(f"{colour} isn't a valid hex, silly!")

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
        roles_deleted = ' '
        for role in context.guild.roles:
            if not any([role.members, role.name in st.saved_roles]):
                print(f'{role.name}')
                roles_deleted += f"{role.name}, "
                await role.delete(reason='Redundant role deleted')
        await context.send(f'Deleted roles:{roles_deleted[:-2]}.')
    
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

    @commands.command(name='role_help')
    async def role_help(
            self,
            context: commands.Context, 
            args: Optional[str],
            *other
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
        .role_help list
        or to see some examples of common usage:
        .role_help examples
        """
        if 'list' in args:
            await context.send(
        "```"
        "T and V indicate channel specific options, * means 2FA may be "
        "required. You can add or remove permissions by listing leftmost "
        "numbers (with a minus sign to revoke if possible). Alternatively, "
        "give the total hexadecimal or octadecimal sum. To get the octa"
        "decimal table use:\n.role_help oct\n"
        """
         1 create_instant_invite 0x00000001 T, V
         2 kick_members          0x00000002 *,
         3 ban_members           0x00000004 *,
         4 administrator         0x00000008 *,
         5 manage_channels       0x00000010 *, T, V
         6 manage_guild          0x00000020 *,
         7 add_reactions         0x00000040 T
         8 view_audit_log        0x00000080
         9 priority_speaker      0x00000100 V
        10 stream                0x00000200 V
        11 view_channel          0x00000400 T, V
        12 send_messages         0x00000800 T
        13 send_tts_messages     0x00001000 T
        14 manage_messages       0x00002000 *, T
        15 embed_links           0x00004000 T
        16 attach_files          0x00008000 T
        17 read_message_history  0x00010000 T
        18 mention_everyone      0x00020000 T
        19 use_external_emojis   0x00040000 T
        20 view_guild_insights   0x00080000
        21 connect               0x00100000 V
        22 speak                 0x00200000 V
        23 mute_members          0x00400000 V
        24 deafen_members        0x00800000 V
        25 move_members          0x01000000 V
        26 use_vad               0x02000000 V
        27 change_nickname       0x04000000
        28 manage_nicknames      0x08000000
        29 manage_roles          0x10000000 *, T, V
        30 manage_webhooks       0x20000000 *, T, V
        31 manage_emojis         0x40000000 *,
        ```""") 
            await context.send(
        """```
        You can give one set of permission overwrites for all channels
        and categories following. You can also give multiple sets of 
        permissions where the first N sets will apply to the first N
        channels and cattegories, after which the last permission set 
        will be applied to all the remaining.
        
        Different overwrite permission sets should each be separated by
        a 0 if naming the permissions by number. 
        If using hexadecimal, you're good.
        ```"""
        )
        elif args == 'examples':
            await context.send('examples here')
        elif args == 'oct':
            table = '```\n'
            for i in rs.perms.values():
                table += f'{i[1]:#0{13}o} - {i[0]}\n'
            await context.send(f'{table}' "\n```")
        pass
    
    @commands.command(name='role_tool')
    async def role_tool(
            self,
            context: commands.Context, 
            role: Optional[discord.Role]=None,
            role_name: Optional[Valid_Str]='new_role',
            permissions: commands.Greedy[Permission]=[],
            separate: bool=False,
            mention: bool=False,
            role_colour: Optional[discord.Colour]=0,
            position: Union[discord.Role, int]=0,
            overwrite_ch: commands.Greedy[discord.TextChannel]=None,
            overwrite_vc: commands.Greedy[discord.VoiceChannel]=None,
            overwrite_cat: commands.Greedy[discord.CategoryChannel]=None,
            overwrite_permissions: commands.Greedy[int]=None,
            *other: str
            ) -> None:
        """
        This is an advanced function, use make_help for info.
        """
        print(self,
		'context: ', context, '\n'
		'role: ', role, '\n'
		'role_name: ', role_name, '\n'
		'permission_hex_oct: ', permission_hex_oct, '\n'
		'permissions: ', permissions, '\n'
                'separate: ', separate, '\n'
		'role_colour: ', role_colour, '\n'
		'position: ', position, '\n'
		'mention: ', mention, '\n'
		'overwrite_permissions: ', overwrite_permissions, '\n'
                'overwrite_ch: ', overwrite_ch, '\n'
                'overwrite_vc: ', overwrite_vc, '\n'
                'overwrite_cat: ', overwrite_cat, '\n'
		'other: ', other, '\n'
                )
        message = ''
        if role and role_name:
            message += f'Renaming {role} to {role_name}. '
        elif role_name and not role:
            try:
                int(role_name,16)
                message += (f'Interpreting {role_name} as role'
                        'name. Weird thing to name a role bro.')
            except:
                pass 
            role = await context.guild.create_role(name=role_name)
            await context.send(f'Creating role {role_name}')
        elif not role:
            await context.send('You need at least a role or a name')
            return None

        perms = sum_perms(permissions,permission_hex_oct)
       
        try:
            role_colour = discord.Colour(role_colour)
        except:
            await context.send(
                    f'Colour {role_colour} not found')

        await role.edit(name=role_name,#hoist=separate,
                mentionable=mention, colour=role_colour,
                permissions=discord.Permissions(perms)
                )

        perm_groups = []
        for i in ','.join(overwrite_permissions).split('0'):
            perm_groups.append(i.split(','))

        pairs = itt.zip_longest(overwrite_ch, perm_groups,
                fillvalue=perm_groups[-1])

        for i in pairs:
            perms = sum_perms(i[1],perms)
            i[0].edit(overwrites={role: discord.PermissionOverwrite(perms)})

    @commands.command(name='role')
    async def role(self, context: discord.Context, *args):
        pass

def setup(client: commands.Bot) -> None:
    client.add_cog(Roles(client))
    
