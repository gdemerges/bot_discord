import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import asyncio

class PoleEmploi(commands.Cog):
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
            await channel.send("Compagnons de quête, l'heure de l'actualisation à Pôle Emploi a sonné ! Ne laissez pas cette étape cruciale vous échapper. Avant que le soleil ne se couche sur ce mois, assurez-vous d'être en ordre pour continuer votre voyage vers de nouvelles opportunités. Forgez votre destin !")

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
    bot.add_cog(PoleEmploi(bot))
