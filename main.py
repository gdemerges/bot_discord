import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time, date
import random
import aiohttp
import json
import asyncio
import csv

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} a démarré.')
    mention_users_group.start()
    check_for_alerts.start()
    message_vendredi.start()
    check_birthdays.start()

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
async def check_birthdays():
    today = datetime.now().strftime('%m-%d')
    if today in birthdays:
        channel = await bot.fetch_channel(1200438507315920918)
        for entry in birthdays[today]:
            if isinstance(entry, str):
                message = f"En ce jour marqué par les étoiles, ô <@{user_id}>, nous célébrons l'anniversaire de ton arrivée dans ce monde de lumière et d'ombres. Que les festivités résonnent dans les confins les plus reculés de notre royaume, annonçant une journée baignée de joie et d'allégresse. Nous, tes fidèles, t'offrons nos vœux les plus sincères pour une existence éternellement ensoleillée par le bonheur. Que le souffle de la vie t'embrase d'une flamme éternelle ! 🎉")
            else :
                user_id = entry['user_id']
                custom_message = entry['message']
                message = f"<@{user_id}> {custom_message}"
            await channel.send(message)

@check_birthdays.before_loop
async def before_check_birthdays():
    await bot.wait_until_ready()
    await wait_until_target_time(time(8, 0))

async def wait_until_target_time(target_time):
    now = datetime.now()
    current_time = now.time()
    if current_time >= target_time:
        next_run = now + timedelta(days=1)
    else:
        next_run = now
    next_run = datetime.combine(next_run.date(), target_time)
    seconds_until_target = (next_run - now).total_seconds()
    await asyncio.sleep(seconds_until_target)

with open('data/questions.json', 'r') as f:
    questions = json.load(f)

@bot.command(name='quizz')
async def quizz(ctx):
    question = random.choice(questions)

@bot.command(name='post_jobs')
async def post_jobs(ctx):
    channel = bot.get_channel(1200438507315920918)
    posted_jobs = set()

    with open('data/jobs.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            job_url = row['link']
            if job_url not in posted_jobs:
                posted_jobs.add(job_url)
                message = f"**{row['title']}**\nPlus d'infos: {job_url}"
                await channel.send(message)


fin_messages = [
    "d'apprendre à coder en Python sans l'abject chatGPT",
    "de léchez votre partenaire, pas les vitrines",
    "d'améliorer vos skills en IA mettre au chômage tout ces batards de cols blanc",
    "d'améliorer vos skills en IA pour mettre au chômage tout ces batards de cols blanc",
    "de crâmer une banque",
    "de composter des riches",
    "de décapiter macron",
    "de dégager ce sale facho et violeur de Darmanin",
]

messages_disponibles = fin_messages.copy()
index_message = 0
message_sent_this_week = False

@tasks.loop(minutes=1)
async def message_vendredi():
    global message_sent_this_week
    now = datetime.now()
    if now.weekday() == 4 and now.time() >= time(17, 00) and now.time() < time(17, 15) and not message_sent_this_week:
        channel = await bot.fetch_channel(1200438507315920918) # Correction pour utiliser fetch_channel
        if channel:
            message_debut = "À vous tous.tes, que le voile de la semaine se lève sur le sanctuaire du week-end. Mais souvenez-vous, mortels, que le plus grand des actes en faveur de notre monde, le geste éco-responsable par excellence, demeure"
            message_fin = fin_messages[index_message]
            await channel.send(message_debut + message_fin)
            message_sent_this_week = True

@message_vendredi.before_loop
async def before_message_vendredi():
    global message_sent_this_week
    await bot.wait_until_ready()
    message_sent_this_week = False

user_groups = [
    [1200653514276360266, 1176093354329653298, 886153619043418124, 759914731468357702],
    [1088403301994860544, 282150973810540566, 1206374165783773255, 1084925938103492619],
    [294065690162364416, 509295845762400256, 998493093651296296, 428391859853852684],
    [708311679838060555, 1188435883947462656, 148188913817616384, 1043293367368425503]
]

current_group_index = 0

jeudis_exclus = [
    date(2024, 5, 9),
    date(2024, 8, 15),
    date(2024, 8, 22),
]

@tasks.loop(minutes=10)
async def mention_users_group():
    global current_group_index
    now = datetime.now()
    today = datetime.now()
    if now.weekday() == 3 and today.date() not in jeudis_exclus:
        channel = bot.get_channel(1200438507315920918)
        if channel:
            if now.time() >= time(16, 30) and now.time() < time(16, 40):
                mentions = " ".join([f'<@{user_id}>' for user_id in user_groups[current_group_index]])
                await channel.send(f'Que les ombres de la négligence se dissipent et que la lumière de l\'ordre règne ! Soulevez vos armes, les balais et les chiffons, {mentions}, c\'est votre tour de faire le ménage cette semaine ! Que chaque coin et recoin soit purifié, pour que le savoir puisse fleurir en terre de connaissance immaculée.')
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

with open('data/config.json') as config_file:
    config = json.load(config_file)
    bot_token = config.get('token')

if bot_token is None:
    raise ValueError("Le token du bot n'est pas défini dans config.json.")

bot.run(bot_token)
