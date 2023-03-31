from aiohttp import ClientSession
from discord.ext import commands
from cogs.utils import get_site_source, get_prefix
import discord
import re

icon = 'https://www.stickpng.com/assets/images/580b585b2edbce24c47b2abb.png'
INVALID_ARGUMENTS = "**Invalid arguments!**\nUsage: `{0}quranmorphology surah:verse:word\nExample: `{0}quranmorphology 1:1:2`" \
                    "(for the second word of the first verse of Surah al-Fatiha)"


class QuranMorphology(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop = bot.loop)
        self.morphologyURL = 'http://corpus.quran.com/wordmorphology.jsp?location=({}:{}:{})'
        self.syntaxURL = 'http://corpus.quran.com/treebank.jsp?chapter={}&verse={}&token={}'

    @discord.app_commands.command(name="morphology", description="Display morphology (Ii'rab)")
    async def morphology(self, ctx: discord.Interaction, ref: str):

        if not self.isInCorrectFormat(ref):
            await ctx.response.send_message(INVALID_ARGUMENTS.format(get_prefix(ctx)))
            return

        try:
            surah, verse, word = ref.split(':')

        except:
            await ctx.response.send_message(INVALID_ARGUMENTS.format(get_prefix(ctx)))
            return

        wordSource = await get_site_source(self.morphologyURL.format(surah, verse, word))
        wordImage = self.getWordImage(wordSource)

        paragraph = wordSource.find("p", "first")
        rawMorphology = str(wordSource.find("td", "morphologyCell").text)
        morphology = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \n\1', rawMorphology)
        grammar = wordSource.find("td", "grammarCell")

        syntax = False
        if self.isSyntaxAvailable(int(surah)):
            syntax = True
            syntaxSource = await get_site_source(self.syntaxURL.format(surah, verse, word))
            syntaxImage = self.getSyntaxImage(syntaxSource, word)

        em = discord.Embed(colour=0x006400)
        em.set_author(name=f"Qurʾān {surah}:{verse}, Word {word}", icon_url=icon)
        em.add_field(name='Morphology', value=f'From right to left: \n {morphology} ({grammar.text})', inline=False)
        em.add_field(name='Information', value=f'{paragraph.text}', inline=False)

        if syntax is True:
            em.set_image(url=syntaxImage)
            em.set_thumbnail(url=wordImage)
        else:
            em.set_image(url=wordImage)
        await ctx.response.send_message(embed=em)

    def getWordImage(self, source):
        imageText = source.find("a", "tokenLink")
        for image in imageText:
            image = (image['src'])
            imageURL = f"http://corpus.quran.com{image}"
            return imageURL

    def isSyntaxAvailable(self, surah):
        if 1 <= surah <= 8 or 59 <= surah <= 114:
            return True
        else:
            return False

    def getSyntaxImage(self, source, word):
        javascript = str(source.find("div", {"class": "graph"}))
        graphID = (javascript.split("url('/"))[1].split("')")[0]
        imageURL = f'http://corpus.quran.com/{graphID}&token={word}'
        return imageURL

    def isInCorrectFormat(self, ref):
        try:
            ref.split(':')
            return True
        except:
            return False


# Register as cog
async def setup(bot):
    await bot.add_cog(QuranMorphology(bot))
