import discord
from discord.ext import commands
import unicodedata
import re
import asyncio
from session_manager import session_manager

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
            if session_manager.has_active_session(user_id):
                await message.channel.send("❌ Hai già una quiz attiva. Completa prima quella prima di iniziarne un'altra.")
                return

            if message.channel.id == 1388866025679880256:
                await self.start_di_da_quiz(message.author)
            elif message.channel.id == 1390080013533052949:
                await self.start_in_per_quiz(message.author)
            elif message.channel.id == 1390247257609207819:
                await self.start_qualche_quiz(message)

        elif isinstance(message.channel, discord.DMChannel) and user_id in self.active_quizzes:
            await self.handle_quiz_answer(message, self.active_quizzes[user_id])

    # ================================
    # === QUALCHE / ALCUNI QUIZ ===
    # ================================

    async def start_qualche_quiz(self, message):
        user_id = str(message.author.id)
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
            ("Non c’è ___ persona che lo sappia.", "nessuna"),
        ]
        try:
            await message.author.send(
                "📘 **Quiz: Qualche, Alcuni, Nessuno, Alcuno**\n"
                "Rispondi con la parola corretta: *qualche, alcuni, alcune, alcuno, alcuna, nessuno, nessuna, nessun, alcun*.\n"
                "Hai 14 frasi. Iniziamo!"
            )
            self.active_quizzes[user_id] = {
                "type": "qualche",
                "index": 0,
                "score": 0,
                "questions": questions
            }
            session_manager.start_quiz(int(user_id))
            await self.ask_next_question(message.author)
        except discord.Forbidden:
            await message.channel.send("❌ Non posso inviarti un messaggio privato. Controlla le impostazioni di privacy.")

    @commands.command(name="qualche-soluzioni")
    async def qualche_soluzioni(self, ctx):
        solutions = [
            "**Non c’è nessun problema**, tutto è sotto controllo.",
            "**Ho conosciuto alcune ragazze simpatiche** ieri sera.",
            "**Non ho ricevuto nessuna risposta** alla mia mail.",
            "**Qualche volta andiamo in bici** al lavoro.",
            "**Non c’era nessuno** alla festa, era deserta.",
            "**Hai letto qualche libro interessante** ultimamente?",
            "**Non ho alcuna voglia** di studiare oggi.",
            "**Alcuni studenti sono partiti** in anticipo.",
            "**Non c’è alcun motivo** di preoccuparsi.",
            "**Non conosco nessuno** con quel nome.",
            "**Qualche idea è stata accettata.**",
            "**Non ho trovato nessuna soluzione.**",
            "**C’erano alcuni problemi tecnici.**",
            "**Non c’è nessuna persona** che lo sappia."
        ]
        try:
            for s in solutions:
                await ctx.author.send(s)
        except discord.Forbidden:
            await ctx.send("❌ Non posso inviarti un messaggio privato. Controlla le impostazioni di privacy.")

    async def handle_quiz_answer(self, message, quiz_data):
        answer = normalize(message.content)
        index = quiz_data["index"]
        question, correct = quiz_data["questions"][index]
        if answer == normalize(correct):
            await message.channel.send("✅ Corretto!")
            quiz_data["score"] += 1
        else:
            await message.channel.send(f"❌ Sbagliato! Risposta corretta: **{correct}**")
        quiz_data["index"] += 1

        if quiz_data["index"] < len(quiz_data["questions"]):
            await self.ask_next_question(message.channel)
        else:
            score = quiz_data["score"]
            del self.active_quizzes[str(message.author.id)]
            session_manager.end_quiz(message.author.id)
            await message.channel.send(
                f"**Quiz completata!**\nHai totalizzato **{score}/14** risposte corrette. 🎉\n"
                "Se vuoi controllare tutte le risposte corrette, scrivi qui in DM:\n`!qualche-soluzioni` 📚\n"
                "➡️ **Opnieuw proberen? Typ gewoon opnieuw quiz in dezelfde thread.**"
            )

    async def ask_next_question(self, user):
        try:
            quiz_data = self.active_quizzes[str(user.id)]
            question, _ = quiz_data["questions"][quiz_data["index"]]
            await user.send(f"{quiz_data['index']+1}/14: {question}")
        except Exception as e:
            print(f"❌ Fout bij het verzenden van de quizvraag: {e}")

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
            session_manager.start_quiz(user.id)

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