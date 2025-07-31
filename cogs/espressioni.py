import discord
from discord.ext import commands
import json
import asyncio
import os
import datetime

QUIZ_CHANNEL_IDS = [1388667261761359932, 1389545682007883816]
DATA_DIR = 'persistent/data/wordle/espressioni'
CURRENT_WEEK_FILE = 'espressioni_settimana_1.json'
TIME_LIMIT = 90  # secondi
SCORE_PATH = os.path.join(DATA_DIR, "scores")
os.makedirs(SCORE_PATH, exist_ok=True)

def weeknummer():
    oggi = datetime.date.today()
    return oggi.isocalendar().week

class Espressioni(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_scores = {}
        self.last_questions = {}
        self.played_users = set()

    def load_questions(self):
        path = os.path.join(DATA_DIR, CURRENT_WEEK_FILE)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['espressioni']

    def format_question(self, index, q):
        formatted = f"❓ **Domanda {index + 1}:** {q['frase']}\n"
        for key, value in q['opzioni'].items():
            formatted += f"*{key})* {value}\n"
        formatted += "\n⏱️ Hai 90 secondi per rispondere! Scrivi A, B, C o D."
        return formatted

    def salva_score(self, user_id, score):
        week = weeknummer()
        path = os.path.join(SCORE_PATH, f"week_{week}.json")

        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {}
        except:
            data = {}

        uid_str = str(user_id)
        if uid_str not in data:  # Alleen eerste score telt
            data[uid_str] = score
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"❌ Fout bij opslaan score: {e}")

    @commands.command(name='espressioni')
    async def start_quiz(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and ctx.channel.id not in QUIZ_CHANNEL_IDS:
            return await ctx.send("❌ Questo quiz può essere avviato solo nel canale designato o tramite DM.")

        try:
            dm = await ctx.author.create_dm()
        except:
            return await ctx.send("⚠️ Impossibile inviare messaggi privati. Controlla le tue impostazioni.")

        await ctx.send("📬 Il quiz è stato avviato nei tuoi DM!")

        questions = self.load_questions()
        self.user_scores[ctx.author.id] = 0
        self.last_questions[ctx.author.id] = questions
        self.played_users.add(ctx.author.id)

        await dm.send("🎉 **Benvenuto al quiz: 'Espressioni Idiomatiche'!**\n📚 15 domande in arrivo...\nPer ogni frase, scegli l'opzione corretta (A, B, C, D).")

        for i, q in enumerate(questions):
            await dm.send(self.format_question(i, q))

            def check(m):
                return (
                    m.channel == dm and
                    m.author == ctx.author and
                    m.content.upper() in ['A', 'B', 'C', 'D']
                )

            try:
                response = await self.bot.wait_for('message', timeout=TIME_LIMIT, check=check)
            except asyncio.TimeoutError:
                await dm.send("⏰ Tempo scaduto per questa domanda!")
                continue

            if response.content.upper() == q['risposta']:
                self.user_scores[ctx.author.id] += 1
                traduzione = q.get('traduzione', '')
                await dm.send(f"✅ Corretto!\n🗣️ **{q['frase']}** → 🇳🇱 {traduzione}")
            else:
                await dm.send(f"❌ Risposta sbagliata. La risposta giusta era **{q['risposta']}**.")

        score = self.user_scores[ctx.author.id]
        self.salva_score(ctx.author.id, score)

        await dm.send(f"\n🏁 **Fine del quiz!**\n🎯 Risposte corrette: **{score}/15**")
        await dm.send("🧠 Vuoi approfondire le espressioni? Digita il comando `!espressioni_spiegazioni` per ricevere le spiegazioni complete in DM.")

    @commands.command(name='espressioni_spiegazioni')
    async def spiega_espressioni(self, ctx):
        user_id = ctx.author.id
        if user_id not in self.played_users:
            return await ctx.send("⚠️ Devi prima completare il quiz `!espressioni` per ricevere le spiegazioni.")

        questions = self.last_questions.get(user_id)
        if not questions:
            return await ctx.send("⚠️ Non ho trovato le tue domande. Riprova il quiz con `!espressioni`.")

        try:
            dm = await ctx.author.create_dm()
            await dm.send("📖 **Spiegazioni delle espressioni idiomatiche:**")

            for q in questions:
                frase = q['frase']
                spiegazione = q.get('spiegazione', "— Nessuna spiegazione fornita.")
                traduzione = q.get('traduzione', "—")
                vocabolario = q.get('vocabolario', {})

                msg = f"🔹 **{frase}**\n🧠 *{spiegazione}*\n🇳🇱 **Vertaling**: {traduzione}"
                if vocabolario:
                    voca_lines = "\n".join([f"📌 **{voce}** = {betekenis}" for voce, betekenis in vocabolario.items()])
                    msg += f"\n📚 **Vocabolario**:\n{voca_lines}"

                await dm.send(msg)

        except Exception:
            await ctx.send("❌ Non posso inviarti le spiegazioni via DM. Controlla le tue impostazioni.")

    @commands.command(name='espressioni_leaderboard')
    @commands.is_owner()
    async def leaderboard(self, ctx):
        week = weeknummer()
        path = os.path.join(SCORE_PATH, f"week_{week}.json")
        kanaal_id = 1388667261761359932

        if not os.path.exists(path):
            return await ctx.send("⚠️ Nessun punteggio trovato per questa settimana.")

        try:
            with open(path, "r", encoding="utf-8") as f:
                scores = json.load(f)
        except:
            return await ctx.send("❌ Errore durante la lettura del file dei punteggi.")

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        embed = discord.Embed(
            title=f"🏆 Leaderboard - Settimana {week}",
            description="📚 Punteggi del quiz *Espressioni Idiomatiche*",
            color=0xFFD700
        )

        for i, (uid, score) in enumerate(sorted_scores[:10], 1):
            try:
                user = await self.bot.fetch_user(int(uid))
                nome = user.display_name if hasattr(user, "display_name") else user.name
            except:
                nome = f"ID: {uid}"
            embed.add_field(name=f"{i}. {nome}", value=f"{score}/15", inline=False)

        channel = self.bot.get_channel(kanaal_id)
        if channel:
            await channel.send(embed=embed)
        else:
            await ctx.send("❌ Canale non trovato.")

    @commands.command(name='upload_espressioni')
    @commands.has_permissions(administrator=True)
    async def upload_espressioni(self, ctx):
        if not ctx.message.attachments:
            return await ctx.send("📎 Devi allegare un file JSON valido.")
        file = ctx.message.attachments[0]
        if not file.filename.endswith(".json"):
            return await ctx.send("❌ Il file deve essere un .json")

        content = await file.read()
        try:
            data = json.loads(content)
            path = os.path.join(DATA_DIR, CURRENT_WEEK_FILE)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            await ctx.send("✅ Nuova lista di espressioni caricata con successo.")
        except Exception as e:
            await ctx.send(f"❌ Errore durante il caricamento: {e}")

    @commands.command(name='cancella_espressioni')
    @commands.has_permissions(administrator=True)
    async def cancella_espressioni(self, ctx):
        path = os.path.join(DATA_DIR, CURRENT_WEEK_FILE)
        if os.path.exists(path):
            os.remove(path)
            await ctx.send("🗑️ File delle espressioni eliminato.")
        else:
            await ctx.send("⚠️ Nessun file da eliminare.")

async def setup(bot):
    await bot.add_cog(Espressioni(bot))