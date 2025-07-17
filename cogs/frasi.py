import discord
from discord.ext import commands
import random
import asyncio
from session_manager import start_session, end_session, is_user_in_active_session

TEST_NL_ZINNEN = [
    ("Waar is het station?", "Dov’è la stazione?"),
    ("Ik zou graag een tafel reserveren.", "Vorrei prenotare un tavolo."),
    ("Mag ik de rekening alstublieft?", "Il conto, per favore."),
    ("Ik heb een kamer gereserveerd.", "Ho prenotato una camera."),
    ("Hoeveel kost het?", "Quanto costa?"),
    ("Wat raad je aan?", "Cosa consigli?"),
    ("Ik begrijp het niet.", "Non capisco."),
    ("Kan je dat herhalen?", "Puoi ripetere?"),
    ("Ik ben allergisch voor melk.", "Sono allergico al latte."),
    ("Ik ben op zoek naar een apotheek.", "Sto cercando una farmacia."),
    ("Ik bel later terug.", "Richiamo più tardi."),
    ("Neem plaats, alstublieft.", "Si accomodi, per favore."),
    ("Dat is een goed idee.", "È una buona idea."),
    ("Sorry, ik kan niet komen.", "Mi dispiace, non posso venire."),
    ("Waar kan ik een taxi nemen?", "Dove posso prendere un taxi?"),
    ("Wilt u iets drinken?", "Vuole qualcosa da bere?"),
    ("Ik kom uit België.", "Vengo dal Belgio."),
    ("Hoe gaat het met u?", "Come sta?"),
    ("Gaat u zitten.", "Si sieda."),
    ("Welkom in Italië!", "Benvenuto in Italia!"),
    ("Bedankt voor de uitnodiging.", "Grazie per l’invito."),
    ("Kunt u mij helpen?", "Può aiutarmi?"),
    ("Ik spreek een beetje Italiaans.", "Parlo un po’ di italiano."),
    ("Ik zou graag iets bestellen.", "Vorrei ordinare qualcosa."),
    ("Tot ziens!", "Arrivederci!")
]

class FrasiIdiomatiche(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_users = {}

    @commands.command(name="frasi")
    async def start_frasi_game(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and ctx.channel.id != 123456789013345:
            return

        if is_user_in_active_session(ctx.author.id):
            await ctx.reply("⏳ Hai già una sessione attiva. Finiscila prima di iniziarne una nuova.", mention_author=False)
            return

        await start_session(ctx.author.id, "frasi")

        try:
            await ctx.reply("📩 Il gioco è stato avviato nella tua DM! Controlla i tuoi messaggi privati.") if not isinstance(ctx.channel, discord.DMChannel) else None
            dm = ctx.author if isinstance(ctx.channel, discord.DMChannel) else await ctx.author.create_dm()
            await self.run_game(dm, ctx.author)
        except Exception as e:
            print(f"Fout bij starten frasi-spel: {e}")
            await end_session(ctx.author.id)

    async def run_game(self, dm, user):
        await dm.send("🎯 Benvenuto/a al gioco **Frasi idiomatiche**! Ti darò 10 frasi in olandese, tu dovrai tradurle in italiano. Hai 90 secondi per ogni frase.\nSe fai almeno 8 su 10, sblocchi un bonus round!")

        selected = random.sample(TEST_NL_ZINNEN, 10)
        score = 0

        for i, (nl, it) in enumerate(selected, 1):
            await dm.send(f"📝 Frase {i}/10:\n**{nl}**\n✍️ Scrivi la traduzione in italiano:")

            try:
                def check(m): return m.author == user and m.channel == dm
                msg = await self.bot.wait_for('message', timeout=90.0, check=check)
            except asyncio.TimeoutError:
                await dm.send("⏰ Tempo scaduto! Nessuna risposta registrata.")
                continue

            if normalize(msg.content) == normalize(it):
                score += 1
                await dm.send("✅ Corretto!")
            else:
                await dm.send(f"❌ Non esatto. La risposta giusta era: **{it}**")

        await dm.send(f"\n📊 Hai ottenuto **{score}/10** risposte corrette.")

        if score >= 8:
            await self.run_bonus_round(dm, user)
        else:
            await dm.send("💡 Riprova la prossima settimana per ottenere una ⭐!")

        await end_session(user.id)

    async def run_bonus_round(self, dm, user):
        await dm.send("\n🌟 Bonus round! Hai sbloccato 5 frasi extra. Se ne traduci almeno 3, guadagni una ⭐!")

        bonus = random.sample([p for p in TEST_NL_ZINNEN if p not in []], 5)
        bonus_score = 0

        for i, (nl, it) in enumerate(bonus, 1):
            await dm.send(f"💬 Bonus {i}/5:\n**{nl}**\n✍️ Traduci in italiano:")

            try:
                def check(m): return m.author == user and m.channel == dm
                msg = await self.bot.wait_for('message', timeout=90.0, check=check)
            except asyncio.TimeoutError:
                await dm.send("⏰ Tempo scaduto!")
                continue

            if normalize(msg.content) == normalize(it):
                bonus_score += 1
                await dm.send("✅ Corretto!")
            else:
                await dm.send(f"❌ Risposta giusta: **{it}**")

        if bonus_score >= 3:
            await dm.send("🏆 Complimenti! Hai ottenuto una ⭐!")
        else:
            await dm.send("✨ Bravo/a per aver completato il bonus round!")

def normalize(text):
    return ''.join(c.lower() for c in text if c.isalnum())
        
async def setup(bot):
    await bot.add_cog(FrasiIdiomatiche(bot))