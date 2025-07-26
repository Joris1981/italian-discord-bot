import discord
from discord.ext import commands, tasks
import random
import asyncio
import datetime
import json
import os
import logging
import time
import re
import zipfile
from io import BytesIO
from session_manager import start_session, end_session, is_user_in_active_session

TIJDSLIMIET = 60
DATA_PATH = "/persistent/data/wordle/coniuga"
SCORE_PATH = "/persistent/data/wordle/coniuga_scores"
LEADERBOARD_THREAD_ID = 1397220124150468618  # <-- pas aan indien nodig
TOEGESTANE_KANALEN = [123456789013345, 1388667261761359932, 1397220124150468618, 1397248870056067113]
TIJDEN = ["presente", "progressivo_presente", "passato_prossimo", "imperfetto", "futuro", "condizionale", "imperativo"]
ZICHTBARE_NAMEN = {
    "presente": "Presente",
    "progressivo_presente": "Progressivo presente :arrow_right: (il gerundio)",
    "passato_prossimo": "Passato prossimo",
    "imperfetto": "Imperfetto",
    "futuro": "Futuro",
    "condizionale": "Condizionale",
    "imperativo": "Imperativo ✋ (istruzioni e ordini)"
}
NIVEAUS = ["A2", "B1", "B2"]

os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(SCORE_PATH, exist_ok=True)

