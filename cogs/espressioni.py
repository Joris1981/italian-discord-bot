import discord
from discord.ext import commands
import json
import asyncio
import os
import logging
import session_manager

logger = logging.getLogger(__name__)

QUIZ_CHANNEL_ID = 1388667261761359932
DATA_DIR = 'persistent/data/wordle/espressioni'
CURRENT_WEEK_FILE = 'espressioni_settimana_1.json'
TIME_LIMIT = 90  # secondi

os.makedirs(DATA_DIR, exist_ok=True)

class Espressioni(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_questions(self):
        path = os.path.join(DATA_DIR, CURRENT_WEEK_FILE)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['espressioni']

    def format_question(self, index, q):
        formatted = f"**Domanda {index + 1}:** {q['frase']}\n"
        for key, value in q['opzioni'].items():
            formatted += f"{key}) {value}\n"
        formatted += "\n⏱️ Hai 90 secondi per rispondere! Scrivi A, B, C o D."
        return formatted

    @commands.command(name='espressioni')
    async def start_quiz(self, ctx):
        user = ctx.author
        user_id = user.id

        if session_manager.is_user_in_active_session(user_id):
            return await ctx.send("⚠️ Hai già una sessione attiva. Completa prima quella prima di iniziarne una nuova.")

        try:
            dm = await user.create_dm()
            questions = self.load_questions()
            user_score = 0

            if ctx.guild and ctx.channel.id == QUIZ_CHANNEL_ID:
                await ctx.send(f"📩 {user.mention} la quiz è iniziata nei tuoi DM!")
            elif isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("📩 Iniziamo!")

            session_manager.start_session(user_id, "espressioni")
            logger.info(f"Quiz Espressioni avviato da utente {user_id}")

            await dm.send("🎉 **Benvenuto al quiz: 'Espressioni Idiomatiche'!**\n15 domande in arrivo...")

            for i, q in enumerate(questions):
                await dm.send(self.format_question(i, q))

                def check(m):
                    return (
                        m.author == user and
                        m.channel == dm and
                        m.content.upper() in ['A', 'B', 'C', 'D']
                    )

                try:
                    response = await self.bot.wait_for('message', timeout=TIME_LIMIT, check=check)
                    if response.content.upper() == q['risposta']:
                        user_score += 1
                        await dm.send("✅ Corretto!")
                        logger.info(f"Risposta corretta da utente {user_id} alla domanda {i+1}")
                    else:
                        await dm.send(f"❌ Sbagliato. La risposta giusta era **{q['risposta']}**.")
                        logger.info(f"Risposta sbagliata da utente {user_id} alla domanda {i+1}")
                except asyncio.TimeoutError:
                    await dm.send("⏰ Tempo scaduto per questa domanda!")
                    logger.info(f"Timeout per utente {user_id} alla domanda {i+1}")

            await dm.send("📊 **Fine del quiz!**")
            await dm.send(f"🏅 Hai totalizzato: **{user_score}/15**")
            logger.info(f"Quiz completato da utente {user_id} con punteggio {user_score}")

        except discord.Forbidden:
            await ctx.send("❌ Non posso inviarti messaggi privati! Controlla le tue impostazioni DM.")
        finally:
            session_manager.end_session(user_id)

    @commands.command(name='uploadespressioni')
    @commands.has_permissions(administrator=True)
    async def upload_espressioni(self, ctx):
        if not ctx.message.attachments:
            return await ctx.send("❌ Per favore, allega un file .json con le espressioni.")

        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith(".json"):
            return await ctx.send("❌ Il file deve essere in formato .json.")

        save_path = os.path.join(DATA_DIR, attachment.filename)

        try:
            await attachment.save(save_path)
            global CURRENT_WEEK_FILE
            CURRENT_WEEK_FILE = attachment.filename
            await ctx.send(f"✅ File **{attachment.filename}** caricato con successo e impostato come attivo!")
            logger.info(f"File caricato: {attachment.filename} da {ctx.author.id}")
        except Exception as e:
            logger.exception("Errore durante il salvataggio del file")
            await ctx.send(f"⚠️ Errore durante il salvataggio del file: {e}")

    @commands.command(name='deleteespressioni')
    @commands.has_permissions(administrator=True)
    async def delete_espressioni(self, ctx, filename: str):
        if not filename.endswith('.json'):
            return await ctx.send("❌ Specifica un file `.json` da eliminare.")

        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            await ctx.send(f"❌ Il file `{filename}` non esiste.")
            return

        try:
            os.remove(file_path)
            await ctx.send(f"🗑️ Il file `{filename}` è stato eliminato con successo.")
            logger.info(f"File eliminato: {filename} da {ctx.author.id}")
        except Exception as e:
            logger.exception("Errore durante l'eliminazione")
            await ctx.send(f"⚠️ Errore durante l'eliminazione del file: {e}")

    @commands.command(name='listeespressioni')
    async def list_espressioni(self, ctx):
        try:
            files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
            if not files:
                return await ctx.send("📂 Nessun file disponibile.")
            elenco = "\n".join(f"- {f}" for f in files)
            await ctx.send(f"📋 File disponibili in `espressioni`:\n{elenco}")
        except Exception as e:
            logger.exception("Errore nel listare i file")
            await ctx.send("⚠️ Errore nel listare i file.")

async def setup(bot):
    await bot.add_cog(Espressioni(bot))