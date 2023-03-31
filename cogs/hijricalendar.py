import discord
from datetime import datetime, date
from discord.ext import commands, tasks
from hijri_converter import convert
from cogs.utils import convert_to_arabic_number, make_embed

ICON = 'https://icons.iconarchive.com/icons/paomedia/small-n-flat/512/calendar-icon.png'
DATE_INVALID = '**Invalid date**. Dates must be in this format: DD-MM-YYYY.\n\n**Example**: 01-12-2020'
GREGORIAN_DATE_OUT_OF_RANGE = '**Sorry, this year is out of range**. The minimum year is 1924; the maximum year is 2077.'
HIJRI_DATE_OUT_OF_RANGE = '**Sorry, this year is out of range**. The minimum year is 1343; the maximum year is 1500.'


class HijriCalendar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.update_hijri_date.start()

    @staticmethod
    def get_current_hijri():
        hijri = convert.Gregorian.today().to_hijri()
        return f'{hijri.day} {hijri.month_name()} {hijri.year} {hijri.notation(language="en")}'

    @staticmethod
    def get_hijri(gregorian_date: date = None, status: bool = False):
        hijri = convert.Gregorian.fromdate(gregorian_date).to_hijri()
        return f'{gregorian_date.strftime("%d %B %Y")} is **{hijri.month_name()} {hijri.day}, {hijri.year} AH**.' \
                      f'\n\nالتاريخ الهجري: __**' \
                      f'{hijri.day_name(language="ar")} {convert_to_arabic_number(str(hijri.day))} ' \
                      f'{hijri.month_name(language="ar")} {convert_to_arabic_number(str(hijri.year))} ' \
                      f'{hijri.notation(language="ar")}**__'

    @staticmethod
    def get_gregorian(hijri_date):
        gregorian = convert.Hijri(hijri_date.year, hijri_date.month, hijri_date.day).to_gregorian()
        return f'{hijri_date.strftime("%d-%m-%Y")} AH is **{gregorian.strftime("%d %B %Y")}**'

    @discord.app_commands.command(name='hijridate', description="Display todays hijri date")
    async def hijridate(self, ctx: discord.Interaction):
        hijri = self.get_current_hijri()
        today = date.today()
        em = make_embed(colour=0x72bcd4, author="Today's Hijri Date", description=hijri + f'\n{today}', author_icon=ICON)
        await ctx.response.send_message(embed=em)

    @discord.app_commands.command(name='converttohijri', description="Convert gregorian date to hijri date")
    async def converttohijri(self, ctx: discord.Integration, gregorian_date: str):
        try:
            gregorian_date = datetime.strptime(gregorian_date, "%d-%m-%Y").date()
        except:
            return await ctx.response.send_message(DATE_INVALID)

        try:
            hijri = self.get_hijri(gregorian_date=gregorian_date)
        except OverflowError:
            return await ctx.response.send_message(GREGORIAN_DATE_OUT_OF_RANGE)

        em = make_embed(colour=0x72bcd4, author="Gregorian → Hijri Conversion", description=hijri, author_icon=ICON)
        await ctx.response.send_message(embed=em)

    @discord.app_commands.command(name='convertfromhijri', description="Convert hijri date to gregorian")
    async def convertfromhijri(self, ctx: discord.Integration, hijri_date: str):
        try:
            hijri_date = datetime.strptime(hijri_date, "%d-%m-%Y").date()
        except:
            return await ctx.response.send_message(DATE_INVALID)

        try:
            hijri = self.get_gregorian(hijri_date=hijri_date)
        except OverflowError:
            return await ctx.response.send_message(HIJRI_DATE_OUT_OF_RANGE)

        em = make_embed(colour=0x72bcd4, author="Hijri → Gregorian Conversion", description=hijri, author_icon=ICON)
        await ctx.response.send_message(embed=em)

    ## Bot Activity
    @tasks.loop(hours=1)
    async def update_hijri_date(self):
        hijri = self.get_current_hijri()
        activity = discord.Activity(type= discord.ActivityType.listening, name=f"Quran | /help | {hijri}")
        await self.bot.change_presence(activity=activity)


# Register as cog
async def setup(bot):
    await bot.add_cog(HijriCalendar(bot))
