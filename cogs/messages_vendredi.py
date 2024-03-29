from discord.ext import commands, tasks
from datetime import datetime, time

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
        self.message_vendredi.start()

    @tasks.loop(minutes=10)
    async def message_vendredi(self):
        now = datetime.now()
        if now.weekday() == 4 and now.time() >= time(16, 50) and now.time() < time(17, 00):
            channel = self.bot.get_channel(1200438507315920918)
            if channel:
                message_debut = "À vous tous.tes, que le voile de la semaine se lève sur le sanctuaire du week-end. Mais souvenez-vous, mortels, que le plus grand des actes en faveur de notre monde, le geste éco-responsable par excellence, demeure "
                message_fin = self.fin_messages[self.index_message]
                await channel.send(message_debut + message_fin)

                self.index_message += 1

                if self.index_message >= len(self.fin_messages):
                    self.index_message = 0

def setup(bot):
    bot.add_cog(MessagesVendredi(bot))
