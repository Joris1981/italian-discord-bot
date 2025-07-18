import discord
from discord.ext import commands, tasks
import json
import os
import random
import datetime
import asyncio
import logging
import openai
from utils import normalize
from session_manager import start_session, end_session, is_user_in_active_session

client = openai.OpenAI()
logging.basicConfig(level=logging.INFO)

DATA_PATH = "/persistent/data/wordle/frasi"
SCORE_PATH = "/persistent/data/wordle/frasi_scores"
SPEELDATA_PATH = "/persistent/data/wordle/frasi_played.json"
LEADERBOARD_THREAD_ID = 1395557049269747887
MAX_SPEEL_PER_WEEK = 10
TIJDSLIMIET = 90

THEMAS = [
    "In caso di emergenza", "Al ristorante", "La mia giornata", "Parlare di emozioni",
    "Chiedere indicazioni", "Al telefono", "Fare la spesa e shopping",
    "Alla stazione / all’aeroporto", "Esprimere opinioni", "Invitare e rifiutare"
]

STARTDATUM = datetime.datetime(2025, 7, 19, 9, 0)


class Frasi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs(DATA_PATH, exist_ok=True)
        os.makedirs(SCORE_PATH, exist_ok=True)
        self.weekelijkse_reminder.start()
        self.weekelijkse_leaderboard.start()

    def get_huidige_week(self):
        verschil = datetime.datetime.now() - STARTDATUM
        weeknummer = max(0, verschil.days // 7)
        return min(weeknummer, len(THEMAS) - 1)

    def get_thema(self):
        return THEMAS[self.get_huidige_week()]

    def laad_data(self, path):
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def bewaar_data(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def start_spel(self, user, ctx):
        start_session(user.id, "frasi")
        week = self.get_huidige_week()
        thema = self.get_thema()
        data_file = f"{DATA_PATH}/week_{week}.json"
        data = self.laad_data(data_file)
        basis = random.sample(data.get("basis", []), 10)
        bonus = random.sample(data.get("bonus", []), 5)
        score, tijd = await self.verwerk_ronde(user, basis, "basis", thema)
        sterren = 0
        if score >= 8:
            await user.send("\U0001F31F Bonusronde! 5 extra zinnen:")
            bonusscore, _ = await self.verwerk_ronde(user, bonus, "bonus", thema)
            if bonusscore >= 3:
                sterren = 1
                await user.send("\n\U0001F389 Bravo! Je hebt een ⭐ verdiend!")
        self.sla_score_op(user, score, sterren, week, tijd)
        self.sla_speelbeurt_op(user, week)
        await user.send("Grazie per aver giocato!")
        end_session(user.id)

    async def verwerk_ronde(self, user, zinnen, soort, thema):
        score = 0
        starttijd = datetime.datetime.now()
        for i, zin in enumerate(zinnen, 1):
            await user.send(f"{i}. **Vertaal:** {zin['nederlands']}\n_Tema: {thema}_\n⏳ ({TIJDSLIMIET} seconden)")
            try:
                msg = await self.bot.wait_for("message", timeout=TIJDSLIMIET, check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel))
                antwoord = normalize(msg.content)
                if antwoord in [normalize(v) for v in zin["italiaans"]]:
                    await user.send("\u2705 Corretto!")
                    score += 1
                else:
                    await user.send(f"❌ No, risposte possibili: {zin['italiaans'][0]}")
            except asyncio.TimeoutError:
                await user.send(f"⏱ Tempo scaduto! Oplossing: {zin['italiaans'][0]}")
        eindtijd = datetime.datetime.now()
        duur = (eindtijd - starttijd).total_seconds()
        return score, duur

    def sla_score_op(self, user, score, sterren, week, tijd):
        scores = self.laad_data(f"{SCORE_PATH}/week_{week}.json")
        uid = str(user.id)
        naam = user.display_name if hasattr(user, "display_name") else str(user.id)
        bestaande = scores.get(uid, {})
        if not bestaande or score > bestaande.get("score", 0):
            scores[uid] = {"naam": naam, "score": score, "sterren": sterren, "tijd": int(tijd)}
            self.bewaar_data(f"{SCORE_PATH}/week_{week}.json", scores)

    def sla_speelbeurt_op(self, user, week):
        gespeeld = self.laad_data(SPEELDATA_PATH)
        key = f"{user.id}_week{week}"
        gespeeld[key] = gespeeld.get(key, 0) + 1
        self.bewaar_data(SPEELDATA_PATH, gespeeld)

    def mag_spelen(self, user_id, week):
        gespeeld = self.laad_data(SPEELDATA_PATH)
        return gespeeld.get(f"{user_id}_week{week}", 0) < MAX_SPEEL_PER_WEEK

    @commands.command(name="frasi")
    async def frasi_start(self, ctx):
        user = ctx.author
        if is_user_in_active_session(user.id, "frasi"):
            await ctx.send("⛔ Hai già iniziato una sessione.")
            return
        week = self.get_huidige_week()
        if not self.mag_spelen(user.id, week):
            await ctx.send("⛔ Hai raggiunto il numero massimo di tentativi per questa settimana. Riprova la prossima settimana!")
            return
        await ctx.send("\U0001F4AC Il gioco sta per iniziare nella tua DM!")
        try:
            await user.send("Ciao! Cominciamo con le frasi da tradurre...")
            await self.start_spel(user, ctx)
        except discord.Forbidden:
            await ctx.send("⚠️ Non posso inviarti messaggi privati. Controlla le impostazioni di privacy.")

    @tasks.loop(hours=168)
    async def weekelijkse_reminder(self):
        await self.bot.wait_until_ready()
        week = self.get_huidige_week()
        thema = self.get_thema()
        scores = self.laad_data(f"{SCORE_PATH}/week_{week}.json")
        gespeeld = self.laad_data(SPEELDATA_PATH)
        for uid, data in scores.items():
            key = f"{uid}_week{week}"
            try:
                user = await self.bot.fetch_user(int(uid))
                if gespeeld.get(key, 0) == 0:
                    await user.send(f"\U0001F4CB Ciao! Non hai ancora giocato a *Frasi* questa settimana. Il tema è: **{thema}**. Digita `!frasi` per iniziare!")
                else:
                    await user.send(f"\U0001F44A Bravo! Hai già giocato a *Frasi* questa settimana. Ricorda, puoi provare tot 10 keer per week.")
            except Exception as e:
                logging.warning(f"Kan gebruiker {uid} niet bereiken: {e}")

    @weekelijkse_reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=168)
    async def weekelijkse_leaderboard(self):
        await self.bot.wait_until_ready()
        kanaal = self.bot.get_channel(LEADERBOARD_THREAD_ID)
        if not kanaal:
            logging.warning("Leaderboard kanaal niet gevonden.")
            return
        week = self.get_huidige_week()
        scores = self.laad_data(f"{SCORE_PATH}/week_{week}.json")
        if not scores:
            await kanaal.send("📊 Er zijn deze week nog geen Frasi-scores.")
            return
        top = sorted(scores.items(), key=lambda x: (-x[1]["score"], -x[1].get("sterren", 0), x[1].get("tijd", float("inf"))))[:10]
        tekst = f"🏆 **Leaderboard – Week {week + 1}: {self.get_thema()}**\n"
        for i, (uid, s) in enumerate(top, 1):
            naam = s.get("naam", uid)
            ster = " ⭐" if s.get("sterren", 0) else ""
            tekst += f"{i}. **{naam}** – {s['score']}/10{ster}\n"
        try:
            await kanaal.send(tekst)
        except Exception as e:
            logging.error(f"Fout bij posten leaderboard: {e}")

    @weekelijkse_leaderboard.before_loop
    async def before_leaderboard(self):
        await self.bot.wait_until_ready()

    @commands.command(name="frasi-speelstatistiek")
    async def frasi_speelstatistiek(self, ctx):
        week = self.get_huidige_week()
        gespeeld = self.laad_data(SPEELDATA_PATH)
        resultaten = [(uid.split("_")[0], aantal) for uid, aantal in gespeeld.items() if uid.endswith(f"week{week}")]
        if not resultaten:
            await ctx.send("📊 Geen speelgegevens gevonden voor deze week.")
            return
        tekst = "🎮 **Aantal keren gespeeld deze week:**\n\n"
        for uid, aantal in sorted(resultaten, key=lambda x: x[1], reverse=True):
            member = ctx.guild.get_member(int(uid))
            naam = member.display_name if member else uid
            tekst += f"• {naam}: {aantal} keer\n"
        await ctx.send(tekst)

    @commands.command(name="frasi-gemiddelde")
    async def frasi_gemiddelde(self, ctx):
        alle_scores = {}
        for week in range(len(THEMAS)):
            scores = self.laad_data(f"{SCORE_PATH}/week_{week}.json")
            for uid, data in scores.items():
                naam = data.get("naam", uid)
                tijd = data.get("tijd", 0)
                if naam not in alle_scores:
                    alle_scores[naam] = []
                alle_scores[naam].append(tijd)
        if not alle_scores:
            await ctx.send("📊 Geen gemiddelde tijden beschikbaar.")
            return
        tekst = "⏱️ **Gemiddelde speeltijd per speler:**\n\n"
        for naam, tijden in sorted(alle_scores.items()):
            gemiddelde = sum(tijden) / len(tijden)
            tekst += f"• {naam}: {int(gemiddelde)} seconden gemiddeld\n"
        await ctx.send(tekst)

async def setup(bot):
    await bot.add_cog(Frasi(bot))