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
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(SCORE_PATH, exist_ok=True)

THEMA_LIJST = [
    "Al ristorante", "La mia giornata", "Parlare di emozioni", "Chiedere indicazioni", "Al telefono",
    "Fare la spesa e shopping", "Alla stazione / all’aeroporto", "Esprimere opinioni",
    "Invitare e rifiutare", "In caso di emergenza"
]

def weeknummer():
    return datetime.datetime.utcnow().isocalendar()[1]

def get_frasi_week_label():
    nummer = max(1, weeknummer() - 28)
    thema = THEMA_LIJST[(weeknummer() - 29) % len(THEMA_LIJST)]
    return f"Week {nummer}: {thema}"

def schrijf_score(user_id, username, score, duration, week):
    pad = f"{SCORE_PATH}/week_{week}.json"
    scores = {}
    if os.path.exists(pad):
        with open(pad, "r", encoding="utf-8") as f:
            scores = json.load(f)
    existing = scores.get(str(user_id))
    if not existing or (score > existing["score"] or (score == existing["score"] and duration < existing["duration"])):
        scores[str(user_id)] = {"username": username, "score": score, "duration": duration}
        with open(pad, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)

def laad_zinnen(week):
    pad = f"{DATA_PATH}/week_{week}.json"
    if os.path.exists(pad):
        with open(pad, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def schrijf_zinnen(data, week):
    with open(f"{DATA_PATH}/week_{week}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
    thema = THEMA_LIJST[(week - 29) % len(THEMA_LIJST)]
    prompt = f"""Crea una lista per studenti di livello B1 con:
- 25 frasi italiane corte e utili da usare nel contesto del tema "{thema}".
- Per ogni frase, fornisci:
    - la frase originale in italiano
    - la traduzione corretta in olandese
    - 1 o 2 alternative italiane accettabili

Poi crea anche 10 frasi BONUS (diverse) sullo stesso tema, con la stessa struttura.

Rispondi in JSON con due chiavi:
- "standard": una lista di 25 oggetti {{"nl": "...", "it": "...", "varianti": ["...", ...]}}
- "bonus": una lista di 10 oggetti simili

Rispondi solo con JSON.
"""
    response = await asyncio.to_thread(client.chat.completions.create,
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
            data = laad_zinnen(current_week) or await genereer_zinnen(current_week)
            zinnen = data["standard"]
            bonus = data["bonus"]
            random.shuffle(zinnen)

            score = 0
            await ctx.send("🎯 Iniziamo! Traduci in italiano le seguenti 10 frasi (90 secondi per frase):")

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
                        if zin.get("varianti"):
                            msg += "\nAltri possibili modi per dirlo:\n" + "\n".join(f"➡️ {v}" for v in zin["varianti"])
                        await ctx.send(msg)
                except asyncio.TimeoutError:
                    await ctx.send(f"⏱️ Tempo scaduto! Risposta corretta:\n**{zin['it']}**")

            await ctx.send(f"🧮 Punteggio: {score}/10")

            bonus_score = 0
            if score >= 8:
                await ctx.send("🎉 Bonus round!")
                random.shuffle(bonus)
                for i, zin in enumerate(bonus[:5]):
                    await ctx.send(f"🌟 Bonus {i+1}/5:\n**{zin['nl']}**")
                    try:
                        reply = await self.bot.wait_for('message', timeout=TIJDSLIMIET, check=check)
                        antwoord = normalize(reply.content)
                        correcte = [normalize(zin["it"])] + [normalize(v) for v in zin.get("varianti", [])]
                        if antwoord in correcte:
                            await ctx.send("✅ Corretto!")
                            bonus_score += 1
                        else:
                            msg = f"❌ Risposta sbagliata.\nLa risposta corretta era:\n**{zin['it']}**"
                            if zin.get("varianti"):
                                msg += "\nAltri possibili modi per dirlo:\n" + "\n".join(f"➡️ {v}" for v in zin["varianti"])
                            await ctx.send(msg)
                    except asyncio.TimeoutError:
                        await ctx.send(f"⏱️ Tempo scaduto! Risposta corretta:\n**{zin['it']}**")

                if bonus_score >= 3:
                    await ctx.send("🏅 Hai guadagnato una **stella**!")
                else:
                    await ctx.send("💡 Non hai ottenuto la stella questa volta.")

            await ctx.send("📚 Gioco terminato. Riprova domani per migliorare!")

            duration = int(time.time() - start_time)
            schrijf_score(ctx.author.id, ctx.author.name, score, duration, current_week)
        except Exception as e:
            logging.exception("❌ Er ging iets fout:")
            await ctx.send("❌ Probleem tijdens het spel.")
        finally:
            end_session(ctx.author.id)

    @commands.command(name='frasi-leaderboard')
    async def toon_leaderboard(self, ctx):
        current_week = weeknummer()
        label = get_frasi_week_label()
        scores = laad_leaderboard(current_week)
        if not scores:
            await ctx.send("📭 Geen scores beschikbaar voor deze week.")
            return

        lines = [f"🏆 **Frasi idiomatiche – Leaderboard {label}**"]
        for i, entry in enumerate(scores[:10], 1):
            ster = " ⭐" if entry["score"] >= 8 else ""
            lines.append(f"{i}. **{entry['username']}** – {entry['score']}/10{ster}")

        try:
            kanaal = await self.bot.fetch_channel(LEADERBOARD_THREAD_ID)
            await kanaal.send("\n".join(lines))
        except Exception:
            await ctx.send("⚠️ Kon het leaderboard niet posten in de vaste thread.")

    @commands.command(name="frasi-speelstatistiek")
    async def frasi_speelstatistiek(self, ctx):
        week = weeknummer()
        scores = laad_leaderboard(week)
        if not scores:
            await ctx.send("📊 Er zijn nog geen gespeelde beurten deze week.")
            return
        tekst = f"🎮 **Aantal gespeelde sessies – {get_frasi_week_label()}**\n\n"
        for entry in scores:
            tekst += f"• **{entry['username']}** – 1 keer gespeeld\n"
        await ctx.send(tekst)

    @commands.command(name="frasi-gemiddelde")
    async def frasi_gemiddelde(self, ctx):
        spelers_tijden = {}
        for bestand in os.listdir(SCORE_PATH):
            if bestand.endswith(".json"):
                with open(os.path.join(SCORE_PATH, bestand), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for uid, entry in data.items():
                        naam = entry.get("username", f"User {uid}")
                        tijd = entry.get("duration", 0)
                        if naam not in spelers_tijden:
                            spelers_tijden[naam] = []
                        spelers_tijden[naam].append(tijd)
        if not spelers_tijden:
            await ctx.send("📊 Geen tijdsgegevens beschikbaar.")
            return

        tekst = "⏱️ **Gemiddelde speeltijd per speler (basisronde):**\n"
        for naam, tijden in sorted(spelers_tijden.items()):
            gemiddelde = int(sum(tijden) / len(tijden))
            tekst += f"• **{naam}**: {gemiddelde} sec\n"
        await ctx.send(tekst)

async def setup(bot):
    await bot.add_cog(Frasi(bot))