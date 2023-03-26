import discord
from discord.ext import commands
from cogs.utils import get_prefix


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @discord.app_commands.command(name="help", description="Display help menus")
    async def help(self, ctx: discord.Interaction, *, section: str = "main"):
        prefix = get_prefix(ctx)
        section = section.lower()

    # Main help page menu
        if section == "main":
            em = discord.Embed(title='\U0001F91D Hello! Im MuslimBot!', colour=0x1f8b4c, description=f"Type `{prefix}help [category | number]` to post its commands here e.g.: `{prefix}help prayer times`")
            em.add_field(name="***Categories***", value='\n0. Audio\n1. Quran\n2. Hadith\n3. Tafsir\n4. Prayer Times\n5. Dua\n6. Calendar\n7. General',
                         inline=False)
            em.add_field(name="***Links***", value="• **[Vote](https://top.gg/bot/574979234578300948/vote)**\n"
                                                   "• **[GitHub](https://github.com/nullbyto/muslimbot)**\n"
                                                   "• **[Documentation](https://github.com/nullbyto/MuslimBot/blob/master/Documentation.md)**\n"
                         , inline=False)
            em.add_field(name="***Support***", value="Join **https://discord.gg/ar9ksAy** and post in the support section")
            em.set_footer(text="Have a nice day!")
            await ctx.response.send_message(embed=em)


    # Categories pages
        elif section == "quran" or section == "1":
            em = discord.Embed(title="Quran", colour=0x1f8b4c, description=f'Available translations: `{prefix}translationlist`')
            em.add_field(name=f"{prefix}quran", inline=True, value="Gets Quranic verses."
                                              f"\n\n`{prefix}quran [surah]:[ayah] [optional translation]`"
                                              f"\nExample: `{prefix}quran 1:1`"
                                              f"\n\n`{prefix}quran [surah:[first_ayah]-[last_ayah] [optional_translation]`"
                                              f"\nExample: `{prefix}quran 1:1-7 turkish`")

            em.add_field(name=f"{prefix}aquran", inline=True, value="Gets Quranic verses in Arabic."

                                              f"\n\n`{prefix}aquran [surah]:[ayah]`"
                                              f"\nExample: `{prefix}aquran 1:1`"
                                              f"\n\n`{prefix}quran [surah]:[first_ayah]-[last_ayah]`"
                                              f"\nExample: `{prefix}aquran 1:1-7`")

            em.add_field(name=f"{prefix}morphology", inline=False, value="View the morphology of a Qur'anic word."

                                              f"\n\n`{prefix}morphology [surah]:[ayah]:[word number]`"
                                              f"\nExample: `{prefix}morphology 2:255:1`")

            em.add_field(name=f"{prefix}mushaf", inline=True, value="View a Quranic verse on a *mushaf*."

                                              f"\n\n`{prefix}mushaf [surah]:[ayah]`"
                                              f"\nExample: `{prefix}mushaf 1:1`"
                                              "\n\nAdd 'tajweed' to the end for a page with color-coded tajweed rules."
                                              f"\nExample: `{prefix}mushaf 1:1 tajweed`")

            em.add_field(name=f"{prefix}random", inline=True, value="View a random verse from Quran."

                                              f"\n\n`{prefix}random verse`")

            await ctx.response.send_message(embed=em)

        elif section == "tafsir" or section == "3":
            em = discord.Embed(title="Tafsir", colour=0x1f8b4c, description=f'Available tafsirs: `{prefix}tafsirlist`')

            em.add_field(name=f"{prefix}tafsir", inline=True, value="Gets tafsir in English."

                                              f"\n\n`{prefix}tafsir [surah]:[ayah] [optional_tafsir_name]`"
                                              f"\n\nExample: `{prefix}tafsir 1:1`"
                                              f"\n\nExample 2: `{prefix}tafsir 1:1 jalalayn`")

            em.add_field(name=f"{prefix}atafsir", inline=True, value="Gets tafsir in Arabic."

                                              f"\n\n`{prefix}atafsir [surah]:[ayah] [optional_tafsir_name]`"
                                              f"\n\nExample: `{prefix}atafsir 1:1`"
                                              f"\n\nExample 2: `{prefix}atafsir 1:1 ibnkathir`")

            await ctx.response.send_message(embed=em)

        elif section == "calendar" or section == "6":
            em = discord.Embed(title="Hijri Calendar", colour=0x1f8b4c)

            em.add_field(name=f"{prefix}hijridate", inline=True, value="Gets the current Hijri date")

            em.add_field(name=f"{prefix}converttohijri", inline=True, value="Converts a Gregorian date to its Hijri."

                                              f"\n\n`{prefix}converttohijri DD-MM-YYYY`"
                                              f"\n\nExample: `{prefix}converttohijri 01-01-2020`")

            em.add_field(name=f"{prefix}convertfromhijri", inline=True, value="Converts a Hijri date to its Gregorian."

                                              f"\n\n`{prefix}convertfromhijri DD-MM-YYYY`"
                                              f"\n\nExample: `{prefix}convertfromhijri 12-03-1440`")
            await ctx.response.send_message(embed=em)

        elif section == "hadith" or section == "2":
            em = discord.Embed(title="Hadith", colour=0x1f8b4c, description="These commands fetch hadith from *sunnah.com*.")

            em.add_field(name=f"{prefix}hadith", inline=True, value="Gets a hadith in English."
              
                                                            f"\n\n`{prefix}hadith [collection] [book_number]:[hadith_number]`"
                                                            f"\n\nExample: `{prefix}hadith bukhari 2:6` for http://sunnah.com/bukhari/2/6")

            em.add_field(name=f"{prefix}ahadith", inline=True, value="Gets a hadith in Arabic."
              
                                                            f"\n\n`{prefix}ahadith [collection] [book_number]:[hadith_number]`"
                                                            f"\n\nExample: `{prefix}ahadith bukhari 2:6` for http://sunnah.com/bukhari/2/6")

            em.add_field(name=f"{prefix}uhadith", inline=True, value="Gets a hadith in Urdu."
              
                                                            f"\n\n`{prefix}uhadith [collection] [book_number]:[hadith_number]`"
                                                            f"\n\nExample: `{prefix}uhadith bukhari 1:1` for http://sunnah.com/bukhari/1/1")

            await ctx.response.send_message(embed=em)

        elif section == "prayer times" or section == "4" :
            em = discord.Embed(title="Prayer Times", colour=0x1f8b4c)

            em.add_field(name=f"{prefix}prayertimes", inline=True, value="Gets prayer times for a specific location."
                   
                                                                 f"\n\n`{prefix}prayertimes [location]`"
                                                                 f"\n\nExample: `{prefix}prayertimes London, UK`")

            await ctx.response.send_message(embed=em)

        elif section == "dua" or section == "5":
            em = discord.Embed(title="Dua", colour=0x1f8b4c, description=f'Available duas: `{prefix}dualist`')
            em.add_field(name=f"{prefix}dua", inline=True, value="Gets a dua for a topic."
           
                                                         f"\n\n`{prefix}dua [topic]`"
                                                         f"\n\nExample: `{prefix}dua forgiveness`")
            await ctx.response.send_message(embed=em)

        elif section == "audio" or section == "0":
            em = discord.Embed(title="Quranic Audio", colour=0x1f8b4c, description=f'Available Reciters: `{prefix}reciters`')
            em.add_field(name=f"{prefix}play", inline=True, value="plays the recitation of a surah, ayah or mushaf page."
                                                                    f"\n**Playing a surah**\n`{prefix}play surah [surah number] [reciter]`"
                                                                    f"\n**Playing an ayah**\n`{prefix}play ayah [surah]:[ayah] [reciter]`"
                                                                    f"\n**Playing a page from the mushaf**\n`{prefix}play page [page number] [reciter]`"
                                                                    f"\n\nFor more info: `{prefix}help play`")
            em.add_field(name=f"{prefix}live", inline=False, value="plays live audio either from Makkah or online Qur'an radio."
                                                                    f"`{prefix}live [makkah / quran radio / alharamayn]` or choose from 1/2/3.")
            em.add_field(name=f"{prefix}search", inline=False, value="search the reciter list for `play` command\n"
                                                                     f"`{prefix}search [reciter name]`")
            em.add_field(name=f"{prefix}pause", inline=False, value="pauses the audio")
            em.add_field(name=f"{prefix}resume", inline=False, value="resume the audio")
            em.add_field(name=f"{prefix}stop", inline=False, value="stops audio and disconnects the bot from voice chat")
            em.add_field(name=f"{prefix}leave", inline=False, value="disconnects the bot from voice chat")
            # em.add_field(name=f"{prefix}volume", inline=False, value="changes the volume of the bot\n"
            #                                                            f"`{prefix}volume [volume]`. volume must be between 1 and 100")
            await ctx.response.send_message(embed=em)

        elif section == "general" or section == "7":
            em = discord.Embed(title="General", colour=0x1f8b4c, description=f'General purpose commands.')
            em.add_field(name=f"{prefix}prefix", inline=False, value="Changes server's prefix for the bot.(Server's owner only)"
           
                                                         f"\n\n`{prefix}prefix` shows current prefix"
                                                         f"\n`{prefix}prefix [prefix]`\nExample: `{prefix}prefix ++`")
            em.add_field(name=f"{prefix}userinfo", inline=False, value="Shows all general info about the user, can be used with mention."
                                                                       
                                                                       f"\n\n`{prefix}userinfo`\n`{prefix}userinfo [@user]`")
                                                                       
            await ctx.response.send_message(embed=em)
            

    # Specific help pages
        elif section == "play":
            em = discord.Embed(colour=0x1f8b4c, title='`play` Command')
            em.add_field(value=f"**{prefix}play** plays a surah, ayah or page from the mushaf in a voice channel."
                               , name='Description', inline=False)
            em.add_field(value=f"`{prefix}play surah [surah number] [reciter]`\n\nExample: `{prefix}play surah 1 Mishary Alafasi`"
                               f"\n__**OR**__ \n`{prefix}play surah [surah name] [reciter]`\n\nExample: `{prefix}play surah al-fatiha"
                               " Mishary Alafasi`", name='Playing a surah', inline=False)
            em.add_field(value=f"`{prefix}play ayah [surah]:[ayah] [reciter]`\n\nExample: `{prefix}play ayah 1:6 hani al-rifai`"
                               , name='Playing an ayah', inline=False)
            em.add_field(value=f"`{prefix}play page [page number] [reciter]`\n\nExample: `{prefix}play page 342 hani al-rifai`"
                               , name='Playing a page from the mushaf', inline=False)
            em.add_field(value=f"Type `{prefix}reciters` for a list of reciters.", name='Reciters', inline=False)
            await ctx.response.send_message(embed=em)

        else:
            await ctx.response.send_message(f'**Invalid category, please choose one of the categories like this example:** `{prefix}help prayer times`')



# Register as cog
async def setup(bot):
    await bot.add_cog(Help(bot))
