import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta

class MessagesVendredi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fin_messages = [
            "d'apprendre à coder en Python sans l'abject chatGPT",
            "de lécher votre partenaire, pas les vitrines",
            "d'améliorer vos skills en IA pour mettre au chômage tout ces bâtards de cols blanc",
            "de crâmer une banque",
            "de composter des riches",
            "de décapiter Macron",
            "de manger un riche",
            "de dégager ce sale facho et violeur de Darmanin",
        ]
        self.index_message = 0
        self.message_sent_this_week = False
        self.message_vendredi.start()

    @tasks.loop(minutes=1)
    async def message_vendredi(self):
        now = datetime.now()
        if now.weekday() == 4 and now.time() >= time(17, 00) and now.time() < time(17, 15) and not self.message_sent_this_week:
            channel = self.bot.get_channel(1200438507315920918)
            if channel:
                message_debut = "..."
                message_fin = self.fin_messages[self.index_message]
                await channel.send(message_debut + message_fin)
                self.index_message = (self.index_message + 1) % len(self.fin_messages)
                self.message_sent_this_week = True

    @message_vendredi.before_loop
    async def before_message_vendredi(self):
        await self.bot.wait_until_ready()
        while not self.message_vendredi.is_running():
            now = datetime.now()
            if now.weekday() == 4 and now.time() < time(17, 00):
                await discord.utils.sleep_until(datetime.combine(now.date(), time(17, 0)))
            elif now.weekday() == 4 and now.time() >= time(17, 15):
                self.message_sent_this_week = False
                next_friday = now + timedelta((4-now.weekday()) % 7 + 7)
                await discord.utils.sleep_until(datetime.combine(next_friday, time(17, 0)))
            else:
                next_friday = now + timedelta((4-now.weekday()) % 7)
                await discord.utils.sleep_until(datetime.combine(next_friday, time(17, 0)))
def setup(bot):
    bot.add_cog(MessagesVendredi(bot))
