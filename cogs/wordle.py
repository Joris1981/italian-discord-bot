import discord
from discord.ext import commands, tasks
import os
import json
import asyncio
import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCORES_PATH = "wordle_scores.json"
PLAYED_PATH = "wordle_played.json"

THEMAS = [
    "La casa", "Il tempo libero", "La scuola", "I mestieri", "Il cibo",
    "Il tempo", "La famiglia", "Le vacanze", "La città", "La salute"
]

KANALEN = [1389545682007883816, 1389552706783543307, 1388667261761359932]
LEADERBOARD_THREAD = 1389552706783543307
MAX_SPEEL_PER_WEEK = 5


class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekelijkse_leaderboard.start()

    def get_huidige_week(self):
        start = datetime.date(2025, 6, 26)
        vandaag = datetime.date.today()
        return (vandaag - start).days // 7

    def get_huidig_thema(self):
        week = self.get_huidige_week()
        return THEMAS[week % len(THEMAS)]

    async def laad_woorden(self, weeknummer, moeilijkheid="B1", aantal=15):
        filename = f"wordle_woorden_week_{weeknummer}.json"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)

        thema = self.get_huidig_thema()
        prompt = (
            f"Geef een lijst van {aantal} zelfstandige naamwoorden op taalniveau {moeilijkheid}, met bijbehorend lidwoord "
            f"in het Italiaans die passen binnen het thema '{thema}', samen met hun Nederlandse vertaling. "
            f"Antwoord in JSON-formaat als een lijst zoals: "
            f'[{{"italiaans": "la casa", "nederlands": "het huis"}}, ...]'
        )

        try:
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Je bent een taalassistent Italiaans voor cursisten."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            antwoord = completion.choices[0].message.content
            woorden = json.loads(antwoord)

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(woorden, f, indent=2, ensure_ascii=False)

            return woorden
        except Exception as e:
            print(f"❌ Fout bij genereren woordenlijst: {e}")
            return []

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

    async def start_wordle_dm(self, user, woorden, week, thema):
        score = 0

        def check(m):
            return m.author == user and isinstance(m.channel, discord.DMChannel)

        await user.send(f"\U0001F4D6 **Wordle – Thema van de week:** *{thema}*")
        for idx, woord in enumerate(woorden, start=1):
            nl = woord["nederlands"]
            it = woord["italiaans"].lower()

            await user.send(f"\n\U0001F522 **{idx}. Wat is het Italiaans voor:** '{nl}'?\n"
                            f"(Je hebt 60 seconden om te antwoorden.)")

            try:
                antwoord = await self.bot.wait_for('message', timeout=60.0, check=check)
                if antwoord.content.lower().strip() == it:
                    await user.send("\u2705 Corretto!")
                    score += 1
                else:
                    hint = f"{len(it)} letters, begint met '{it[0]}', eindigt met '{it[-1]}'"
                    await user.send(f"\u274C No, la risposta era: **{it}**. ({hint})")
            except asyncio.TimeoutError:
                await user.send(f"\u23F1 Tempo scaduto! De juiste oplossing was **{it}**.")

        await user.send(f"\n\U0001F4CA **Resultaat:** {score}/15 correcte antwoorden.")

        sterren = 0
        if score >= 12:
            await user.send("\n\U0001F31F Bonusronde! 5 extra woorden op niveau B2:")
            bonuswoorden = await self.laad_woorden(week, moeilijkheid="B2", aantal=5)
            bonus_score = 0

            for idx, woord in enumerate(bonuswoorden, start=1):
                nl = woord["nederlands"]
                it = woord["italiaans"].lower()
                await user.send(f"\n\U0001F195 **Bonus {idx}.** Wat is het Italiaans voor '{nl}'?")

                try:
                    antwoord = await self.bot.wait_for('message', timeout=60.0, check=check)
                    if antwoord.content.lower().strip() == it:
                        await user.send("\u2705 Corretto!")
                        bonus_score += 1
                    else:
                        await user.send(f"\u274C No, la risposta era: **{it}**.")
                except asyncio.TimeoutError:
                    await user.send(f"\u23F1 Tempo scaduto! De juiste oplossing was **{it}**.")

            if bonus_score >= 4:
                sterren = 1
                await user.send("\U0001F31F Bravo! Je hebt een ster verdiend! \U0001F31F")

        return score, sterren

    @commands.command(name="wordle")
    async def wordle(self, ctx):
        if ctx.channel.id not in KANALEN:
            return

        gebruiker = ctx.author
        gebruikersnaam = str(gebruiker)
        week = self.get_huidige_week()
        thema = self.get_huidig_thema()
        woorden = await self.laad_woorden(week, "B1", 15)

        played = self.laad_played()
        scores = self.laad_scores()

        if str(week) not in played:
            played[str(week)] = {}

        if played[str(week)].get(gebruikersnaam, 0) >= MAX_SPEEL_PER_WEEK:
            await ctx.send("⛔ Je hebt deze week al 5 keer gespeeld. Probeer volgende week opnieuw!")
            return

        nieuwe_score, sterren = await self.start_wordle_dm(gebruiker, woorden, week, thema)

        if str(week) not in scores:
            scores[str(week)] = {}

        huidige_score = scores[str(week)].get(gebruikersnaam, {"score": 0, "ster": 0})

        if nieuwe_score > huidige_score["score"]:
            scores[str(week)][gebruikersnaam] = {"score": nieuwe_score, "ster": sterren}
            self.bewaar_scores(scores)
            await ctx.send(f"\U0001F389 Je nieuwe score ({nieuwe_score}/15) is opgeslagen!")
        else:
            await ctx.send(f"\U0001F4DD Je score ({nieuwe_score}/15) werd niet verbeterd.")

        played[str(week)][gebruikersnaam] = played[str(week)].get(gebruikersnaam, 0) + 1
        self.bewaar_played(played)

    @commands.command(name="genereer_woorden_test")
    async def genereer_woorden_test(self, ctx):
        week = self.get_huidige_week()
        woorden = await self.laad_woorden(week, "B1", 15)
        if woorden:
            await ctx.send("✅ Woordenlijst gegenereerd voor deze week.")
        else:
            await ctx.send("⚠️ Geen woorden gegenereerd. Controleer OpenAI logs.")

    @tasks.loop(hours=168)
    async def weekelijkse_leaderboard(self):
        await self.bot.wait_until_ready()
        thread = self.bot.get_channel(LEADERBOARD_THREAD)
        week = self.get_huidige_week()
        scores = self.laad_scores()

        if str(week) not in scores:
            await thread.send("Er zijn nog geen scores voor deze week.")
            return

        resultaten = scores[str(week)]
        gesorteerd = sorted(resultaten.items(), key=lambda x: x[1]["score"], reverse=True)

        bericht = f"\U0001F4CA **Leaderboard – Week {week + 1}: {THEMAS[week]}**\n\n"
        for idx, (naam, data) in enumerate(gesorteerd, start=1):
            ster = "\u2B50" * data.get("ster", 0)
            bericht += f"{idx}. **{naam}** – {data['score']}/15 {ster}\n"

        await thread.send(bericht)

    @weekelijkse_leaderboard.before_loop
    async def before_leaderboard(self):
        now = datetime.datetime.now()
        volgende_maandag = now + datetime.timedelta(days=(7 - now.weekday()) % 7)
        volgende_maandag = volgende_maandag.replace(hour=9, minute=0, second=0, microsecond=0)
        wachtijd = (volgende_maandag - now).total_seconds()
        await asyncio.sleep(wachtijd)


async def setup(bot):
    await bot.add_cog(Wordle(bot))