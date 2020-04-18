import discord
from discord.ext import commands

class MemberCheck(discord.Member):
     
    def has_roles(self, roles: set) -> bool:
        role_set = set()
        for role in self.roles:
            role_set.add(role.name)
        return roles <= role_set

    def has_perms(self, context: commands.Context, perms: set) -> bool:
        pass

    def self_check(self, perms: set, roles: set) -> bool:
        return True

    def targer_check(self, author: discord.Member, perms: set, roles: set) -> bool:
        return True
