import discord
from discord.ext import commands
from discord.commands import slash_command, Option

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1274788639901221045, 1271477574538629150

    @slash_command(description="⛔️︱Kicke einen Member")
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def kick(self, ctx, member: Option(discord.Member, "Wähle einen Member"), reason: Option(str, "Gib einen Grund an")):
        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            await ctx.respond("Ich habe keine Berechtigung, um diesen Member zu kicken")
            return
        await ctx.respond(f"{member.mention} wurde gekickt!\nGrund: {reason}")

        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="Member gekickt",
                description=f"{member.mention} wurde gekickt.",
                color=discord.Color.red()
            )
            embed.add_field(name="Grund", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await log_channel.send(embed=embed)

    @slash_command(description="⛔️︱Banne einen Member")
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def ban(self, ctx, member: Option(discord.Member, "Wähle einen Member"), reason: Option(str, "Gib einen Grund an")):
        try:
            await member.ban(reason=reason)
        except discord.Forbidden:
            await ctx.respond("Ich habe keine Berechtigung, um diesen Member zu bannen")
            return
        await ctx.respond(f"{member.mention} wurde gebannt!\nGrund: {reason}")

        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="Member gebannt",
                description=f"{member.mention} wurde gebannt.",
                color=discord.Color.red()
            )
            embed.add_field(name="Grund", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        await ctx.respond(f"Es ist ein Fehler aufgetreten: ```{error}```")
        raise error

def setup(bot):
    bot.add_cog(Admin(bot))
