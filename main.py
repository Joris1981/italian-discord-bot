import os
import discord
import openai
import asyncio
import datetime
import random
import logging
import unicodedata
import re
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from session_manager import is_user_in_active_session
from utils import normalize
from langdetect import detect_langs

# === 🔁 Load env ===
if not load_dotenv():
    logging.warning("⚠️ Kon .env-bestand niet laden.")

# === 📂 Zorg dat wordle-map en frasi-map bestaan ===
os.makedirs("/persistent/data/wordle", exist_ok=True)
os.makedirs("/persistent/data/wordle/frasi", exist_ok=True)

# === 🦥 Logging ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# === 🌐 Keep-alive server ===
app = Flask(__name__)
@app.route('/')
def home(): return "✅ Bot is online!"
@app.route('/ping')
def ping(): return "pong", 200
@app.route('/health')
def health(): return "OK", 200

def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), use_reloader=False)
def keep_alive(): Thread(target=run).start()

# === 🔑 OpenAI setup ===
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logging.error("❌ OPENAI_API_KEY ontbreekt!")
else:
    openai.api_key = openai_api_key
    logging.info("✅ OpenAI ingesteld.")
client = openai.OpenAI(api_key=openai_api_key)

# === 🌍 Globals ===
user_message_counts = {}
MAX_CORRECTION_LENGTH = 2000
EXPLICIT_CORRECTION_REPLIES = {
    1394015695246725303: (
        "Hai ragione, a volte il feedback diretto funziona e altre volte no… Ci dispiace! 🙏\n"
        "Purtroppo il bot non sempre riesce a rispondere correttamente, per motivi diversi (ad esempio quando ci sono parole o strutture in olandese).\n"
        "Per questo abbiamo aggiunto il comando `!correggi_ultimo`, così puoi far correggere il tuo ultimo messaggio manualmente se il bot non ha reagito da solo.\n"
        "Anche il bot, in fondo, è (quasi) umano 😄"
    )
}
REACTION_CHANNELS = {
    1388667261761359932, 1387910961846947991, 1387571841442385951,
    1387569943746318386, 1390410564093743285, 1387853018845810891
}
REACTION_THREADS = {1387594096759144508, 1387571841442385951}

# === 🤖 Bot class ===
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.members = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        for extension in ["cogs.grammatica", "cogs.wordle", "cogs.quiz", "cogs.lyrics", "cogs.ascolto", "cogs.frasi", "cogs.reminder", "cogs.coniuga", "cogs.post"]:
            try:
                await self.load_extension(extension)
                logging.info(f"✅ Extension geladen: {extension}")
            except Exception as e:
                logging.error(f"❌ Fout bij laden van {extension}: {e}")
        self.loop.create_task(reminder_task())

bot = MyBot(command_prefix='!', intents=intents, case_insensitive=True)

# === 📜 Bot events ===
@bot.event
async def on_ready():
    logging.info(f"✅ Bot is online als {bot.user}")
    logging.info("📜 Geregistreerde commando's:")
    for command in bot.commands:
        logging.info(f"- {command.name}")
    logging.info("🌐 Bot is klaar om te corrigeren en te chatten!")

# === 🔔 Reminder woensdagavond ===
async def reminder_task():
    await bot.wait_until_ready()
    kanaal_id = 1387552031631478945
    while not bot.is_closed():
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        if now.weekday() == 2 and now.hour == 20 and now.minute == 0:
            guild = discord.utils.get(bot.guilds)
            if not guild: await asyncio.sleep(60); continue
            vc = guild.get_channel(kanaal_id)
            if not vc: await asyncio.sleep(60); continue
            present = {m for m in vc.members if not m.bot}
            all_members = {m for m in guild.members if not m.bot}
            absent = all_members - present
            for m in present:
                try: await m.send("🎉 Grazie per aver partecipato al nostro incontro vocale!")
                except: pass
            for m in absent:
                try: await m.send("🕖 Promemoria – conversazione italiana mercoledì alle 19:00!")
                except: pass
            await asyncio.sleep(60)
        await asyncio.sleep(30)

