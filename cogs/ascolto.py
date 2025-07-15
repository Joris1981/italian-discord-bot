import discord
from discord.ext import commands
import re

class AscoltoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channels = {1394806609991598181, 1388667261761359932, 1394796805283385454}
        self.keywords = {
            "cinema": "Lei è andata al cinema insieme a sue amiche",
            "film": "Loro hanno visto un film",
            "ballare": "Loro sono andati a ballare",
            "casa": "Lei è rimasta a casa",
            "tv": "Lei ha guardato la TV",
            "londra": "La cugina di Paola è venuta da Londra",
            "gita al mare": "Loro hanno fatto una piccola gita al mare",
            "museo": "Loro hanno visitato un museo",
            "calcetto": "Loro sono andati a giocare a calcetto",
            "jogging": "Loro hanno fatto un po’ di jogging",
            "sardegna": "Loro sono stati in Sardegna",
            "vacanza": "Loro sono stati in vacanza",
            "macchina": "Loro hanno noleggiato una macchina",
            "giro": "Loro hanno fatto il giro dell’isola",
            "caffè": "Loro sono andati a bere un caffè",
            "lavoro": "Lei ha parlato un po’ del suo lavoro",
            "vita": "Lei ha anche parlato della sua vita",
            "chiesto": "Lei ha chiesto di te, se stai con qualche ragazza"
        }

    def detect_keywords(self, content):
        normalized = content.lower()
        found = []
        ik_vorm_detected = False

        for keyword, full_sentence in self.keywords.items():
            if keyword in normalized:
                found.append((keyword, full_sentence))

        # detectie van ik-vorm (prima persona)
        if re.search(r"\b(io|sono|ho)\b", normalized):
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

        found, ik_vorm = self.detect_keywords(content)
        totaal = len(set(self.keywords.keys()))
        gevonden = len(set([k for k, _ in found]))

        # Reactie in thread
        try:
            await message.reply(f"📬 {message.author.mention} ti ho inviato un DM con il risultato del tuo ascolto!", mention_author=False)
        except:
            pass

        # DM
        try:
            feedback = f"Hai identificato **{gevonden}** su **{totaal}** attività chiave."
            if gevonden >= 6:
                feedback += "\n\n🎉 Complimenti, hai trovato molte attività chiave!"
            if gevonden:
                feedback += "\n\n✅ Le attività che hai menzionato correttamente:\n"
                for _, full in found:
                    feedback += f"• {full}\n"
            if gevonden < totaal:
                feedback += "\n📌 Attività che mancavano nel tuo ascolto:\n"
                for keyword, full in self.keywords.items():
                    if keyword not in [k for k, _ in found]:
                        feedback += f"• {full}\n"
            if ik_vorm:
                feedback += ("\n⚠️ Hai usato forme verbali legate alla **prima persona singolare**. "
                             "Ricorda che nel frammento non si parlava di 'io', ma di **lei** o **loro**. "
                             "Controlla bene i soggetti e adatta i verbi di conseguenza.")

            feedback += "\n\nPer ricevere il transcript completo con soluzioni, digita `!ascolto_coshaifatto`."

            await message.author.send(feedback)
        except Exception as e:
            print(f"❌ Kan geen DM sturen: {e}")

    @commands.command(name="ascolto_coshaifatto")
    async def ascolto_transcript(self, ctx):
        transcript = (
            "🎧 **Transcript – Cos’hai fatto?**\n\n"
            "Lunedì scorso sono andata al cinema insieme a due mie amiche. Abbiamo visto un film americano, una commedia, ma ad essere sincera, non è stato tanto divertente.\n"
            "Ieri sera Luca e la sua compagnia sono andati a ballare e hanno invitato anche me. Ma io ero un po’ stanca e ho preferito stare a casa e guardare la tv.\n"
            "Un mese fa è venuta da Londra mia cugina Paola ed è rimasta un’intera settimana. Siamo usciti ogni sera, abbiamo fatto una piccola gita al mare, abbiamo anche visitato un museo; insomma un po’ di tutto!\n"
            "Domenica mattina, come ogni domenica, siamo andati a giocare a calcetto. Questa volta però Giacomo si è dimenticato di prenotare il campo; così, invece di giocare, abbiamo fatto solo un po’ di jogging!\n"
            "L’estate scorsa siamo stati in Sardegna in vacanza. Abbiamo noleggiato una macchina e abbiamo fatto il giro dell’isola. È stata una vacanza bellissima. Chi non ci è stato non sa cosa perde.\n"
            "Sai, l’altro ieri ho incontrato Mara per strada e siamo andati a bere un caffè. Mi ha parlato un po’ del suo lavoro, della sua vita. Poi ha chiesto di te, se stai con qualche ragazza. Secondo me, è ancora innamorata di te."
        )
        try:
            await ctx.author.send(transcript)
            await ctx.reply("📬 Transcript inviato in DM!", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("⚠️ Non posso inviarti un DM. Controlla le impostazioni della privacy.", mention_author=False)

async def setup(bot):
    await bot.add_cog(AscoltoCog(bot))