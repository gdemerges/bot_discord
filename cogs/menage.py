from discord.ext import commands, tasks
from datetime import datetime, date, time, timedelta
import discord

class Menage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jeudis_exclus = [
            date(2024, 5, 9),
            date(2024, 8, 15),
            date(2024, 8, 22),
        ]
        self.user_groups = [
            [1200653514276360266, 1176093354329653298, 985859071754260510, 759914731468357702],
            [1088403301994860544, 282150973810540566, 1206374165783773255, 1084925938103492619],
            [294065690162364416, 509295845762400256, 998493093651296296, 428391859853852684],
            [708311679838060555, 1188435883947462656, 148188913817616384, 1043293367368425503]
        ]
        self.current_group_index = 0
        self.mention_users_group.start()

    @tasks.loop(minutes=10)
    async def mention_users_group(self):
        now = datetime.now()
        if now.weekday() == 3 and now.date() not in self.jeudis_exclus:
            channel = self.bot.get_channel(1200438507315920918)
            if channel and now.time() >= time(16, 30) and now.time() < time(16, 40):
                mentions = " ".join([f'<@{user_id}>' for user_id in self.user_groups[self.current_group_index]])
                await channel.send(f'Que les ombres de la négligence se dissipent et que la lumière de l\'ordre règne ! Soulevez vos armes, les balais et les chiffons, {mentions}, c\'est votre tour de faire le ménage cette semaine ! Que chaque coin et recoin soit purifié, pour que le savoir puisse fleurir en terre de connaissance immaculée.')
                self.current_group_index = (self.current_group_index + 1) % len(self.user_groups)

    @mention_users_group.before_loop
    async def before_mention_users_group(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        if now.weekday() < 3 or (now.weekday() == 3 and now.time() > time(17, 0)):
            days_until_thursday = (3 - now.weekday()) % 7
            next_run = now + timedelta(days=days_until_thursday)
            next_run_time = datetime.combine(next_run, time(16, 0))
            await discord.utils.sleep_until(next_run_time)
        elif now.weekday() == 3 and now.time() < time(17, 0):
            await discord.utils.sleep_until(datetime.combine(now, time(16, 0)))

def setup(bot):
    bot.add_cog(Menage(bot))