# === 📥 on_message ===
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    if len(message.content.strip()) < 10 or message.content.lower().strip() in {"quiz", "ciao", "grazie", "ok"}:
        return

    if len(message.content) > MAX_CORRECTION_LENGTH:
        await message.channel.send("⚠️ Il messaggio è troppo lungo per una correzione automatica. Potresti dividerlo in parti più piccole?")
        return

    # Geen correctie tijdens actieve sessie
    if is_user_in_active_session(message.author.id):
        if isinstance(message.channel, discord.DMChannel):
            return
        if message.channel.id in REACTION_CHANNELS or (
            hasattr(message.channel, 'parent_id') and message.channel.parent_id in REACTION_THREADS
        ):
            return

    if message.channel.id == 1394796805283385454:
        return

    if message.id in EXPLICIT_CORRECTION_REPLIES:
        try:
            await message.reply(EXPLICIT_CORRECTION_REPLIES[message.id], mention_author=False)
        except Exception as e:
            logging.error(f"❌ Fout bij automatische uitleg-reply: {e}")

    try:
        langs = detect_langs(message.content)
        is_dutch_dominant = any(l.lang == "nl" and l.prob > 0.95 for l in langs)
    except Exception:
        is_dutch_dominant = False

    if is_dutch_dominant:
        await message.reply("💬 Prova a scrivere in italiano, così posso aiutarti a migliorare e imparare di più! 🇮🇹", suppress_embeds=True)
        return

    if isinstance(message.channel, discord.DMChannel) and is_user_in_active_session(message.author.id):
        return

    try:
        correction = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "Correggi il testo a livello B1. Correggi errori grammaticali, lessicali, ortografici o strutturali. "
                    "Migliora la fluidità anche se il testo è già corretto. Se il testo è perfetto, rispondi con 'NO_CORRECTION_NEEDED'."
                )},
                {"role": "user", "content": message.content}
            ]
        )
    except Exception as e:
        logging.error(f"❌ Fout bij OpenAI API call: {e}")
        await message.channel.send("⚠️ Er ging iets mis bij het ophalen van de correzione automatica.")
        return

    reply = correction.choices[0].message.content.strip()

    if reply.upper() == "NO_CORRECTION_NEEDED":
        if isinstance(message.channel, discord.DMChannel) and is_user_in_active_session(message.author.id):
            return
        compliments = [
            "✅ Ottimo lavoro! Continua così! 🇮🇹👏",
            "✅ Perfetto! Sei sulla strada giusta! 🚀",
            "✅ Benissimo! 🌟",
            "✅ Sei fantastico/a! Continua a scrivere! ✍️❤️",
            "✅ Super! La tua passione per l'italiano è evidente! 🎉",
            "✅ Eccellente! Ogni giorno migliori! 🌈",
            "✅ Che bello vedere i tuoi progressi! 💪"
        ]
        await message.reply(random.choice(compliments), mention_author=False)
        return

    else:
        await message.reply(f"\U0001F4DD **{reply}**", suppress_embeds=True)

        if message.channel.id in REACTION_CHANNELS or (
            hasattr(message.channel, 'parent_id') and message.channel.parent_id in REACTION_THREADS
        ):
            try:
                feedback = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": (
                            "Analizza la versione originale del testo e quella corretta. "
                            "Non ripetere le frasi. "
                            "Elenca solo gli errori riscontrati o i miglioramenti stilistici effettuati. "
                            "Per ogni punto, indica se si tratta di un errore grammaticale, lessicale, stilistico o di registro. "
                            "Spiega brevemente perché era sbagliato o meno naturale e proponi la forma corretta o più adeguata. "
                            "Usa questo formato:\n"
                            "❌ *Tipo di errore:* spiegazione\n"
                            "✅ **Corretto:** versione migliorata\n"
                            "Usa Markdown per la formattazione. Rispondi solo se ci sono modifiche rispetto all'originale."
                            "Evita risposte vaghe come 'versione corretta'. Specifica sempre gli errori e le correzioni. "
                            "Non rispondere con 'nessun errore' o 'nessuna correzione necessaria'."
                            "⚠️ Se non ci sono errori, NON scrivere nulla. Lascia la risposta vuota."
                        )},
                        {"role": "user", "content": f"Testo originale:\n{message.content}\n\nVersione corretta:\n{reply}"}
                    ]
                )

                feedback_text = feedback.choices[0].message.content.strip()
                if feedback_text:
                    embed = discord.Embed(
                        title="🧠 Feedback sugli errori",
                        description=feedback_text,
                        color=0x2ECC71
                    )
                    embed.set_footer(text="Correzioni automatiche – ItalianoBot")
                    await message.reply(embed=embed, mention_author=False)

            except Exception as e:
                logging.error(f"❌ Fout bij feedback reactie: {e}")

    # GPT DM Chat
    if isinstance(message.channel, discord.DMChannel):
        if is_user_in_active_session(message.author.id):
            return

        user_id = message.author.id
        today = datetime.datetime.utcnow().date().isoformat()
        key = f"{user_id}:{today}"
        count = user_message_counts.get(key, 0)

        if count >= 5:
            await message.channel.send("🚫 Hai raggiunto il limite di 5 messaggi per oggi. Riprova domani.")
            return

        try:
            reply = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Rispondi sempre in italiano."},
                    {"role": "user", "content": message.content}
                ]
            )
            await message.channel.send(reply.choices[0].message.content.strip())
            user_message_counts[key] = count + 1
        except Exception as e:
            logging.error(f"GPT DM fout: {e}")
            await message.channel.send("⚠️ Er ging iets mis bij het ophalen van uw antwoord.")

