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
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.voice_states = {}
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.info_url = 'http://api.quran.com/api/v3/chapters/{}'
        self.reciter_info_url = 'http://mp3quran.net/api/_english.php'
        self.makkah_url = 'http://mediaserver2.islamicity.com:8000/SaudiTVArabic'
        self.quranradio_url = 'http://live.mp3quran.net:8006/stream?type=http&nocache=29554'
        self.page_url = 'https://everyayah.com/data/{}/PageMp3s/Page{}.mp3'
        self.ayah_url = 'https://everyayah.com/data/{}/{}.mp3'
        self.mushaf_url = 'https://www.searchtruth.org/quran/images1/{}.jpg'
        self.radio3_url = 'http://212.32.255.144:9300/stream.mp3'
        self.tree = bot.tree

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.response.send_message(':x: **Error**: *{}*'.format(str(error)))
        print(error)

    # @discord.app_commands.command(name="volume", description="Control volume of the audio")
    # async def volume(self, ctx: discord.Interaction, volume: int):
    #     player: discord.PCMVolumeTransformer = ctx.guild._voice_states.get(ctx.guild.id)
    #     if not 0 <= volume <= 100:
    #         return await ctx.response.send_message(INVALID_VOLUME)
    #     if ctx.guild.voice_client is None:
    #         return await ctx.response.send_message("Not connected to a voice channel.")
    #     # ctx.voice_client.source.volume = volume / 100
    #     player.volume = volume / 100
    #     await ctx.response.send_message(f"Changed volume to **{volume}%**.")


    # Leave empty voice channels to conserve bandwidth.
    @commands.Cog.listener()
    async def on_voice_state_update(self, _, before, after):
        if after.channel is None:
            if len(before.channel.members) == 1 and self.bot.user in before.channel.members:
                voice_client = discord.utils.get(self.bot.voice_clients, guild=before.channel.guild)
                if voice_client is not None:
                    await voice_client.disconnect()

    @discord.app_commands.command(name="pause", description="Pauses playing audio")
    async def pause(self, ctx: discord.Interaction):
        voice_client = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
        if voice_client is not None and voice_client.is_playing():
            voice_client.pause()
            await ctx.response.send_message("⏸ Audio paused.")
        else:
            await ctx.response.send_message(NOT_PLAYING)

    @discord.app_commands.command(name="leave", description="Leave voice channel if connected")
    async def leave(self, ctx: discord.Interaction):
        voice_client = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
        if voice_client is not None:
            await voice_client.disconnect()
            await ctx.response.send_message(DISCONNECTED)
        else:
            await ctx.response.send_message(NOT_PLAYING)
    
    @discord.app_commands.command(name="resume", description="Resume playing audio")
    async def resume(self, ctx: discord.Interaction):
        voice_client = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
        if voice_client is not None and voice_client.is_paused():
            voice_client.resume()
            await ctx.response.send_message("▶ Audio resumed.")
        else:
            await ctx.response.send_message("Audio cannot be resumed!")

    @discord.app_commands.command(name="stop", description="Stop playing audio")
    async def stop(self, ctx: discord.Interaction):
        voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await ctx.response.send_message("⏹ Audio stopped.")

        else:
            await ctx.response.send_message(NOT_PLAYING)
    
