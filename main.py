# main.py

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
import session_manager

load_dotenv()

# --- Normaliseer tekst ---
def normalize(text):
    text = unicodedata.normalize("NFKD", text).lower().strip()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = re.sub(r"[\s’‘`]", "", text)
    if text == "dell":
        return "dell'"
    return text

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Keep alive ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is online!"

@app.route('/ping')
def ping():
    return "pong", 200

@app.route('/health')
def health():
    return "OK", 200

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- OpenAI ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logging.error("❌ OPENAI_API_KEY ontbreekt!")
else:
    openai.api_key = openai_api_key
    logging.info("✅ OpenAI ingesteld.")

client = openai.OpenAI(api_key=openai_api_key)

# --- Globals ---
user_message_counts = {}
TARGET_CHANNEL_IDS = {
    1387910961846947991,
    1387571841442385951,
    1387569943746318386,
    1388667261761359932
}

# --- Bot setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.grammatica")
        await self.load_extension("cogs.wordle")
        await self.load_extension("cogs.quiz")
        self.loop.create_task(reminder_task())

bot = MyBot(command_prefix='!', intents=intents)

# --- Reminder op woensdagavond ---
async def reminder_task():
    await bot.wait_until_ready()
    channel_id = 1387552031631478945  # voice kanaal ID
    while not bot.is_closed():
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        if now.weekday() == 2 and now.hour == 20 and now.minute == 0:
            guild = discord.utils.get(bot.guilds)
            if not guild:
                await asyncio.sleep(60)
                continue
            voice_channel = guild.get_channel(channel_id)
            if not voice_channel:
                await asyncio.sleep(60)
                continue
            present = {m for m in voice_channel.members if not m.bot}
            all_members = {m for m in guild.members if not m.bot}
            absent = all_members - present
            for m in present:
                try:
                    await m.send("🎉 Grazie per aver partecipato al nostro incontro vocale!")
                except:
                    pass
            for m in absent:
                try:
                    await m.send("🕖 Promemoria – conversazione italiana mercoledì alle 19:00!")
                except:
                    pass
            await asyncio.sleep(60)
        await asyncio.sleep(30)

# --- on_ready ---
@bot.event
async def on_ready():
    logging.info(f"✅ Bot online als {bot.user}!")

# --- on_message: taalcorrectie & GPT in DM ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # ✅ Taalcorrectie in kanalen
    parent_id = message.channel.id
    if isinstance(message.channel, discord.Thread):
        parent_id = message.channel.parent_id

    if parent_id in TARGET_CHANNEL_IDS:
        try:
            detection = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Rispondi solo con 'ITALIANO' se il testo è italiano, altrimenti 'ALTRO'."},
                    {"role": "user", "content": message.content}
                ],
                max_tokens=5
            )
            if detection.choices[0].message.content.strip().upper() != "ITALIANO":
                return

            correction = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Correggi errori grammaticali, ortografici e di struttura. Rispondi con 'NO_CORRECTION_NEEDED' se è tutto perfetto."},
                    {"role": "user", "content": message.content}
                ]
            )
            reply = correction.choices[0].message.content.strip()
            if reply == "NO_CORRECTION_NEEDED":
                compliments = [
                    "✅ Ottimo lavoro! Continua così! 🇮🇹👏",
                    "✅ Perfetto! Sei sulla strada giusta! 🚀",
                    "✅ Benissimo! 🌟",
                    "✅ Sei fantastico/a! Continua a scrivere! ✍️❤️",
                    "✅ Super! La tua passione per l'italiano è evidente! 🎉"
                ]
                await message.reply(random.choice(compliments))
            elif reply.lower().strip() != message.content.lower().strip():
                await message.reply(f"📝 **{reply}**")
        except Exception as e:
            logging.error(f"Taalcorrectie fout: {e}")
        return

    # ✅ GPT in DM (max 5/dag)
    if isinstance(message.channel, discord.DMChannel):
        if session_manager.is_user_in_active_session(message.author.id):
            return  # Wordle of quiz sessie actief, geen GPT-reactie

        user_id = message.author.id
        today = datetime.datetime.utcnow().date().isoformat()
        key = f"{user_id}:{today}"
        count = user_message_counts.get(key, 0)

        if count >= 5:
            await message.channel.send("🚫 Hai raggiunto il limite di 5 messaggi per oggi. Riprova domani.")
            return

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Rispondi sempre in italiano."},
                    {"role": "user", "content": message.content}
                ]
            )
            await message.channel.send(response.choices[0].message.content.strip())
            user_message_counts[key] = count + 1
        except Exception as e:
            logging.error(f"Fout bij OpenAI-verzoek: {e}")
            await message.channel.send("⚠️ Probleem bij ophalen van antwoord.")
        return

    # ✅ Laat commando’s toe
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)

# --- Commando: ascolto_dai_accompagnami ---
@bot.command()
async def ascolto_dai_accompagnami(ctx):
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
            "**A:** Ok, allora ti faccio un’altra promessa... compro solo una cosa. Tra l'altro ho bisogno di un cappotto nuovo. La mia amica mi ha detto che hanno cose belissime a un prezzo stracciato.\n"
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

# --- Commando: ascolto_puttanesca ---
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
    try:
        await ctx.author.send(
            "🍝 **Curiosità:**\n"
            "La puttanesca è nata a Napoli negli anni '50. "
            "Il nome deriva dalle *puttane* (prostituees) che preparavano questo piatto veloce tra un cliente e l'altro!"
        )
        await ctx.reply("✅ Curiosità verzonden via DM!", mention_author=False)
    except discord.Forbidden:
        await ctx.reply("⚠️ Kan geen DM verzenden – check je DM-instellingen.", mention_author=False)

# --- Bot starten ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))