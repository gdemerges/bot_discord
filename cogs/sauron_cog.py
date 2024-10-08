import discord
from discord.ext import commands
import openai
import json
from datetime import datetime

class SauronCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('data/config.json') as config_file:
            config = json.load(config_file)

        self.OPENAI_API_KEY = config['OPENAI_API_KEY']
        openai.api_key = self.OPENAI_API_KEY

        self.calendar = self.load_calendar_from_json()

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

    def load_calendar_from_json(self):
        try:
            with open('calendar.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("Le fichier calendar.json est introuvable.")
            return {}

    def generate_calendar_summary(self):
        now = datetime.now()
        weeks = self.calendar.get('calendrier', {}).get('weeks', [])

        summary = "\n".join([
            f"Semaine {week['week']}: du {week['start_date']} au {week['end_date']} - {week['status']}"
            for week in weeks
            if datetime.strptime(week['start_date'], "%d/%m/%Y") >= now
        ])

        return summary if summary else "Aucun événement futur dans le calendrier."

    def generate_birthday_summary(self):
        today = datetime.now().strftime('%m-%d')  # Format: MM-DD
        upcoming_birthdays = []

        for date_str, users in self.birthdays.items():
            if date_str >= today:
                if isinstance(users[0], dict):
                    for user in users[0]['user_id']:
                        upcoming_birthdays.append(
                            f"Anniversaire de {user} le {date_str}: {users[0]['message']}"
                        )
                else:
                    for user_id in users:
                        upcoming_birthdays.append(
                            f"Anniversaire de l'utilisateur {user_id} le {date_str}"
                        )

        return "\n".join(upcoming_birthdays) if upcoming_birthdays else "Aucun anniversaire à venir."

    def get_openai_response(self, question, calendar_summary, birthday_summary):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es Sauron, Seigneur des Ténèbres. Réponds à toutes les questions avec le ton "
                        "imposant et autoritaire de Sauron, en utilisant des termes grandiloquents et archaïques. "
                        "Cependant, formate tes réponses pour être claires et lisibles, avec des paragraphes et des "
                        "sauts de ligne si nécessaire. Tu écriras des messages relativement brefs."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Voici le calendrier des événements à venir :\n{calendar_summary}\n\n"
                        f"Et voici les anniversaires à venir :\n{birthday_summary}\n\n"
                        f"Question : {question}"
                    )
                }
            ]
        )
        answer = response['choices'][0]['message']['content']
        return answer

    @commands.command(name='sauron')
    async def ask_question(self, ctx, *, question):
        print(f"Question reçue : {question}")

        calendar_summary = self.generate_calendar_summary()
        birthday_summary = self.generate_birthday_summary()

        response = self.get_openai_response(question, calendar_summary, birthday_summary)

        await ctx.send(response)

def setup(bot):
    bot.add_cog(SauronCog(bot))
