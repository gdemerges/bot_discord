import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import asyncio

class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # ID du canal où les rappels seront envoyés
        self.channel_id = 1200438507315920918

        # Groupes d'utilisateurs pour les mentions hebdomadaires
        self.user_groups = [
            [294065690162364416, 509295845762400256, 998493093651296296, 428391859853852684],
            [708311679838060555, 1188435883947462656, 148188913817616384, 1043293367368425503],
            [1176093354329653298, 886153619043418124, 759914731468357702],
            [861540082262605826, 714403161346932823, 1192414156243091609]
        ]
        self.current_group_index = 0

        # Dates des jeudis exclus
        self.jeudis_exclus = [
            datetime(2024, 4, 18).date(),
            datetime(2024, 5, 9).date(),
            datetime(2024, 6, 13).date(),
            datetime(2024, 8, 15).date(),
            datetime(2024, 8, 22).date(),
        ]

        self.monthly_reminder.start()
        self.mention_users_group.start()

    @tasks.loop(hours=24)
    async def monthly_reminder(self):
        today = datetime.now()
        if today.day == 28:
            channel = self.bot.get_channel(self.channel_id)
            if channel is None:
                channel = await self.bot.fetch_channel(self.channel_id)

            message = (
                "@everyone Avant que le mois ne s'efface, accomplissez votre devoir : actualisez-vous chez Pôle Emploi "
                "pour maintenir vos droits. Que la promptitude soit votre alliée !"
            )
            await channel.send(message)

    @monthly_reminder.before_loop
    async def before_monthly_reminder(self):
        await self.bot.wait_until_ready()
        await self.wait_until_target_time(time(10, 0))

    @tasks.loop(minutes=10)
    async def mention_users_group(self):
        now = datetime.now()
        today = now.date()

        if now.weekday() == 3 and today not in self.jeudis_exclus:
            if time(16, 20) <= now.time() < time(16, 30):
                channel = self.bot.get_channel(self.channel_id)
                if channel is None:
                    channel = await self.bot.fetch_channel(self.channel_id)

                user_ids = self.user_groups[self.current_group_index]
                mentions = " ".join([f'<@{user_id}>' for user_id in user_ids])

                message = (
                    f"{mentions}, unissez vos efforts pour transformer nos espaces en havres de propreté et d'ordre."
                )
                await channel.send(message)

                self.current_group_index = (self.current_group_index + 1) % len(self.user_groups)

    @mention_users_group.before_loop
    async def before_mention_users_group(self):
        await self.bot.wait_until_ready()
        await self.wait_until_next_check()

    async def wait_until_target_time(self, target_time):
        now = datetime.now()
        target_datetime = datetime.combine(now.date(), target_time)
        if now > target_datetime:
            target_datetime += timedelta(days=1)
        await asyncio.sleep((target_datetime - now).total_seconds())

    async def wait_until_next_check(self):
        now = datetime.now()
        next_run = now + timedelta(minutes=10 - (now.minute % 10), seconds=-now.second, microseconds=-now.microsecond)
        await asyncio.sleep((next_run - now).total_seconds())

    @commands.command(name='next_group')
    async def show_next_group(self, ctx):
        """Affiche le prochain groupe qui sera mentionné."""
        user_ids = self.user_groups[self.current_group_index]
        mentions = " ".join([f'<@{user_id}>' for user_id in user_ids])
        await ctx.send(f"Le prochain groupe est : {mentions}")

def setup(bot):
    bot.add_cog(ReminderCog(bot))
