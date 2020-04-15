from discord.ext import commands
from discord.ext.commands import BadArgument
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

async def hexoctbin(name: str):
    d = {'x': 16,'o': 8,'b': 2}
    return int(name, base=d[name[1]])

class Hex_Oct_Bin(commands.Converter):
    """
    Useful converter for alternative number formats.
    """
    async def convert(self, context: commands.Context, name: str):
        try:
            return await hexoctbin(name)
        except KeyError or TypeError:
            raise BadArgument

class Valid_Str(commands.Converter):
    """
    Potentially useful, avoid interpreting hex/oct/bin int as str. 
    """
    async def convert(self, context: commands.Context, name: str):
        try:
            try:
                await hexoctbin(name)
                raise BadArgument
            except KeyError or TypeError:
                int(name)
                raise BadArgument
        except ValueError:
            return name

class Permission(commands.Converter):
    """
    Check if valid permission hex/oct/bin/int value.
    """
    async def convert(self, context: commands.Context, name: str) -> dict:
        try:
            try:
                value = await hexoctbin(name)
                if value < total_perms:
                    return dict(iter(discord.Permissions(value)))
                else:
                    raise ValueError
            except:
                key = abs(int(name))
                return {f'{rs.perms[key][2]}': int(name)>0}
        except:
            raise BadArgument

class Position(commands.Converter):
    async def convert(self, context: commands.Context, name:str):
        try:
            number = int(name)
            if number < len(context.guild.roles):
                return number
            else:
                print('Position {name} out of range')
                raise ValueError 
        except ValueError:
            role = await discord.utils.get(context.guild.roles, name=name)
            if role:
                return role.positive-1
            else:
                print(f'Role {name} not found')
                raise BadArgument

async def chop_list(mylist: list, at: int):
    bundle = []
    for _ in range(mylist.count(at)):
        bundle.append(mylist[:mylist.index(at)])
        del mylist[:mylist.index(at)]
    return bundle
    
async def sum_perms(extra: List[dict],starting: dict={}) -> dict:
    print('Starting initial: ', starting,type(starting))
    for i in extra:
        print('\ni inside loop: ',i,type(i),'\n')
        starting.update(**dict(i))
    print('Starting type: ',starting,type(starting))
    return starting


def perm_get(value: int):
    """
    Get permissions. Similar to list(iter(discord.Permissions(value))).
    """
    perm_list = []
    for i in reversed(rs.perms.values()):
        if i[1]<value:
            perm_list.append(i[0])
            value -= i[1]
    return perm_list[:-1]

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
        "```"
        "You can give one set of perm overwrites for all channels "
        "and categories."
        "\n"
        "You can also give multiple sets of perms, each separated "
        "by a zero 0 where the first N sets will apply to the first "
        "N channels and cattegories (in the order listed). "
        "The last perm set will be applied to all remaining channels/"
        "categories, if any."
        "\n"
        "Note that perm overwrites are applied on top of the global "
        "permissions, instead of resetting them to none."
        "```"
        )
        elif args == 'examples':
            await context.send('examples here')
        elif args == 'oct':
            table = '```\n'
            for i in rs.perms.values():
                table += f'{i[1]:#0{13}o} - {i[0]}\n'
            await context.send(f'{table}' "\n```")
        pass
    
    @commands.command(name='role')
    async def role(
            self,
            context: commands.Context, 
            role: Optional[discord.Role]=None,
            name: Optional[Valid_Str]=None,
            permissions: commands.Greedy[Permission]=[],
            hoist: Optional[bool]=None,
            mentionable: Optional[bool]=None,
            colour: Optional[discord.Colour]=None,
            position: Optional[Position]=None,
            overwrite_ch: commands.Greedy[discord.TextChannel]=[],
            overwrite_vc: commands.Greedy[discord.VoiceChannel]=[],
            overwrite_cat: commands.Greedy[discord.CategoryChannel]=[],
            overwrite_perms: commands.Greedy[Permission]=[],
            *other: str
            ) -> None:
        """
        This is an advanced function, use make_help for info.
        Arguments are positional so if
        """
        raw = {'name': name,'hoist': hoist,
                'mentionable': mentionable,'colour': colour,
                'position': position}

        parameters = dict(itt.compress(
                raw.items(),[i!=None for i in raw.values()]))

        print(self,
		'context: ', context, '\n'
		'role: ', role, '\n'
		'name: ', name, '\n'
		'permissions: ', permissions, '\n'
                'hoist: ', hoist, '\n'
		'mentionable: ', mentionable, '\n'
		'colour: ', colour, '\n'
		'position: ', position, '\n'
                'overwrite_ch: ', overwrite_ch, '\n'
                'overwrite_vc: ', overwrite_vc, '\n'
                'overwrite_cat: ', overwrite_cat, '\n'
		'overwrite_perms: ', overwrite_perms, '\n'
		'other: ', other, '\n'
                )

        if role:
            await context.send(f'Updating role {role}.')
            permissions = await sum_perms(permissions,
                    dict(iter(role.permissions)))
            await role.edit(**parameters,
                    permissions=discord.Permissions(**permissions))
        elif name:
            permissions = await sum_perms(permissions)
            role = await context.guild.create_role(**parameters,
                permissions=discord.Permissions(**permissions))
            await context.send(f'Created role {name}.')
        else:
            await context.send('You need to provide a name!')
            return None



        perm_list = itt.compress(permissions.keys(),permissions.values())

        message = [
                'Context:           ', str(context), '\n'
		'Name:              ', str(name), '\n'
                'Created at:        ', str(role.created_at), '\n'
                'Permissions list:  ', '\n',
                ', '.join(perm_list), '\n',
                'Shown separately:  ', str(hoist), '\n'
		'Mentionable:       ', str(mentionable), '\n'
		'Colour value:      ', str(colour), '\n'
		'Position:          ', str(position), '\n'
    		'Other:             ', str(other), '\n'
                ]

        if overwrite_perms:
            all_ch = itt.chain(overwrite_ch,overwrite_vc,overwrite_cat)
            perm_groups = chop_list(overwrite_perms, 0)

            pairs = itt.zip_longest(all_ch, perm_groups,
                    fillvalue=perm_groups[-1])


            for i in pairs:
                message.append(f'Overwrite perms for {i[0]}:\n', i[1], '\n')
                perms = sum_perms(i[1],perms)
                overwrites = discord.PermissionOverwrite(
                        dict(iter(discord.Permissions(perms))))
                await i[0].edit(overwrites={role: overwrites}) 

        messagestr = "```\n" + ''.join(message) + "\n```"
        await context.send(messagestr)

    """
    @commands.command(name='role')
    async def role(self, context: commands.Context, *args):
        pass
    """
def setup(client: commands.Bot) -> None:
    client.add_cog(Roles(client))
    
