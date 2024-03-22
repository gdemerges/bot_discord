import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time, date
import random
import aiohttp
import json

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

user_groups = [
    [1200653514276360266, 1176093354329653298, 985859071754260510, 759914731468357702],
    [1088403301994860544, 282150973810540566, 1206374165783773255, 1084925938103492619],
    [294065690162364416, 509295845762400256, 998493093651296296, 428391859853852684],
    [708311679838060555, 1188435883947462656, 148188913817616384, 1043293367368425503]
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
        check_for_alerts.start()
        message_vendredi.start()

fin_messages = [
    "de manger un riche",
    "de crâmer une banque",
    "de décapiter macron",
    "d'envoyer Djessim faire le ménage à Grenoble",
    "de dégager ce sale facho et violeur de Darmanin",
    "de léchez votre partenaire, pas les vitrines"
]

@tasks.loop(minutes=30)
async def message_vendredi():
    now = datetime.now()
    if now.weekday() == 4 and now.hour == 17:
        channel = bot.get_channel(1200438507315920918)
        if channel:
            message_debut = "Bon WE à tous.tes ! Et n'oubliez pas, le meilleur écogeste est "
            message_fin = random.choice(fin_messages)
            await channel.send(message_debut + message_fin)


@bot.command(name='alternance')
async def alternance(ctx):
    maintenant = datetime.now()
    debut_alternance = datetime(2024, 9, 23)
    delta = debut_alternance - maintenant
    jours = delta.days
    heures, reste = divmod(delta.seconds, 3600)
    minutes, secondes = divmod(reste, 60)
    message = f"Il reste {jours} jours, {heures} heures, {minutes} minutes et {secondes} secondes avant le début de l'alternance."
    await ctx.send(message)

@bot.command(name='djessim')
async def djessim(ctx):
    special_user_id = 985859071754260510
    message = f'<@{special_user_id}>, tu dois aller faire le ménage à Regmind !'
    await ctx.send(message)

@bot.command(name='reveil')
async def reveil(ctx):
    special_user_id = 985859071754260510
    message = f'<@{special_user_id}>, réveille toi !!'
    await ctx.send(message)

jeudis_exclus = [
    date(2024, 5, 9),
    date(2024, 8, 15),
    date(2024, 8, 22),
]

@tasks.loop(minutes=30)
async def mention_users_group():
    global current_group_index
    now = datetime.now()
    today = datetime.now()
    if now.weekday() == 3 and today.date() not in jeudis_exclus:
        channel = bot.get_channel(1200438507315920918)
        if channel:
            if now.time() >= time(16, 30) and now.time() < time(16, 40):
                mentions = " ".join([f'<@{user_id}>' for user_id in user_groups[current_group_index]])
                await channel.send(f'Hello {mentions}, c\'est votre tour de faire le ménage cette semaine !')
                current_group_index = (current_group_index + 1) % len(user_groups)

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

@tasks.loop(minutes=1)
async def check_for_alerts():
    now = datetime.now()
    if now.weekday() < 5 and now.time() >= time(8, 0) and now.time() < time(9, 0):
        await fetch_and_send_alerts()

async def fetch_and_send_alerts():
    url = 'https://data.grandlyon.com/fr/datapusher/ws/rdata/tcl_sytral.tclalertetrafic_2/all.json'
    webhook_url = 'https://discord.com/api/webhooks/1219376934572523561/68iUsrDxMrIsreP5ZHfySA0viFhoSnLU0fZ4jzwe1mOf9HnUpqde0IFKvD3qOMxym-2a'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                alerts = data['values']
                filtered_alerts = [alert for alert in alerts if alert['ligne_cli'] in ['B', 'T3']]
                for alert in filtered_alerts:
                    await send_alert_to_discord(session, webhook_url, alert)

async def send_alert_to_discord(session, webhook_url, alert):
    message_content = f"Alerte Trafic : {alert['titre']} - {alert['message']}"
    payload = {
        "content": message_content
    }
    headers = {
        "Content-Type": "application/json",
    }
    async with session.post(webhook_url, json=payload, headers=headers) as response:
        if response.status != 200:
            print(f"Erreur lors de l'envoi du message: {response.status}")

@check_for_alerts.before_loop
async def before_check_for_alerts():
    await bot.wait_until_ready()
    now = datetime.now()
    if now.time() < time(8, 0):
        await discord.utils.sleep_until(datetime.combine(now.date(), time(8, 0)))
    elif now.time() >= time(9, 0):
        tomorrow = now.date() + timedelta(days=1)
        await discord.utils.sleep_until(datetime.combine(tomorrow, time(8, 0)))

with open('config.json') as config_file:
    config = json.load(config_file)
    bot_token = config.get('token')

if bot_token is None:
    raise ValueError("Le token du bot n'est pas défini dans config.json.")

bot.run(bot_token)
