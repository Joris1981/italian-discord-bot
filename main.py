import os
import discord
import openai
import asyncio
import datetime
import random
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- Keep-alive server voor Replit Deployment ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is online!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# --- OpenAI client setup ---
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Globals ---
user_message_counts = {}
TARGET_CHANNEL_IDS = {
    1387910961846947991,
    1387571841442385951,
    1388667261761359932
}

# --- Discord bot setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is nu online en klaar voor gebruik!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # --- Commando's eerst verwerken ---
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    # --- GPT DM Chat functie ---
    if isinstance(message.channel, discord.DMChannel):
        user_id = message.author.id
        today = datetime.datetime.utcnow().date().isoformat()
        key = f"{user_id}:{today}"

        if key not in user_message_counts:
            user_message_counts[key] = 0

        if user_message_counts[key] >= 5:
            await message.channel.send("🚫 Hai raggiunto il limite di 5 messaggi per oggi. Riprova domani. 🇮🇹")
            return

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Rispondi sempre in italiano, anche se la domanda è in un'altra lingua."},
                    {"role": "user", "content": message.content}
                ]
            )
            reply = response.choices[0].message.content.strip()
            if len(reply) > 1900:
                reply = reply[:1900] + "\n\n_(Risposta troncata per lunghezza.)_"
            await message.channel.send(reply)
            user_message_counts[key] += 1
        except Exception as e:
            print(f"❌ Fout bij OpenAI: {e}")
            await message.channel.send("⚠️ Er ging iets mis bij het ophalen van een antwoord.")
        return

    # --- Taalcorrectie in bepaalde kanalen/threads ---
    parent_id = message.channel.id
    if isinstance(message.channel, discord.Thread):
        parent_id = message.channel.parent_id

    if parent_id in TARGET_CHANNEL_IDS:
        try:
            # Stap 1: taal detectie
            detection = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Rispondi solo con 'ITALIANO' se il seguente testo è scritto in italiano. Altrimenti rispondi con 'ALTRO'."},
                    {"role": "user", "content": message.content}
                ],
                max_tokens=5
            )
            lang_reply = detection.choices[0].message.content.strip().upper()
            if lang_reply != "ITALIANO":
                return

            # Stap 2: grammaticale correctie
            correction = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Correggi solo errori grammaticali e ortografici. Ignora punteggiatura e maiuscole/minuscole. Se è tutto corretto, rispondi con: NO_CORRECTION_NEEDED."},
                    {"role": "user", "content": message.content}
                ],
                max_tokens=300
            )
            reply = correction.choices[0].message.content.strip()

            if reply == "NO_CORRECTION_NEEDED":
                compliments = [
                    "✅ Ottimo lavoro! Continua così! 🇮🇹👏",
                    "✅ Perfetto! Sei sulla strada giusta! 🚀",
                    "✅ Benissimo! 🌟",
                    "✅ Sei fantastico/a! Continua a scrivere! ✍️❤️"
                ]
                await message.reply(random.choice(compliments))
            elif reply.lower().strip() != message.content.lower().strip():
                await message.reply(f"📝 **{reply}**")

        except Exception as e:
            print(f"❌ Fout bij taalcorrectie: {e}")

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
            "**A:** Dai, accompagnami!...\n"
            "**B:** Sì, sì... Tu dici sempre così...\n"
            "**A:** Ok, allora ti faccio un’altra promessa...\n"
            "**B:** Cominciamo bene...\n\n"
            "---\n\n"
            "🗣️ **Modi di dire – Uitleg**\n\n"
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
    except discord.Forbidden:
        await ctx.reply("⚠️ Kan geen DM verzenden – check je DM-instellingen.", mention_author=False)

# --- Commando: curiosita_puttanesca ---
@bot.command()
async def curiosita_puttanesca(ctx):
    try:
        curiosita = (
            "🍝 **Curiosità:**\n"
            "La puttanesca è nata a Napoli negli anni '50. "
            "Il nome deriva dalle *puttane* (prostituees) che preparavano questo piatto veloce tra un cliente e l'altro!"
        )
        await ctx.author.send(curiosita)
        await ctx.reply("✅ Curiosità verzonden via DM!", mention_author=False)
    except discord.Forbidden:
        await ctx.reply("⚠️ Kan geen DM verzenden – check je DM-instellingen.", mention_author=False)

# --- Reminder bij nieuwe thread ---
@bot.event
async def on_thread_create(thread):
    if thread.parent_id == 1387910961846947991:
        for member in thread.guild.members:
            if not member.bot:
                try:
                    await member.send(
                        "🔔 **REMINDER / PROMEMORIA**\n\n"
                        "Ciao! 🇮🇹 Een nieuwe dag = een nieuwe kans om je Italiaans te oefenen!\n"
                        "👉 *Ogni giorno un po’ di italiano… e si migliora!*\n"
                        "Ci vediamo lì! 💬"
                    )
                except:
                    print(f"❌ Geen DM naar {member.name}")

# --- Woensdagavond herinnering voicekanaal ---
async def reminder_task():
    await bot.wait_until_ready()
    channel_id = 1387552031631478945  # voice channel ID
    while not bot.is_closed():
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # UTC+2
        if now.weekday() == 2 and now.hour == 20 and now.minute == 0:
            guild = discord.utils.get(bot.guilds)
            if not guild:
                await asyncio.sleep(60)
                continue
            voice_channel = guild.get_channel(channel_id)
            if not voice_channel:
                print("⚠️ Voicekanaal niet gevonden.")
                await asyncio.sleep(60)
                continue

            present = {m for m in voice_channel.members if not m.bot}
            all_members = {m for m in guild.members if not m.bot}
            absent = all_members - present

            for m in present:
                try:
                    await m.send(
                        "🎉 **Grazie per aver partecipato al nostro incontro vocale!**\n"
                        "Je doet het geweldig – blijf oefenen.\n"
                        "🇮🇹 *Parlare è il modo migliore per imparare.*\n"
                        "**Ci sentiamo presto!** 🎧"
                    )
                except:
                    pass

            for m in absent:
                try:
                    await m.send(
                        "🕖 **Promemoria – conversazione italiana!**\n"
                        "Ciao! 🇮🇹 We hebben je gemist vandaag. Volgende woensdag om **19u** weer een kans!\n"
                        "**Ci sentiamo presto!** 💬"
                    )
                except:
                    pass

            await asyncio.sleep(60)
        await asyncio.sleep(30)

# --- Bot starten ---
bot.loop.create_task(reminder_task())
bot.run(os.getenv("DISCORD_TOKEN"))