class PlayGroup(discord.app_commands.Group):
    def __init__(self, bot: commands.AutoShardedBot, name: str, description: str):
        super(PlayGroup, self).__init__(name=name, description=description)

        self.bot = bot
        self.voice_states = {}
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.info_url = 'http://api.quran.com/api/v3/chapters/{}'
        self.reciter_info_url = 'http://mp3quran.net/api/_english.php'
        self.makkah_url = 'http://mediaserver2.islamicity.com:8000/SaudiTVArabic'
        self.quranradio_url = 'http://live.mp3quran.net:8006/stream?type=http&nocache=29554'
        self.page_url = 'https://everyayah.com/data/{}/PageMp3s/Page{}.mp3'
        self.ayah_url = 'https://everyayah.com/data/{}/{}.mp3'
        self.mushaf_url = 'https://www.searchtruth.org/quran/images1/{}.jpg'
        self.radio3_url = 'http://212.32.255.144:9300/stream.mp3'
        self.tree = bot.tree

    def make_ayah_url(self, surah, ayah, reciter):
        url_surah = str(surah).zfill(3)
        url_ayah = str(ayah).zfill(3)

        try: url_reciter = everyayah_reciters[reciter]
        except KeyError: return None

        url_ref = f'{url_surah}{url_ayah}'
        url = self.ayah_url.format(url_reciter, url_ref)

        return url


    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.response.send_message(':x: **Error**: *{}*'.format(str(error)))
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

    async def join_ch(self, ctx: discord.Interaction):
        voice = ctx.user.voice
        voice_client = ctx.guild.voice_client

        if not voice or not voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        elif voice_client:
            if voice_client.channel != voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')
            else:
                raise commands.CommandError('Bot is already playing.')

        else:
            return await voice.channel.connect()

    async def create_player(self, ctx: discord.Interaction, url: str):
        voice_client = await self.join_ch(ctx)
        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        except:
            return await ctx.response.send_message(RECITATION_NOT_FOUND)

        self.voice_states[ctx.guild.id] = player

        try:
            voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(voice_client.disconnect()
                                                                                           , self.bot.loop))
        except discord.errors.ClientException as e:
            return print(e)

    @discord.app_commands.command(name="live", description="Play live quran in voice channel")
    async def live(self, ctx: discord.Interaction, *, channel: str = '1'):
        voice_client = await self.join_ch(ctx)

        # voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            return await ctx.response.send_message(ALREADY_PLAYING.format(get_prefix(ctx)))

        channel = channel.lower()

        if channel == 'quran radio' or channel == 'quran' or channel == '1':
            player = await YTDLSource.from_url(self.quranradio_url, loop=self.bot.loop, stream=True)
            voice_client.play(player)
            await ctx.response.send_message("Now playing **mp3quran.net radio** (الإذاعة العامة - اذاعة متنوعة لمختلف القراء).")

        elif channel == 'makkah' or channel == '2':
            player = await YTDLSource.from_url(self.makkah_url, loop=self.bot.loop, stream=True)
            voice_client.play(player)
            await ctx.response.send_message("Now playing **Makkah Live** (قناة القرآن الكريم- بث مباشر).")
        
        elif channel == 'alharamayn' or channel == '3':
            player = await YTDLSource.from_url(self.radio3_url, loop=self.bot.loop, stream=True)
            voice_client.play(player)
            await ctx.response.send_message("Now playing **Alharamayn Voice net Live** (إذاعة صوت الحرمين للقرآن الكريم - بث مباشر).")
    
    @discord.app_commands.command()
    async def surah(self, ctx: discord.Interaction, surah: str, *, reciter: str = 'Mishary Alafasi'):

        # if ctx.voice_client.is_playing():
        #     return await ctx.response.send_message(ALREADY_PLAYING.format(get_prefix(ctx)))


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
                    await ctx.response.send_message(f'Could not find {surah}, so the closest match - *{result[0][0]}* - will be used.')
                    surah = await get_surah_id_from_name(result[0][0].lower())
                else:
                    return await ctx.response.send_message(SURAH_NOT_FOUND.format(get_prefix(ctx)))

        reciter = await get_mp3quran_reciter(reciter.lower())

        if reciter is None:
            return await ctx.response.send_message(RECITER_NOT_FOUND.format(get_prefix(ctx)))

        if not 0 < surah <= 114:
            return await ctx.response.send_message(SURAH_NOT_FOUND.format(get_prefix(ctx)))

        file_url = self.get_play_file(reciter.server, surah)

        await self.create_player(ctx, file_url)

        transliterated_surah, arabic_surah = await self.get_surah_info(surah)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}).\nReciter: **{reciter.name}**.' \
                      f'\nRiwayah: {reciter.riwayah}'

        # em = self.make_embed("\U000025B6 Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400)
        em = self.make_embed("\U000025B6 Qurʼān", description, f'', 0x006400)
        await ctx.response.send_message(embed=em)

    @discord.app_commands.command()
    async def ayah(self, ctx: discord.Interaction, ref: str, *, reciter: str = 'mishary al-afasy'):

        # if ctx.voice_client.is_playing():
        #     return await ctx.response.send_message(ALREADY_PLAYING.format(get_prefix(ctx)))

        try:
            surah, ayah = ref.split(':')
            surah = int(surah)
            ayah = int(ayah)

        except:
            return await ctx.response.send_message("Invalid arguments. Commands: `{}play ayah [surah]:[ayah] [reciter]`."
                                  "\n\nExample: `{}play ayah 2:255 abdul rahman al-sudais`.".format(get_prefix(ctx)))

        reciter = reciter.lower()

        if reciter is None:
            return await ctx.response.send_message(RECITER_NOT_FOUND.format(get_prefix(ctx)))

        if not 0 < surah <= 114:
            return await ctx.response.send_message(SURAH_NOT_FOUND.format(get_prefix(ctx)))

        verse_count = await self.get_verse_count(surah)
        if ayah > verse_count:
            return await ctx.response.send_message(NON_EXISTENT_VERSE.format(verse_count))

        url = self.make_ayah_url(surah, ayah, reciter)
        try: player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        except:
            return await ctx.response.send_message(RECITATION_NOT_FOUND)

        await self.create_player(ctx, url)

        reciter = reciter.replace('-', ' - ').title().replace(' - ', '-')
        transliterated_surah, arabic_surah = await self.get_surah_info(surah)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}), Ayah {ayah}. ' \
                      f'\nReciter: **{reciter}**.'

        # em = self.make_embed("\U000025B6 Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400,
        #                      f'https://everyayah.com/data/QuranText_jpg/{surah}_{ayah}.jpg')
        em = self.make_embed("\U000025B6 Qurʼān", description, f'', 0x006400,
                             f'https://everyayah.com/data/QuranText_jpg/{surah}_{ayah}.jpg')
        await ctx.response.send_message(embed=em)

    @discord.app_commands.command()
    async def page(self, ctx: discord.Interaction, page: int, *, reciter: str = 'mishary al-afasy'):

        # if ctx.voice_client.is_playing():
        #     return await ctx.response.send_message(ALREADY_PLAYING.format(get_prefix(ctx)))

        try:
            page = int(page)
        except:
            return await ctx.response.send_message("Invalid arguments. Commands: `{}page [page]:[ayah] [reciter]`."
                                  "\n\nExample: `{}ayah 604 abdul rahman al-sudais`.".format(get_prefix(ctx)))

        reciter = reciter.lower()
        readable_reciter = reciter.replace('-', ' - ').title().replace(' - ', '-')

        if reciter not in everyayah_reciters:
            return await ctx.response.send_message(RECITER_NOT_FOUND.format(get_prefix(ctx)))

        if not 0 < page <= 604:
            return await ctx.response.send_message(PAGE_NOT_FOUND)

        url, url_page = self.make_page_url(page, reciter)

        await self.create_player(ctx, url)

        description = f'Playing **Page {page}.**\nReciter: **{readable_reciter}**.'

        # em = self.make_embed("\U000025B6 Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400,
        #                      f'https://www.searchtruth.org/quran/images2/large/page-{url_page}.jpeg')
        em = self.make_embed("\U000025B6 Qurʼān", description, f'', 0x006400,
                             f'https://www.searchtruth.org/quran/images2/large/page-{url_page}.jpeg')
        await ctx.response.send_message(embed=em)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Audio(bot))
    bot.tree.add_command(PlayGroup(bot=bot, name="play", description="Play quran audio"))
