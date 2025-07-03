import discord
from discord.ext import commands
import unicodedata
import re
import asyncio
import session_manager

def normalize(text):
    text = unicodedata.normalize("NFKD", text).lower().strip()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = re.sub(r"[\s’‘`]", "", text)
    return text

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_quizzes = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = message.author.id
        if normalize(message.content) == "quiz":
            if session_manager.is_busy(user_id):
                await message.channel.send("❌ Hai già una quiz attiva. Completa prima quella prima di iniziarne un'altra.")
                return

            if message.channel.id == 1388866025679880256:
                session_manager.start_quiz(user_id)
                await self.start_di_da_quiz(message.author)
            elif message.channel.id == 1390080013533052949:
                session_manager.start_quiz(user_id)
                await self.start_in_per_quiz(message.author)
            elif message.channel.id == 1390371003414216805:
                session_manager.start_quiz(user_id)
                await self.start_qualche_quiz(message.author)

    async def start_qualche_quiz(self, user):
        questions = [
            ("Non c’è ___ problema, tutto è sotto controllo.", "nessun"),
            ("Ho conosciuto ___ ragazze simpatiche ieri sera.", "alcune"),
            ("Non ho ricevuto ___ risposta alla mia mail.", "nessuna"),
            ("___ volta andiamo in bici al lavoro.", "qualche"),
            ("Non c’era ___ alla festa, era deserta.", "nessuno"),
            ("Hai letto ___ libro interessante ultimamente?", "qualche"),
            ("Non ho ___ voglia di studiare oggi.", "alcuna"),
            ("___ studenti sono partiti in anticipo.", "alcuni"),
            ("Non c’è ___ motivo di preoccuparsi.", "alcun"),
            ("Non conosco ___ con quel nome.", "nessuno"),
            ("___ idea è stata accettata.", "qualche"),
            ("Non ho trovato ___ soluzione.", "nessuna"),
            ("C’erano ___ problemi tecnici.", "alcuni"),
            ("Non c’è ___ persona che lo sappia.", "nessuna")
        ]
        try:
            await user.send(
                "📘 **Quiz: Qualche, Alcuni, Nessuno, Alcuno**\n"
                "Rispondi con la parola corretta: *qualche, alcuni, alcune, alcuno, alcuna, nessuno, nessuna, nessun, alcun*.\n"
                "Hai 14 frasi. Hai 60 secondi per ogni frase. Iniziamo!"
            )
            score = 0
            for index, (question, correct) in enumerate(questions):
                await user.send(f"{index + 1}/14: {question}")
                try:
                    reply = await self.bot.wait_for(
                        "message",
                        timeout=60,
                        check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel)
                    )
                    if normalize(reply.content) == normalize(correct):
                        await user.send("✅ Corretto!")
                        score += 1
                    else:
                        await user.send(f"❌ Sbagliato! Risposta corretta: **{correct}**")
                except asyncio.TimeoutError:
                    await user.send("⏰ Tempo scaduto per questa frase!")

            await user.send(
                f"🏁 **Quiz completata!**\nHai totalizzato **{score}/14** risposte corrette. 🎉\n"
                "Se vuoi controllare tutte le risposte corrette, scrivi qui in DM:\n`!qualche-soluzioni` 📚\n"
                "➡️ **Opnieuw proberen? Typ gewoon opnieuw quiz in dezelfde thread.**"
            )
        except discord.Forbidden:
            await user.send("❌ Non posso inviarti un messaggio privato. Controlla le impostazioni di privacy.")
        finally:
            session_manager.end_quiz(user.id)

    @commands.command(name="qualche-soluzioni")
    async def qualche_soluzioni(self, ctx):
        solutions = [
            "**1.** Non c’è **nessun** problema, tutto è sotto controllo.",
            "**2.** Ho conosciuto **alcune** ragazze simpatiche ieri sera.",
            "**3.** Non ho ricevuto **nessuna** risposta alla mia mail.",
            "**4.** **Qualche** volta andiamo in bici al lavoro.",
            "**5.** Non c’era **nessuno** alla festa, era deserta.",
            "**6.** Hai letto **qualche** libro interessante ultimamente?",
            "**7.** Non ho **alcuna** voglia di studiare oggi.",
            "**8.** **Alcuni** studenti sono partiti in anticipo.",
            "**9.** Non c’è **alcun** motivo di preoccuparsi.",
            "**10.** Non conosco **nessuno** con quel nome.",
            "**11.** **Qualche** idea è stata accettata.",
            "**12.** Non ho trovato **nessuna** soluzione.",
            "**13.** C’erano **alcuni** problemi tecnici.",
            "**14.** Non c’è **nessuna** persona che lo sappia."
        ]
        try:
            for s in solutions:
                await ctx.author.send(s + "\n")
        except discord.Forbidden:
            await ctx.send("❌ Non posso inviarti un messaggio privato. Controlla le impostazioni di privacy.")

    # ================================
    # === DI / DA QUIZ ===
    # ================================

    async def start_di_da_quiz(self, user):
        questions = [
            {"question": "1. Vengo ___ Milano.", "answer": "da"},
            {"question": "2. Sono ___ Napoli.", "answer": "di"},
            {"question": "3. Vado ___ dentista.", "answer": "dal"},
            {"question": "4. La chiave ___ macchina.", "answer": "della"},
            {"question": "5. Parto ___ casa alle otto.", "answer": "da"},
            {"question": "6. Un amico ___ università.", "answer": "dell'"},
            {"question": "7. Il profumo ___ mia madre.", "answer": "di"},
            {"question": "8. Torno ___ Roma domani.", "answer": "da"},
            {"question": "9. Il libro ___ professore.", "answer": "del"},
            {"question": "10. La finestra ___ cucina.", "answer": "della"},
            {"question": "11. La penna ___ Giulia.", "answer": "di"},
            {"question": "12. Vado ___ Giulia più tardi.", "answer": "da"},
            {"question": "13. Il cane ___ vicino.", "answer": "del"},
            {"question": "14. Uscita ___ scuola alle tre.", "answer": "da"},
            {"question": "15. Il computer ___ ragazzo è rotto.", "answer": "del"}
        ]
        await self.run_quiz(user, questions, "DI o DA")

    # ================================
    # === PER / IN QUIZ ===
    # ================================

    async def start_in_per_quiz(self, user):
        questions = [
            {"question": "1. ___ estate vado spesso al mare.", "answer": "in"},
            {"question": "2. Ho studiato ___ due ore.", "answer": "per"},
            {"question": "3. Abitiamo ___ via Dante.", "answer": "in"},
            {"question": "4. Passiamo ___ Milano per andare a Roma.", "answer": "per"},
            {"question": "5. Vado al lavoro ___ bicicletta.", "answer": "in"},
            {"question": "6. Il treno parte ___ Milano alle 8.", "answer": "per"},
            {"question": "7. È ___ crisi per il lavoro.", "answer": "in"},
            {"question": "8. Studio ___ migliorare il mio italiano.", "answer": "per"},
            {"question": "9. Vado a scuola ___ piedi.", "answer": "a"},
            {"question": "10. Sono ___ piedi da due ore!", "answer": "in"}
        ]
        await self.run_quiz(user, questions, "IN o PER")

    async def run_quiz(self, user, questions, title):
        try:
            dm = await user.create_dm()
            await dm.send(f"📚 **Quiz: {title}**\nRispondi scrivendo solo la preposizione corretta (es: `di`, `da`, `in`, `per`, `a`). Hai 60 secondi per ogni frase. Buona fortuna!")

            score = 0
            for q in questions:
                await dm.send(q["question"])
                try:
                    reply = await self.bot.wait_for(
                        "message",
                        timeout=60,
                        check=lambda m: m.author == user and m.channel == dm
                    )
                    if normalize(reply.content) == normalize(q["answer"]):
                        await dm.send("✅ Corretto!")
                        score += 1
                    else:
                        await dm.send(f"❌ Sbagliato! La risposta giusta era **{q['answer']}**.")
                except asyncio.TimeoutError:
                    await dm.send("⏰ Tempo scaduto per questa frase!")

            await dm.send(f"\n🏁 **Quiz finita!** Hai risposto correttamente a **{score} su {len(questions)}** frasi.")
            await dm.send("Vuoi riprovare? Torna nella thread e scrivi di nuovo `quiz`.")
        except Exception as e:
            print(f"❌ Errore nella quiz ({title}): {e}")
        finally:
            session_manager.end_quiz(user.id)

async def setup(bot):
    await bot.add_cog(Quiz(bot))