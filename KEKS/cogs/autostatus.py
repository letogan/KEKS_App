import discord
from discord.ext import commands, tasks
import asyncio

class StatusChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_task.start()

    def cog_unload(self):
        self.status_task.cancel()

    @tasks.loop(seconds=15)
    async def status_task(self):
        statuses = [
            discord.Game("/help"),
            discord.Game("/daily"),
            discord.Game("🔗 dsc.gg/keks-app")
        ]

        for status in statuses:
            await self.bot.change_presence(activity=status)
            await asyncio.sleep(7)

    @status_task.before_loop
    async def before_status_task(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(StatusChanger(bot))
