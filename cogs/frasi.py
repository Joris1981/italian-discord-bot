import discord
from discord.ext import commands
import random
import asyncio
import datetime
import re
from session_manager import start_session, end_session, is_user_in_active_session

TIJDSLIMIET = 90

# Tijdelijke testzinnen
TEST_ZINNEN = {
    "Mag ik een tafel voor twee reserveren?": "Posso prenotare un tavolo per due?",
    "Ik zou graag willen bestellen.": "Vorrei ordinare.",
    "Hoeveel kost dit gerecht?": "Quanto costa questo piatto?",
    "De rekening alstublieft.": "Il conto, per favore.",
    "Waar is het dichtstbijzijnde metrostation?": "Dove si trova la stazione della metropolitana più vicina?",
    "Ik ben mijn sleutels kwijt.": "Ho perso le chiavi.",
    "Kan ik u iets vragen?": "Posso chiederle qualcosa?",
    "Ik wil graag een glas water.": "Vorrei un bicchiere d'acqua.",
    "Kunt u dat herhalen, alstublieft?": "Può ripetere, per favore?",
    "Ik begrijp het niet goed.": "Non capisco bene.",
    "Wat raadt u aan?": "Cosa consiglia?",
    "Ik heb een tafel gereserveerd.": "Ho prenotato un tavolo.",
    "Ik ben allergisch voor noten.": "Sono allergico alle noci.",
    "Ik spreek een beetje Italiaans.": "Parlo un po' di italiano.",
    "Kunt u trager spreken?": "Può parlare più lentamente?"
}

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # verwijder leestekens
    return text.strip()

class Frasi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='frasi')
    async def start_frasi_game(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and ctx.channel.id != 123456789013345:
            await ctx.send("❗ Puoi usare questo comando solo in DM o nel thread designato.")
            return

        if is_user_in_active_session(ctx.author.id):
            await ctx.send("⏳ Hai già una sessione attiva.")
            return

        if not start_session(ctx.author.id, "frasi"):
            await ctx.send("⏳ Hai già una sessione attiva.")
            return

        try:
            await ctx.send("🎯 Benvenuto/a al gioco *Frasi idiomatiche*! Prova a tradurre in italiano le seguenti frasi. Hai 90 secondi per ogni frase. Se ne traduci correttamente 8 su 10, avrai accesso a un bonus round! Iniziamo!\n")

            zinnen = list(TEST_ZINNEN.items())
            random.shuffle(zinnen)
            score = 0

            for i, (nl, it) in enumerate(zinnen[:10]):
                await ctx.send(f"📝 Frase {i+1}/10:\n**{nl}**")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    reply = await self.bot.wait_for('message', timeout=TIJDSLIMIET, check=check)
                    if normalize(reply.content) == normalize(it):
                        await ctx.send("✅ Corretto!")
                        score += 1
                    else:
                        await ctx.send(f"❌ Risposta sbagliata.\nLa risposta corretta era:\n**{it}**")
                except asyncio.TimeoutError:
                    await ctx.send(f"⏱️ Tempo scaduto! La risposta corretta era:\n**{it}**")

            await ctx.send(f"🧮 Hai ottenuto {score}/10 punti.")

            if score >= 8:
                await ctx.send("🎉 Complimenti! Hai diritto al **bonus round**! Prova a tradurre altre 5 frasi!")

                bonus_zinnen = zinnen[10:15]
                bonus_score = 0

                for i, (nl, it) in enumerate(bonus_zinnen):
                    await ctx.send(f"\n🌟 Bonus frase {i+1}/5:\n**{nl}**")

                    try:
                        reply = await self.bot.wait_for('message', timeout=TIJDSLIMIET, check=check)
                        if normalize(reply.content) == normalize(it):
                            await ctx.send("✅ Corretto!")
                            bonus_score += 1
                        else:
                            await ctx.send(f"❌ Risposta sbagliata.\nLa risposta corretta era:\n**{it}**")
                    except asyncio.TimeoutError:
                        await ctx.send(f"⏱️ Tempo scaduto! La risposta corretta era:\n**{it}**")

                await ctx.send(f"⭐ Hai ottenuto {bonus_score}/5 nel bonus round.")

                if bonus_score >= 3:
                    await ctx.send("🏅 Bravo! Hai guadagnato una **stella** per questa settimana!")
                else:
                    await ctx.send("💡 Non hai guadagnato la stella, ma ottimo tentativo!")

            await ctx.send("🎯 *Il gioco è terminato.* Se vuoi migliorare il tuo punteggio, puoi sempre riprovare! Grazie per aver partecipato!")
        finally:
            end_session(ctx.author.id)

async def setup(bot):
    await bot.add_cog(Frasi(bot))