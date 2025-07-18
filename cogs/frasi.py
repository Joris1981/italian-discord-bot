# frasi.py
import discord
from discord.ext import commands, tasks
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
DATA_PATH = "./data/wordle/frasi"
SCORE_PATH = "./data/frasi_scores"
LEADERBOARD_THREAD_ID = 1395535498348593313
TOEGESTANE_KANALEN = [123456789013345, 1388667261761359932]
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(SCORE_PATH, exist_ok=True)

THEMA_LIJST = [
    "In caso di emergenza", "La mia giornata", "Parlare di emozioni",
    "Chiedere indicazioni", "Al telefono", "Fare la spesa e shopping",
    "Alla stazione / all’aeroporto", "Esprimere opinioni", "Invitare e rifiutare",
    "Al ristorante"
]

def weeknummer():
    return datetime.datetime.utcnow().isocalendar()[1]

def get_frasi_week_label():
    nummer = max(1, weeknummer() - 28)
    thema = THEMA_LIJST[(weeknummer() - 29) % len(THEMA_LIJST)]
    return f"Week {nummer}: {thema}"

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

def laad_scores():
    alles = {}
    for bestand in os.listdir(SCORE_PATH):
        if bestand.endswith(".json"):
            with open(os.path.join(SCORE_PATH, bestand), "r", encoding="utf-8") as f:
                data = json.load(f)
                for uid, inhoud in data.items():
                    alles.setdefault(uid, {"naam": inhoud["username"], "tijd": 0, "beurten": 0})
                    alles[uid]["tijd"] += inhoud["duration"]
                    alles[uid]["beurten"] += 1
    return alles

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
    - 1 o 2 alternative italiane accettabili.

Poi crea anche 10 frasi BONUS sullo stesso tema.

Rispondi in JSON con due chiavi:
- "standard": una lista di 25 oggetti {{"nl": "...", "it": "...", "varianti": ["...", ...]}}
- "bonus": una lista di 10 oggetti simili
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
        self.weekelijkse_herinnering.start()

    @commands.command(name='frasi')
    async def start_frasi_game(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and ctx.channel.id not in TOEGESTANE_KANALEN:
            await ctx.send("❗ Puoi usare questo comando solo in DM o nei canali autorizzati.")
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
                await ctx.send("🧠 Sto preparando le frasi per questa settimana...")
                data = await genereer_zinnen(current_week)

            zinnen = data["standard"]
            bonus = data["bonus"]
            random.shuffle(zinnen)

            score = 0
            await ctx.send("🎯 Traduci in italiano le seguenti 10 frasi:")

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
                        msg = f"❌ Risposta sbagliata.\n**{zin['it']}**"
                        varianten = zin.get("varianti", [])
                        if varianten:
                            msg += "\nAltri possibili modi per dirlo:\n" + "\n".join(f"➡️ {v}" for v in varianten)
                        await ctx.send(msg)
                except asyncio.TimeoutError:
                    await ctx.send(f"⏱️ Tempo scaduto! **{zin['it']}**")

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
                            msg = f"❌ Risposta sbagliata.\n**{zin['it']}**"
                            varianten = zin.get("varianti", [])
                            if varianten:
                                msg += "\nAltri possibili modi per dirlo:\n" + "\n".join(f"➡️ {v}" for v in varianten)
                            await ctx.send(msg)
                    except asyncio.TimeoutError:
                        await ctx.send(f"⏱️ Tempo scaduto! **{zin['it']}**")

                await ctx.send(f"⭐ Bonus score: {bonus_score}/5")
                if bonus_score >= 3:
                    await ctx.send("🏅 Hai guadagnato una **stella**!")

            await ctx.send("📚 Il gioco è finito. Puoi riprovare domani!")

            end_time = time.time()
            schrijf_score(ctx.author.id, ctx.author.name, score, int(end_time - start_time), current_week)
        except Exception as e:
            logging.exception("Fout tijdens frasi-spel")
            await ctx.send("❌ Er is iets fout gegaan.")
        finally:
            end_session(ctx.author.id)

    @commands.command(name='frasi-leaderboard')
    async def toon_leaderboard(self, ctx):
        scores = laad_leaderboard(weeknummer())
        if not scores:
            await ctx.send("📭 Nessun punteggio per questa settimana.")
            return
        titel = get_frasi_week_label()
        lines = [f"🏆 **Frasi idiomatiche – Leaderboard {titel}**"]
        for i, entry in enumerate(scores[:10], 1):
            ster = " ⭐" if entry['score'] >= 8 else ""
            lines.append(f"{i}. **{entry['username']}** – {entry['score']}/10{ster}")
        try:
            thread = await self.bot.fetch_channel(LEADERBOARD_THREAD_ID)
            await thread.send("\n".join(lines))
        except:
            await ctx.send("⚠️ Er is iets misgegaan bij het posten van het leaderboard.")

    @commands.command(name="frasi-speelstatistiek")
    async def speelstatistiek(self, ctx):
        week = weeknummer()
        pad = f"{SCORE_PATH}/week_{week}.json"
        if not os.path.exists(pad):
            await ctx.send("📊 Nessuna partecipazione registrata.")
            return
        with open(pad, "r", encoding="utf-8") as f:
            data = json.load(f)
        tekst = "🎮 **Partecipazioni questa settimana:**\n"
        for entry in data.values():
            tekst += f"• {entry['username']}: 1 volta\n"
        await ctx.send(tekst)

    @commands.command(name="frasi-gemiddelde")
    async def gemiddelde_tijd(self, ctx):
        alles = laad_scores()
        if not alles:
            await ctx.send("📊 Nessun dato disponibile.")
            return
        tekst = "⏱️ **Tempo medio di gioco:**\n"
        for naam, gegevens in alles.items():
            if gegevens["beurten"] > 0:
                gemiddeld = int(gegevens["tijd"] / gegevens["beurten"])
                tekst += f"• {naam}: {gemiddeld} sec\n"
        await ctx.send(tekst)

    @tasks.loop(time=datetime.time(hour=7, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=2))))
    async def weekelijkse_herinnering(self):
        guild = discord.utils.get(self.bot.guilds)
        if not guild:
            return
        week = weeknummer()
        pad = f"{SCORE_PATH}/week_{week}.json"
        gespeelden = set()
        if os.path.exists(pad):
            with open(pad, "r", encoding="utf-8") as f:
                gespeelden = set(json.load(f).keys())

        for lid in guild.members:
            if lid.bot or lid.dm_channel is None:
                continue
            try:
                await lid.create_dm()
                if str(lid.id) in gespeelden:
                    await lid.dm_channel.send("🔔 Hai già giocato questa settimana! Ma puoi ancora migliorare il tuo punteggio fino a venerdì!")
                else:
                    await lid.dm_channel.send("🔔 Non hai ancora giocato questa settimana a *Frasi idiomatiche*! Prova ora con `!frasi`!")
            except:
                continue

async def setup(bot):
    await bot.add_cog(Frasi(bot))