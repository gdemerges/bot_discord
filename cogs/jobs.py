import discord
from discord.ext import commands
import csv

class Jobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='post_jobs')
    async def post_jobs(self, ctx):

        channel = ctx.channel

        try:
            with open('data/jobs.csv', mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    job_title = row['title']
                    job_link = row['link']
                    job_description = row.get('description', 'Pas de description disponible.')

                    embed = discord.Embed(title=job_title, url=job_link, description=job_description, color=0x00ff00)
                    embed.add_field(name="Plus d'infos", value=job_link, inline=False)
                    await channel.send(embed=embed)

        except FileNotFoundError:
            await ctx.send("Le fichier des offres d'emploi n'a pas été trouvé.")
        except Exception as e:
            await ctx.send(f"Une erreur est survenue lors de la publication des offres d'emploi : {str(e)}")

def setup(bot):
    bot.add_cog(Jobs(bot))
