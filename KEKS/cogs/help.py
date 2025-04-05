import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ui import View, Select

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="❓︱Hilfe + Liste meiner Befehle")
    async def help(self, ctx):
        class HelpMenu(discord.ui.Select):
            def __init__(self, bot):
                self.bot = bot
                options = [
                    discord.SelectOption(label="Rang & Leaderboard", description="Befehle für Rang und Leaderboard anzeigen", emoji="📊"),
                    discord.SelectOption(label="Kekse & Wetten", description="Befehle für Kekse und Wetten anzeigen", emoji="🍪"),
                    discord.SelectOption(label="Sonstige Befehle", description="Andere verfügbare Befehle anzeigen", emoji="⚙️")
                ]
                super().__init__(placeholder="Wähle eine Kategorie...", options=options)

            async def callback(self, interaction: discord.Interaction):
                if self.values[0] == "Rang & Leaderboard":
                    embed = discord.Embed(
                        title="Rang & Leaderboard Befehle",
                        description="**Hier sind die Befehle für deinen Rang und das Leaderboard:**",
                        color=0xEDAB54
                    )
                    embed.add_field(name="</rank:1272667832781508740>", value="Erfahre deinen aktuellen XP-Rang.", inline=False)
                    embed.add_field(name="</leaderboard:1273032947494162484>", value="Zeigt dir die Top 10 aktivsten Nutzer an.", inline=False)

                elif self.values[0] == "Kekse & Wetten":
                    embed = discord.Embed(
                        title="Kekse & Wetten Befehle",
                        description="**Hier sind die Befehle für Kekse und Wetten:**",
                        color=0xEDAB54
                    )
                    embed.add_field(name="</balance:1273372601149816872>", value="Zeigt dir deine Kekse an.", inline=False)
                    embed.add_field(name="</bet:1273372601149816873>", value="Wette Kekse.", inline=False)
                    embed.add_field(name="</daily:1276214626790543556>", value="Hol dir deine tägliche Belohnung.", inline=False)

                elif self.values[0] == "Sonstige Befehle":
                    embed = discord.Embed(
                        title="Sonstige Befehle",
                        description="**Hier sind einige weitere verfügbare Befehle:**",
                        color=0xEDAB54
                    )
                    embed.add_field(name="</buy:1278470931093913651>", value="Kaufe eine der 5 Rollen, um Vorteile zu erhalten.", inline=False)
                    embed.add_field(name="</create_temp_channel:1273382529772028005>", value="Falls kein Kanal erstellt wird.", inline=False)
                    embed.add_field(name="</bug:1278496007335841794>", value="Falls du einen Bug findest.", inline=False)

                embed.set_footer(text="Wende dich bei Fragen an einen Moderator")

                bot_avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else None
                if bot_avatar_url:
                    embed.set_thumbnail(url=bot_avatar_url)

                await interaction.response.send_message(embed=embed, ephemeral=True)

        view = View()
        view.add_item(HelpMenu(self.bot))

        embed = discord.Embed(
            title="Hilfe",
            description="**Wähle eine Kategorie aus dem Menü aus, um die verfügbaren Befehle anzuzeigen.**",
            color=0xEDAB54
        )
        embed.set_footer(text="Wende dich bei Fragen an einen Moderator")

        bot_avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else None
        if bot_avatar_url:
            embed.set_thumbnail(url=bot_avatar_url)

        await ctx.respond(embed=embed, view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        await ctx.respond(f"Es ist ein Fehler aufgetreten: ```{error}```")
        raise error

def setup(bot):
    bot.add_cog(Help(bot))
