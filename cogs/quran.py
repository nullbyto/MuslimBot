import aiohttp
import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import CheckFailure
from cogs.utils import get_prefix, convert_to_arabic_number, make_embed
from collections import OrderedDict
import random
import requests
# from dbhandler import create_connection, update_guild_translation, get_guild_translation


INVALID_TRANSLATION = "**Invalid translation**. List of translations: <https://github.com/galacticwarrior9/is" \
                      "lambot/blob/master/Translations.md>"

INVALID_ARGUMENTS_ARABIC = "Invalid arguments! Do `{0}aquran [surah]:[ayah]`. Example: `{0}aquran 1:1`" \
                               "\nTo fetch multiple verses, do `{0}quran [surah]:[first ayah]-[last ayah]`" \
                               "\nExample: `{0}aquran 1:1-7`"

INVALID_ARGUMENTS_ENGLISH = "Invalid arguments! Do `{0}quran [surah]:[ayah]`. Example: `{0}quran 1:1`" \
                               "\nTo fetch multiple verses, do `{0}quran [surah]:[first ayah]-[last ayah]`" \
                               "\nExample: `{0}quran 1:1-7`"

SQL_ERROR = "There was an error connecting to the database."

DATABASE_UNREACHABLE = "Could not contact database. Please report this on the support server!"

ICON = 'https://cdn6.aptoide.com/imgs/6/a/6/6a6336c9503e6bd4bdf98fda89381195_icon.png'


class QuranSpecifics:
    def __init__(self, ref, edition):
        self.edition = edition
        self.ordered_dict = OrderedDict()
        self.surah, self.offset, self.limit = self.process_ref(ref)
        self.quran_com = self.is_quran_com(edition)

    @staticmethod
    def process_ref(ref):
        surah = int(ref.split(':')[0])
        min_ayah = int(ref.split(':')[1].split('-')[0])

        try:
            max_ayah = int(ref.split(':')[1].split('-')[1]) + 1
        except IndexError:
            max_ayah = min_ayah + 1

        # If the min ayah is larger than the max ayah, we assume this is a mistake and swap their values.
        if min_ayah > max_ayah:
            temp = min_ayah
            min_ayah = max_ayah
            max_ayah = temp

        offset = min_ayah - 1
        limit = max_ayah - min_ayah
        if limit > 25:
            limit = 25

        return [surah, offset, limit]

    @staticmethod
    def is_quran_com(edition):
        return True if isinstance(edition, int) else False


