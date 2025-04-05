from discord.ext import commands
from discord.commands import slash_command
import discord

class TempChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}
        self.settings_channel_id = 1327644750261653555  # Statische ID für den Settings-Kanal

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.name == "〣︱➕︱Kanal erstellen":
            category = after.channel.category

            temp_channel = await category.create_voice_channel(f"{member.name}")
            await member.move_to(temp_channel)
            self.temp_channels[member.id] = {'voice_channel': temp_channel.id}

        if before.channel and before.channel.id in [data['voice_channel'] for data in self.temp_channels.values()]:
            temp_channel = before.channel
            owner_id = next((uid for uid, data in self.temp_channels.items() if data['voice_channel'] == temp_channel.id), None)

            if owner_id and member.id == owner_id and len(temp_channel.members) == 0:
                await temp_channel.delete()

                settings_channel_id = self.temp_channels[owner_id]['settings_channel']
                settings_channel = self.bot.get_channel(settings_channel_id)
                if settings_channel:
                    await settings_channel.delete()

                del self.temp_channels[owner_id]

    @slash_command(description="🎵︱Erstellt einen Sprachkanal, der gelöscht wird, wenn er leer ist.")
    @discord.guild_only()
    async def create_temp_channel(self, ctx):
        category = ctx.channel.category
        temp_channel = await category.create_voice_channel(f"{ctx.author.name}")
        await ctx.author.move_to(temp_channel)
        self.temp_channels[ctx.author.id] = {'voice_channel': temp_channel.id}

        await ctx.respond(f"Ein temporärer Sprachkanal wurde erstellt: {temp_channel.name}", ephemeral=True, delete_after=10)

    @slash_command(description="Erstellt das Embed für die Kanalverwaltung mit den Buttons.")
    @discord.guild_only()
    async def create_settings_embed(self, ctx):
        # Senden des Embeds und der Schaltflächen im statischen Settings-Kanal
        settings_channel = self.bot.get_channel(self.settings_channel_id)

        # Embed für die Verwaltung
        embed = discord.Embed(title="Kanalverwaltung",
                              description="Verwalte deinen temporären Sprachkanal mit den unten stehenden Optionen.",
                              color=0xEDAB54)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        # Schaltflächen für die Verwaltung
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Umbenennen", custom_id="rename", style=discord.ButtonStyle.primary))
        view.add_item(discord.ui.Button(label="Limit setzen", custom_id="limit", style=discord.ButtonStyle.primary))
        view.add_item(discord.ui.Button(label="Sperren", custom_id="lock", style=discord.ButtonStyle.danger))
        view.add_item(discord.ui.Button(label="Entsperren", custom_id="unlock", style=discord.ButtonStyle.success))
        view.add_item(discord.ui.Button(label="Kick", custom_id="kick", style=discord.ButtonStyle.danger))
        view.add_item(discord.ui.Button(label="Ban", custom_id="ban", style=discord.ButtonStyle.danger))
        view.add_item(discord.ui.Button(label="Unban", custom_id="unban", style=discord.ButtonStyle.success))

        # Überprüfen, ob das Embed bereits gesendet wurde
        async for message in settings_channel.history(limit=1):
            if message.embeds:
                # Falls das Embed bereits existiert, nichts tun
                await ctx.respond("Das Embed für die Kanalverwaltung wurde bereits erstellt.", ephemeral=True)
                return

        # Das Embed mit den Schaltflächen senden
        await settings_channel.send(embed=embed, view=view)
        await ctx.respond("Das Embed mit den Buttons wurde im Settings-Kanal erstellt.", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.custom_id == 'rename':
            await interaction.response.send_message("Bitte gib einen neuen Namen ein:", ephemeral=True)

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            msg = await self.bot.wait_for('message', check=check)
            temp_channel = discord.utils.get(interaction.guild.voice_channels, id=self.temp_channels[interaction.user.id]['voice_channel'])
            if temp_channel:
                await temp_channel.edit(name=msg.content)
                await interaction.followup.send(f"Der Kanal wurde umbenannt zu {msg.content}.", ephemeral=True)

        elif interaction.custom_id == 'lock':
            temp_channel = discord.utils.get(interaction.guild.voice_channels, id=self.temp_channels[interaction.user.id]['voice_channel'])
            if temp_channel:
                overwrite = temp_channel.overwrites_for(interaction.guild.default_role)
                overwrite.connect = False
                await temp_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
                await interaction.response.send_message("Der Kanal wurde gesperrt.", ephemeral=True)

        elif interaction.custom_id == 'unlock':
            temp_channel = discord.utils.get(interaction.guild.voice_channels, id=self.temp_channels[interaction.user.id]['voice_channel'])
            if temp_channel:
                overwrite = temp_channel.overwrites_for(interaction.guild.default_role)
                overwrite.connect = True
                await temp_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
                await interaction.response.send_message("Der Kanal wurde entsperrt.", ephemeral=True)

        elif interaction.custom_id == 'kick':
            await interaction.response.send_message("Bitte gib den Namen des Benutzers ein, den du kicken möchtest:", ephemeral=True)

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            msg = await self.bot.wait_for('message', check=check)
            member = discord.utils.get(interaction.guild.members, name=msg.content)
            temp_channel = discord.utils.get(interaction.guild.voice_channels, id=self.temp_channels[interaction.user.id]['voice_channel'])
            if member and temp_channel and member in temp_channel.members:
                await member.move_to(None)
                await interaction.followup.send(f"{member.name} wurde aus dem Kanal entfernt.", ephemeral=True)

        elif interaction.custom_id == 'limit':
            await interaction.response.send_message("Bitte gib das neue Benutzerlimit ein:", ephemeral=True)

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            msg = await self.bot.wait_for('message', check=check)
            if msg.content.isdigit():
                limit = int(msg.content)
                temp_channel = discord.utils.get(interaction.guild.voice_channels, id=self.temp_channels[interaction.user.id]['voice_channel'])
                if temp_channel:
                    await temp_channel.edit(user_limit=limit)
                    await interaction.followup.send(f"Das Benutzerlimit wurde auf {limit} gesetzt.", ephemeral=True)

        elif interaction.custom_id == 'ban':
            await interaction.response.send_message("Bitte gib den Namen des Benutzers ein, den du bannen möchtest:", ephemeral=True)

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            msg = await self.bot.wait_for('message', check=check)
            member = discord.utils.get(interaction.guild.members, name=msg.content)
            temp_channel = discord.utils.get(interaction.guild.voice_channels, id=self.temp_channels[interaction.user.id]['voice_channel'])
            if member and temp_channel and member in temp_channel.members:
                await temp_channel.set_permissions(member, connect=False)
                await member.move_to(None)
                await interaction.followup.send(f"{member.name} wurde gebannt.", ephemeral=True)

        elif interaction.custom_id == 'unban':
            await interaction.response.send_message("Bitte gib den Namen des Benutzers ein, den du entbannen möchtest:", ephemeral=True)

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            msg = await self.bot.wait_for('message', check=check)
            member = discord.utils.get(interaction.guild.members, name=msg.content)
            temp_channel = discord.utils.get(interaction.guild.voice_channels, id=self.temp_channels[interaction.user.id]['voice_channel'])
            if member and temp_channel:
                await temp_channel.set_permissions(member, connect=True)
                await interaction.followup.send(f"{member.name} wurde entbannt.", ephemeral=True)

def setup(bot):
    bot.add_cog(TempChannel(bot))
