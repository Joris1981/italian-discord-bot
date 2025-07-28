import discord
from discord.ext import commands
import asyncio
import json
import os
import random
from datetime import datetime
import session_manager
import logging

logger = logging.getLogger(__name__)

DATA_PATH = "/persistent/data/indovina"
XP_PATH = os.path.join(DATA_PATH, "xp_scores.json")
WEEKLY_FILE = os.path.join(DATA_PATH, "indovina_settimana_1.json")
ALLOWED_THREAD_ID = 1389545682007883816
MAX_TIME = 90
TIP_TIME_PENALTY = 30

os.makedirs(DATA_PATH, exist_ok=True)

class Indovina(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="indovina")
    async def start_indovina(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and ctx.channel.id != ALLOWED_THREAD_ID:
            return await ctx.send("❌ Questo gioco può essere avviato solo nel thread autorizzato o tramite DM.")

        user_id = ctx.author.id
        if session_manager.is_user_in_active_session(user_id):
            return await ctx.send("⚠️ Hai già una sessione attiva. Completa prima quella prima di iniziarne una nuova.")

        try:
            with open(WEEKLY_FILE, encoding="utf-8") as f:
                descrizioni = json.load(f)
        except Exception as e:
            logger.exception("Errore nel caricamento del file delle descrizioni")
            return await ctx.send("Errore nel caricamento delle descrizioni.")

        session_manager.start_session(user_id, "indovina")
        logger.info(f"Gioco Indovina avviato da utente {user_id}")

        dm = await ctx.author.create_dm()
        await dm.send("🎯 Hai iniziato il gioco **Indovina**! Hai 90 secondi per ogni descrizione. Scrivi `!tip` per un suggerimento (perderai 30 secondi).\n")

        punteggio = 0
        domande = random.sample(descrizioni, 15)

        for idx, item in enumerate(domande, 1):
            logger.info(f"Domanda {idx}/15 per utente {user_id}: {item['descrizione']}")
            await dm.send(f"**{idx}/15**\n🔎 Tipo: **{item['tipo']}**\n❓ _{item['descrizione']}_")
            tempo_rimanente = MAX_TIME
            tip_usato = False

            def check(m):
                return m.author == ctx.author and m.channel == dm

            while tempo_rimanente > 0:
                try:
                    risposta_task = asyncio.create_task(self.bot.wait_for('message', check=check, timeout=tempo_rimanente))
                    risposta = await risposta_task

                    if risposta.content.lower().strip() == "!tip" and not tip_usato:
                        tip_usato = True
                        tempo_rimanente -= TIP_TIME_PENALTY
                        logger.info(f"Utente {user_id} ha richiesto un suggerimento alla domanda {idx}")
                        await dm.send(f"💡 Suggerimento: {item['tip']} (⏱️ {tempo_rimanente} secondi rimanenti)")
                        continue

                    normalizzata = risposta.content.lower().strip()
                    varianti = [v.lower().strip() for v in item.get("varianti", [])] + [item['soluzione'].lower()]
                    if normalizzata in varianti:
                        await dm.send("✅ Corretto!")
                        punteggio += 1
                        logger.info(f"Risposta corretta da utente {user_id} alla domanda {idx}")
                    else:
                        await dm.send(f"❌ Sbagliato. La risposta corretta era: **{item['soluzione']}**")
                        logger.info(f"Risposta sbagliata da utente {user_id} alla domanda {idx}")
                    break
                except asyncio.TimeoutError:
                    await dm.send(f"⏰ Tempo scaduto! La risposta corretta era: **{item['soluzione']}**")
                    logger.info(f"Timeout per utente {user_id} alla domanda {idx}")
                    break

        await dm.send(f"\n🏁 Hai completato il gioco!\n🎯 Risposte corrette: **{punteggio}/15**\n⭐ Hai guadagnato **{punteggio} XP**.")
        self.salva_xp(str(user_id), punteggio)
        session_manager.end_session(user_id)
        logger.info(f"Gioco Indovina completato da utente {user_id} con punteggio {punteggio}")

    def salva_xp(self, user_id, punteggio):
        oggi = datetime.now().strftime("%Y-%m-%d")
        try:
            if os.path.exists(XP_PATH):
                with open(XP_PATH, encoding="utf-8") as f:
                    dati = json.load(f)
            else:
                dati = {}
        except Exception as e:
            logger.exception("Errore nel caricamento del file XP")
            dati = {}

        if user_id not in dati:
            dati[user_id] = {"totale_xp": 0, "sessioni": []}

        dati[user_id]["totale_xp"] += punteggio
        dati[user_id]["sessioni"].append({"data": oggi, "punteggio": punteggio})

        try:
            with open(XP_PATH, "w", encoding="utf-8") as f:
                json.dump(dati, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.exception("Errore nel salvataggio del file XP")

    @commands.command(name="upload_indovina")
    @commands.has_permissions(administrator=True)
    async def upload_indovina(self, ctx):
        if not ctx.message.attachments:
            return await ctx.send("📎 Devi allegare un file JSON valido.")

        allegato = ctx.message.attachments[0]
        if not allegato.filename.endswith(".json"):
            return await ctx.send("❌ Il file deve essere un .json")

        contenuto = await allegato.read()
        try:
            dati = json.loads(contenuto)
            with open(WEEKLY_FILE, "w", encoding="utf-8") as f:
                json.dump(dati, f, ensure_ascii=False, indent=2)
            await ctx.send("✅ Nuova lista Indovina caricata con successo.")
            logger.info(f"Nuova lista caricata da {ctx.author.id} ({allegato.filename})")
        except Exception as e:
            logger.exception("Errore durante il caricamento del file JSON")
            await ctx.send(f"❌ Errore durante il caricamento: {e}")

    @commands.command(name="cancella_indovina")
    @commands.has_permissions(administrator=True)
    async def cancella_indovina(self, ctx):
        try:
            if os.path.exists(WEEKLY_FILE):
                os.remove(WEEKLY_FILE)
                await ctx.send("🗑️ Lista settimanale eliminata con successo.")
                logger.info(f"File settimanale eliminato da {ctx.author.id}")
            else:
                await ctx.send("⚠️ Nessun file da eliminare.")
                logger.info(f"Tentativo di cancellare un file inesistente da {ctx.author.id}")
        except Exception as e:
            logger.exception("Errore durante l'eliminazione del file settimanale")
            await ctx.send("❌ Errore durante l'eliminazione del file.")

async def setup(bot):
    await bot.add_cog(Indovina(bot))