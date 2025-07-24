import discord
from discord.ext import commands

class OefeningenOverzicht(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.toegestaan_kanaal = 1388667261761359932  # testkanaal
        self.doel_kanaal = 1397885271248470056        # waar het embedbericht naartoe moet

    @commands.command(name="post-oefeningen")
    @commands.is_owner()
    async def post_oefeningen_embed(self, ctx):
        if ctx.channel.id != self.toegestaan_kanaal:
            return await ctx.send("⛔ Dit commando is enkel beschikbaar in het testkanaal.")

        kanaal = self.bot.get_channel(self.doel_kanaal)
        if not kanaal:
            return await ctx.send("⚠️ Doelkanaal niet gevonden. Controleer het ID.")

        # Embed 1: Intro + Quiz interattivi (in 2 delen)
        embed1 = discord.Embed(
            title="📚 Oefeningen en tools om je Italiaans te oefenen 🇮🇹",
            description=(
                "Ik heb jullie feedback gehoord: de quizzen en oefeningen waren soms moeilijk terug te vinden."
                " Daarom vind je hier een duidelijk overzicht van alle interactieve tools, oefeningen en spellen"
                " die je kunt gebruiken om je Italiaans te verbeteren.\n\n"
                "📌 Alle links in dit bericht zijn klikbaar – ze brengen je rechtstreeks naar het juiste onderwerp.\n"
                "🔄 We voegen regelmatig nieuwe oefeningen toe. Kom dus zeker terug om te ontdekken wat er nieuw is!"
            ),
            color=discord.Color.blue()
        )

        embed1.add_field(
            name="🎯 Quiz interattivi (deel 1)",
            value=(
                "Lees eerst de grammaticale uitleg in de thread van het onderwerp dat je wil oefenen.\n"
                "Typ daarna `quiz` als bericht in diezelfde thread.\n"
                "De bot stuurt je dan 20 oefenzinnen in je privéberichten (DM).\n"
                "Beantwoord de zinnen in je inbox – je krijgt onmiddellijk feedback op elk antwoord.\n\n"
                "Kies hieronder het onderwerp dat je wil oefenen:\n"
                "[DI o DA](https://discord.com/channels/1387552031132094709/1388866025679880256)\n"
                "[PER o IN](https://discord.com/channels/1387552031132094709/1390080013533052949)\n"
                "[QUALCHE / ALCUNI / NESSUNO](https://discord.com/channels/1387552031132094709/1390371003414216805)\n"
                "[CI – usi diversi](https://discord.com/channels/1387552031132094709/1388241920790237347)\n"
                "[PRONOMI – diretti e indiretti](https://discord.com/channels/1387552031132094709/1394735397824758031)"
            ),
            inline=False
        )

        embed1.add_field(
            name="🎯 Quiz interattivi (deel 2)",
            value=(
                "[BELLO – tutte le forme](https://discord.com/channels/1387552031132094709/1396072250221920276)\n"
                "[COMPARATIVI](https://discord.com/channels/1387552031132094709/1393289069009830038)\n"
                "[CHI o CHE](https://discord.com/channels/1387552031132094709/1393269447094960209)\n"
                "[CI / DI / NE](https://discord.com/channels/1387552031132094709/1393280441221644328)\n"
                "[TRA / FRA / DOPO](https://discord.com/channels/1387552031132094709/1390091443678478397)\n"
                "[BUONO o BENE](https://discord.com/channels/1387552031132094709/1397860505808535573)"
            ),
            inline=False
        )

        # Embed 2: Esercizi + schrijven + luisteren
        embed2 = discord.Embed(color=discord.Color.blue())

        embed2.add_field(
            name="✍️ Esercizi su carta",
            value=(
                "Er zijn ook klassieke invuloefeningen die je op je eigen tempo kunt maken, op papier.\n"
                "Typ in het grammatica kanaal het commando, bv. `!passato-esercizio`, in de betreffende thread om de oefening te krijgen.\n"
                "Maak eerst de oefening zonder hulp, en gebruik daarna het bijhorende commando, bv. `!passato-esercizio-soluzioni`, om je antwoorden te controleren.\n"
                "Zo oefen je actief en leer je uit je fouten.\n"
                "[Imperfetto](https://discord.com/channels/1387552031132094709/1388907175920795658) – `!imperfetto-esercizio` / `!imperfetto-soluzioni`\n"
                "[Passato prossimo](https://discord.com/channels/1387552031132094709/1388907630889664522) – `!passato-esercizio` / `!passato-esercizio-soluzioni`"
            ),
            inline=False
        )

        embed2.add_field(
            name="📝 Schrijfoefeningen",
            value=(
                "In deze threads kun je korte teksten of zinnen schrijven. De bot controleert automatisch je spelling en grammatica.\n"
                "[A chi? A cosa?](https://discord.com/channels/1387552031132094709/1394729973939699753)\n"
                "[Com'era la situazione](https://discord.com/channels/1387552031132094709/1387853018845810891)\n"
                "[Oggi ho fatto](https://discord.com/channels/1387552031132094709/1387573784055255263)\n\n"
                "📌 Vrij schrijven? Gebruik [Due Parole](https://discord.com/channels/1387552031132094709/1387569943746318386) voor eigen teksten met bot-feedback."
            ),
            inline=False
        )

        embed2.add_field(
            name="🎧 Luistervaardigheid",
            value=(
                "We posten regelmatig een interessante podcast die je kan beluisteren met of zonder transcript.\n"
                "Een ideale manier om je luistervaardigheid te verbeteren én je woordenschat uit te breiden op een leuke manier.\n"
                "Wekelijkse podcasts met transcript in PDF:\n"
                "📥 [Podcastkanaal](https://discord.com/channels/1387552031132094709/1387594096759144508)\n\n"
                "**Begrijpend luisteren** – luister naar het fragment, doe de bijhorende oefening of beantwoord de vragen.\n"
                "Gebruik nadien het juiste commando in de thread om het transcript in jouw inbox te ontvangen.\n"
                "Bijvoorbeeld: `!ascolto_cristina`, `!ascolto_coshaifatto`, ... enz.\n\n"
                "🔊 [Dai accompagni](https://discord.com/channels/1387552031132094709/1388473121346027520)\n"
                "🔊 [Spaghetti alla puttanesca](https://discord.com/channels/1387552031132094709/1390073410826014903)\n"
                "🔊 [Cristina e la sua famiglia](https://discord.com/channels/1387552031132094709/1390410564093743285)\n"
                "🔊 [Cos'hai fatto?](https://discord.com/channels/1387552031132094709/1394796805283385454)"
            ),
            inline=False
        )

        # Embed 3: Lezen, muziek, spel en afsluiter
        embed3 = discord.Embed(color=discord.Color.blue())

        embed3.add_field(
            name="📖 Begrijpend lezen",
            value=(
                "Lees korte nieuwsberichten in het Italiaans. Vaak met audio zodat je ook uitspraak kan oefenen.\n"
                "📚 [Nieuws & lettura](https://discord.com/channels/1387552031132094709/1395140458493251776)"
            ),
            inline=False
        )

        embed3.add_field(
            name="🎶 Italiaanse muziek delen",
            value=(
                "Deel je favoriete nummers met een YouTube-link.\n"
                "De bot helpt met tekst en vertaling.\n"
                "🎵 [Muziek & vertaling](https://discord.com/channels/1387552031132094709/1390448992520765501)"
            ),
            inline=False
        )

        embed3.add_field(
            name="🎮 Giochi – leer via spel! (deel 1)",
            value=(
                "🆕 Elke week publiceert de bot nieuwe zinnen of thema’s, zodat je telkens iets nieuws kunt oefenen.\n"
                "📊 Je resultaten worden automatisch opgenomen in het wekelijkse [Leaderboard](https://discord.com/channels/1387552031132094709/1390779837593026594).\n"
                "Een beetje competitie houdt iedereen gemotiveerd! 💪🇮🇹\n\n"
                "[!wordle](https://discord.com/channels/1387552031132094709/1389552706783543307) – Vertaal woorden uit het Nederlands naar het Italiaans. Elke week een nieuw thema.\n"
                "[!frasi](https://discord.com/channels/1387552031132094709/1395771435632431104) – Vertaal volledige zinnen naar het Italiaans en leer ook mogelijke varianten."
            ),
            inline=False
        )

        embed3.add_field(
            name="🎮 Giochi – leer via spel! (deel 2)",
            value=(
                "[!verbi](https://discord.com/channels/1387552031132094709/1397248870056067113) – Vervoeg Italiaanse werkwoorden correct in context. Elke week nieuwe zinnen.\n\n"
                "📌 Je kunt deze spellen ook rechtstreeks starten in je inbox (DM) door een bericht te sturen naar **ItalianoBot** 🤖.\n"
                "Typ daar gewoon `!wordle`, `!frasi` of `!verbi` om het spel onmiddellijk te starten."
            ),
            inline=False
        )

        embed3.add_field(
            name="📢 Heb je een suggestie?",
            value=(
                "Heb je een idee voor een nieuwe oefening of spel? Laat het weten in de [suggesties thread](https://discord.com/channels/1387552031132094709/1387552031631478942)!\n"
                "Nieuwe ideeën om samen te leren en te groeien zijn altijd welkom. Grazie mille! 🙏"
            ),
            inline=False
        )
        embed3.set_footer(
            text="✨ **Elke oefening helpt je weer een stapje verder.** Forza! Continuiamo insieme 💪🇮🇹"
        )

        await kanaal.send(embed=embed1)
        await kanaal.send(embed=embed2)
        await kanaal.send(embed=embed3)
        await ctx.send("✅ Alle overzichtsberichten zijn gepost!")

async def setup(bot):
    await bot.add_cog(OefeningenOverzicht(bot))