# === ⛑️ Handmatige correctie ===
@bot.command(name='correggi_id')
@commands.has_permissions(manage_messages=True)
async def correggi_id(ctx, message_id: int):
    try:
        msg = None
        try:
            msg = await ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            pass

        if not msg:
            for channel in ctx.guild.text_channels:
                try:
                    msg = await channel.fetch_message(message_id)
                    if msg:
                        break
                except:
                    continue

        if not msg:
            await ctx.reply("❌ Geen bericht gevonden met dat ID in dit kanaal of andere tekstkanalen.", mention_author=False)
            return

        if msg.author.bot or msg.content.startswith("!"):
            await ctx.reply("⚠️ Dat bericht kan niet worden gecorrigeerd.", mention_author=False)
            return

        await on_message(msg)

    except Exception as e:
        logging.error(f"Fout bij !correggi_id: {e}")
        await ctx.reply("⚠️ Er ging iets mis bij het ophalen van het bericht.", mention_author=False)

@bot.command(name='correggi_ultimo')
async def correggi_ultimo(ctx, member: discord.Member = None):
    target_id = member.id if member and ctx.author.guild_permissions.manage_messages else ctx.author.id
    async for msg in ctx.channel.history(limit=50):
        if msg.author.id == target_id and not msg.content.startswith("!") and not msg.author.bot:
            await on_message(msg)
            return
    await ctx.reply("⚠️ Geen geschikt recent bericht gevonden om te corrigeren.", mention_author=False)

