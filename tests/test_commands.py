import unittest
from discord.ext import commands
from bot import bot

class TestCommands(unittest.TestCase):
    def setUp(self):
        self.bot = bot

    def test_ping_command(self):
        pass

if __name__ == '__main__':
    unittest.main()
