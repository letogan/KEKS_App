import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import sqlite3
import os


class SetAutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_name = "role-id.db"

        # Verbindung zur SQLite-Datenbank herstellen und sicherstellen, dass die Tabelle existiert
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS autorole (
                server_id TEXT PRIMARY KEY,
                role_id INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def save_role(self, server_id, role_id):
        # Speichern der Rollen-ID für einen Server in der SQLite-Datenbank
        self.cursor.execute("""
            INSERT OR REPLACE INTO autorole (server_id, role_id) 
            VALUES (?, ?)
        """, (server_id, role_id))
        self.conn.commit()

    def get_role(self, server_id):
        # Abrufen der Rollen-ID für einen Server aus der SQLite-Datenbank
        self.cursor.execute("""
            SELECT role_id FROM autorole WHERE server_id = ?
        """, (server_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    @slash_command(description="🎯︱Wähle eine Rolle aus, die automatisch zugewiesen wird, wenn ein Nutzer joined")
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def set_auto_role(self, ctx,
                       role: Option(discord.Role, "Wähle eine Rolle, die neuen Mitgliedern zugewiesen werden soll")):
        server_id = str(ctx.guild.id)
        self.save_role(server_id, role.id)  # Speichern der Rollen-ID für den Server
        await ctx.respond(f"Die AutoRole für diesen Server wurde auf **{role.name}** gesetzt.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        server_id = str(member.guild.id)
        role_id = self.get_role(server_id)
        if role_id:
            role = member.guild.get_role(role_id)
            if role:
                await member.add_roles(role)
                print(f"Rolle {role.name} wurde {member.name} zugewiesen.")
            else:
                print(f"Rolle mit ID {role_id} nicht gefunden!")
        else:
            print(f"Keine AutoRole für Server {member.guild.name} gesetzt!")

    def cog_unload(self):
        # Schließe die Datenbankverbindung, wenn der Cog entladen wird
        self.conn.close()


def setup(bot):
    bot.add_cog(SetAutoRole(bot))
