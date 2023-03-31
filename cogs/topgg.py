import dbl
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
DBL = os.getenv('DBL_API')

class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = DBL
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)

    async def on_guild_post(self):
        print("Server count posted successfully!")


async def setup(bot):
    await bot.add_cog(TopGG(bot))
