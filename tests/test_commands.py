import unittest
from unittest.mock import MagicMock
import asynctest
import discord
from discord.ext import commands
from unittest.mock import patch

from bot import bot

class TestPingCommand(asynctest.TestCase):
    def setUp(self):
        self.ctx = MagicMock()
        self.ctx.bot = bot
        self.ctx.send = asynctest.CoroutineMock()
        self.ctx.author = MagicMock()
        self.ctx.author.id = 1234567890

    async def test_ping_command(self):
        command = bot.get_command('ping')
        self.assertIsNotNone(command)

        await command.callback(self.ctx)

        self.ctx.send.assert_awaited_with('pong')

class TestSauronCommand(asynctest.TestCase):
    def setUp(self):
        self.ctx = MagicMock()
        self.ctx.bot = bot
        self.ctx.send = asynctest.CoroutineMock()
        self.ctx.author = MagicMock()
        self.ctx.author.id = 1234567890

    @patch('cogs.sauron_cog.openai.ChatCompletion.create')
    async def test_sauron_command(self, mock_openai):
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': 'Réponse simulée de Sauron.'
                    }
                }
            ]
        }
        mock_openai.return_value = mock_response

        command = bot.get_command('sauron')
        self.assertIsNotNone(command)

        question = 'Quelle est la prochaine réunion ?'
        await command.callback(self.ctx, question=question)

        self.ctx.send.assert_awaited_with('Réponse simulée de Sauron.')

if __name__ == '__main__':
    unittest.main()
