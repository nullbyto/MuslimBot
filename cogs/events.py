import discord
from discord.ext import commands
import json
from cogs.topgg import TopGG
from discord.utils import find
from cogs.utils import get_prefix

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
    async def on_guild_join(self, guild):
        # Join guild message
        em = discord.Embed(title='\U0001F91D Hello! Im MuslimBot!', colour=0x1f8b4c, description="Thanks for adding me to your server."
                                                                                            " Type `+help` to get the help menu!\n"
                                                                                            "*__My default prefix is:__* `+`\n\n**Support: join https://discord.gg/ar9ksAy**")
        em.set_footer(text="Have a nice day!")
        general = find(lambda x: x.name == 'general',  guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
            await general.send(embed=em)
        else: 
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(embed=em)
                break

        # Post guild count to TopGG
        await TopGG.dblpy.post_guild_count()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as file:
            prefixes = json.load(file)

        prefixes.pop(str(guild.id))

        with open('prefixes.json', 'w') as file:
            json.dump(prefixes, file, indent=4)
        
        await TopGG.dblpy.post_guild_count()
    
    



def setup(bot):
    bot.add_cog(Events(bot))