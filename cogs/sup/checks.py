import discord
from discord.ext import commands

discord.Member.guild_permissions

def has_roles(author: discord.Member, roles: set) -> bool:
    role_set = set()
    for role in author.roles:
        role_set.add(role.name)
    return roles <= role_set

def has_perms(author: discord.Member, perms) -> bool:
    pass

def author(author: discord.Member, perms, roles) -> bool:
    return True

def target(author: discord.Member, 
        target: discord.Member, perms, roles) -> bool:
    return True
