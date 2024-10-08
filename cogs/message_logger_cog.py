import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import asyncio

class MessageLoggerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.first_run = True
        self.excluded_channels = [1206906418226266122, 1249671264520376320]  # IDs des canaux à exclure
        self.auto_get_all_messages.start()

    @tasks.loop(hours=24)
    async def auto_get_all_messages(self):
        all_messages = []

        # Si c'est la première exécution, récupérer tout l'historique des messages
        if self.first_run:
            print("Première exécution - récupération de tout l'historique des messages.")
            self.first_run = False
            last_24_hours = None  # Aucune limite de temps, récupérer tout
        else:
            last_24_hours = datetime.utcnow() - timedelta(hours=24)  # Récupérer les messages des dernières 24 heures

        for channel in self.bot.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                if channel.id in self.excluded_channels:
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

        await self.save_messages_to_json(all_messages)
        print(f'{len(all_messages)} messages ont été sauvegardés dans messages.json')

    @auto_get_all_messages.before_loop
    async def before_auto_get_all_messages(self):
        await self.bot.wait_until_ready()

    async def save_messages_to_json(self, messages, file_name="messages.json"):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        for message in messages:
            reactions_data = await self.get_reactions_for_message(message)

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

    async def get_reactions_for_message(self, message):
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

    @commands.command(name='get_all_messages')
    async def get_all_messages_command(self, ctx, limit: int = 100):
        """Commande pour récupérer manuellement les messages."""
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

        await self.save_messages_to_json(all_messages)
        await ctx.send(f'{len(all_messages)} messages de tous les canaux ont été sauvegardés dans messages.json.')

def setup(bot):
    bot.add_cog(MessageLoggerCog(bot))
