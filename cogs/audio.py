import discord
import asyncio
import youtube_dl
import aiohttp
from discord.ext.commands import MissingRequiredArgument
from discord.ext import commands
from fuzzywuzzy import process, fuzz
from cogs.utils import get_prefix

from cogs.reciters import everyayah_reciters, get_mp3quran_reciter

RECITATION_NOT_FOUND = "**Could not find a recitation for the surah by this reciter.** Try a different surah."
RECITER_NOT_FOUND = "**Couldn't find reciter!** Type `{}reciters` for a list of available reciters."
SURAH_NOT_FOUND = "**Surah not found** Use the surah's name or number. Examples: \n\n`{}play surah" \
                  " al-fatihah`\n\n`{}play surah 1`"
PAGE_NOT_FOUND = "**Sorry, the page must be between 1 and 604.**"
DISCONNECTED = "**Successfully disconnected.**"
INVALID_VOLUME = "**The volume must be between 0 and 100.**"
INVALID_VERSE = "**Please provide a verse.** For example, 1:2 is Surah al-Fatiha, ayah 2."
NON_EXISTENT_VERSE = "**There are only {} verses in this surah.**"
ALREADY_PLAYING = "**Already playing**. To stop playing, type `{}stop`."
NOT_PLAYING = "The bot is not playing."
WRONG_COMMAND = "You typed the command wrongly. Type `{}help play` for help."

players = {}


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}


