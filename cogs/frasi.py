# frasi.py
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
from utils import normalize
import time

client = OpenAI()
logging.basicConfig(level=logging.INFO)

TIJDSLIMIET = 90
DATA_PATH = "/persistent/data/wordle/frasi"
SCORE_PATH = "/persistent/data/frasi_scores"
LEADERBOARD_THREAD_ID = 1395535498348593313
EXTRA_KANAAL_ID = 1388667261761359932
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(SCORE_PATH, exist_ok=True)

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

def weeknummer():
    return datetime.datetime.utcnow().isocalendar()[1]

def laad_zinnen(week: int):
    pad = f"{DATA_PATH}/week_{week}.json"
    if os.path.exists(pad):
        with open(pad, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def schrijf_zinnen(data, week):
    with open(f"{DATA_PATH}/week_{week}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def schrijf_score(user_id, username, score, duration, week):
    pad = f"{SCORE_PATH}/week_{week}.json"
    scores = {}
    if os.path.exists(pad):
        with open(pad, "r", encoding="utf-8") as f:
            scores = json.load(f)

    existing = scores.get(str(user_id))
    if not existing or (score > existing["score"] or (score == existing["score"] and duration < existing["duration"])):
        scores[str(user_id)] = {
            "username": username,
            "score": score,
            "duration": duration
        }
        with open(pad, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)

def laad_leaderboard(week):
    pad = f"{SCORE_PATH}/week_{week}.json"
    if not os.path.exists(pad):
        return []

    with open(pad, "r", encoding="utf-8") as f:
        scores = json.load(f)

    lijst = list(scores.values())
    lijst.sort(key=lambda x: (-x["score"], x["duration"]))
    return lijst

async def genereer_zinnen(week: int):
    thema = THEMA_LIJST[week % len(THEMA_LIJST)]
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

    response = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    data = json.loads(response.choices[0].message.content)
    await asyncio.to_thread(schrijf_zinnen, data, week)
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
            start_time = time.time()
            current_week = weeknummer()
            data = laad_zinnen(current_week)
            if not data:
                await ctx.send("🧠 Sto preparando le frasi per questa settimana... Attendi un momento.")
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
                    antwoord = normalize(reply.content)
                    correcte = [normalize(zin["it"])] + [normalize(v) for v in zin.get("varianti", [])]
                    if antwoord in correcte:
                        await ctx.send("✅ Corretto!")
                        score += 1
                    else:
                        msg = f"❌ Risposta sbagliata.\nLa risposta corretta era:\n**{zin['it']}**"
                        varianten = zin.get("varianti", [])
                        if varianten:
                            msg += "\nAltri possibili modi per dirlo:\n" + "\n".join(f"➡️ {v}" for v in varianten)
                        await ctx.send(msg)
                except asyncio.TimeoutError:
                    await ctx.send(f"⏱️ Tempo scaduto! La risposta corretta era:\n**{zin['it']}**")

            await ctx.send(f"🧮 Hai ottenuto {score}/10 punti.")

            bonus_score = 0
            if score >= 8:
                await ctx.send("🎉 Bravo! Hai diritto al **bonus round**!")
                random.shuffle(bonus)
                for i, zin in enumerate(bonus[:5]):
                    await ctx.send(f"\n🌟 Bonus frase {i+1}/5:\n**{zin['nl']}**")
                    try:
                        reply = await self.bot.wait_for('message', timeout=TIJDSLIMIET, check=check)
                        antwoord = normalize(reply.content)
                        correcte = [normalize(zin["it"])] + [normalize(v) for v in zin.get("varianti", [])]
                        if antwoord in correcte:
                            await ctx.send("✅ Corretto!")
                            bonus_score += 1
                        else:
                            msg = f"❌ Risposta sbagliata.\nLa risposta corretta era:\n**{zin['it']}**"
                            varianten = zin.get("varianti", [])
                            if varianten:
                                msg += "\nAltri possibili modi per dirlo:\n" + "\n".join(f"➡️ {v}" for v in varianten)
                            await ctx.send(msg)
                    except asyncio.TimeoutError:
                        await ctx.send(f"⏱️ Tempo scaduto! La risposta corretta era:\n**{zin['it']}**")

                await ctx.send(f"⭐ Hai ottenuto {bonus_score}/5 nel bonus round.")
                if bonus_score >= 3:
                    await ctx.send("🏅 Hai guadagnato una **stella** per questa settimana!")
                else:
                    await ctx.send("💡 Non hai guadagnato la stella, ma ottimo tentativo!")

            await ctx.send("📚 Il gioco è terminato. Vuoi migliorare il tuo punteggio? Prova di nuovo domani!")

            end_time = time.time()
            duration = int(end_time - start_time)
            schrijf_score(ctx.author.id, ctx.author.name, score, duration, current_week)

        except Exception as e:
            logging.exception("❌ Fout tijdens frasi-spel:")
            await ctx.send("❌ Er is iets misgegaan. Probeer het later opnieuw.")
        finally:
            end_session(ctx.author.id)

    @commands.command(name='frasi-leaderboard')
    async def toon_leaderboard(self, ctx):
        if ctx.channel.id not in [LEADERBOARD_THREAD_ID, EXTRA_KANAAL_ID]:
            return

        current_week = weeknummer()
        scores = laad_leaderboard(current_week)
        if not scores:
            await ctx.send("📭 Er zijn nog geen scores voor deze week.")
            return

        lines = [f"🏆 **Frasi idiomatiche – Leaderboard week {current_week}**"]
        for i, entry in enumerate(scores[:10], 1):
            lines.append(f"{i}. **{entry['username']}** – {entry['score']}/10")

        await ctx.send("\n".join(lines))

async def setup(bot):
    await bot.add_cog(Frasi(bot))