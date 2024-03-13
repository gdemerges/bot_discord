import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

user_groups = [
    "id user à mettre"
]
current_group_index = 0

if not hasattr(bot, 'mention_users_group_started'):
    bot.mention_users_group_started = False

@bot.event
async def on_ready():
    print(f'{bot.user.name} a démarré.')
    if not bot.mention_users_group_started:
        mention_users_group.start()
        bot.mention_users_group_started = True

@tasks.loop(hours=24)
async def mention_users_group():
    global current_group_index
    now = datetime.now()
    if now.weekday() == 3 and now.time() >= time(16, 0):
        channel = bot.get_channel(1200438507315920918)
        if channel:
            mentions = " ".join([f'<@{user_id}>' for user_id in user_groups[current_group_index]])
            await channel.send(f'Hello {mentions}, c\'est votre tour de faire le ménage cette semaine !')
            current_group_index = (current_group_index + 1) % len(user_groups)
            next_day = now + timedelta(days=1)
            next_day = next_day.replace(hour=0, minute=1)
            await discord.utils.sleep_until(next_day)

@mention_users_group.before_loop
async def before_mention_users_group():
    await bot.wait_until_ready()
    now = datetime.now()
    if now.weekday() < 3 or (now.weekday() == 3 and now.time() > time(17, 0)):
        days_until_thursday = (3 - now.weekday()) % 7
        next_run = now + timedelta(days=days_until_thursday)
        next_run_time = datetime.combine(next_run, time(16, 0))
        await discord.utils.sleep_until(next_run_time)
    elif now.weekday() == 3 and now.time() < time(17, 0):
        await discord.utils.sleep_until(datetime.combine(now, time(16, 0)))

bot.run('token bot')
