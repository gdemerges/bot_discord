import discord
from discord.ext import commands
import json

def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    for extension in ['cogs.birthdays', 'cogs.jobs', 'cogs.quizz',
                      'cogs.messages_vendredi', 'cogs.menage',
                      'cogs.traffic_alerts', 'cogs.pole_emploi']:
        bot.load_extension(extension)

    with open('data/config.json') as config_file:
        config = json.load(config_file)
        bot_token = config.get('token')

    if bot_token is None:
        raise ValueError("Le token du bot n'est pas défini dans config.json.")
    bot.run(bot_token)

if __name__ == '__main__':
    main()
