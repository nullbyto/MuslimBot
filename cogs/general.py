import discord
from discord.ext import commands
import json
from cogs.utils import get_prefix

def is_guild_owner(ctx):
    return ctx.author.id == ctx.guild.owner.id

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(is_guild_owner)
    async def prefix(self, ctx, prefix = None):
        if prefix is None:
            await ctx.send(f"Server's current prefix is: `{get_prefix(ctx)}`")

        else:    
            with open('prefixes.json', 'r') as file:
                prefixes = json.load(file)

            prefixes[str(ctx.guild.id)] = prefix

            with open('prefixes.json', 'w') as file:
                json.dump(prefixes, file, indent=4)

            await ctx.send(f"Server's Prefix changed to `{prefix}`")    


    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        roles = [role for role in member.roles]

        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

        embed.set_author(name=f'User Info - {member}')
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)

        embed.add_field(name='ID:', value=member.id)
        embed.add_field(name='Name in Guild:', value=member.display_name)

        embed.add_field(name='Created at:', value=member.created_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'))
        embed.add_field(name='Joined at:', value=member.joined_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'))

        embed.add_field(name=f'Roles: ({len(roles)})', value=" ".join([role.mention for role in roles]))
        embed.add_field(name='Top role:', value=member.top_role.mention)

        embed.add_field(name='Bot?', value=member.bot)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
