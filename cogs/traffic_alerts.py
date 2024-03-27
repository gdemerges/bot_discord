from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
import aiohttp
import discord

class TrafficAlerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_for_alerts.start()

    @tasks.loop(minutes=1)
    async def check_for_alerts(self):
        now = datetime.now()
        if now.weekday() < 5 and now.time() >= time(8, 0) and now.time() < time(9, 0):
            await self.fetch_and_send_alerts()

    async def fetch_and_send_alerts(self):
        url = 'https://data.grandlyon.com/fr/datapusher/ws/rdata/tcl_sytral.tclalertetrafic_2/all.json'
        webhook_url = 'https://discord.com/api/webhooks/1219376934572523561/68iUsrDxMrIsreP5ZHfySA0viFhoSnLU0fZ4jzwe1mOf9HnUpqde0IFKvD3qOMxym-2a'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    alerts = data['values']
                    filtered_alerts = [alert for alert in alerts if alert['ligne_cli'] in ['B', 'T3']]
                    for alert in filtered_alerts:
                        await self.send_alert_to_discord(session, webhook_url, alert)

    async def send_alert_to_discord(self, session, webhook_url, alert):
        message_content = f"Alerte Trafic : {alert['titre']} - {alert['message']}"
        payload = {"content": message_content}
        headers = {"Content-Type": "application/json"}
        async with session.post(webhook_url, json=payload, headers=headers) as response:
            if response.status != 200:
                print(f"Erreur lors de l'envoi du message: {response.status}")

    @check_for_alerts.before_loop
    async def before_check_for_alerts(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        if now.time() < time(8, 0):
            await discord.utils.sleep_until(datetime.combine(now.date(), time(8, 0)))
        elif now.time() >= time(9, 0):
            tomorrow = now.date() + timedelta(days=1)
            await discord.utils.sleep_until(datetime.combine(tomorrow, time(8, 0)))

def setup(bot):
    bot.add_cog(TrafficAlerts(bot))
