import discord
from discord.ext import commands, tasks
import json
import os
import random
import datetime
import asyncio
import logging
import openai
import time

from session_manager import start_wordle, end_wordle, is_user_in_active_session

client = openai.OpenAI()

THEMAS = [
    "In giro per negozi", "Gli animali", "Lessico su aspetto fisico e carattere",
    "L’oroscopo", "Viaggi e tempo libero", "Frutti e verdura",
    "Parti del corpo", "Prepararsi per un colloquio", "Tempo e natura", "Relazioni e sentimenti"
]

STARTDATUM = datetime.datetime(2025, 6, 30, 9, 0)
WOORDEN_PATH = "data/wordle_woorden.json"
SCORES_PATH = "data/wordle_scores.json"
PLAYED_PATH = "data/wordle_played.json"
TIJDEN_PATH = "data/wordle_tijden.json"

KANALEN = [
    1389545682007883816,
    1389552706783543307,
    1388667261761359932,
    1390779837593026594
]
LEADERBOARD_THREAD = 1390779837593026594
MAX_SPEEL_PER_WEEK = 5

class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekelijkse_leaderboard.start()

    def get_huidige_week(self):
        verschil = datetime.datetime.now() - STARTDATUM
        weken_verstreken = max(0, verschil.days // 7)
        return min(weken_verstreken, len(THEMAS) - 1)

    def get_huidig_thema(self):
        return THEMAS[self.get_huidige_week()]

    async def genereer_woorden(self, thema, moeilijkheid="B1", aantal=40):
        prompt = (
            f"Geef {aantal} Italiaanse woorden met lidwoord op niveau {moeilijkheid} rond het thema '{thema}'. "
            "Toon ze als lijst met het Nederlands en de vertaling in het Italiaans met lidwoord. Bijvoorbeeld:\n"
            "1. de kat – il gatto"
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            inhoud = response.choices[0].message.content
            woorden = []
            for lijn in inhoud.strip().split("\n"):
                if not lijn.strip():
                    continue
                if "–" in lijn:
                    parts = lijn.split("–")
                elif ":" in lijn:
                    parts = lijn.split(":")
                elif "-" in lijn:
                    parts = lijn.split("-")
                else:
                    continue
                if len(parts) == 2:
                    nl = parts[0].split(".")[-1].strip()
                    it = parts[1].strip()
                    woorden.append({"nederlands": nl, "italiaans": it})
            return woorden
        except Exception as e:
            logging.error(f"Fout bij genereren woorden: {e}")
            return []

    async def generate_weekly_wordlist(self):
        week = self.get_huidige_week()
        if not os.path.exists(WOORDEN_PATH):
            os.makedirs(os.path.dirname(WOORDEN_PATH), exist_ok=True)
            with open(WOORDEN_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f)
        with open(WOORDEN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        sleutel_b1 = f"week{week}_B1"
        sleutel_b2 = f"week{week}_B2"
        if sleutel_b1 not in data or not data[sleutel_b1]:
            data[sleutel_b1] = await self.genereer_woorden(self.get_huidig_thema(), "B1", 40)
        if sleutel_b2 not in data or not data[sleutel_b2]:
            data[sleutel_b2] = await self.genereer_woorden(self.get_huidig_thema(), "B2", 10)
        with open(WOORDEN_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def laad_woorden(self, week, moeilijkheid="B1", aantal=15, uitgesloten=[]):
        with open(WOORDEN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        sleutel = f"week{week}_{moeilijkheid}"
        woorden = [w for w in data.get(sleutel, []) if w not in uitgesloten]
        return random.sample(woorden, min(aantal, len(woorden)))

    def laad_scores(self):
        if not os.path.exists(SCORES_PATH):
            return {}
        with open(SCORES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def bewaar_scores(self, scores):
        with open(SCORES_PATH, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)

    def laad_played(self):
        if not os.path.exists(PLAYED_PATH):
            return {}
        with open(PLAYED_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def bewaar_played(self, played):
        with open(PLAYED_PATH, "w", encoding="utf-8") as f:
            json.dump(played, f, indent=2, ensure_ascii=False)

    def laad_tijden(self):
        if not os.path.exists(TIJDEN_PATH):
            return {}
        with open(TIJDEN_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def bewaar_tijden(self, tijden):
        with open(TIJDEN_PATH, "w", encoding="utf-8") as f:
            json.dump(tijden, f, indent=2, ensure_ascii=False)

    async def start_wordle_dm(self, user, woorden, week, thema):
        score = 0
        start = time.time()
        def check(m): return m.author == user and isinstance(m.channel, discord.DMChannel)
        await user.send(f"📖 **Wordle – Tema della settimana:** *{thema}*")
        for idx, woord in enumerate(woorden, start=1):
            await user.send(f"\n🔢 **{idx}. Wat is het Italiaans voor:** '{woord['nederlands']}'?\n(Je hebt 60 seconden.)")
            try:
                antwoord = await self.bot.wait_for('message', timeout=60.0, check=check)
                if antwoord.content.lower().strip() == woord["italiaans"].lower():
                    await user.send("✅ Corretto!")
                    score += 1
                else:
                    await user.send(f"❌ No, la risposta era: **{woord['italiaans']}**.")
            except asyncio.TimeoutError:
                await user.send(f"⏱ Tempo scaduto! Oplossing: **{woord['italiaans']}**.")
        end = time.time()
        speeltijd = round(end - start)
        sterren = 0
        if score >= 12:
            await user.send("\n🌟 Bonusronde! 5 extra woorden op niveau B2:")
            bonuswoorden = await self.laad_woorden(week, "B2", 5, uitgesloten=woorden)
            bonus_score = 0
            for idx, woord in enumerate(bonuswoorden, start=1):
                await user.send(f"\n🆕 **Bonus {idx}.** '{woord['nederlands']}'?")
                try:
                    antwoord = await self.bot.wait_for('message', timeout=60.0, check=check)
                    if antwoord.content.lower().strip() == woord["italiaans"].lower():
                        await user.send("✅ Corretto!")
                        bonus_score += 1
                    else:
                        await user.send(f"❌ No, la risposta era: **{woord['italiaans']}**.")
                except asyncio.TimeoutError:
                    await user.send(f"⏱ Tempo scaduto! Oplossing: **{woord['italiaans']}**.")
            if bonus_score >= 3:
                sterren = 1
                await user.send("🌟 Bravo! Je hebt een ster verdiend! 🌟")
        return score, sterren, speeltijd

    @commands.command()
    async def wordle(self, ctx):
        if ctx.channel.id not in KANALEN:
            return
        user = ctx.author
        if is_user_in_active_session(user.id):
            await ctx.send(f"{user.mention}, je bent al met een quiz of Wordle bezig.")
            return
        week = self.get_huidige_week()
        thema = self.get_huidig_thema()
        played = self.laad_played()
        week_key = f"{user.id}_week{week}"
        if played.get(week_key, 0) >= MAX_SPEEL_PER_WEEK:
            await ctx.send(f"{user.mention}, je hebt deze week al {MAX_SPEEL_PER_WEEK} keer gespeeld.")
            return
        await self.generate_weekly_wordlist()
        woorden = await self.laad_woorden(week, aantal=15)
        try:
            await user.send("📧 Ciao! Het spel start nu in je DM!")
            await ctx.send(f"{user.mention}, het spel is gestart in je inbox.")
        except discord.Forbidden:
            await ctx.send(f"{user.mention}, ik kan je geen DM sturen.")
            return
        start_wordle(user.id)
        score, sterren, speeltijd = await self.start_wordle_dm(user, woorden, week, thema)
        end_wordle(user.id)
        scores = self.laad_scores()
        tijden = self.laad_tijden()
        uid = str(user.id)
        if uid not in scores or scores[uid].get("week", -1) != week or score > scores[uid].get("score", 0):
            scores[uid] = {"naam": user.display_name, "score": score, "sterren": min(sterren, 1), "week": week, "tijd": speeltijd}
            tijden.setdefault(uid, []).append(speeltijd)
            self.bewaar_scores(scores)
            self.bewaar_tijden(tijden)
        played[week_key] = played.get(week_key, 0) + 1
        self.bewaar_played(played)
        await user.send("Grazie per aver giocato! 👍")

    @commands.command(name="wordle_tijden")
    async def wordle_tijden(self, ctx):
        tijden = self.laad_tijden()
        if not tijden:
            await ctx.send("Geen tijden beschikbaar.")
            return
        tekst = "**Gemiddelde speeltijd per speler (15 woorden):**\n"
        for uid, tijdenlijst in tijden.items():
            avg = round(sum(tijdenlijst) / len(tijdenlijst))
            naam = self.laad_scores().get(uid, {}).get("naam", "Onbekend")
            tekst += f"• {naam}: {avg} sec\n"
        await ctx.send(tekst)

    @tasks.loop(hours=168)
    async def weekelijkse_leaderboard(self):
        await self.bot.wait_until_ready()
        kanaal = self.bot.get_channel(LEADERBOARD_THREAD)
        if not kanaal:
            return
        scores = self.laad_scores()
        week = self.get_huidige_week()
        huidige_scores = {k: v for k, v in scores.items() if v.get("week") == week}
        if not huidige_scores:
            await kanaal.send("📊 Er zijn deze week nog geen Wordle-scores.")
            return
        top = sorted(huidige_scores.values(), key=lambda x: (-x["score"], -x.get("sterren", 0), x.get("tijd", 9999)))[:10]
        tekst = f"🏆 **Leaderboard – Week {week + 1}: {self.get_huidig_thema()}**\n"
        for i, s in enumerate(top, 1):
            ster = " ⭐" if s.get("sterren", 0) else ""
            tekst += f"{i}. **{s['naam']}** – {s['score']}/15{ster}\n"
        await kanaal.send(tekst)

    @weekelijkse_leaderboard.before_loop
    async def before_leaderboard(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Wordle(bot))