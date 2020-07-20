import discord
from discord.ext import commands
import json

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            await ctx.send('**This command is disabled!**')

        if isinstance(error, commands.CommandNotFound):
            await ctx.send('**This command does not exist!**')
        
        raise error

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as file:
            prefixes = json.load(file)

        prefixes.pop(str(guild.id))

        with open('prefixes.json', 'w') as file:
            json.dump(prefixes, file, indent=4)



def setup(bot):
    bot.add_cog(Events(bot))