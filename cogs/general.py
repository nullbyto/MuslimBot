import discord
from discord.ext import commands
import json
from cogs.utils import get_prefix

def is_guild_owner(ctx):
    return ctx.author == ctx.Guild.owner

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="prefix")
    @commands.has_permissions(administrator = True)
    async def prefix(self, ctx, prefix: str = None):
        if prefix is None:
            await ctx.response.send_message(f"Server's current prefix is: `{get_prefix(ctx)}`")

        else:    
            with open('prefixes.json', 'r') as file:
                prefixes = json.load(file)

            prefixes[str(ctx.guild.id)] = prefix

            with open('prefixes.json', 'w') as file:
                json.dump(prefixes, file, indent=4)

            await ctx.response.send_message(f"Server's Prefix changed to `{prefix}`")    


    @discord.app_commands.command(name="userinfo", description="Displays info about the user mentioned")
    async def userinfo(self, ctx: discord.Interaction, member: discord.Member):
        member = ctx.message.author if not member else member
        roles = [role for role in member.roles]

        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

        embed.set_author(name=f'User Info - {member}')
        embed.set_thumbnail(url=member.avatar)
        embed.set_footer(text=f'Requested by {ctx.message.author}', icon_url=ctx.message.author.avatar)

        embed.add_field(name='ID:', value=member.id)
        embed.add_field(name='Name in Guild:', value=member.display_name)

        embed.add_field(name='Created at:', value=member.created_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'))
        embed.add_field(name='Joined at:', value=member.joined_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'))

        embed.add_field(name=f'Roles: ({len(roles)})', value=" ".join([role.mention for role in roles]))
        embed.add_field(name='Top role:', value=member.top_role.mention)

        embed.add_field(name='Bot?', value=member.bot)

        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
