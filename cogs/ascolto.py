import discord
from discord.ext import commands
import re
import unicodedata

class AscoltoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channels = {1394806609991598181, 1388667261761359932, 1394796805283385454}
        self.activities = [
            ("lei", ["sono andata al cinema", "è andata al cinema"]),
            ("loro", ["hanno visto un film americano", "hanno visto un film"]),
            ("loro", ["sono andati a ballare"]),
            ("lei", ["è rimasta a casa", "ha guardato la tv", "ha preferito stare a casa"]),
            ("lei", ["è venuta da londra"]),
            ("loro", ["sono usciti ogni sera"]),
            ("loro", ["hanno fatto una piccola gita al mare"]),
            ("loro", ["hanno visitato un museo"]),
            ("loro", ["sono andati a giocare a calcetto"]),
            ("loro", ["hanno fatto jogging", "hanno fatto un po' di jogging"]),
            ("loro", ["sono stati in sardegna"]),
            ("loro", ["hanno noleggiato una macchina"]),
            ("loro", ["hanno fatto il giro dell'isola"]),
            ("loro", ["sono andati a bere un caffe"]),
            ("lei", ["ha parlato del suo lavoro", "ha chiesto di te"])
        ]

    def normalize_text(self, text):
        return unicodedata.normalize("NFD", text.lower()).encode("ascii", "ignore").decode("utf-8")

    def match_activities(self, content):
        found = []
        used_indexes = set()
        ik_vorm_detected = False

        normalized = self.normalize_text(content)
        for i, (subject, variants) in enumerate(self.activities):
            for variant in variants:
                if re.search(re.escape(self.normalize_text(variant)), normalized):
                    found.append((subject, variant))
                    used_indexes.add(i)
                    break

        # Ik-vorm detectie uitgebreid
        if re.search(r"\b(sono|ho)\s+(andat[oa]|visto|fatto|noleggiato|uscito|guardato|visitato|noleggiato|stato|giocato)", normalized):
            ik_vorm_detected = True

        return found, ik_vorm_detected

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id not in self.allowed_channels:
            return

        if message.content.startswith("!"):
            return

        content = message.content.lower().strip()
        if not content:
            return

        found, ik_vorm = self.match_activities(content)
        totaal = len(self.activities)
        gevonden = len(set([self.activities.index((x, y)) for x, y in found]))

        # Reactie in thread
        try:
            await message.reply(f"\U0001F4EC {message.author.mention} ti ho inviato un DM con il risultato del tuo ascolto!", mention_author=False)
        except:
            pass

        # DM
        try:
            feedback = f"Hai identificato **{gevonden}** su **{totaal}** attività chiave."
            if gevonden:
                feedback += "\n\n✅ Le attività che hai menzionato correttamente:\n"
                for _, act in found:
                    feedback += f"\u2022 {act}\n"
            if gevonden < totaal:
                feedback += "\n\U0001F4CC Altre attività presenti nel frammento erano:\n"
                for i, (s, vs) in enumerate(self.activities):
                    if i not in [self.activities.index((x, y)) for x, y in found]:
                        feedback += f"\u2022 {vs[0]}\n"
            if ik_vorm:
                feedback += ("\n\u26A0\uFE0F Hai usato la **prima persona singolare** (io), ma nel frammento si parlava di **altre persone**: `lei`, `lui`, `loro`.\n"
                             "Assicurati di usare i verbi coniugati correttamente per il soggetto.")

            feedback += "\n\nPer ricevere il transcript completo con soluzioni, digita `!ascolto_coshaifatto`."
            await message.author.send(feedback)
        except Exception as e:
            print(f"\u274C Kan geen DM sturen: {e}")

    @commands.command(name="ascolto_coshaifatto")
    async def ascolto_transcript(self, ctx):
        transcript = (
            "\U0001F3A7 **Transcript – Cos’hai fatto?**\n\n"
            "Lunedì scorso sono andata al cinema insieme a due mie amiche. Abbiamo visto un film americano, una commedia, ma ad essere sincera, non è stato tanto divertente.\n"
            "Ieri sera Luca e la sua compagnia sono andati a ballare e hanno invitato anche me. Ma io ero un po’ stanca e ho preferito stare a casa e guardare la tv.\n"
            "Un mese fa è venuta da Londra mia cugina Paola ed è rimasta un’intera settimana. Siamo usciti ogni sera, abbiamo fatto una piccola gita al mare, abbiamo anche visitato un museo; insomma un po’ di tutto!\n"
            "Domenica mattina, come ogni domenica, siamo andati a giocare a calcetto. Questa volta però Giacomo si è dimenticato di prenotare il campo; così, invece di giocare, abbiamo fatto solo un po’ di jogging!\n"
            "L’estate scorsa siamo stati in Sardegna in vacanza. Abbiamo noleggiato una macchina e abbiamo fatto il giro dell’isola. È stata una vacanza bellissima. Chi non ci è stato non sa cosa perde.\n"
            "Sai, l’altro ieri ho incontrato Mara per strada e siamo andati a bere un caffè. Mi ha parlato un po’ del suo lavoro, della sua vita. Poi ha chiesto di te, se stai con qualche ragazza. Secondo me, è ancora innamorata di te."
        )
        try:
            await ctx.author.send(transcript)
            await ctx.reply("\U0001F4EC Transcript inviato in DM!", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("\u26A0\ufe0f Non posso inviarti un DM. Controlla le impostazioni della privacy.", mention_author=False)

def setup(bot):
    bot.add_cog(AscoltoCog(bot))

async def setup(bot):
    await bot.add_cog(AscoltoCog(bot))