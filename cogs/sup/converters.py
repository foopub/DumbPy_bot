import discord
from discord.ext import commands
from discord.ext.commands import BadArgument
from cogs.sup import role_settings as rs

total_perms = sum(rs.perms[i][1] for i in rs.perms)

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
                condition = any([name.isnumeric(),
                    all([name[0]=='-', name[1:].isnumeric]),
                    name[2:-1].isnumeric()])
                if condition:
                    raise BadArgument #exclude discord IDs also 
                
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


