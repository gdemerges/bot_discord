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

morning_message_sent = False
afternoon_message_sent = False

excluded_dates = [
    date(2024, 8, 12),
    date(2024, 8, 13),
    date(2024, 8, 14),
    date(2024, 8, 15),
    date(2024, 8, 16),
    date(2024, 8, 17),
    date(2024, 8, 18),
    date(2024, 8, 19),
    date(2024, 8, 20),
    date(2024, 8, 21),
    date(2024, 8, 22),
    date(2024, 8, 23)
]

@bot.event
async def on_ready():
    print(f'{bot.user.name} a démarré.')
    mention_users_group.start()
    check_for_alerts.start()
    #message_vendredi.start()
    check_birthdays.start()
    monthly_reminder.start()
    check_messages_morning.start()
    check_messages_afternoon.start()
    schedule_election_reminder.start()

@tasks.loop(minutes=1)
async def schedule_election_reminder():
    now = datetime.now()
    election_reminder_date = datetime(2024, 6, 7, 14, 0)  # 7 juin 2024 à 14h00
    if now >= election_reminder_date:
        channel = bot.get_channel(1200438507315920918)
        await channel.send("@everyone Ô peuples de cette vaste contrée, l'heure solennelle du choix approche avec les élections européennes. Que chacun de vous prenne les armes de la démocratie et marche vers les urnes. Pour faire écho à l'appel de notre camarade <@205740195914579969>, considérez de porter votre voix vers La France Insoumise, pour que leurs idéaux résonnent au cœur des débats européens. Que votre vote forge l'avenir de notre continent. Levez-vous, citoyens, et faites entendre votre voix !")
        schedule_election_reminder.stop()

async def check_messages(start_time, end_time, period):
    global morning_message_sent, afternoon_message_sent

    channel = bot.get_channel(1206906418226266122)
    now = datetime.utcnow()

    messages = await channel.history(after=start_time, before=now).flatten()

    if not messages:
        await channel.send("Envoyez immédiatement le lien pour signature et fortifiez ainsi notre pacte. Que cet acte rapide renforce notre grand dessein. Agissez sans délai !")
        if period == "morning":
            morning_message_sent = True
        elif period == "afternoon":
            afternoon_message_sent = True

@tasks.loop(minutes=1)
async def check_messages_morning():
    global morning_message_sent
    now = datetime.now().date()
    current_time = datetime.now().time()
    if now.weekday() < 5 and now not in excluded_dates:
        if current_time.hour == 12 and current_time.minute == 0 and not morning_message_sent:
            start_time = datetime.combine(now, time(9, 0))
            end_time = datetime.combine(now, time(12, 0))
            await check_messages(start_time, end_time, "morning")
        elif current_time.hour == 12 and current_time.minute > 0:
            morning_message_sent = False

@tasks.loop(minutes=1)
async def check_messages_afternoon():
    global afternoon_message_sent
    now = datetime.now().date()
    current_time = datetime.now().time()
    if now.weekday() < 5 and now not in excluded_dates:
        if current_time.hour == 16 and current_time.minute == 0 and not afternoon_message_sent:
            start_time = datetime.combine(now, time(13, 0))
            end_time = datetime.combine(now, time(16, 0))
            await check_messages(start_time, end_time, "afternoon")
        elif current_time.hour == 16 and current_time.minute > 0:
            afternoon_message_sent = False

@check_messages_morning.before_loop
async def before_check_messages_morning():
    await bot.wait_until_ready()

@check_messages_afternoon.before_loop
async def before_check_messages_afternoon():
    await bot.wait_until_ready()

@schedule_election_reminder.before_loop
async def before_schedule_election_reminder():
    await bot.wait_until_ready()


