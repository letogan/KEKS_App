import sqlite3
from discord.ext import commands
from discord.commands import slash_command
import discord
import os

class SetTempChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}
        self.db_path = "temp_channels.db"
        self.init_database()

    def init_database(self):
        """Initialize SQLite database and create necessary tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            # Create the table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS temp_channel_settings (
                    guild_id INTEGER PRIMARY KEY,
                    create_channel_id INTEGER NOT NULL
                )
            ''')
            conn.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            conn.close()

    def get_db(self):
        """Get a database connection and create table if needed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Ensure table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temp_channel_settings (
                guild_id INTEGER PRIMARY KEY,
                create_channel_id INTEGER NOT NULL
            )
        ''')
        conn.commit()
        return conn, cursor

    async def get_create_channel_id(self, guild_id: int) -> int:
        """Get the create channel ID for a specific guild."""
        conn, cursor = self.get_db()
        try:
            cursor.execute('SELECT create_channel_id FROM temp_channel_settings WHERE guild_id = ?', (guild_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()

    @slash_command(description="Set the channel that users will join to create temporary channels")
    @commands.has_permissions(administrator=True)
    async def set_tempchannel(self, ctx, channel: discord.VoiceChannel):
        """Set the channel that will be used as the temporary channel creator."""
        conn, cursor = self.get_db()
        try:
            # Insert or update the create channel ID for this guild
            cursor.execute('''
                INSERT OR REPLACE INTO temp_channel_settings (guild_id, create_channel_id)
                VALUES (?, ?)
            ''', (ctx.guild.id, channel.id))
            conn.commit()
            await ctx.respond(f"✅ Successfully set {channel.name} as the temporary channel creator!", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ An error occurred: {str(e)}", ephemeral=True)
        finally:
            conn.close()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not after.channel:
            return

        create_channel_id = await self.get_create_channel_id(member.guild.id)
        if not create_channel_id:
            return

        if after.channel.id == create_channel_id:
            # Create a new temporary channel
            category = after.channel.category
            temp_channel = await category.create_voice_channel(f"{member.name}'s Channel")
            await member.move_to(temp_channel)
            self.temp_channels[member.id] = {'voice_channel': temp_channel.id}

        # Check if user left a temporary channel
        if before.channel and before.channel.id in [data['voice_channel'] for data in self.temp_channels.values()]:
            temp_channel = before.channel
            owner_id = next((uid for uid, data in self.temp_channels.items()
                           if data['voice_channel'] == temp_channel.id), None)

            if owner_id and member.id == owner_id and len(temp_channel.members) == 0:
                await temp_channel.delete()
                del self.temp_channels[owner_id]

    @slash_command(description="Manage your temporary voice channel")
    async def channel(self, ctx):
        # Only respond if the user has a temporary channel
        if ctx.author.id not in self.temp_channels:
            await ctx.respond("You don't have an active temporary channel!", ephemeral=True)
            return

        # Create the management embed
        embed = discord.Embed(
            title="Channel Management",
            description="Manage your temporary voice channel with the buttons below.",
            color=discord.Color.blue()
        )

        # Create the button view
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Rename", custom_id="rename", style=discord.ButtonStyle.primary))
        view.add_item(discord.ui.Button(label="Set Limit", custom_id="limit", style=discord.ButtonStyle.primary))
        view.add_item(discord.ui.Button(label="Lock", custom_id="lock", style=discord.ButtonStyle.danger))
        view.add_item(discord.ui.Button(label="Unlock", custom_id="unlock", style=discord.ButtonStyle.success))

        await ctx.respond(embed=embed, view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.custom_id in ['rename', 'limit', 'lock', 'unlock']:
            return

        if interaction.user.id not in self.temp_channels:
            await interaction.response.send_message("You don't have an active temporary channel!", ephemeral=True)
            return

        temp_channel = self.bot.get_channel(self.temp_channels[interaction.user.id]['voice_channel'])
        if not temp_channel:
            await interaction.response.send_message("Could not find your temporary channel!", ephemeral=True)
            return

        if interaction.custom_id == 'rename':
            await interaction.response.send_modal(
                discord.ui.Modal(
                    title="Rename Channel",
                    custom_id="rename_modal",
                    components=[
                        discord.ui.TextInput(
                            label="New Name",
                            custom_id="channel_name",
                            style=discord.TextStyle.short,
                            placeholder="Enter new channel name",
                            required=True
                        )
                    ]
                )
            )

        elif interaction.custom_id == 'limit':
            await interaction.response.send_modal(
                discord.ui.Modal(
                    title="Set User Limit",
                    custom_id="limit_modal",
                    components=[
                        discord.ui.TextInput(
                            label="User Limit",
                            custom_id="user_limit",
                            style=discord.TextStyle.short,
                            placeholder="Enter a number (0-99)",
                            required=True
                        )
                    ]
                )
            )

        elif interaction.custom_id == 'lock':
            await temp_channel.set_permissions(interaction.guild.default_role, connect=False)
            await interaction.response.send_message("Channel locked! 🔒", ephemeral=True)

        elif interaction.custom_id == 'unlock':
            await temp_channel.set_permissions(interaction.guild.default_role, connect=True)
            await interaction.response.send_message("Channel unlocked! 🔓", ephemeral=True)

    @commands.Cog.listener()
    async def on_modal_submit(self, interaction: discord.Interaction):
        if interaction.custom_id not in ['rename_modal', 'limit_modal']:
            return

        temp_channel = self.bot.get_channel(self.temp_channels[interaction.user.id]['voice_channel'])
        if not temp_channel:
            await interaction.response.send_message("Could not find your temporary channel!", ephemeral=True)
            return

        if interaction.custom_id == 'rename_modal':
            new_name = interaction.data['components'][0]['components'][0]['value']
            await temp_channel.edit(name=new_name)
            await interaction.response.send_message(f"Channel renamed to {new_name}! ✏️", ephemeral=True)

        elif interaction.custom_id == 'limit_modal':
            try:
                limit = int(interaction.data['components'][0]['components'][0]['value'])
                if 0 <= limit <= 99:
                    await temp_channel.edit(user_limit=limit)
                    await interaction.response.send_message(
                        f"User limit set to {limit}! 👥", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "Please enter a number between 0 and 99!", ephemeral=True
                    )
            except ValueError:
                await interaction.response.send_message(
                    "Please enter a valid number!", ephemeral=True
                )

def setup(bot):
    bot.add_cog(SetTempChannel(bot))