import discord
from discord.ext import commands
import random
import asyncio
import datetime
import json
import os
import logging
from openai import OpenAI
from session_manager import start_session, end_session, is_user_in_active_session

# OpenAI client en logging setup
client = OpenAI()
logging.basicConfig(level=logging.INFO)

TIJDSLIMIET = 90
DATA_PATH = "./data/frasi"
os.makedirs(DATA_PATH, exist_ok=True)

THEMA_LIJST = [
    "Al ristorante",
    "La mia giornata",
    "Parlare di emozioni",
    "Chiedere indicazioni",
    "Al telefono",
    "Fare la spesa e shopping",
    "Alla stazione / all’aeroporto",
    "Esprimere opinioni",
    "Invitare e rifiutare",
    "In caso di emergenza"
]

def normaliseer(zin):
    return ''.join(c.lower() for c in zin if c.isalnum() or c.isspace()).strip()

def weeknummer():
    return datetime.datetime.utcnow().isocalendar()[1]

def laad_zinnen(week: int):
    pad = f"{DATA_PATH}/week_{week}.json"
    if os.path.exists(pad):
        logging.info(f"Zinnenbestand geladen voor week {week}")
        with open(pad, "r", encoding="utf-8") as f:
            return json.load(f)
    logging.info(f"Geen bestaand zinnenbestand gevonden voor week {week}")
    return None

async def genereer_zinnen(week: int):
    thema = THEMA_LIJST[week % len(THEMA_LIJST)]
    logging.info(f"Zinnen worden gegenereerd voor thema: {thema}")

    prompt = f"""Crea una lista per studenti di livello B1 con:
- 25 frasi italiane corte e utili da usare nel contesto del tema "{thema}".
- Per ogni frase, fornisci:
    - la frase originale in italiano
    - la traduzione corretta in olandese
    - 1 o 2 alternative italiane accettabili (formulazioni simili).

Poi crea anche 10 frasi BONUS (diverse) sullo stesso tema, con la stessa struttura.

Rispondi in JSON con due chiavi:
- "standard": una lista di 25 oggetti {{"nl": "...", "it": "...", "varianti": ["...", ...]}}
- "bonus": una lista di 10 oggetti simili

Rispondi solo con JSON.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    data = json.loads(response.choices[0].message.content)

    # 🔍 Debug JSON voor week 29 (eenmalige inspectie)
    if week == 29:
        logging.info("✅ DEBUG: Gecontroleerde zinnen en varianten voor frasi:")
        logging.info(json.dumps(data, ensure_ascii=False, indent=2))

    with open(f"{DATA_PATH}/week_{week}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logging.info(f"Zinnen opgeslagen in week_{week}.json")
    return data

class Frasi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='frasi')
    async def start_frasi_game(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and ctx.channel.id != 123456789013345:
            await ctx.send("❗ Puoi usare questo comando solo in DM o nel thread designato.")
            return

        if is_user_in_active_session(ctx.author.id):
            await ctx.send("⏳ Hai già una sessione attiva.")
            return

        if not start_session(ctx.author.id, "frasi"):
            await ctx.send("⏳ Hai già una sessione attiva.")
            return

        try:
            current_week = weeknummer()
            data = laad_zinnen(current_week)
            if not data:
                await ctx.send("🧠 Sto preparando le frasi per questa settimana... Attendi un momento.")
                logging.info("Start met genereren van nieuwe zinnen via OpenAI")
                data = await genereer_zinnen(current_week)

            zinnen = data["standard"]
            bonus = data["bonus"]
            random.shuffle(zinnen)

            score = 0
            await ctx.send("🎯 Benvenuto/a al gioco *Frasi idiomatiche*! Hai 90 secondi per frase. Traduci in italiano le seguenti 10 frasi:")

            for i, zin in enumerate(zinnen[:10]):
                await ctx.send(f"📝 Frase {i+1}/10:\n**{zin['nl']}**")

                def check(m): return m.author == ctx.author and m.channel == ctx.channel

                try:
                    reply = await self.bot.wait_for('message', timeout=TIJDSLIMIET, check=check)
                    antwoord = normaliseer(reply.content)
                    correcte = [normaliseer(zin["it"])] + [normaliseer(v) for v in zin.get("varianti", [])]
                    if antwoord in correcte:
                        await ctx.send("✅ Corretto!")
                        score += 1
                    else:
                        await ctx.send(f"❌ Risposta sbagliata.\nLa risposta corretta era:\n**{zin['it']}**")
                except asyncio.TimeoutError:
                    await ctx.send(f"⏱️ Tempo scaduto! La risposta corretta era:\n**{zin['it']}**")

            await ctx.send(f"🧮 Hai ottenuto {score}/10 punti.")
            logging.info(f"Score basisronde: {score}/10 voor gebruiker {ctx.author}")

            if score >= 8:
                await ctx.send("🎉 Bravo! Hai diritto al **bonus round**!")

                random.shuffle(bonus)
                bonus_score = 0

                for i, zin in enumerate(bonus[:5]):
                    await ctx.send(f"\n🌟 Bonus frase {i+1}/5:\n**{zin['nl']}**")

                    try:
                        reply = await self.bot.wait_for('message', timeout=TIJDSLIMIET, check=check)
                        antwoord = normaliseer(reply.content)
                        correcte = [normaliseer(zin["it"])] + [normaliseer(v) for v in zin.get("varianti", [])]
                        if antwoord in correcte:
                            await ctx.send("✅ Corretto!")
                            bonus_score += 1
                        else:
                            await ctx.send(f"❌ Risposta sbagliata.\nLa risposta corretta era:\n**{zin['it']}**")
                    except asyncio.TimeoutError:
                        await ctx.send(f"⏱️ Tempo scaduto! La risposta corretta era:\n**{zin['it']}**")

                await ctx.send(f"⭐ Hai ottenuto {bonus_score}/5 nel bonus round.")
                if bonus_score >= 3:
                    await ctx.send("🏅 Hai guadagnato una **stella** per questa settimana!")
                else:
                    await ctx.send("💡 Non hai guadagnato la stella, ma ottimo tentativo!")

            await ctx.send("📚 Il gioco è terminato. Vuoi migliorare il tuo punteggio? Prova di nuovo domani!")
        except Exception as e:
            logging.exception("Er is een fout opgetreden tijdens het frasi-spel:")
            await ctx.send("❌ Er is iets misgegaan. Probeer het later opnieuw.")
        finally:
            end_session(ctx.author.id)

async def setup(bot):
    await bot.add_cog(Frasi(bot))