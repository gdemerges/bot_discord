import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, date
import asyncio
import json

class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.birthdays = {
            '01-09': ['714403161346932823'],  # Alison
            '02-20': ['1088403301994860544'],  # Alou
            '02-27': ['708311679838060555'],  # Quentin
            '03-25': ['1188435883947462656'],  # Mathieu
            '04-29': ['886153619043418124'],  # Djessim
            '06-02': ['998493093651296296'],  # Anne
            '07-24': ['294065690162364416'],  # JS
            '08-05': ['1043293367368425503'],  # Momo
            '08-11': ['428391859853852684'],  # Mélanie
            '08-13': [
                {
                    'user_id': ['1192414156243091609', '282150973810540566'],
                    'message': ". Que l'éclat de cette journée spéciale illumine votre année à venir avec réussite et allégresse. Joyeux anniversaire à vous deux ! Que les festivités soient dignes des plus grands récits épiques du Mordor. 🎉"
                }
            ],  # Kim / Guillaume
            '09-13': ['509295845762400256'],  # Héloïse
        }

        self.channel_id = 1200438507315920918

        self.check_birthdays.start()

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        today = datetime.now().strftime('%m-%d')
        if today in self.birthdays:
            channel = self.bot.get_channel(self.channel_id)
            if channel is None:
                channel = await self.bot.fetch_channel(self.channel_id)

            user_ids = []
            custom_messages = []

            for entry in self.birthdays[today]:
                if isinstance(entry, str):
                    user_ids.append(entry)
                else:
                    user_ids.extend(entry['user_id'])
                    custom_messages.append(entry['message'])

            if user_ids:
                tagged_users = ' et '.join(f"<@{uid}>" for uid in user_ids)
                if custom_messages:
                    custom_message = ' '.join(custom_messages)
                    message = f"En ce jour, les étoiles s'alignent pour célébrer {tagged_users}{custom_message}"
                else:
                    message = (
                        f"{tagged_users}, en ce jour spécial, nous célébrons ton anniversaire avec joie et enthousiasme. "
                        "Que cette journée soit remplie de bonheur et que la fête résonne à travers notre royaume. "
                        "Nous te souhaitons une vie rayonnante de bonheur. Joyeux anniversaire ! 🎉"
                    )
                await channel.send(message)

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()
        await self.wait_until_target_time()

    async def wait_until_target_time(self):
        now = datetime.now()
        target_time = datetime.combine(now.date(), datetime.strptime("08:00", "%H:%M").time())
        if now > target_time:
            target_time += timedelta(days=1)
        await asyncio.sleep((target_time - now).total_seconds())

def setup(bot):
    bot.add_cog(BirthdayCog(bot))
