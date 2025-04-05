import discord
from discord.ext import commands


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        role_id = 1271468996260270294
        role = member.guild.get_role(role_id)

        if role:
            await member.add_roles(role)
            print(f"Rolle '{role.name}' wurde {member.name} zugewiesen.")
        else:
            print(f"Rolle mit ID {role_id} nicht gefunden.")

def setup(bot):
    bot.add_cog(AutoRole(bot))