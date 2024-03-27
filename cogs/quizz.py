import discord
from discord.ext import commands, tasks
import json
import random
from datetime import datetime, timedelta
import asyncio

class Quizz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('data/questions.json', 'r') as f:
            self.questions = json.load(f)

    @commands.command(name='quizz')
    async def quizz(self, ctx):
        question = random.choice(self.questions)
        choices = '\n'.join(question['choices'])
        await ctx.send(f"{question['question']}\n{choices}")

        def check(m):
            return m.channel == ctx.channel and m.content.lower() in [choice.lower() for choice in question['choices']]

        end_time = datetime.now() + timedelta(seconds=30)

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            if msg.content.lower() == question['answer'].lower():
                await ctx.send(f"{msg.author.mention}, tu as la bonne réponse! 🎉")
            else:
                await ctx.send(f"{msg.author.mention}, ce n'est pas la bonne réponse. 😢 La bonne réponse était : {question['answer']}.")
        except asyncio.TimeoutError:
            await ctx.send(f"Temps écoulé! La bonne réponse était : {question['answer']}.")

def setup(bot):
    bot.add_cog(Quizz(bot))