class Quran(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.quran_com_url = 'http://api.quran.com/api/v3/chapters/{}/verses?translations={}&language=en&offset={' \
                             '}&limit={}&text_type=words'
        self.alquran_url = 'http://api.alquran.cloud/surah/{}/{}?offset={}&limit={}'
        self.arabic_url = 'http://api.alquran.cloud/surah/{}?offset={}&limit={}'

    @staticmethod
    def format_edition(edition):
        edition_dict = {
            'mammadaliyev': 'az.mammadaliyev',
            'musayev': 'az.musayev',
            'bengali': 'bn.bengali',
            'bulgarian': 'bg.theophanov',
            'bosnian': 25,
            'hrbek': 'cs.hrbek',
            'nykl': "cs.nykl",
            'aburida': 'de.aburida',
            'bubenheim': 'de.bubenheim',
            'khoury': 'de.khoury',
            'zaidan': "de.zaidan",
            'divehi': 'dv.divehi',
            'amharic': 87,
            'haleem': 85,
            'taqiusmani': 84,
            'khattab': 101,
            'ghali': 17,
            'finnish': 30,
            'indonesian': 33,
            'tajik': 74,
            'chechen': 106,
            'czech': 26,
            'sahih': 20,
            'ahmedali': 'en.ahmedali',
            'arberry': 'en.arberry',
            'asad': 'en.asad',
            'daryabadi': 'en.daryabadi',
            'hilali': 18,
            'pickthall': 19,
            'qaribullah': 'en.qaribullah',
            'sarwar': 'en.sarwar',
            'yusufali': 22,
            'shakir': 'en.shakir',
            'transliteration': 'en.transliteration',
            'spanish': 83,
            'ansarian': 'fa.ansarian',
            'ayati': 'fa.ayati',
            'fooladvand': 'fa.fooladvand',
            'ghomshei': 'fa.ghomshei',
            'makarem': 'fa.makarem',
            'french': 31,
            'hausa': 32,
            'hindi': 82,
            'italian': 34,
            'japanese': 'ja.japanese',
            'korean': 'ko.korean',
            'kurdish': 	81,
            'malayalam': 37,
            'dutch': 40,
            'norwegian': 'no.berg',
            'polish': 'pl.bielawskiego',
            'portuguese': 'pt.elhayek',
            'romanian': 'ro.grigore',
            'kuliev': 45,
            'osmanov': 'ru.osmanov',
            'porokhova': 'ru.porokhova',
            'sindhi': 'sd.amroti',
            'somali': 46,
            'ahmeti': 'sq.ahmeti',
            'mehdiu': 'sq.mehdiu',
            'nahi': 'sq.nahi',
            'swedish': 48,
            'swahili': 'sw.barwani',
            'tamil': 'ta.tamil',
            'thai': 'th.thai',
            'ates': 'tr.ates',
            'bulac': 'tr.bulac',
            'diyanet': 77,
            'golpinarli': 'tr.golpinarli',
            'ozturk': 'tr.ozturk',
            'vakfi': 'tr.vakfi',
            'yazir': 'tr.yazir',
            'yildirim': 'tr.yildirim',
            'yuksel': 'tr.yuksel',
            'tatar': 'tt.nugman',
            'uyghur': 'ug.saleh',
            'jalandhry': 'ur.jalandhry',
            'jawadi': 'ur.jawadi',
            'qadri': 'ur.qadri',
            'urdu': 97,
            'maududi': 97,
            'junagarhi': 54,
            'maududi.en': 95,
            'malay': 39,
            'uzbek': 'uz.sodik',
            'chinese': 'zh.jian',
            'ukrainian': 104,
            'abuadel': 79,
            'maranao': 38,
            #EDITED
            'turkish': 77,
            'russian': 79,
            'albanian': 'sq.ahmeti' ,
            'azerbaijani': 'az.mammadaliyev', 
            'german': 'de.aburida',
            'english': 85,
            'farsi': 'fa.ansarian',
            'persian': 'fa.ansarian',
            'czech': 'cs.hrbek',
            'urdu': 95
        }
        return edition_dict[edition]

    @staticmethod
    def get_edition_name(edition):
        edition_names = {
            85: 'Abdel Haleem',
            101: "Dr. Mustafa Khattab",
            84: "Mufti Taqi Usmani",
            17: "Dr. Ghali",
            22: "Yusuf Ali",
            30: "Finnish",
            33: "Bahasa Indonesia (Kementerian Agama)",
            74: "Tajik (Abdolmohammad Ayati)",
            106: "Chechen (Magomed Magomedov)",
            87: "አማርኛ (Sadiq & Sani)",
            20: 'Sahih International',
            31: 'Français (Muhammad Hamidullah)',
            77: 'Türkçe (Diyanet İşleri)',
            81: 'Kurdî (Burhan Muhammad-Amin)',
            82: 'हिन्दी (Suhel Farooq Khan)',
            95: 'Abul Ala Maududi (with tafsir)',
            26: 'Čeština',
            104: 'Українська мова (Mykhaylo Yakubovych)',
            83: 'Español (Sheikh Isa García)',
            37: 'മലയാളം (Abdul Hameed & Kunhi Mohammed)',
            19: 'Pickthall',
            18: 'Muhsin Khan & Hilali',
            34: 'Italiano (Hamza Roberto Piccardo)',
            39: 'Bahasa Melayu (Abdullah Muhammad Basmeih)',
            97: 'اردو, (ابو الاعلی مودودی)',
            54: 'اردو, (محمد جوناگڑھی)',
            40: 'Nederlands (Salomo Keyzer)',
            25: 'Bosanski',
            45: 'Русский (Эльми́р Кули́ев)',
            79: 'Русский (Абу Адель)',
            78: 'Русский (Министерство вакуфов, Египта)',
            48: 'Svenska (Knut Bernström)',
            32: 'Hausa (Abubakar Mahmoud Gumi)',
            38: 'Mëranaw',
            46: 'Af-Soomaali (Mahmud Muhammad Abduh)'
        }
        return edition_names[edition]

    @staticmethod
    def get_language_code(edition):
        language_codes = {
            31: 'fr',  # Hamidullah, French
            97: 'ur',  # Maududi, Urdu
            54: 'ur',  # Junagarhi, Urdu
            'ur.jalandhry': 'ur',
            'ur.jawadi': 'ur',
            'ur.qadri': 'ur',
            83: 'es',  # Isa Garcia, Spanish
            40: 'nl',  # Salomo Keyzar, Dutch
            25: 'bs',  # Bosnian
            33: 'id',  # Indonesian
            45: 'ru',  # Kuliev, Russian
            78: 'ru',  # Ministry of Awqaf, Russian
            79: 'ru',  # Abu Adel, Russian
            48: 'sv',  # Knut Bernström, Swedish
        }
        return language_codes[edition]


    @commands.command(name="settranslation", enabled=False)
    @commands.has_permissions(administrator=True)
    async def settranslation(self, ctx: discord.Interaction, translation: str):

        if translation is None:
            return await ctx.response.send_message(INVALID_TRANSLATION)

        try:
            self.format_edition(translation)
        except:
            return await ctx.response.send_message(INVALID_TRANSLATION)

        try:
            await create_connection()
        except Exception as e:
            print(e)
            return await ctx.response.send_message(DATABASE_UNREACHABLE)

        await update_guild_translation(ctx.guild.id, translation)
        await ctx.response.send_message(f"**Successfully updated default translation to `{translation}`!**")

    @settranslation.error
    async def settranslation_error(self, ctx: discord.Interaction, error):
        if isinstance(error, CheckFailure):
            await ctx.response.send_message("You need the **Administrator** permission to use this command.")


    # Should have edition: str = None to get the default_guild_set_translation to put it
    # I just modified it to have a default English edition = 'haleem'
    @discord.app_commands.command(name="quran", description="Read the quran in english")
    async def quran(self, ctx: discord.Interaction, ref: str, edition: str = 'haleem'):
        async with ctx.channel.typing():

            # If no translation was specified, find a translation to use.
            if edition is None:
                try:

                    # edition = await get_guild_translation(ctx.message.guild.id)
                    edition = self.format_edition(edition)
                except AttributeError:
                    edition = 85

            # If a translation was specified in the command, check whether it is valid:
            else:
                try:
                    edition = self.format_edition(edition)
                except KeyError:
                    return await ctx.response.send_message(INVALID_TRANSLATION)

            # Now fetch the verses:
            try:
                spec = self.get_spec(ref, edition)
            except:
                return await ctx.response.send_message(INVALID_ARGUMENTS_ENGLISH.format(get_prefix(ctx)))

            surah_name, readable_edition, revelation_type = await self.get_metadata(spec, edition)
            translated_surah_name = await self.get_translated_surah_name(spec, edition)

            if revelation_type == "makkah":
                revelation_type = "Meccan"
            else:
                revelation_type = "Medinan"

            await self.get_verses(spec)

            em = make_embed(fields=spec.ordered_dict, author=f"Surah {surah_name} ({translated_surah_name})",
                            author_icon=ICON, colour=0x048c28, inline=False, footer=f'Translation: {readable_edition} |'
                                                                                    f' {revelation_type}')

            if len(em) > 6000:
                return await ctx.response.send_message("This passage was too long to send.")

            await ctx.response.send_message(embed=em)

    @discord.app_commands.command(name="aquran", description="Read the quran in arabic")
    async def aquran(self, ctx: discord.Interaction, *, ref: str):
        try:
            spec = self.get_spec(ref)
        except:
            return await ctx.response.send_message(INVALID_ARGUMENTS_ARABIC.format(get_prefix(ctx)))

        surah_name = await self.get_metadata(spec, edition='ar')
        await self.get_verses(spec)

        em = make_embed(fields=spec.ordered_dict, author=f' سورة {surah_name}', author_icon=ICON, colour=0x048c28,
                        inline=False, footer="")

        if len(em) > 6000:
            return await ctx.response.send_message("This passage was too long to send.")

        await ctx.response.send_message(embed=em)

    @staticmethod
    def get_spec(ref, edition='ar'):
        return QuranSpecifics(ref, edition)


    async def get_verses(self, spec):
        """Fetches the verses' text. We use the quran.com API or alquran.cloud API depending on the translation used."""
        if spec.quran_com:
            async with self.session.get(self.quran_com_url.format(spec.surah, spec.edition, spec.offset, spec.limit)) as r:
                data = await r.json()
                data = data['verses']
            verses = [(verse['verse_number'], verse['translations'][0]['text']) for verse in data]

        elif spec.edition == 'ar':
            async with self.session.get(self.arabic_url.format(spec.surah, spec.offset, spec.limit)) as r:
                data = await r.json()
                data = data['data']['ayahs']
            verses = [(verse['numberInSurah'], verse['text']) for verse in data]

        else:
            async with self.session.get(self.alquran_url.format(spec.surah, spec.edition, spec.offset, spec.limit)) as r:
                data = await r.json()
                data = data['data']['ayahs']
            verses = [(verse['numberInSurah'], verse['text']) for verse in data]

        await self.make_ordered_dict(spec, verses)


    @staticmethod
    async def make_ordered_dict(spec, verses):
        """Make an ordered dict from the verse text. The verse text is truncated if it's too long for the embed field"""
        for verse in verses:
            key, text = verse
            if spec.edition == 'ar':
                key = f'{convert_to_arabic_number(str(spec.surah))}:{convert_to_arabic_number(str(key))}'
            else:
                key = f'{spec.surah}:{key}'
            spec.ordered_dict[key] = text


    async def get_metadata(self, spec, edition):
        """Get the surah name in Arabic along with the revelation location."""
        if spec.edition == 'ar':
            async with self.session.get(f'http://api.quran.com/api/v3/chapters/{spec.surah}') as r:
                data = await r.json()
                return data['chapter']['name_arabic']

        elif spec.is_quran_com(edition):
            async with self.session.get(f'http://api.quran.com/api/v3/chapters/{spec.surah}') as r:
                data = await r.json()
                return data['chapter']['name_simple'], self.get_edition_name(edition), data['chapter']['revelation_place']
        else:
            async with self.session.get(f'http://api.alquran.cloud/v1/surah/{spec.surah}/{spec.edition}') as r:
                data = await r.json()
                return data['data']['englishName'], data['data']['edition']['name'], data['data']['revelationType']

    async def get_translated_surah_name(self, spec, edition):
        try:
            language_code = self.get_language_code(edition)
        except KeyError:
            language_code = None

        async with self.session.get(f'http://api.quran.com/api/v3/chapters/{spec.surah}?language={language_code}') as r:
            data = await r.json()
            return data['chapter']['translated_name']['name']


    @discord.app_commands.command(name="translationlist", description="Get translation list")
    async def translationlist(self,ctx):
        with open('translations.txt') as f:
            lines = f.readlines()
        pages = 3
        page = 1
        embed = discord.Embed(colour=0x048c28, title='Translation list for `quran` command:')
        embed.add_field(name='★━━━━━━━━━━━━━━━━━━━━★', value=''.join(lines[0:34]))
        embed.add_field(name='★━━━━━━━━━━━━━━━━━━━━★', value=''.join(lines[34:68]))
        msg = await ctx.response.send_message(embed=embed)
        await msg.add_reaction(emoji='⬅')
        await msg.add_reaction(emoji='➡')
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add",
                        timeout=90, check=lambda reaction,
                        user: (reaction.emoji == '➡'
                               or reaction.emoji == '⬅')
                               and user != self.bot.user
                               and reaction.message.id == msg.id)
            except asyncio.TimeoutError:
                await msg.remove_reaction(emoji='➡', member=self.bot.user)
                await msg.remove_reaction(emoji='⬅', member=self.bot.user)
                break

            await msg.remove_reaction(reaction.emoji, user)

            if reaction.emoji == '➡' and page < pages:
                page += 1

            if reaction.emoji == '⬅' and page > 1:
                page -= 1

            if page == 2:
                embed = discord.Embed(colour=0x048c28, title='Translation list for `quran` command:')
                embed.add_field(name='★━━━━━━━━━━━━━━━━━━━━★', value=''.join(lines[68:102]))
                embed.add_field(name='★━━━━━━━━━━━━━━━━━━━━★', value=''.join(lines[102:136]))
                await msg.edit(embed=embed)

            elif page == 3:
                embed = discord.Embed(colour=0x048c28, title='Translation list for `quran` command:')
                embed.add_field(name='★━━━━━━━━━━━━━━━━━━━━★', value=''.join(lines[136:170]))
                await msg.edit(embed=embed)

            elif page == 1:
                embed = discord.Embed(colour=0x048c28, title='Translation list for `quran` command:')
                embed.add_field(name='★━━━━━━━━━━━━━━━━━━━━★', value=''.join(lines[0:34]))
                embed.add_field(name='★━━━━━━━━━━━━━━━━━━━━★', value=''.join(lines[34:68]))
                await msg.edit(embed=embed)
            
    @discord.app_commands.command(name="random", description="Display random ayah from the quran")
    async def random(self, ctx , type: str = None):
        if type is None:
            await ctx.response.send_message('Invalid Arguments, please choose a type. `{}random verse`'.format(get_prefix(ctx)))

        elif type == 'verse':
            random_num = random.randint(1,6236)
            async with self.session.get(f'http://api.alquran.cloud/ayah/{random_num}/editions/quran-uthmani,en.pickthall') as r:
                data = await r.json()
                text_ar = data['data'][0]['text']
                text_eng = data['data'][1]['text']
                name_ar = data['data'][0]['surah']['name']
                name_eng = data['data'][1]['surah']['englishName']
                name_eng_tr = data['data'][1]['surah']['englishNameTranslation']
                edition_ar = data['data'][0]['edition']['name']
                edition_eng = data['data'][1]['edition']['name']
            embed = discord.Embed(title='Random Verse from Quran', author_icon=ICON, description=f'{name_ar}\n{name_eng} ({name_eng_tr})\n\n'
                                                                                                 f'{text_ar}\n{text_eng}')
            embed.set_footer(text=f"Arabic: {edition_ar} | English: {edition_eng}")
            await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Quran(bot))
