import aiohttp
import discord
from discord.ext import commands
from fuzzywuzzy import process
from cogs.utils import get_prefix

everyayah_reciters = {
    'abdulrahman al-sudais': 'Abdurrahmaan_As-Sudais_192kbps',
    'mishary al-afasy': 'Alafasy_128kbps',
    'abdullah basfar': 'Abdullah_Basfar_192kbps',
    'abu bakr al-shatri': 'Abu_Bakr_Ash-Shaatree_128kbps',
    'abdulbaset abdulsamad': 'Abdul_Basit_Murattal_192kbps',
    'ahmed al-ajmy': 'Ahmed_ibn_Ali_al-Ajamy_128kbps_ketaballah.net',
    'hani al-rifai': 'Hani_Rifai_192kbps',
    'ali al-hudhaify': 'Hudhaify_128kbps',
    'maher al-muaiqly': 'MaherAlMuaiqly128kbps',
    'muhammad al-minshawi': 'Minshawy_Mujawwad_192kbps',
    'muhammad jibreel': 'Muhammad_Jibreel_128kbps',
    'muhsin al-qasim': 'Muhsin_Al_Qasim_192kbps',
    'muhammad ayyub': 'Muhammad_Ayyoub_128kbps',
    'saud al-shuraym': 'Saood_ash-Shuraym_128kbps',
    'abdullah matroud': 'Abdullah_Matroud_128kbps',
    'mahmoud khalil al-hussary': 'Husary_128kbps',
    'muhammad al-tablawi': 'Mohammad_al_Tablaway_128kbps'
}


'''
Creates a list of reciter objects using mp3quran.net's API.
We fetch the list anew every time because the API is frequently updated with new reciters and information.
'''


async def get_mp3quran_reciters():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://mp3quran.net/api/_english.php') as r:
            try:
                data = await r.json()
            # If the JSON response is malformed - which occasionally occurs - then we select HTML as the content type.
            except aiohttp.ContentTypeError:
                data = await r.json(content_type='text/html')
        raw_reciters = data['reciters']

    # Filter out reciters with recitations of < 90 surahs.
    raw_reciters = [reciter for reciter in raw_reciters if int(reciter['count']) >= 90]

    # Create reciter object from each reciter and add it to the reciters list
    reciters = []
    for reciter in raw_reciters:
        name = reciter['name']
        riwayah = reciter['rewaya']
        server = reciter['Server']
        reciters.append(Reciter(name, riwayah, server))

    return reciters


async def get_mp3quran_reciter(name):
    reciter_list = await get_mp3quran_reciters()
    for reciter in reciter_list:
        if reciter.name.lower() == name:
            return reciter
    return None


class Reciter:
    def __init__(self, name, riwayah, server):
        self.name = name
        self.riwayah = riwayah
        self.server = server


class Reciters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

    '''
    Use fuzzy search to allow users to search the mp3quran.net reciter list.
    '''
    @commands.command()
    async def search(self, ctx, search_term: str):
        reciter_list = await get_mp3quran_reciters()
        reciters = [reciter.name for reciter in reciter_list]

        results = process.extractWithoutOrder(search_term, reciters, score_cutoff=65)
        formatted_results = ''
        i = 0
        for result in results:
            i += 1
            formatted_result = result[0].replace('-', ' - ').title().replace(' - ', '-')
            formatted_results = formatted_results + f'\n{i}. {formatted_result}'
        if formatted_results == '':
            await ctx.send('**No results.**')
        else:
            em = discord.Embed(title='\U0001F50D Search Results', colour=0x006400, description=formatted_results)
            await ctx.send(embed=em)

    @commands.command(name='reciters')
    async def reciters(self, ctx):
        prefix = get_prefix(ctx)

        everyayah_reciter_list = ''
        for key in everyayah_reciters.keys():
            everyayah_reciter_list = everyayah_reciter_list + f'{key}, '
        mp3quran_reciters = len(await get_mp3quran_reciters())
        em = discord.Embed(description=f'\n\n**`{prefix}play surah` Reciters**\n\nAvailable reciters: '
                                       f'**{mp3quran_reciters}\n\n'
                                       f'[Click here for the full surah reciter list]'
                                       f'(https://github.com/nullbyto/MuslimBot/blob/master/Reciters.md)**\n\n'
                                       f'To search this list, type `{prefix}search [reciter name]`, e.g. '
                                       f'`{prefix}search dossary`\n'
                                       f'\n\n**`{prefix}play ayah` and `{prefix}play page` Reciters**'
                                       f'\n\nAvailable reciters: **{len(everyayah_reciters.keys())}**\n\n'
                                       f'List: ```{everyayah_reciter_list}```', colour=0x006400, title="Reciters")
        em.set_footer(text="Use the ayah/page reciter list when playing individual ayahs and pages. Use the surah recit"
                           "er list when playing surahs.")
        await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(Reciters(bot))