# === 🎧 Commando’s ===
@bot.command()
async def ascolto_dai_accompagnami(ctx):
    print(f"🔔 Commando 'ascolto_dai_accompagnami' uitgevoerd door: {ctx.author}")
    try:
        await ctx.author.send(
            "📘 **Transcript – \"Dai, accompagnami – una conversazione tra amici\"**\n\n"
            "🎧 Fragment: kort gesprek tussen twee vrienden over plannen en shoppen.\n\n"
            "**A:** Che fai oggi pomeriggio?\n"
            "**B:** Non lo so ancora, ma credo che andrò in studio a dipingere. Sono due settimane che non faccio niente.\n"
            "**A:** Te lo chiedo perché mi hanno detto che oggi in centro inaugura un nuovo negozio che si chiama Zara...\n"
            "**B:** Anche oggi mi fai andare in giro per vetrine?...\n"
            "**B:** Io non ho tanta voglia. Due giorni fa siamo stati tutto il pomeriggio al centro commerciale e oggi fare il bis... non è che mi attiri tanto.\n"
            "**A:** Dai, accompagnami!... Ti prometto che non compro niente. Andiamo solo a dare un'occhiata.\n"
            "**B:** Sì, sì... Tu dici sempre così... e poi non sai resistere: una nuova gonna, un paio di pantaloni, un nuovo paio di ...\n"
            "**A:** Ok, allora ti faccio un’altra promessa... compro solo una cosa. Tra l'altro ho bisogno di un cappotto nuovo. La mia amica mi ha detto che hanno cose bellissime a un prezzo stracciato.\n"
            "**B:** Cominciamo bene...\n\n"
            "---\n\n"
            "🗣️ **Modi di dire – Uitleg**\n"
            "🔹 `andare in giro per vetrine` → rondkijken in winkels\n"
            "🔹 `fare il bis` → iets opnieuw doen\n"
            "🔹 `dare un’occhiata` → een blik werpen\n"
            "🔹 `a un prezzo stracciato` → voor een spotprijs\n"
            "🔹 `cominciamo bene...` → sarcastisch: dat begint goed\n\n"
            "---\n"
            "🎯 **Quiz Antwoorden:**\n"
            "1️⃣ = 🅱️\n2️⃣ = 🅰️\n3️⃣ = 🅱️\n4️⃣ = 🅱️\n5️⃣ = 🅱️\n6️⃣ = 🅱️\n7️⃣ = 🅱️"
        )
        await ctx.reply("✅ Je transcript is verzonden via DM!", mention_author=False)
    except discord.Forbidden:
        await ctx.reply("⚠️ Kan geen DM verzenden – check je instellingen.", mention_author=False)

@bot.command()
async def ascolto_puttanesca(ctx):
    print(f"🔔 Commando 'ascolto_puttanesca' uitgevoerd door: {ctx.author}")

    try:
        deel_1 = (
            "📘 **Transcript – Spaghetti alla puttanesca**\n\n"
            "🎧 _Questa ricetta è originaria dell'isola di Ischia e ha tutto il sapore del sud._\n\n"
            "**Ingredienti:**\n"
            "- Aglio, uno spicchio tritato\n"
            "- Peperoncino, un pizzico\n"
            "- Olio extravergine d'oliva, due cucchiai\n"
            "- Pomodori pelati, 400g\n"
            "- Filetti d'acciuga, 4 (sbriciolati)\n"
            "- Olive nere snocciolate, 100g\n"
            "- Capperi, un cucchiaio\n"
            "- Sale e pepe nero\n"
            "- Spaghettini, 450g\n"
            "- Vino: bianco secco tipo Vernaccia\n\n"
            "**Preparazione:**\n"
            "1. Soffriggere aglio e peperoncino in olio\n"
            "2. Aggiungere pomodori, capperi, olive – cuocere 5 min\n"
            "3. Aggiungere acciughe, sale e pepe – cuocere 15-20 min\n"
            "4. Cuocere pasta, mescolare e servire"
        )

        deel_2 = (
            "---\n\n"
            "*Questa ricetta è originaria dell'isola di Ischia e ha tutto il sapore del sud. "
            "Ingredienti: Aglio, uno spicchio tritato. Peperoncino, un pizzico. Olio extravergine d'oliva, due cucchiai. "
            "Pomodori pelati, 400 grammi. Quattro filetti d'acciuga sbriciolati con la forchetta. Olive nere snocciolate e spezzettate, "
            "100 grammi. Capperi, un cucchiaio. Sale e pepe nero. Spaghettini, 450 grammi. Vino, un bianco secco tipo Vernaccia. "
            "Preparazione: 10 minuti. Cottura: 25-30 minuti. Livello di difficoltà: semplice. "
            "Mettete l'olio in una padella e fatevi soffriggere aglio e peperoncino finché l'aglio non avrà preso un bel colore dorato. "
            "Unite quindi i pomodori, i capperi e le olive e fate cuocere per 5 minuti circa. Aggiungete i filetti di acciuga, "
            "insaporite con sale e pepe e lasciate cuocere a fuoco moderato per altri 15-20 minuti. "
            "Cuocete gli spaghetti al dente, scolate, condite e servite.*"
        )

        deel_3 = (
            "---\n\n"
            "🧠 **Soluzioni Quiz:**\n"
            "1️⃣ = 🅰️\n2️⃣ = 🅰️\n3️⃣ = 🅰️\n4️⃣ = 🅰️\n5️⃣ = 🅱️\n6️⃣ = 🅱️\n\n"
            "👉 *Bravissimo/a!* Continua a esercitarti e... buon appetito 🇮🇹"
        )

        await ctx.author.send(deel_1)
        await ctx.author.send(deel_2)
        await ctx.author.send(deel_3)

        await ctx.reply("✅ Je transcript, recept en quizoplossingen zijn verzonden via DM!", mention_author=False)
        print(f"📨 DM succesvol verzonden naar: {ctx.author}")

    except discord.Forbidden:
        await ctx.reply("⚠️ Kan geen DM verzenden – check je DM-instellingen.", mention_author=False)
        print(f"❌ DM gefaald – vermoedelijk geblokkeerd door: {ctx.author}")
    except Exception as e:
        await ctx.reply("⚠️ Er ging iets mis bij het verzenden van de DM.", mention_author=False)
        print(f"❌ Onverwachte fout bij ascolto_puttanesca: {e}")