def weeknummer():
    vandaag = datetime.date.today()
    eerste_week = datetime.date(2025, 7, 22)
    week = ((vandaag - eerste_week).days // 7) + 1
    return max(1, week)

def laad_zinnen(week, tijd, niveau, bonus=False):
    bestand = f"{tijd}_{niveau}_{'bonus' if bonus else 'base'}.json"
    pad = os.path.join(DATA_PATH, f"week_{week}", bestand)
    try:
        with open(pad, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Lijst niet gevonden: {pad}")
        return []

def schrijf_score(user_id, display_name, score, tijd, ster, week):
    pad = os.path.join(SCORE_PATH, f"week_{week}.json")
    if os.path.exists(pad):
        with open(pad, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    vorige = data.get(str(user_id))
    if not vorige or score > vorige["score"] or (score == vorige["score"] and tijd < vorige["tijd"]):
        data[str(user_id)] = {
            "naam": display_name,
            "score": score,
            "tijd": tijd,
            "ster": ster
        }
        with open(pad, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

class Coniuga(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ... (hier komt jouw bestaande spelcode met !verbi, leaderboard, enz.)
    @commands.command(name='verbi')
    async def start_coniuga(self, ctx):
        user = ctx.author

        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.reply("\U0001F4E9 Il gioco è partito nei tuoi DM!")
        try:
            start_session(user.id, "coniuga")
            dm = await user.create_dm()
            week = weeknummer()

            # Controle of de weekmap al bestaat
            pad = os.path.join(DATA_PATH, f"week_{week}")
            if not os.path.exists(pad):
                await dm.send("\U0001F9E0 Sto preparando le frasi per questa settimana...\nRiprova tra qualche minuto!")
                end_session(user.id)
                return

            # Tijden (inclusief progressivo en misto)
            tijden = ["presente", "progressivo_presente", "passato_prossimo", "imperfetto", "futuro", "condizionale", "imperativo", "Misto"]
            niveaus = ["A2", "B1", "B2"]

            def check(m):
                return m.author == user and isinstance(m.channel, discord.DMChannel)

            # Tijdkeuze
            await dm.send("⏳ Quale tempo verbale vuoi esercitare?\n(Digita un numero da 1 a 8)\n\n" +
                            "\n".join(f"{i+1}. {ZICHTBARE_NAMEN.get(t, t)}" for i, t in enumerate(tijden)))

            try:
                msg = await self.bot.wait_for("message", timeout=60, check=check)
                tijd_index = int(msg.content.strip()) - 1
                tijd = tijden[tijd_index]
            except:
                await dm.send("Risposta non valida o tempo scaduto. Riprova con `!verbi`.")
                end_session(user.id)
                return

            # Niveaukeuze
            await dm.send("🎯 Quale livello vuoi esercitare?\n(Digita un numero da 1 a 3)\n1. A2\n2. B1\n3. B2")
            try:
                msg = await self.bot.wait_for("message", timeout=60, check=check)
                niveau = niveaus[int(msg.content.strip()) - 1]
            except:
                await dm.send("Risposta non valida o tempo scaduto. Riprova con `!verbi`.")
                end_session(user.id)
                return
            
            await dm.send(f"👍 Perfetto! Hai scelto:\n– Tempo verbale: **{tijd}**\n– Livello: **{niveau}**\n\n"
                          "🔄 Puoi digitare `!stop-verbi` in qualsiasi momento per interrompere il quiz.")

            # Zinnen laden
            if tijd == "misto":
                alle_zinnen = []
                for t in tijden[:-1]:  # alle behalve misto
                    zinnen_per_tijd = laad_zinnen(week, t, niveau, bonus=False)
                    for item in zinnen_per_tijd:
                        # Voeg tijdsaanduiding toe aan de zin, achter het werkwoord
                        zin_met_tijd = re.sub(
                            r"\((\w+)\)", rf"(\1) ({t})", item["zin"]
                        )
                        nieuwe_item = {
                            "zin": zin_met_tijd,
                            "oplossing": item["oplossing"],
                            "varianten": item.get("varianten", [])
                        }
                        alle_zinnen.append(nieuwe_item)

            else:
                alle_zinnen = laad_zinnen(week, tijd, niveau, bonus=False)

            if len(alle_zinnen) < 20:
                await dm.send("⚠️ Non ci sono abbastanza frasi disponibili per il livello selezionato.")
                end_session(user.id)
                return
            geselecteerd = random.sample(alle_zinnen, 20)

            # Spel starten
            correcte = 0
            start = time.time()

            for i, item in enumerate(geselecteerd, 1):
                zin = item["zin"]
                oplossing = item["oplossing"]
                varianten = item.get("varianten", [])
                await dm.send(f"{i}. {zin}")
                try:
                    msg = await self.bot.wait_for("message", timeout=TIJDSLIMIET, check=check)

                    if msg.content.strip().lower() == "!stop-verbi":
                        await dm.send("🛑 Quiz gestopt. Puoi riprovare quando vuoi con `!verbi`.")
                        end_session(user.id)
                        return

                    antwoord = msg.content.strip().lower()
                    
                    if antwoord == oplossing.lower() or antwoord in [v.lower() for v in varianten]:
                        await dm.send("✅ Corretto!")
                        correcte += 1
                    else:
                        await dm.send(f"❌ Sbagliato. Risposta corretta: **{oplossing}**")
                except asyncio.TimeoutError:
                    await dm.send(f"⏰ Tempo scaduto! Risposta corretta: **{oplossing}**")

            tijdsduur = round(time.time() - start)
            await self.verwerk_score(user, dm, correcte, tijdsduur, week, tijd, livello=niveau)

        except Exception as e:
            logging.error(f"Fout in coniuga: {e}")
            await user.send("Si è verificato un errore. Riprova più tardi.")
            end_session(user.id)

    async def verwerk_score(self, user, dm, correcte, tijdsduur, week, tijd, livello):
        if correcte >= 16:
            await dm.send(f"\n🎉 Hai ottenuto {correcte}/20 risposte corrette! Hai sbloccato il **bonus round**!\n"
                          "Preparati per altre 10 frasi...")

            # Bonuszinnen laden
            if tijd == "misto":
                alle_bonus = []
                for t in ["presente", "progressivo_presente", "passato_prossimo", "imperfetto", "futuro", "condizionale", "imperativo", "Misto"]:
                    bonus_per_tijd = laad_zinnen(week, t, livello, bonus=True)
                    for item in bonus_per_tijd:
                        zin_met_tijd = re.sub(
                            r"\((\w+)\)", rf"(\1) ({t})", item["zin"]
                        )
                        nieuwe_item = {
                            "zin": zin_met_tijd,
                            "oplossing": item["oplossing"],
                            "varianten": item.get("varianten", [])
                        }
                        alle_bonus.append(nieuwe_item)

                if len(alle_bonus) < 10:
                    await dm.send("⚠️ Il bonus round non è disponibile per questa combinazione.")
                    ster = False
                    bonus_correct = 0
                else:
                    geselecteerd_bonus = random.sample(alle_bonus, 10)
                    ster, bonus_correct = await self.bonusronde(dm, user, geselecteerd_bonus)

            else:
                bonuszinnen = laad_zinnen(week, tijd, livello, bonus=True)
                if len(bonuszinnen) < 10:
                    await dm.send("⚠️ Il bonus round non è disponibile per questa combinazione.")
                    ster = False
                    bonus_correct = 0
                else:
                    geselecteerd_bonus = random.sample(bonuszinnen, 10)
                    ster, bonus_correct = await self.bonusronde(dm, user, geselecteerd_bonus)

            if ster:
                await dm.send(f"\n🏅 Hai ottenuto {bonus_correct}/10 nel bonus round. Hai guadagnato una **⭐**!")
            else:
                await dm.send(f"\nHai ottenuto {bonus_correct}/10 nel bonus round. Nessuna ⭐ stavolta.")
        else:
            ster = False
            await dm.send(f"\nHai ottenuto {correcte}/20 risposte corrette. Niente bonus round stavolta!")

        # Score opslaan
        display_name = user.display_name if hasattr(user, 'display_name') else user.name
        schrijf_score(user.id, display_name, correcte, tijdsduur, ster, week)
        await dm.send("📊 La tua partita è stata registrata. Puoi riprovare quando vuoi con `!verbi`.")
        end_session(user.id)

    async def bonusronde(self, dm, user, zinnen):
        correcte = 0
        def check(m):
            return m.author == user and isinstance(m.channel, discord.DMChannel)

        for i, item in enumerate(zinnen, 1):
            zin = item["zin"]
            oplossing = item["oplossing"]
            varianten = item.get("varianten", [])
            await dm.send(f"[Bonus] {i}. {zin}")
            try:
                msg = await self.bot.wait_for("message", timeout=TIJDSLIMIET, check=check)

                if msg.content.strip().lower() == "!stop-verbi":
                    await dm.send("🛑 Quiz gestopt. Puoi riprovare quando vuoi con `!verbi`.")
                    end_session(user.id)
                    return

                antwoord = msg.content.strip().lower()
                
                if antwoord == oplossing.lower() or antwoord in [v.lower() for v in varianten]:
                    await dm.send("✅ Corretto!")
                    correcte += 1
                else:
                    await dm.send(f"❌ Sbagliato. Risposta corretta: **{oplossing}**")
            except asyncio.TimeoutError:
                await dm.send(f"⏰ Tempo scaduto! Risposta corretta: **{oplossing}**")
        ster = correcte >= 8
        return ster, correcte
    
    @commands.command(name='stop-verbi')
    async def stop_verbi(self, ctx):
        user_id = ctx.author.id
        if is_user_in_active_session(user_id):
            end_session(user_id)
            await ctx.send("🛑 Hai interrotto il quiz. Puoi riprovare quando vuoi con `!verbi`.")
        else:
            await ctx.send("ℹ️ Non hai un quiz attivo al momento.")

    @commands.command(name='coniuga-leaderboard')
    async def coniuga_leaderboard(self, ctx):
        week = weeknummer()
        await self._toon_leaderboard(ctx, week)

    @commands.command(name='coniuga-leaderboard-week')
    async def coniuga_leaderboard_week(self, ctx, week: int):
        await self._toon_leaderboard(ctx, week)

    async def _toon_leaderboard(self, ctx, week):
        pad = os.path.join(SCORE_PATH, f"week_{week}.json")
        if not os.path.exists(pad):
            await ctx.send(f"Nessun punteggio disponibile per la settimana {week}.")
            return

        with open(pad, "r", encoding="utf-8") as f:
            data = json.load(f)

        scores = list(data.items())
        scores.sort(key=lambda x: (-x[1]["score"], x[1]["tijd"]))
        titel = f"🏆 **Coniuga – Classifica settimana {week}**"
        lines = [titel]
        for i, (user_id, info) in enumerate(scores[:10], 1):
            naam = info.get("naam") or str(user_id)
            ster = " ⭐" if info.get("ster") else ""
            lines.append(f"{i}. **{naam}** – {info['score']}/20{ster}")

        try:
            thread = self.bot.get_channel(LEADERBOARD_THREAD_ID)
            await thread.send("\n".join(lines))
        except:
            await ctx.send("\n".join(lines))

    @commands.command(name='coniuga-gemiddelde')
    async def coniuga_gemiddelde(self, ctx):
        week = weeknummer()
        pad = os.path.join(SCORE_PATH, f"week_{week}.json")
        if not os.path.exists(pad):
            await ctx.send("Nessun dato disponibile per questa settimana.")
            return

        with open(pad, "r", encoding="utf-8") as f:
            data = json.load(f)

        tijden = [(v["naam"] or k, v["tijd"]) for k, v in data.items() if v.get("tijd")]
        if not tijden:
            await ctx.send("Nessun dato disponibile.")
            return

        lines = ["⏱️ **Tempo medio per la parte principale:**"]
        for naam, tijd in sorted(tijden, key=lambda x: x[1]):
            lines.append(f"– **{naam}**: {tijd} sec")

        await ctx.send("\n".join(lines))

    @commands.command(name='coniuga-speelstatistiek')
    async def coniuga_speelstatistiek(self, ctx):
        week = weeknummer()
        pad = os.path.join(SCORE_PATH, f"week_{week}.json")
        if not os.path.exists(pad):
            await ctx.send("Nessun dato disponibile per questa settimana.")
            return

        with open(pad, "r", encoding="utf-8") as f:
            data = json.load(f)

        lines = ["📈 **Numero di partite registrate:**"]
        for uid, info in data.items():
            naam = info.get("naam") or str(uid)
            lines.append(f"– **{naam}**: 1")

        await ctx.send("\n".join(lines))
    
    @commands.command(name='verwijder-coniuga-week')
    @commands.is_owner()
    async def verwijder_coniuga_week(self, ctx, week: int = None):
        logging.info(f"[Command] verwijder-coniuga-week opgeroepen door {ctx.author} in kanaal {ctx.channel} voor week {week}")
        if ctx.channel.id not in TOEGESTANE_KANALEN:
            return
        if week is None:
            week = weeknummer()
        pad = os.path.join(DATA_PATH, f"week_{week}")
        if not os.path.exists(pad):
            await ctx.send(f"ℹ️ Geen lijsten gevonden voor week {week}.")
            return
        try:
            for bestand in os.listdir(pad):
                os.remove(os.path.join(pad, bestand))
            os.rmdir(pad)
            await ctx.send(f"🗑️ Lijsten van week {week} succesvol verwijderd.")
            logging.info(f"[Coniuga] Lijsten van week {week} verwijderd door {ctx.author}.")
        except Exception as e:
            logging.error(f"[Coniuga] Fout bij verwijderen lijsten: {e}")
            await ctx.send("❌ Fout bij verwijderen van de lijsten.")

    @commands.command(name='download-coniuga-week')
    @commands.is_owner()
    async def download_coniuga_week(self, ctx, week: int = None):
        if week is None:
            week = weeknummer()
        weekmap = os.path.join(DATA_PATH, f"week_{week}")

        if not os.path.exists(weekmap):
            await ctx.send(f"❌ Geen map gevonden voor week {week}.")
            return

        bestanden = os.listdir(weekmap)
        if not bestanden:
            await ctx.send(f"📁 De map voor week {week} is leeg.")
            return

    # Maak een zip in het geheugen
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for bestandsnaam in bestanden:
                pad = os.path.join(weekmap, bestandsnaam)
                zip_file.write(pad, arcname=bestandsnaam)
        zip_buffer.seek(0)

    # Upload als bijlage
        discord_file = discord.File(fp=zip_buffer, filename=f"coniuga_week_{week}.zip")
        await ctx.send(f"📦 Alle bestanden voor week {week}:", file=discord_file)

    @commands.command(name='upload-coniuga-week')
    @commands.is_owner()
    async def upload_coniuga_week(self, ctx, week: int):
        if not ctx.message.attachments:
            await ctx.send("❌ Voeg een `.zip` bestand toe aan je bericht.")
            return

        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith(".zip"):
            await ctx.send("❌ Het bestand moet een `.zip` bestand zijn.")
            return

        zip_bytes = await attachment.read()

        try:
            zip_file = zipfile.ZipFile(BytesIO(zip_bytes))
            bestanden = zip_file.namelist()

            foutieve_bestanden = []
            for naam in bestanden:
                if not naam.endswith(".json"):
                    continue  # enkel JSON controleren
                try:
                    inhoud = zip_file.read(naam).decode("utf-8")
                    json.loads(inhoud)
                except Exception as e:
                    foutieve_bestanden.append(naam)

            if foutieve_bestanden:
                await ctx.send("❌ De volgende bestanden bevatten geen geldige JSON:\n" +
                                "\n".join(f"- `{f}`" for f in foutieve_bestanden))
                return

            # Als alles OK is → uitpakken
            weekmap = os.path.join(DATA_PATH, f"week_{week}")
            os.makedirs(weekmap, exist_ok=True)
            zip_file.extractall(weekmap)
            await ctx.send(f"✅ ZIP-bestand is uitgepakt naar `week_{week}`. {len(bestanden)} bestanden toegevoegd:\n" +
                            "\n".join(f"- `{b}`" for b in bestanden if b.endswith(".json")))
        except Exception as e:
            logging.error(f"[Coniuga Upload ZIP] Fout bij controleren of uitpakken: {e}")
            await ctx.send("❌ Er ging iets mis bij het controleren of uitpakken van de ZIP.")

async def setup(bot):
    logging.info("🧩 setup() van cogs.coniuga gestart")  # 👈 Extra loggingregel
    await bot.add_cog(Coniuga(bot))
    logging.info("✅ Coniuga-cog toegevoegd aan bot")     # 👈 Nog een loggingregel
    for command in bot.commands:
        logging.info(f"✅ Commando geladen: {command.name}")