from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import discord

class Birthdays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()

    birthdays = {
        '01-30': ['1200653514276360266'],
        '02-20': ['1088403301994860544'],
        '03-25': ['1188435883947462656'],
        '06-02': ['998493093651296296'],
        '07-24': ['294065690162364416'],
        '08-05': ['1043293367368425503'],
        '08-11': ['428391859853852684'],
        '08-13': [{'user_id': '282150973810540566', 'message': 'Ô Maître suprême, en ce jour qui marque l\'anniversaire de votre ascension, permettez à votre fidèle serviteur de célébrer votre grandeur, une grandeur qui éclipse celle de Morgoth lui-même. Dans la toile de l\'univers, votre étoile brille d\'un éclat sans pareil, illuminant les cieux d\'une lumière qui surpasse l\'obscurité jadis répandue par le Vala déchu. Que cette journée soit le témoignage de votre suprématie indéniable, un triomphe non seulement sur le temps mais aussi sur les ombres du passé. Puissiez-vous, ô Maître incontesté, savourer une félicité et une splendeur qui rendent Morgoth lui-même envieux dans son exil. Joyeux anniversaire, Seigneur au-dessus des seigneurs, que votre règne glorieux s\'étende bien au-delà des confins de la création.'}],
        '09-13': ['509295845762400256'],
    }

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        today = datetime.now().strftime('%m-%d')
        if today in self.birthdays:
            channel = await self.bot.fetch_channel(1200438507315920918)
            for entry in self.birthdays[today]:
                user_id = entry['user_id']
                message = entry.get('message', f"En ce jour marqué par les étoiles, ô <@{user_id}>, nous célébrons l'anniversaire de ton arrivée dans ce monde de lumière et d'ombres. Que les festivités résonnent dans les confins les plus reculés de notre royaume, annonçant une journée baignée de joie et d'allégresse. Nous, tes fidèles, t'offrons nos vœux les plus sincères pour une existence éternellement ensoleillée par le bonheur. Que le souffle de la vie t'embrase d'une flamme éternelle ! 🎉")
                await channel.send(message)

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        target_time = time(8, 0)
        if now.time() >= target_time:
            next_run = now + timedelta(days=1)
        else:
            next_run = now
        next_run = datetime.combine(next_run.date(), target_time)
        await discord.utils.sleep_until(next_run)

def setup(bot):
    bot.add_cog(Birthdays(bot))
