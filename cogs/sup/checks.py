import discord
from discord.ext import commands

discord.Member.guild_permissions

class Member(discord.Member):
    def __init__(self):
        pass
     
    def has_roles(author: discord.Member, roles: set) -> bool:
        role_set = set()
        for role in author.roles:
            role_set.add(role.name)
        return roles <= role_set

    def has_perms(author: discord.Member, perms) -> bool:
        pass

    def self_check(self, perms, roles):
        return True

    def targer_check(self, target: discord.Member, perms, roles):
        return True
