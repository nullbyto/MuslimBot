import discord
from discord.ext import commands
import os, sys, platform, time, datetime
import psutil


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @discord.app_commands.command()
    @commands.is_owner()
    async def botinfo(self, ctx: discord.Interaction):
        current_time = time.time()
        channels = len(set(self.bot.get_all_channels()))
        difference = int(round(current_time - self.start_time))
        uptime = str(datetime.timedelta(seconds=difference))
        embed = discord.Embed(title='Bot Info:', description=f"Guilds Amount: {len(self.bot.guilds)}\n"
                                                             f"User Amount: {len(self.bot.users)}\n"
                                                             f"Emoji Amount: {len(self.bot.emojis)}\n"
                                                             f"Commands Amount: {len(self.bot.commands)}\n"
                                                             f"Channels Amount: {channels}\n"
                                                             f"Cogs Amount: {len(self.bot.cogs)}\n"
                                                             f"Voice Connections: {len(self.bot.voice_clients)}\n"
                                                             f"Operating System: {platform.system()}\n"
                                                             f"Python Version: {sys.version}\n"
                                                             f"CPU Usage: {psutil.cpu_percent()}%\n"
                                                             f"RAM Usage: {psutil.virtual_memory().percent}%\n"
                                                             f"Available RAM: {round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)}%\n"
                                                             f"Ping: {round(self.bot.latency * 1000)}ms\n"
                                                             f"Uptime: {uptime}\n")
        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))