ffmpeg_options = {
    'options': '-vn'
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


async def get_surah_names():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://api.quran.com/api/v3/chapters') as r:
            data = await r.json()
        surahs = data['chapters']

    surah_names = {}
    for surah in surahs:
        surah_names[surah['name_simple'].lower()] = surah['id']

    return surah_names


async def get_surah_id_from_name(surah_name):
    surah_names = await get_surah_names()
    surah_id = surah_names[surah_name]
    return surah_id


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()

        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        filename = data['url'] if stream else ytdl.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.info_url = 'http://api.quran.com:3000/api/v3/chapters/{}'
        self.reciter_info_url = 'http://mp3quran.net/api/_english.php'
        self.makkah_url = 'http://66.226.10.51:8000/SaudiTVArabic?dl=1'
        self.quranradio_url = 'http://live.mp3quran.net:8006/stream?type=http&nocache=29554'
        self.page_url = 'https://everyayah.com/data/{}/PageMp3s/Page{}.mp3'
        self.ayah_url = 'https://everyayah.com/data/{}/{}.mp3'
        self.mushaf_url = 'https://www.searchtruth.org/quran/images1/{}.jpg'
        self.radio3_url = 'http://212.32.255.144:9300/stream.mp3'

    def make_ayah_url(self, surah, ayah, reciter):
        url_surah = str(surah).zfill(3)
        url_ayah = str(ayah).zfill(3)

        try: url_reciter = everyayah_reciters[reciter]
        except KeyError: return None

        url_ref = f'{url_surah}{url_ayah}'
        url = self.ayah_url.format(url_reciter, url_ref)

        return url


    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(':x: **Error**: *{}*'.format(str(error)))
        print(error)


    def make_page_url(self, page, reciter):
        try: url_reciter = everyayah_reciters[reciter]
        except KeyError: return None

        url_page = str(page).zfill(3)
        url = self.page_url.format(url_reciter, url_page)

        return url, url_page

    async def get_surah_info(self, surah):
        async with self.session.get(self.info_url.format(surah)) as r:
            data = await r.json()
            name = data['chapter']['name_simple']
            arabic_name = data['chapter']['name_arabic']

        return name, arabic_name

    @staticmethod
    def get_play_file(url, surah):
        file_name = str(surah).zfill(3) + '.mp3'
        file_url = f'{url}/{file_name}'
        return file_url

    async def get_verse_count(self, surah):
        async with self.session.get(self.info_url.format(surah)) as r:
            data = await r.json()
            verses_count = data['chapter']['verses_count']
            verses_count = int(verses_count)
        return verses_count

    def make_embed(self, title, description, footer, colour, image=None):
        em = discord.Embed(title=title, colour=colour, description=description)
        em.set_footer(text=footer)
        if image is not None:
            em.set_image(url=image)
        return em


    async def create_player(self, ctx, url):
        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        except:
            return await ctx.send(RECITATION_NOT_FOUND)

        self.voice_states[ctx.guild.id] = player

        try:
            ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect()
                                                                                           , self.bot.loop))
        except discord.errors.ClientException as e:
            return print(e)

    @commands.group()
    async def play(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('**Invalid arguments**. For help, type `{}help play`.'.format(get_prefix(ctx)))

    @play.command()
    async def surah(self, ctx, surah, *, reciter: str = 'Mishary Alafasi'):

        # if ctx.voice_client.is_playing():
        #     return await ctx.send(ALREADY_PLAYING.format(get_prefix(ctx)))

        try:
            surah = int(surah)

        except ValueError:
            try:
                surah = await get_surah_id_from_name(surah.lower())
            # We try to suggest a correction if an invalid surah name string is given.
            except KeyError:
                surah_names = await get_surah_names()
                result = process.extract(surah, surah_names.keys(), scorer=fuzz.partial_ratio, limit=1)
                if result is not None:
                    await ctx.send(f'Could not find {surah}, so the closest match - *{result[0][0]}* - will be used.')
                    surah = await get_surah_id_from_name(result[0][0].lower())
                else:
                    return await ctx.send(SURAH_NOT_FOUND.format(get_prefix(ctx)))

        reciter = await get_mp3quran_reciter(reciter.lower())

        if reciter is None:
            return await ctx.send(RECITER_NOT_FOUND.format(get_prefix(ctx)))

        if not 0 < surah <= 114:
            return await ctx.send(SURAH_NOT_FOUND.format(get_prefix(ctx)))

        file_url = self.get_play_file(reciter.server, surah)

        await self.create_player(ctx, file_url)

        transliterated_surah, arabic_surah = await self.get_surah_info(surah)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}).\nReciter: **{reciter.name}**.' \
                      f'\nRiwayah: {reciter.riwayah}'

        em = self.make_embed("\U000025B6 Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400)
        await ctx.send(embed=em)

    @play.command()
    async def ayah(self, ctx, ref: str, *, reciter: str = 'mishary al-afasy'):

        # if ctx.voice_client.is_playing():
        #     return await ctx.send(ALREADY_PLAYING.format(get_prefix(ctx)))

        try:
            surah, ayah = ref.split(':')
            surah = int(surah)
            ayah = int(ayah)

        except:
            return await ctx.send("Invalid arguments. Commands: `{}play ayah [surah]:[ayah] [reciter]`."
                                  "\n\nExample: `{}play ayah 2:255 abdul rahman al-sudais`.".format(get_prefix(ctx)))

        reciter = reciter.lower()

        if reciter is None:
            return await ctx.send(RECITER_NOT_FOUND.format(get_prefix(ctx)))

        if not 0 < surah <= 114:
            return await ctx.send(SURAH_NOT_FOUND.format(get_prefix(ctx)))

        verse_count = await self.get_verse_count(surah)
        if ayah > verse_count:
            return await ctx.send(NON_EXISTENT_VERSE.format(verse_count))

        url = self.make_ayah_url(surah, ayah, reciter)
        try: player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        except:
            return await ctx.send(RECITATION_NOT_FOUND)

        await self.create_player(ctx, url)

        reciter = reciter.replace('-', ' - ').title().replace(' - ', '-')
        transliterated_surah, arabic_surah = await self.get_surah_info(surah)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}), Ayah {ayah}. ' \
                      f'\nReciter: **{reciter}**.'

        em = self.make_embed("\U000025B6 Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400,
                             f'https://everyayah.com/data/QuranText_jpg/{surah}_{ayah}.jpg')
        await ctx.send(embed=em)

    @play.command()
    async def page(self, ctx, page: int, *, reciter: str = 'mishary al-afasy'):

        if ctx.voice_client.is_playing():
            return await ctx.send(ALREADY_PLAYING.format(get_prefix(ctx)))

        try:
            page = int(page)
        except:
            return await ctx.send("Invalid arguments. Commands: `{}page [page]:[ayah] [reciter]`."
                                  "\n\nExample: `{}ayah 604 abdul rahman al-sudais`.".format(get_prefix(ctx)))

        reciter = reciter.lower()
        readable_reciter = reciter.replace('-', ' - ').title().replace(' - ', '-')

        if reciter not in everyayah_reciters:
            return await ctx.send(RECITER_NOT_FOUND.format(get_prefix(ctx)))

        if not 0 < page <= 604:
            return await ctx.send(PAGE_NOT_FOUND)

        url, url_page = self.make_page_url(page, reciter)

        await self.create_player(ctx, url)

        description = f'Playing **Page {page}.**\nReciter: **{readable_reciter}**.'

        em = self.make_embed("\U000025B6 Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400,
                             f'https://www.searchtruth.org/quran/images2/large/page-{url_page}.jpeg')
        await ctx.send(embed=em)

    @surah.error
    @ayah.error
    @page.error
    async def error_handler(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send(WRONG_COMMAND.format(get_prefix(ctx)))


    @commands.command()
    async def live(self, ctx, *, link: str = 'makkah'):

        if ctx.voice_client.is_playing():
            return await ctx.send(ALREADY_PLAYING.format(get_prefix(ctx)))

        link = link.lower()

        if link == 'quran radio' or link == 'quran' or link == '1':
            player = await YTDLSource.from_url(self.quranradio_url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player)
            await ctx.send("Now playing **mp3quran.net radio** (الإذاعة العامة - اذاعة متنوعة لمختلف القراء).")

        elif link == 'makkah' or link == '2':
            player = await YTDLSource.from_url(self.makkah_url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player)
            await ctx.send("Now playing **Makkah Live** (قناة القرآن الكريم- بث مباشر).")
        
        elif link == 'alharamayn' or link == '3':
            player = await YTDLSource.from_url(self.radio3_url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player)
            await ctx.send("Now playing **Alharamayn Voice net Live** (إذاعة صوت الحرمين للقرآن الكريم - بث مباشر).")


    @commands.command(name="volume", enabled=False)
    async def volume(self, ctx, volume: int):
        if not 0 <= volume <= 100:
            return await ctx.send(INVALID_VOLUME)
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to **{volume}%**.")

    # @play.before_invoke
    @ayah.before_invoke
    @page.before_invoke
    @surah.before_invoke
    @live.before_invoke
    async def join_voice(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        elif ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')
            else:
                raise commands.CommandError('Bot is already playing.')

        else:
            await ctx.author.voice.channel.connect()

    # Leave empty voice channels to conserve bandwidth.
    @commands.Cog.listener()
    async def on_voice_state_update(self, _, before, after):
        if after.channel is None:
            if len(before.channel.members) == 1 and self.bot.user in before.channel.members:
                voice_client = discord.utils.get(self.bot.voice_clients, guild=before.channel.guild)
                if voice_client is not None:
                    await voice_client.disconnect()

    @commands.command()
    async def pause(self, ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client is not None and voice_client.is_playing():
            voice_client.pause()
            await ctx.message.add_reaction("\U000023F8")
        else:
            await ctx.send(NOT_PLAYING)

    @commands.command()
    async def join(self, ctx):
        pass

    @commands.command()
    async def leave(self, ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client is not None:
            await voice_client.disconnect()
            await ctx.message.add_reaction("\U0001F44B")
            # await ctx.send(DISCONNECTED)
        else:
            await ctx.send(NOT_PLAYING)
    
    @commands.command()
    async def resume(self, ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client is not None and voice_client.is_paused():
            voice_client.resume()
            await ctx.message.add_reaction("\U000025B6")
        else:
            await ctx.send("Audio cannot be resumed!")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.message.add_reaction("\U000023F9")
        else:
            await ctx.send(NOT_PLAYING)


def setup(bot):
    bot.add_cog(Audio(bot))
