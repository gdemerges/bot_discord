import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

initial_extensions = [
    'cogs.sauron_cog',
    'cogs.birthday_cog',
    'cogs.reminder_cog',
    'cogs.message_logger_cog'
]

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f'{bot.user.name} est connecté.')
    print('------')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Cette commande n'existe pas.")
    else:
        await ctx.send("Une erreur est survenue.")
        print(f"Erreur : {error}")

bot.run(DISCORD_TOKEN)
