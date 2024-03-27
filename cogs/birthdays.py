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
        '08-13': ['282150973810540566'],
        '09-13': ['509295845762400256'],
    }

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        today = datetime.now().strftime('%m-%d')
        if today in self.birthdays:
            channel = await self.bot.fetch_channel(1200438507315920918)
            for user_id in self.birthdays[today]:
                await channel.send(f"Joyeux anniversaire <@{user_id}> 🎉! Le Mordor te souhaite une journée pleine de joie et de bonheur !")

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
