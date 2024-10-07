import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time, date
import random
import aiohttp
import json
import asyncio
import csv
import openai

with open('data/config.json') as config_file:
    config = json.load(config_file)

DISCORD_TOKEN = config['DISCORD_TOKEN']
OPENAI_API_KEY = config['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

morning_message_sent = False
afternoon_message_sent = False
first_run = True

birthdays = {
    '01-09': ['714403161346932823'], # Alison
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

excluded_channels = [1206906418226266122, 1249671264520376320]

user_reactions = {
    1192414156243091609: '❤️',
    714403161346932823: '💶',
    861540082262605826: '🫡',
    294065690162364416: '👎',
    708311679838060555: '⏱️',
    282150973810540566: '🔥',
    1188435883947462656: '🍬',
    148188913817616384: '💪',
    1043293367368425503: '💯',
    1088403301994860544: '🥐'
}

target_bot_id = 159985870458322944
target_user_id = 708311679838060555
lol_user_id = 294065690162364416

def load_calendar_from_json():
    with open('calendar.json', 'r') as file:
        return json.load(file)

def generate_calendar_summary(calendar):
    now = datetime.now()

    weeks = calendar.get('calendrier', {}).get('weeks', [])

    summary = "\n".join([f"Semaine {week['week']}: du {week['start_date']} au {week['end_date']} - {week['status']}"
                         for week in weeks if datetime.strptime(week['start_date'], "%d/%m/%Y") >= now])

    return summary if summary else "Aucun événement futur dans le calendrier."

def generate_birthday_summary():
    today = datetime.now().strftime('%m-%d')  # Format: MM-DD
    upcoming_birthdays = []

    for date, users in birthdays.items():
        if date >= today:
            if isinstance(users[0], dict):
                for user in users[0]['user_id']:
                    upcoming_birthdays.append(f"Anniversaire de {user} le {date}: {users[0]['message']}")
            else:
                for user_id in users:
                    upcoming_birthdays.append(f"Anniversaire de l'utilisateur {user_id} le {date}")

    return "\n".join(upcoming_birthdays) if upcoming_birthdays else "Aucun anniversaire à venir."


def get_openai_response(question, calendar_summary, birthday_summary):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es Sauron, Seigneur des Ténèbres. Réponds à toutes les questions avec le ton imposant et autoritaire de Sauron, en utilisant des termes grandiloquents et archaïques. Cependant, formate tes réponses pour être claires et lisibles, avec des paragraphes et des sauts de ligne si nécessaire. Tu écriras des messages relativement bref."},
            {"role": "user", "content": f"Voici le calendrier des événements à venir :\n{calendar_summary}\n\nEt voici les anniversaires à venir :\n{birthday_summary}\n\nQuestion : {question}"}
        ]
    )
    answer = response['choices'][0]['message']['content']
    return answer

@bot.command(name='sauron')
async def ask_question(ctx, *, question):
    print(f"Question reçue : {question}")

    calendar = load_calendar_from_json()

    calendar_summary = generate_calendar_summary(calendar)

    birthday_summary = generate_birthday_summary()

    response = get_openai_response(question, calendar_summary, birthday_summary)

    await ctx.send(response)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('pong')

@bot.event
async def on_ready():
    print(f'{bot.user.name} a démarré.')
    #mention_users_group.start()
    #message_vendredi.start()
    check_birthdays.start()
    monthly_reminder.start()
    auto_get_all_messages.start()
    #send_evening_message.start()

@bot.event
async def on_message(message):
    # Ne pas répondre à ses propres messages
    if message.author == bot.user:
        return

    # Réaction automatique si l'auteur est dans `user_reactions`
    if message.author.id in user_reactions:
        reaction = user_reactions[message.author.id]
        await message.add_reaction(reaction)

    # Vérifier si le message provient du bot cible
    if message.author.id == target_bot_id:
        response = get_openai_response(message.content)
        await message.reply(response)

    # Vérifier si l'auteur du message est l'utilisateur à qui envoyer "double lol"
    elif message.author.id == lol_user_id:
        await message.reply("double lol")

    # Toujours traiter les commandes après avoir réagi
    await bot.process_commands(message)

"""
@tasks.loop(minutes=1)
async def send_evening_message():
    now = datetime.now()
    print(f"Vérification de l'heure: {now}")
    if now.hour == 10 and now.minute == 30:
        channel = bot.get_channel(1200438507315920918)
        message = ("Mortels, Mercredi prochain, nul ne manquera à l'appel. Votre présence est requise, et aucune excuse ne sera tolérée. "
                       "Ceux qui oseraient défier cet ordre seront confrontés à <@1192414156243091609>, et sachez que sa sanction sera aussi implacable que "
                       "les flammes de la Montagne du Destin. Ne tentez pas le sort, ou vous subirez les conséquences. Vous êtes prévenus.")
        await channel.send(message)
        print("Message envoyé")
    else:
        print("Channel non trouvé")
"""

