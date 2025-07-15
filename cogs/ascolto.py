import discord
from discord.ext import commands
import re
import unicodedata
from utils import normalize
import asyncio

class AscoltoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kernactiviteiten = [
            ("lei", [
                "è andata al cinema",
                "ha visto un film americano",
                "è rimasta a casa",
                "ha guardato la tv",
                "è venuta da Londra",
                "ha parlato del suo lavoro",
                "ha chiesto di te"
            ]),
            ("loro", [
                "sono andati a ballare",
                "sono usciti ogni sera",
                "hanno fatto una piccola gita al mare",
                "hanno visitato un museo",
                "sono andati a giocare a calcetto",
                "hanno fatto solo un po’ di jogging",
                "sono stati in Sardegna",
                "hanno noleggiato una macchina",
                "hanno fatto il giro dell’isola",
                "sono andati a bere un caffè"
            ])
        ]
        self.allowed_channels = {1388667261761359932, 1394796805283385454}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id not in self.allowed_channels:
            return

        if len(message.content.strip()) < 10:
            return

        normalized_text = normalize(message.content.lower())
        juist = set()
        fouten = []
        ikvorm = []

        for subject, phrases in self.kernactiviteiten:
            for phrase in phrases:
                pattern = rf"\b{re.escape(phrase)}\b"
                if re.search(pattern, normalized_text):
                    juist.add(phrase)
                    if subject == "loro" and re.search(r"\b(sono|abbiamo|hanno|siamo)\b.*\b(io|ho|sono andato|sono andata)\b", normalized_text):
                        ikvorm.append(phrase)

        overige = [p for _, lst in self.kernactiviteiten for p in lst if p not in juist]
        aantal_juist = len(juist)

        try:
            await message.author.send(
                f"📊 Hai riconosciuto **{aantal_juist}** attività correttamente."
                + ("\n⚠️ Alcune frasi sembrano essere nella forma 'io', ma nel testo originale si trattava di *lei* o *loro*." if ikvorm else "")
                + f"\n\n🔎 Le attività che hai *non* menzionato:\n- " + "\n- ".join(overige)
                + "\n\n📜 Vuoi il transcript? Digita `!ascolto_coshaifatto` qui o in DM."
            )
            await message.channel.send(f"✅ {message.author.mention} il tuo risultato è stato inviato in DM!", mention_author=False)
        except:
            await message.channel.send(f"⚠️ {message.author.mention} non riesco a mandarti un DM. Controlla le impostazioni.", mention_author=False)

    @commands.command(name="ascolto_coshaifatto")
    async def ascolto_coshaifatto(self, ctx):
        transcript = (
            "🎧 **Transcript – Cos’hai fatto?**\n\n"
            "Lunedì scorso sono andata al cinema insieme a due mie amiche. Abbiamo visto un film americano, una commedia...\n"
            "Ieri sera Luca e la sua compagnia sono andati a ballare e hanno invitato anche me. Ma io ero un po’ stanca...\n"
            "Un mese fa è venuta da Londra mia cugina Paola ed è rimasta un’intera settimana. Siamo usciti ogni sera...\n"
            "Domenica mattina, come ogni domenica, siamo andati a giocare a calcetto. Ma Giacomo si è dimenticato di prenotare il campo...\n"
            "L’estate scorsa siamo stati in Sardegna in vacanza. Abbiamo noleggiato una macchina e abbiamo fatto il giro dell’isola...\n"
            "Sai, l’altro ieri ho incontrato Mara per strada e siamo andati a bere un caffè. Mi ha parlato del suo lavoro e della sua vita."
        )
        try:
            await ctx.author.send(transcript)
            if ctx.guild:
                await ctx.reply("✅ Il transcript è stato inviato via DM!", mention_author=False)
        except:
            await ctx.reply("❌ Non posso inviarti un DM. Controlla le tue impostazioni.", mention_author=False)

def setup(bot):
    bot.add_cog(AscoltoCog(bot))

async def setup(bot):
    await bot.add_cog(AscoltoCog(bot))