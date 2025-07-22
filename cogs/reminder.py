import discord
from discord.ext import commands, tasks
import random
import datetime
import pytz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📬 Motiverende DM-berichten
REMINDER_MESSAGGI = [
    "📚 Allenarsi ogni giorno è il segreto del successo. Anche solo 5 minuti fanno la differenza!",
    "🇮🇹 Non dimenticare: un po’ di italiano al giorno toglie l’insicurezza di torno!",
    "💡 Ogni quiz è un passo in più verso la fluidità. Ne hai già fatto uno oggi?",
    "🧠 La costanza batte il talento. Fai un quiz oggi e allenati con piacere!",
    "🚀 Anche una piccola pratica quotidiana ti porta lontano. Continua così!",
    "⏰ È il momento giusto per fare un quiz! Scegli un tema e mettiti alla prova!",
    "✨ Ogni esercizio ti avvicina alla padronanza dell’italiano. Non mollare!",
    "🔄 La ripetizione è la chiave. Torna sui quiz e consolida ciò che hai imparato!",
    "🎯 Hai già fatto il quiz su DI o DA? O su i pronomi? Sfidati ora!",
    "🌟 Nuovi quiz sono disponibili! Apri i tuoi DM e comincia a esercitarti!"
]

# 👤 Gebruikers-ID's voor DM reminders
GEBRUIKERS_IDS = [
    1387550404748906516,
    1387553057285345432,
    1387645018847838270,
    1389172460867555413,
    1387557586844385361
    # voeg extra gebruikers toe
]

# 📣 Kanaal en thread ID's
WORDLE_KANAAL_ID = 1390779837593026594
FRASI_THREAD_ID = 1395557049269747887

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quiz_reminder.start()
        self.weekly_wordle_reminder.start()
        self.weekly_frasi_reminder.start()

    def cog_unload(self):
        self.quiz_reminder.cancel()
        self.weekly_wordle_reminder.cancel()
        self.weekly_frasi_reminder.cancel()

    # 🔁 DM-reminder elke 72 uur
    @tasks.loop(hours=72)
    async def quiz_reminder(self):
        for user_id in GEBRUIKERS_IDS:
            try:
                user = await self.bot.fetch_user(user_id)
                reminder = random.choice(REMINDER_MESSAGGI)
                await user.send(reminder)
                logger.info(f"Reminder sent to {user.name} ({user.id})")
            except discord.Forbidden:
                logger.warning(f"Cannot DM user {user_id}, permission denied.")
            except Exception as e:
                logger.error(f"Error sending reminder to {user_id}: {e}")
    
    @quiz_reminder.before_loop
    async def before_quiz_reminder(self):
        await self.bot.wait_until_ready()
        # Start de eerste cyclus pas 72 uur NA het opstarten
        logger.info("Wacht 72 uur tot eerste quiz reminder.")

    # 📆 Dinsdag 9u00 – Wordle reminder
    @tasks.loop(minutes=1)
    async def weekly_wordle_reminder(self):
        await self.bot.wait_until_ready()
        now = datetime.datetime.now(pytz.timezone("Europe/Brussels"))
        if now.weekday() == 1 and now.hour == 9 and now.minute == 0:  # dinsdag 09:00
            try:
                channel = self.bot.get_channel(WORDLE_KANAAL_ID)
                if channel:
                    await channel.send(
                        "@everyone 🕘 *Ultimo giorno per migliorare il tuo punteggio!*\n\n"
                        "Mercoledì arriva un nuovo tema per il gioco `!wordle`.\n"
                        "Hai tempo fino a stasera per giocare o riprovare per migliorare la tua classifica!\n"
                        "💪 Non mollare — ogni punto può fare la differenza!\n"
                        " Per iniziare, digita il comando !wordle nella tua inbox con ItalianoBot.\n"
                    )
                    logger.info("Wordle reminder verzonden.")
            except Exception as e:
                logger.error(f"Fout bij verzenden Wordle reminder: {e}")

    # 📆 Donderdag 9u00 – Frasi reminder
    @tasks.loop(minutes=1)
    async def weekly_frasi_reminder(self):
        await self.bot.wait_until_ready()
        now = datetime.datetime.now(pytz.timezone("Europe/Brussels"))
        if now.weekday() == 5 and now.hour == 9 and now.minute == 0:  # sabato 09:00
            try:
                thread = self.bot.get_channel(FRASI_THREAD_ID)
                if thread:
                    await thread.send(
                        "@everyone 🕘 *Ultimo giorno per migliorare il tuo punteggio nel gioco `!frasi`!*\n\n"
                        "Domani arriva un nuovo tema: gioca o riprova ora per salire nella classifica! 🏆\n"
                        "Ogni frase conta, non lasciarti sfuggire l'occasione! ✨ \n"
                        "Hai tempo fino a stasera per giocare o riprovare per migliorare il tuo punteggio.\n" \
                        "Per iniziare, digita il comando !frasi nella tua inbox con ItalianoBot.\n"
                    )
                    logger.info("Frasi reminder verzonden.")
            except Exception as e:
                logger.error(f"Fout bij verzenden Frasi reminder: {e}")

    @weekly_wordle_reminder.before_loop
    @weekly_frasi_reminder.before_loop
    async def before_all_reminders(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Reminder(bot))