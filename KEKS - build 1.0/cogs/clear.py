import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from discord import InteractionContextType, IntegrationType


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="🔙︱Lösche eine bestimmte Anzahl an Nachrichten")
    @discord.guild_only()
    @discord.default_permissions(manage_messages=True)
    async def clear(self, ctx, amount: Option(int, "Anzahl der zu löschenden Nachrichten", required=True, min_value=1,
                                              max_value=100)):
        await ctx.defer(ephemeral=True)

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.respond(f"**{len(deleted)}** Nachrichten wurden gelöscht.", ephemeral=True, delete_after=10)


def setup(bot):
    bot.add_cog(Moderation(bot))