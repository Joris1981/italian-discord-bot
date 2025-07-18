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
LEADERBOARD_THREAD = 1395557049269747887
MAX_SPEEL_PER_WEEK = 10

THEMAS = [
    "In caso di emergenza", "La mia giornata", "Parlare di emozioni",
    "Chiedere indicazioni", "Al telefono", "Fare la spesa e shopping",
    "Alla stazione / all’aeroporto", "Esprimere opinioni",
    "Invitare e rifiutare", "Al ristorante"
]

STARTDATUM = datetime.datetime(2025, 7, 12, 9, 0)  # vrijdag 12 juli = week 1

class Frasi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekelijks_leaderboard.start()
        self.weekelijkse_reminder.start()

    def get_huidige_week(self):
        verschil = datetime.datetime.now() - STARTDATUM
        week = max(0, verschil.days // 7)
        return min(week, len(THEMAS) - 1)

    def get_thema(self, week):
        return THEMAS[week]

    def laad_scores(self):
        if not os.path.exists(SCORE_PATH): return {}
        with open(SCORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def bewaar_scores(self, scores):
        os.makedirs(SCORE_PATH, exist_ok=True)
        with open(SCORE_PATH, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)

    def laad_played(self):
        if not os.path.exists(SPEELDATA_PATH): return {}
        with open(SPEELDATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def bewaar_played(self, played):
        os.makedirs(SPEELDATA_PATH, exist_ok=True)
        with open(SPEELDATA_PATH, "w", encoding="utf-8") as f:
            json.dump(played, f, indent=2, ensure_ascii=False)

    def laad_zinnen(self, week):
        path = f"{DATA_PATH}/week_{week}.json"
        if not os.path.exists(path): return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def start_frasi_dm(self, user, zinnen, thema, week):
        def check(m):
            return m.author == user and isinstance(m.channel, discord.DMChannel)

        await user.send(f"\U0001F4AC **Frasi idiomatiche – Thema:** *{thema}*")
        score = 0
        starttijd = datetime.datetime.now()

        for idx, zin in enumerate(zinnen[:10], start=1):
            await user.send(f"\n{idx}. Vertaal naar het Italiaans:\n**{zin['nederlands']}**\n(90 seconden)")
            try:
                antwoord = await self.bot.wait_for("message", timeout=90.0, check=check)
                if normalize(antwoord.content) in [normalize(v) for v in zin["toegestane_vertalingen"]]:
                    await user.send("\u2705 Corretto!")
                    score += 1
                else:
                    await user.send(f"❌ Antwoord fout. Een correcte vertaling is: **{zin['italiaans']}**")
            except asyncio.TimeoutError:
                await user.send(f"⏱ Tempo scaduto! Oplossing: **{zin['italiaans']}**")

        sterren = 0
        bonus_score = 0
        if score >= 8:
            await user.send("\n\U0001F31F Bonusronde! 5 extra zinnen op B2-niveau:")
            for idx, zin in enumerate(zinnen[10:], start=1):
                await user.send(f"\nBonus {idx}. Vertaal:\n**{zin['nederlands']}**")
                try:
                    antwoord = await self.bot.wait_for("message", timeout=90.0, check=check)
                    if normalize(antwoord.content) in [normalize(v) for v in zin["toegestane_vertalingen"]]:
                        await user.send("\u2705 Corretto!")
                        bonus_score += 1
                    else:
                        await user.send(f"❌ Nee, correcte vertaling: **{zin['italiaans']}**")
                except asyncio.TimeoutError:
                    await user.send(f"⏱ Tempo scaduto! Oplossing: **{zin['italiaans']}**")

            if bonus_score >= 3:
                sterren = 1
                await user.send("\n\U0001F31F Bravo! Je hebt een ster verdiend!")

        eindtijd = datetime.datetime.now()
        totale_tijd = int((eindtijd - starttijd).total_seconds())
        await user.send(f"\n\U0001F4CA Resultaat: {score}/10\nTotale tijd: {totale_tijd} seconden")

        return score, sterren, totale_tijd

    @commands.command(name="frasi")
    async def frasi(self, ctx):
        user = ctx.author
        logging.info(f"!frasi gestart door {user}")

        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send(f"{user.mention}, ⏳ *Un attimo... il gioco inizia nella tua inbox!*")

        if is_user_in_active_session(user.id, "frasi"):
            await ctx.send("⛔ Je speelt al een Frasi-ronde.")
            return

        week = self.get_huidige_week()
        week_key = f"{user.id}_week{week}"
        played = self.laad_played()
        if played.get(week_key, 0) >= MAX_SPEEL_PER_WEEK:
            await ctx.send("⛔ Hai raggiunto il numero massimo di tentativi per questa settimana. Riprova la prossima settimana!")
            return

        try:
            await user.send("🎯 Ciao! We gaan van start!")
        except discord.Forbidden:
            await ctx.send("❌ Ik kan je geen DM sturen. Kijk je privacy-instellingen na.")
            return

        zinnen_data = self.laad_zinnen(week)
        if not zinnen_data:
            await user.send("❌ Geen zinnen beschikbaar voor deze week.")
            return

        start_session(user.id, "frasi")
        score, sterren, tijd = await self.start_frasi_dm(user, zinnen_data, self.get_thema(week), week)
        end_session(user.id)

        scores = self.laad_scores()
        uid = str(user.id)

        try:
            member = await self.bot.fetch_user(user.id)
            naam = member.display_name
        except:
            naam = uid  # fallback

        if uid not in scores or scores[uid].get("week", -1) != week or score > scores[uid].get("score", 0):
            scores[uid] = {
                "naam": naam,
                "score": score,
                "sterren": sterren,
                "tijd": tijd,
                "week": week
            }
            self.bewaar_scores(scores)

        played[week_key] = played.get(week_key, 0) + 1
        self.bewaar_played(played)

        await user.send("\nGrazie per aver giocato!")

    def laad_scores(self):
        if not os.path.exists(SCORE_FILE): return {}
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def bewaar_scores(self, scores):
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)

    def laad_played(self):
        if not os.path.exists(SPEELDATA_PATH): return {}
        with open(SPEELDATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def bewaar_played(self, data):
        with open(SPEELDATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @commands.command(name="frasi-leaderboard")
    async def frasi_leaderboard(self, ctx):
        await self.weekelijkse_leaderboard()
        await ctx.send("🏆 Leaderboard gegenereerd.")

    @commands.command(name="frasi-speelstatistiek")
    async def frasi_speelstatistiek(self, ctx):
        week = self.get_huidige_week()
        played = self.laad_played()
        stats = {}
        for key, aantal in played.items():
            if key.endswith(f"_week{week}"):
                uid = key.replace(f"_week{week}", "")
                stats[uid] = aantal

        if not stats:
            await ctx.send("📊 Geen speeldata beschikbaar voor deze week.")
            return

        tekst = "**🎯 Speelstatistiek:**\n\n"
        for uid, aantal in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            try:
                user = await self.bot.fetch_user(int(uid))
                naam = user.display_name
            except:
                naam = uid
            tekst += f"• {naam}: {aantal} keer gespeeld\n"

        await ctx.send(tekst)

    @commands.command(name="frasi-gemiddelde")
    async def frasi_gemiddelde(self, ctx):
        scores = self.laad_scores()
        tijden = {}
        for uid, data in scores.items():
            naam = data.get("naam", uid)
            tijd = data.get("tijd", 0)
            if tijd > 0:
                tijden.setdefault(naam, []).append(tijd)

        if not tijden:
            await ctx.send("⏱️ Geen tijdsdata beschikbaar.")
            return

        tekst = "**⏱️ Gemiddelde speeltijd per speler:**\n\n"
        for naam, lijst in sorted(tijden.items(), key=lambda x: sum(x[1]) / len(x[1])):
            gemiddelde = sum(lijst) / len(lijst)
            tekst += f"• {naam}: {int(gemiddelde)} seconden gemiddeld\n"

        await ctx.send(tekst)

    @tasks.loop(hours=168)
    async def weekelijkse_leaderboard(self):
        await self.bot.wait_until_ready()
        kanaal = self.bot.get_channel(LEADERBOARD_THREAD)
        if not kanaal:
            logging.warning("Leaderboard kanaal niet gevonden.")
            return

        scores = self.laad_scores()
        week = self.get_huidige_week()
        data = {k: v for k, v in scores.items() if v.get("week") == week}

        if not data:
            await kanaal.send("📊 Er zijn deze week nog geen Frasi-scores.")
            return

        top = sorted(
            data.values(),
            key=lambda x: (-x["score"], -x.get("sterren", 0), x.get("tijd", float("inf")))
        )[:10]

        thema = self.get_thema(week)
        tekst = f"🏆 **Leaderboard – Week {week + 1}: {thema}**\n"
        for i, s in enumerate(top, start=1):
            ster = " ⭐" if s.get("sterren", 0) else ""
            naam = s.get("naam") or str(i)
            tekst += f"{i}. **{naam}** – {s['score']}/10{ster}\n"

        try:
            await kanaal.send(tekst)
        except Exception as e:
            logging.error(f"Fout bij posten leaderboard: {e}")

    @weekelijkse_leaderboard.before_loop
    async def before_leaderboard(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=168)
    async def weekelijkse_reminder(self):
        await self.bot.wait_until_ready()
        played = self.laad_played()
        scores = self.laad_scores()
        week = self.get_huidige_week()
        thema = self.get_thema(week)

        for uid, data in scores.items():
            week_key = f"{uid}_week{week}"
            try:
                user = await self.bot.fetch_user(int(uid))
                if played.get(week_key, 0) == 0:
                    await user.send(f"\U0001F4AC Ciao! Je hebt deze week nog geen Frasi gespeeld.\nThema: *{thema}*.\nTyp `!frasi` in de chat om te beginnen!")
                else:
                    await user.send(f"📣 Ciao! Je hebt al gespeeld, maar je kunt je score nog verbeteren tot vrijdag.\nThema: *{thema}*.")
            except Exception as e:
                logging.warning(f"Kon gebruiker {uid} niet bereiken: {e}")

    @weekelijkse_reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Frasi(bot))