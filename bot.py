# Main bot file
import os, time
import discord
import datetime
import json
from dotenv import load_dotenv
from discord.ext import commands

__version__='1.0.0'

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

DEFAULT_PREFIX = '+'

description = "A Discord bot with Quran player and Islamic utilities."

cog_list = ['topgg', 'reciters', 'audio', 'admin', 'events', 'general', 'quran', 'hadith', 'hijricalendar',
            'prayertimes', 'quran-morphology', 'tafsir', 'tafsir-english', 'mushaf', 'dua', 'help']


def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)

    with open('prefixes.json', 'r') as file:
        prefixes = json.load(file)
    
    if str(message.guild.id) not in prefixes:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)

    prefix = prefixes[str(message.guild.id)]
    return commands.when_mentioned_or(prefix)(bot, message)

bot = commands.AutoShardedBot(command_prefix=get_prefix, description=description, intents=discord.Intents.default())
bot.remove_command('help')

@bot.event
async def on_ready():
    for cog in cog_list:
        cog = f'cogs.{cog}'
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f'Couldn\'t load cog {cog}')
            raise e

    print('------------------------')
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id}) on {len(bot.guilds)} servers')
    print(f'Discord Version: {discord.__version__}')
    print(f'Bot Version: {__version__}')
    bot.AppInfo = await bot.application_info()
    print(f'Owner: {bot.AppInfo.owner}')
    print('------Bot is Ready------')


@bot.command()
@commands.is_owner()
async def reload(ctx, cog=None):
    if cog == None:
        try:
            for item in cog_list:    
                bot.unload_extension(f'cogs.{item}')
                bot.load_extension(f'cogs.{item}')
            await ctx.send(f'All cogs got reloaded.')
            print(f'----------\nAll cogs got reloaded.\n----------')
        except Exception as e:
            await ctx.send(f'Cogs can not be loaded!')
            raise e

    else:    
        try:
            bot.unload_extension(f'cogs.{cog}')
            bot.load_extension(f'cogs.{cog}')
            await ctx.send(f'`{cog}` got reloaded.')
            print(f'----------\n`{cog}` got reloaded.\n----------')
        except Exception as e:
            if cog in cog_list:
                await ctx.send(f'`{cog}` can not be loaded! **Check the Log**')
            else:
                await ctx.send(f'`{cog}` is not a valid cog!')
            raise e

bot.run(TOKEN)