async def get_reactions_for_message(message):
    reactions_data = []
    for reaction in message.reactions:
        users = []
        async for user in reaction.users():
            users.append({
                "username": str(user),
                "display_name": user.display_name,
                "user_id": user.id
            })
        reactions_data.append({
            "emoji": str(reaction.emoji),
            "count": reaction.count,
            "users": users
        })
    return reactions_data


async def save_messages_to_json(messages, file_name="messages.json"):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    for message in messages:
        reactions_data = await get_reactions_for_message(message)

        message_data = {
            "author": str(message.author),
            "display_name": message.author.display_name,
            "author_id": message.author.id,
            "content": message.content,
            "channel": str(message.channel),
            "timestamp": str(message.created_at),
            "reactions": reactions_data
        }
        data.append(message_data)

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@tasks.loop(hours=24)
async def auto_get_all_messages():
    global first_run
    all_messages = []

    # Si c'est la première exécution, récupérer tout l'historique des messages
    if first_run:
        print("Première exécution - récupération de tout l'historique des messages.")
        first_run = False
        last_24_hours = None  # Aucune limite de temps, récupérer tout
    else:
        last_24_hours = datetime.utcnow() - timedelta(hours=24)  # Récupérer les messages des dernières 24 heures

    for channel in bot.get_all_channels():
        if isinstance(channel, discord.TextChannel):
            if channel.id in excluded_channels:
                print(f"Canal {channel.name} exclu.")
                continue

            if channel.permissions_for(channel.guild.me).read_message_history:
                try:
                    async for message in channel.history(after=last_24_hours):
                        all_messages.append(message)
                except discord.HTTPException as e:
                    print(f"Erreur HTTP lors de la récupération des messages dans le canal {channel.name}: {e}")
                except discord.Forbidden as e:
                    print(f"Accès refusé au canal {channel.name}: {e}")

    await save_messages_to_json(all_messages)
    print(f'{len(all_messages)} messages ont été sauvegardés dans messages.json')

@auto_get_all_messages.before_loop
async def before_auto_get_all_messages():
    await bot.wait_until_ready()

# Commande pour manuellement récupérer les messages de tous les canaux texte
@bot.command()
async def get_all_messages(ctx, limit: int = 100):
    all_messages = []

    for channel in ctx.guild.text_channels:
        if channel.permissions_for(ctx.guild.me).read_message_history:
            try:
                async for message in channel.history(limit=limit):
                    all_messages.append(message)
            except discord.HTTPException as e:
                await ctx.send(f"Erreur lors de la récupération des messages dans le canal {channel.name}: {e}")
            except discord.Forbidden as e:
                await ctx.send(f"Accès refusé au canal {channel.name}: {e}")

    save_messages_to_json(all_messages)
    await ctx.send(f'{len(all_messages)} messages de tous les canaux ont été sauvegardés dans messages.json.')

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

user_groups = [
    [294065690162364416, 509295845762400256, 998493093651296296, 428391859853852684],
    [708311679838060555, 1188435883947462656, 148188913817616384, 1043293367368425503],
    [1176093354329653298, 886153619043418124, 759914731468357702],
    [861540082262605826, 714403161346932823, 1192414156243091609]
]

current_group_index = 3

jeudis_exclus = [
    date(2024, 4, 18),
    date(2024, 5, 9),
    date(2024, 6, 13),
    date(2024, 8, 15),
    date(2024, 8, 22),
]

@tasks.loop(minutes=10)
async def mention_users_group():
    global current_group_index
    now = datetime.now()
    today = datetime.now().date()
    if now.weekday() == 3 and today not in jeudis_exclus:
        channel = bot.get_channel(1200438507315920918)
        if channel:
            if now.time() >= time(16, 20) and now.time() < time(16, 30):
                mentions = " ".join([f'<@{user_id}>' for user_id in user_groups[current_group_index]])
                await channel.send(
                    f"{mentions}, unissez vos efforts pour transformer nos espaces en havres de propreté et d'ordre."
                )
                current_group_index = (current_group_index + 1) % len(user_groups)


@mention_users_group.before_loop
async def before_mention_users_group():
    await bot.wait_until_ready()
    now = datetime.now()
    if now.weekday() < 3 or (now.weekday() == 3 and now.time() > time(17, 0)):
        days_until_thursday = (3 - now.weekday()) % 7
        next_run = now + timedelta(days=days_until_thursday)
        next_run_time = datetime.combine(next_run, time(15, 0))
        await discord.utils.sleep_until(next_run_time)
    elif now.weekday() == 3 and now.time() < time(17, 0):
        await discord.utils.sleep_until(datetime.combine(now, time(15, 0)))

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

bot.run(DISCORD_TOKEN)
