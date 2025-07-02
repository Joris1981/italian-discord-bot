import discord
from discord.ext import commands
import asyncio

class InPerQuiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quiz_thread_id = 1390080013533052949
        self.active_quizzes = {}

        self.questions = [
            {"question": "___ estate vado spesso al mare.", "answer": "in"},
            {"question": "Ho studiato ___ due ore.", "answer": "per"},
            {"question": "Abitiamo ___ via Dante.", "answer": "in"},
            {"question": "Passiamo ___ Milano per andare a Roma.", "answer": "per"},
            {"question": "Vado al lavoro ___ bicicletta.", "answer": "in"},
            {"question": "Il treno parte ___ Milano alle 8.", "answer": "per"},
            {"question": "È ___ crisi per il lavoro.", "answer": "in"},
            {"question": "Studio ___ migliorare il mio italiano.", "answer": "per"},
            {"question": "Vado a scuola ___ piedi.", "answer": "a"},  # uitzondering!
            {"question": "Sono ___ piedi da due ore!", "answer": "in"},
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == self.quiz_thread_id and message.content.lower().strip() == "quiz":
            if message.author.id in self.active_quizzes:
                await message.channel.send(f"{message.author.mention} stai già facendo la quiz in DM!")
                return
            await self.start_quiz(message)

    async def start_quiz(self, message):
        user = message.author
        self.active_quizzes[user.id] = True

        try:
            dm = await user.create_dm()
            await dm.send("📚 **Quiz: IN o PER?**\nRispondi scrivendo solo `in`, `per` oppure `a` (in 1 geval).\nHai 60 secondi per ogni frase. Buona fortuna!")

            score = 0
            for idx, q in enumerate(self.questions, 1):
                await dm.send(f"{idx}. {q['question']}")
                try:
                    response = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author == user and m.channel == dm,
                        timeout=60
                    )
                    answer = response.content.lower().strip()
                    if answer == q["answer"]:
                        await dm.send("✅ Corretto!")
                        score += 1
                    else:
                        await dm.send(f"❌ Sbagliato! La risposta giusta era **{q['answer']}**.")
                except asyncio.TimeoutError:
                    await dm.send("⏰ Tempo scaduto per questa frase!")

            await dm.send(f"\n🏁 **Quiz finita!** Hai risposto correttamente a **{score} su {len(self.questions)}** frasi.")
            await dm.send("Vuoi riprovare? Torna nella thread e scrivi di nuovo `quiz`.")
        except Exception as e:
            print(f"Fout tijdens quiz: {e}")
        finally:
            if user.id in self.active_quizzes:
                del self.active_quizzes[user.id]

async def setup(bot):
    await bot.add_cog(InPerQuiz(bot))