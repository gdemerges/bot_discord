import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time, date
import random
import aiohttp
import json
import asyncio
import csv

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

user_groups = [
    [294065690162364416, 509295845762400256, 998493093651296296, 428391859853852684],
    [708311679838060555, 1188435883947462656, 148188913817616384, 1043293367368425503],
    [1200653514276360266, 1176093354329653298, 985859071754260510, 759914731468357702],
    [1088403301994860544, 282150973810540566, 1206374165783773255, 1084925938103492619]
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
        check_birthdays.start()


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
async def check_birthdays():
    today = datetime.now().strftime('%m-%d')
    if today in birthdays:
        channel = bot.get_channel(1200438507315920918)
        for user_id in birthdays[today]:
            await channel.send(f"Joyeux anniversaire <@{user_id}> 🎉! Nous te souhaitons une journée pleine de joie et de bonheur !")

@check_birthdays.before_loop
async def before_check_birthdays():
    await bot.wait_until_ready()
    now = datetime.now()
    target_time = time(8, 0)
    if now.time() >= target_time:
        next_run = now + timedelta(days=1)
    else:
        next_run = now
    next_run = datetime.combine(next_run.date(), target_time)
    wait_seconds = (next_run - now).total_seconds()
    await asyncio.sleep(wait_seconds)

with open('questions.json', 'r') as f:
    questions = json.load(f)

@bot.command(name='post_jobs')
async def post_jobs(ctx):
    channel = bot.get_channel(1200438507315920918)
    posted_jobs = set()

    with open('jobs.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            job_url = row['link']
            if job_url not in posted_jobs:
                posted_jobs.add(job_url)
                message = f"**{row['title']}**\nPlus d'infos: {job_url}"
                await channel.send(message)

@bot.command(name='quizz')
async def quizz(ctx):
    question = random.choice(questions)
    choices = '\n'.join(question['choices'])
    await ctx.send(f"{question['question']}\n{choices}")

    answers = {}

    def check(m):
        return m.channel == ctx.channel and m.content.lower() in [choice.lower() for choice in question['choices']]

    end_time = datetime.now() + timedelta(seconds=30)

    while datetime.now() < end_time:
        try:
            msg = await bot.wait_for('message', check=check, timeout=(end_time - datetime.now()).total_seconds())
            if msg:
                answers[msg.author] = msg.content
        except asyncio.TimeoutError:
            break

    correct_answers = [author.mention for author, answer in answers.items() if answer.lower() == question['answer'].lower()]

    if correct_answers:
        await ctx.send(f"Les utilisateurs suivants ont répondu correctement: {', '.join(correct_answers)} 🎉")
    else:
        await ctx.send(f"Personne n'a trouvé la bonne réponse. La bonne réponse était : {question['answer']}")

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

@bot.command(name='reveil')
async def reveil(ctx):
    special_user_id = 985859071754260510
    message = f'<@{special_user_id}>, réveille toi !!'
    await ctx.send(message)

fin_messages = [
    "d'apprendre à coder en Python sans l'abject chatGPT",
    "de léchez votre partenaire, pas les vitrines",
    "d'améliorer vos skills en IA pour mettre au chômage tout ces batards de cols blanc",
    "de crâmer une banque",
    "de composter des riches",
    "de décapiter macron",
    "de manger un riche",
    "de dégager ce sale facho et violeur de Darmanin",
]

index_message = 0

@tasks.loop(minutes=10)
async def message_vendredi():
    global index_dernier_message

    now = datetime.now()
    if now.weekday() == 4 and now.time() >= time(16, 50) and now.time() < time(17, 00):
        channel = bot.get_channel(1200438507315920918)
        if channel:
            message_debut = "Bon WE à tous.tes ! Et n'oubliez pas, le meilleur écogeste est "
            message_fin = fin_messages[index_message]
            await channel.send(message_debut + message_fin)

            index_dernier_message += 1

            if index_message >= len(fin_messages):
                index_message = 0

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
            if now.time() >= time(16, 40) and now.time() < time(16, 50):
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