birthdays = {
    '01-30': ['1200653514276360266'], # Myriam
    '02-20': ['1088403301994860544'], # Alou
    '02-27': ['708311679838060555'], # Quentin
    '03-25': ['1188435883947462656'], # Mathieu
    '04-29': ['886153619043418124'], # Djessim
    '06-02': ['998493093651296296'], # Anne
    '07-24': ['294065690162364416'], # JS
    '08-05': ['1043293367368425503'], # Momo
    '08-11': ['428391859853852684'], # Mélanie
    '08-13': [{'user_id': ['1192414156243091609', '282150973810540566'], 'message': ". Que l'éclat de cette journée spéciale illumine votre année à venir avec réussite et allégresse. Joyeux anniversaire à vous deux ! Que les festivités soient dignes des plus grands récits épiques du Mordor. 🎉"}
    ], # Kim / Guillaume
    '09-13': ['509295845762400256'], # Heloise
}

@tasks.loop(hours=24)
async def check_birthdays():
    today = datetime.now().strftime('%m-%d')
    if today in birthdays:
        channel = await bot.fetch_channel(1200438507315920918)
        user_ids = []
        custom_messages = []

        for entry in birthdays[today]:
            if isinstance(entry, str):
                user_ids.append(entry)
            else:
                user_ids.extend(entry['user_id'])
                custom_messages.append(entry['message'])

        if user_ids:
            tagged_users = ' et '.join(f"<@{uid}>" for uid in user_ids)
            if custom_messages:
                custom_message = ' '.join(custom_messages)
                message = f"En ce jour, les étoiles s'alignent pour célébrer {tagged_users} {custom_message}"
            else:
                message = f"{tagged_users}, en ce jour spécial, nous célébrons ton anniversaire avec joie et enthousiasme. Que cette journée soit remplie de bonheur et que la fête résonne à travers notre royaume. Nous te souhaitons une vie rayonnante de bonheur. Joyeux anniversaire ! 🎉 !"
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

vendredis_exclu = [
    date(2024, 5, 10),
    date(2024, 8, 16)
]
"""
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

index_message = 0
message_sent_this_week = False

@tasks.loop(minutes=1)
async def message_vendredi():
    global message_sent_this_week
    global index_message
    now = datetime.now()
    if now.weekday() == 4 and now.time() >= time(16, 55) and now.time() < time(17, 00) and not message_sent_this_week and now.date() not in vendredis_exclu:
        channel = await bot.fetch_channel(1200438507315920918)
        if channel:
            message_debut = "À vous tous.tes, que le voile de la semaine se lève sur le sanctuaire du week-end. Mais souvenez-vous, mortels, que votre quête ne s'arrête pas ici. "
            message_fin = fin_messages[index_message]
            await channel.send(message_debut + message_fin)
            message_sent_this_week = True
            index_message = (index_message + 1) % len(fin_messages)

@message_vendredi.before_loop
async def before_message_vendredi():
    global message_sent_this_week
    await bot.wait_until_ready()
    message_sent_this_week = False
"""

user_groups = [
    [294065690162364416, 509295845762400256, 998493093651296296, 428391859853852684],
    [708311679838060555, 1188435883947462656, 148188913817616384, 1043293367368425503],
    [1200653514276360266, 1176093354329653298, 886153619043418124, 759914731468357702],
    [1088403301994860544, 282150973810540566, 1206374165783773255, 1084925938103492619]
]

current_group_index = 0

jeudis_exclus = [
    date(2024, 4, 18),
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

@tasks.loop(hours=24)
async def monthly_reminder():
    today = datetime.now()
    if today.day == 28:
        channel = await bot.fetch_channel(1200438507315920918)
        message = "@everyone Avant que le mois ne s'efface, accomplissez votre devoir : actualisez-vous chez Pôle Emploi pour maintenir vos droits. Que la promptitude soit votre alliée !"
        await channel.send(message)

@monthly_reminder.before_loop
async def before_monthly_reminder():
    await bot.wait_until_ready()
    now = datetime.now()
    if now.time() < datetime.strptime("10:00", "%H:%M").time():
        wait_time = (datetime.combine(now.date(), datetime.strptime("10:00", "%H:%M").time()) - now).total_seconds()
    else:
        wait_time = (datetime.combine(now.date() + timedelta(days=1), datetime.strptime("10:00", "%H:%M").time()) - now).total_seconds()
    await asyncio.sleep(wait_time)

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
