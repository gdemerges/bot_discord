import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import asyncio

class PoleEmploiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_for_pole_emploi_update.start()

    def cog_unload(self):
        self.check_for_pole_emploi_update.cancel()

    @tasks.loop(hours=24)
    async def check_for_pole_emploi_update(self):
        today = datetime.now()
        if today.day == 28:
            channel = self.bot.get_channel(1200438507315920918)
            await channel.send("N'oubliez pas de vous actualiser à Pôle Emploi aujourd'hui !")

    @check_for_pole_emploi_update.before_loop
    async def before_check_for_pole_emploi_update(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        if now.time() < time(9, 0):
            target_time = datetime.combine(now.date(), time(9, 0))
        else:
            tomorrow = now.date() + timedelta(days=1)
            target_time = datetime.combine(tomorrow, time(9, 0))
        initial_delay = (target_time - now).total_seconds()
        await asyncio.sleep(initial_delay)

def setup(bot):
    bot.add_cog(PoleEmploiCog(bot))
