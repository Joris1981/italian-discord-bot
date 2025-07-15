import discord
from discord.ext import commands
import re
import unicodedata

class AscoltoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channels = {
            1394806609991598181,
            1388667261761359932,
            1394796805283385454
        }
        self.activities = [
            ("lei", ["\u00e8 andata al cinema"]),
            ("loro", ["hanno visto un film americano", "hanno visto un film"]),
            ("loro", ["sono andati a ballare"]),
            ("lei", ["\u00e8 rimasta a casa", "ha guardato la tv", "ha preferito stare a casa"]),
            ("lei", ["\u00e8 venuta da londra"]),
            ("loro", ["sono usciti ogni sera"]),
            ("loro", ["hanno fatto una piccola gita al mare"]),
            ("loro", ["hanno visitato un museo"]),
            ("loro", ["sono andati a giocare a calcetto"]),
            ("loro", ["hanno fatto jogging", "hanno fatto un po' di jogging"]),
            ("loro", ["sono stati in sardegna"]),
            ("loro", ["hanno noleggiato una macchina"]),
            ("loro", ["hanno fatto il giro dell'isola"]),
            ("loro", ["sono andati a bere un caff\u00e8"]),
            ("lei", ["ha parlato del suo lavoro", "ha chiesto di te"])
        ]

    def normalize(self, text):
        text = text.lower()
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        return text

    def match_activities(self, content):
        found = []
        used_indexes = set()
        ik_vorm_detected = False

        normalized = self.normalize(content)
        for i, (subject, variants) in enumerate(self.activities):
            for variant in variants:
                pattern = rf"\b(?:[a-z]+\s)?{re.escape(self.normalize(variant))}\b"
                if re.search(pattern, normalized):
                    found.append((subject, variant))
                    used_indexes.add(i)
                    break

        # Detectie van ik-vorm
        if re.search(r"\b(io|ho|sono andat[oa])\b", normalized):
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

        content = message.content.strip()
        if not content:
            return

        found, ik_vorm = self.match_activities(content)
        totaal = len(self.activities)
        gevonden = len(found)

        try:
            await message.reply(f"\U0001F4EC {message.author.mention} ti ho inviato un DM con il risultato del tuo ascolto!", mention_author=False)
        except:
            pass

        try:
            feedback = f"Hai identificato **{gevonden}** su **{totaal}** attivit\u00e0 chiave."
            if gevonden:
                feedback += "\n\n\u2705 Le attivit\u00e0 che hai menzionato correttamente:\n"
                for _, act in found:
                    feedback += f"\u2022 {act}\n"
            if gevonden < totaal:
                feedback += "\n\U0001F4CC Altre attivit\u00e0 presenti nel frammento erano:\n"
                for i, (s, vs) in enumerate(self.activities):
                    if i not in [self.activities.index((x, y)) for x, y in found]:
                        feedback += f"\u2022 {vs[0]}\n"
            if ik_vorm:
                feedback += ("\n\u26A0\uFE0F Hai usato la **prima persona singolare** (io), ma nel frammento si parlava di **altre persone**: `lei`, `lui`, `loro`.\n"
                             "Assicurati di usare i verbi coniugati correttamente per il soggetto.")

            feedback += "\n\nPer ricevere il transcript completo con soluzioni, digita `!ascolto_coshaifatto`."
            await message.author.send(feedback)
        except Exception as e:
            print(f"❌ Kan geen DM sturen: {e}")

    @commands.command(name="ascolto_coshaifatto")
    async def ascolto_transcript(self, ctx):
        transcript = (
            "\U0001F3A7 **Transcript – Cos’hai fatto?**\n\n"
            "Luned\u00ec scorso sono andata al cinema insieme a due mie amiche. Abbiamo visto un film americano... (volledige tekst hier)."
        )
        try:
            await ctx.author.send(transcript)
            await ctx.reply("\U0001F4EC Transcript inviato in DM!", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("\u26A0\uFE0F Non posso inviarti un DM. Controlla le impostazioni della privacy.", mention_author=False)


async def setup(bot):
    await bot.add_cog(AscoltoCog(bot))