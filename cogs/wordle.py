import discord
from discord.ext import commands, tasks
import json
import os
import random
import datetime
import asyncio
import logging
import openai
import unicodedata
import re
from utils import normalize

from session_manager import start_session, end_session, is_user_in_active_session

client = openai.OpenAI()

THEMAS = [
    "In giro per negozi", "Gli animali", "Lessico su aspetto fisico e carattere",
    "L’oroscopo", "Viaggi e tempo libero", "Frutti e verdura",
    "Parti del corpo", "Prepararsi per un colloquio", "Tempo e natura", "Relazioni e sentimenti"
]

STARTDATUM = datetime.datetime(2025, 7, 2, 9, 0)
WOORDEN_PATH = "/persistent/data/wordle/wordle_woorden.json"
SCORES_PATH = "/persistent/data/wordle/wordle_scores.json"
PLAYED_PATH = "/persistent/data/wordle/wordle_played.json"

KANALEN = [1389545682007883816, 1389552706783543307, 1388667261761359932, 1390779837593026594]
LEADERBOARD_THREAD = 1390779837593026594
MAX_SPEEL_PER_WEEK = 7

class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekelijkse_leaderboard.start()
        self.weekelijkse_reminder.start()

    def get_huidige_week(self):
        verschil = datetime.datetime.now() - STARTDATUM
        weken_verstreken = max(0, verschil.days // 7)
        return min(weken_verstreken, len(THEMAS) - 1)

    def get_huidig_thema(self):
        return THEMAS[self.get_huidige_week()]

    def laad_scores(self):
        if not os.path.exists(SCORES_PATH): return {}
        with open(SCORES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def laad_played(self):
        if not os.path.exists(PLAYED_PATH): return {}
        with open(PLAYED_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @tasks.loop(hours=168)
    async def weekelijkse_reminder(self):
        await self.bot.wait_until_ready()
        played = self.laad_played()
        scores = self.laad_scores()
        week = self.get_huidige_week()
        thema = self.get_huidig_thema()

        for uid, data in scores.items():
            week_key = f"{uid}_week{week}"
            if played.get(week_key, 0) == 0:
                try:
                    user = await self.bot.fetch_user(int(uid))
                    await user.send(f"\U0001F4CB Ciao! Je hebt deze week nog geen Wordle gespeeld.\nHet thema is *{thema}*. Typ `!wordle` in het kanaal om te starten!")
                except Exception as e:
                    logging.warning(f"Kon gebruiker {uid} niet bereiken: {e}")

    @weekelijkse_reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def wordle_herinnering_test(self, ctx):
        await self.weekelijkse_reminder()
        await ctx.send("✅ Herinnering handmatig verstuurd (indien van toepassing).")

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
        os.makedirs(os.path.dirname(WOORDEN_PATH), exist_ok=True)
        if not os.path.exists(WOORDEN_PATH):
            with open(WOORDEN_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f)
        with open(WOORDEN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        sleutel_b1 = f"week{week}_B1"
        sleutel_b2 = f"week{week}_B2"
        if sleutel_b1 not in data:
            data[sleutel_b1] = await self.genereer_woorden(self.get_huidig_thema(), "B1", 40)
        if sleutel_b2 not in data:
            b1_set = set(w["italiaans"] for w in data[sleutel_b1])
            b2_lijst = await self.genereer_woorden(self.get_huidig_thema(), "B2", 15)
            unieke_b2 = [w for w in b2_lijst if w["italiaans"] not in b1_set]
            data[sleutel_b2] = unieke_b2[:10]
        with open(WOORDEN_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @commands.command(name="reset-woordenlijst")
    @commands.has_permissions(administrator=True)
    async def reset_woordenlijst(self, ctx):
        await ctx.send("🔄 Nieuwe woordenlijst wordt gegenereerd... Dit kan even duren.")
        try:
            await self.generate_weekly_wordlist()
            await ctx.send("✅ Woordenlijst voor deze week is succesvol opnieuw gegenereerd!")
        except Exception as e:
            logging.error(f"Fout bij reset_woordenlijst: {e}")
            await ctx.send("❌ Er is iets misgegaan bij het genereren van de woordenlijst.")

    async def laad_woorden(self, week, moeilijkheid="B1", aantal=15):
        with open(WOORDEN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        sleutel = f"week{week}_{moeilijkheid}"
        return random.sample(data.get(sleutel, []), min(aantal, len(data.get(sleutel, []))))

    def laad_scores(self):
        if not os.path.exists(SCORES_PATH): return {}
        with open(SCORES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def bewaar_scores(self, scores):
        os.makedirs(os.path.dirname(SCORES_PATH), exist_ok=True)
        with open(SCORES_PATH, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)

    def laad_played(self):
        if not os.path.exists(PLAYED_PATH): return {}
        with open(PLAYED_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def bewaar_played(self, played):
        os.makedirs(os.path.dirname(PLAYED_PATH), exist_ok=True)
        with open(PLAYED_PATH, "w", encoding="utf-8") as f:
            json.dump(played, f, indent=2, ensure_ascii=False)

    async def start_wordle_dm(self, user, woorden, week, thema):
        score = 0
        def check(m): return m.author == user and isinstance(m.channel, discord.DMChannel)
        await user.send(f"\U0001F4D6 **Wordle – Tema della settimana:** *{thema}*")
        starttijd = datetime.datetime.now()
        for idx, woord in enumerate(woorden, start=1):
            await user.send(f"\n\U0001F522 **{idx}. Wat is het Italiaans voor:** '{woord['nederlands']}'?\n(Je hebt 60 seconden.)")
            try:
                antwoord = await self.bot.wait_for('message', timeout=60.0, check=check)
                if normalize(antwoord.content) == normalize(woord["italiaans"]):
                    await user.send("\u2705 Corretto!")
                    score += 1
                else:
                    await user.send(f"❌ No, la risposta era: **{woord['italiaans']}**.")
            except asyncio.TimeoutError:
                await user.send(f"⏱ Tempo scaduto! Oplossing: **{woord['italiaans']}**.")
        eindtijd = datetime.datetime.now()
        totale_tijd = (eindtijd - starttijd).total_seconds()
        await user.send(f"\n\U0001F4CA **Resultaat:** {score}/15 correcte antwoorden.")
        sterren = 0
        if score >= 12:
            await user.send("\n\U0001F31F Bonusronde! 5 extra woorden op niveau B2:")
            bonuswoorden = await self.laad_woorden(week, "B2", 5)
            bonus_score = 0
            for idx, woord in enumerate(bonuswoorden, start=1):
                await user.send(f"\n🆕 **Bonus {idx}.** '{woord['nederlands']}'?")
                try:
                    antwoord = await self.bot.wait_for('message', timeout=60.0, check=check)
                    if normalize(antwoord.content) == normalize(woord["italiaans"]):
                        await user.send("\u2705 Corretto!")
                        bonus_score += 1
                    else:
                        await user.send(f"❌ No, la risposta era: **{woord['italiaans']}**.")
                except asyncio.TimeoutError:
                    await user.send(f"⏱ Tempo scaduto! Oplossing: **{woord['italiaans']}**.")
            if bonus_score >= 3:
                sterren = 1
                await user.send("\U0001F31F Bravo! Je hebt een ster verdiend! \U0001F31F")
        return score, sterren, totale_tijd

    @commands.command()
    async def wordle(self, ctx):
        user = ctx.author
        if not isinstance(ctx.channel, discord.DMChannel) and ctx.channel.id not in KANALEN:
            return

        if is_user_in_active_session(user.id, "wordle"):
            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.send(f"{user.mention}, je bent al met een Wordle bezig.")
            else:
                await ctx.send("❌ Je bent al met een Wordle bezig.")
            return

        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send(f"{user.mention}, ⏳ *Un attimo... il gioco inizia nella tua inbox!*")

        week = self.get_huidige_week()
        thema = self.get_huidig_thema()
        played = self.laad_played()
        week_key = f"{user.id}_week{week}"

        if played.get(week_key, 0) >= MAX_SPEEL_PER_WEEK:
            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.send(f"{user.mention}, je hebt deze week al {MAX_SPEEL_PER_WEEK} keer gespeeld.")
            else:
                await ctx.send(f"❌ Je hebt deze week al {MAX_SPEEL_PER_WEEK} keer gespeeld.")
            return

        await self.generate_weekly_wordlist()
        woorden = await self.laad_woorden(week, aantal=15)

        try:
            await user.send("\U0001F4E7 Ciao! Het spel start nu in je DM!")
        except discord.Forbidden:
            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.send(f"{user.mention}, ik kan je geen DM sturen. Kijk je instellingen na.")
            return

        start_session(user.id, "wordle")
        score, sterren, tijd = await self.start_wordle_dm(user, woorden, week, thema)
        end_session(user.id)

        scores = self.laad_scores()
        uid = str(user.id)

        if uid not in scores or scores[uid].get("week", -1) != week or score > scores[uid].get("score", 0):
            scores[uid] = {
                "naam": user.display_name,
                "score": score,
                "sterren": sterren,
                "week": week,
                "tijd": int(tijd)
            }
            self.bewaar_scores(scores)

        played[week_key] = played.get(week_key, 0) + 1
        self.bewaar_played(played)

        await user.send("\nGrazie per aver giocato!")

    @commands.command()
    async def test_leaderboard(self, ctx):
        await self.weekelijkse_leaderboard()
        await ctx.send("✅ Leaderboard gegenereerd.")

    @commands.command(name="wordle-speelstatistiek")
    async def wordle_speelstatistiek(self, ctx):
        played = self.laad_played()
        week = self.get_huidige_week()

        resultaten = []
        for key, aantal in played.items():
            if key.endswith(f"_week{week}"):
                uid = key.replace(f"_week{week}", "")
                member = ctx.guild.get_member(int(uid))
                naam = member.display_name if member else f"User {uid}"
                resultaten.append((naam, aantal))

        if not resultaten:
            await ctx.send("📊 Er zijn nog geen gespeelde beurten deze week.")
            return

        resultaten.sort(key=lambda x: x[1], reverse=True)

        tekst = "🎮 **Statistieken voor deze week:**\n\n"
        for naam, tries in resultaten:
            tekst += f"• {naam} – {tries} keer gespeeld"
            if tries >= 7:
                tekst += " ✅"
            tekst += "\n"

        await ctx.send(tekst)

    @commands.command(name="wordle-gemiddelde")
    async def wordle_gemiddelde(self, ctx):
        """Toont de gemiddelde speeltijd per speler over alle gespeelde weken."""
        scores = self.laad_scores()
        spelers_tijden = {}

        for uid, data in scores.items():
            naam = data.get("naam", "Onbekend")
            tijd = data.get("tijd", 0)
            if tijd > 0:
                if naam not in spelers_tijden:
                    spelers_tijden[naam] = []
                spelers_tijden[naam].append(tijd)

        if not spelers_tijden:
            await ctx.send("📊 Geen tijdsgegevens beschikbaar.")
            return

        tekst = "⏱️ **Gemiddelde speeltijd per speler (basisronde):**\n"
        for naam, tijden in sorted(spelers_tijden.items()):
            gemiddelde = sum(tijden) / len(tijden)
            tekst += f"• **{naam}**: {int(gemiddelde)} seconden gemiddeld\n"

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
        top = sorted(huidige_scores.values(), key=lambda x: (-x["score"], -x.get("sterren", 0), x.get("tijd", float('inf'))))[:10]
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