# --- Commando: curiosita_puttanesca ---
@bot.command()
async def curiosita_puttanesca(ctx):
    print(f"🔔 Commando 'curiosita_puttanesca' uitgevoerd door: {ctx.author}")
    try:
        await ctx.author.send(
            "🍝 **Curiosità:**\n"
            "La puttanesca è nata a Napoli negli anni '50. "
            "Il nome deriva dalle *puttane* (prostituees) che preparavano questo piatto veloce tra un cliente e l'altro!"
        )
        await ctx.reply("✅ Curiosità verzonden via DM!", mention_author=False)
    except discord.Forbidden:
        await ctx.reply("⚠️ Kan geen DM verzenden – check je DM-instellingen.", mention_author=False)
        
# --- Commando: ascolto_cristina ---
@bot.command(name='ascolto_cristina')
async def ascolto_cristina(ctx):
    print(f"🔔 Commando 'ascolto_cristina' uitgevoerd door: {ctx.author}")
    try:
        await ctx.author.send(
            "**📄 Transcript – 'Cristina e la sua famiglia'**\n"
            "Mi chiamo Cristina, ho 11 anni e vivo in un paesino nella campagna toscana.\n"
            "Mio padre si chiama Giacomo ed è un apicoltore che produce del miele dolce e squisito: lui mi dice sempre che le api sono degli insetti preziosi che bisogna sempre proteggere.\n"
            "Mia madre, Liliana, è un'illustratrice di libri per bambini che nel tempo libero ama leggere e fare giardinaggio.\n"
            "Ho una sorella più piccola di me che si chiama Ginevra ed ha 7 anni: trascorriamo molto tempo insieme a giocare e a disegnare.\n"
            "Ogni giorno dopo la scuola vado a trovare la nonna Berta che abita vicino a noi: con lei mi piace preparare tanti dolci, come ad esempio la crostata di fragole e i biscotti.\n\n"
            "**✅ Soluzioni quiz**\n"
            "1️⃣ = 🅱️\n"
            "2️⃣ = 🅰️\n"
            "3️⃣ = 🅱️\n"
            "4️⃣ = 🅱️\n"
            "5️⃣ = 🅰️\n"
            "6️⃣ = 🅱️"
        )
        await ctx.reply("📬 Ti ho inviato il transcript e le soluzioni in DM!", mention_author=False)
    except discord.Forbidden:
        await ctx.reply("❌ Non posso inviarti un DM. Controlla le tue impostazioni di privacy.", mention_author=False)

# === ▶️ Start de bot ===
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))