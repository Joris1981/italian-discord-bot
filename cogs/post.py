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

        # Embed 1: Intro + Quiz interattivi
        embed1 = discord.Embed(
            title="📚 Oefeningen en tools om je Italiaans te oefenen 🇮🇹",
            description=(
                "Ik heb jullie feedback gehoord: de quizzen en oefeningen waren soms moeilijk terug te vinden."
                " Daarom vind je hier een duidelijk overzicht van alle interactieve tools, oefeningen en spellen"
                " die je kunt gebruiken om je Italiaans te verbeteren.\n\n"
                "🔄 We voegen regelmatig nieuwe oefeningen toe. Kom dus zeker terug om te ontdekken wat er nieuw is!"
            ),
            color=discord.Color.blue()
        )

        embed1.add_field(
            name="🎯 Quiz interattivi",
            value=(
                "Typ `quiz` in de thread van een specifiek onderwerp. De bot stuurt je dan 20 zinnen die je meteen kunt oplossen."
                " Je krijgt directe feedback op elk antwoord. Kies hieronder het onderwerp dat je wil oefenen:\n"
                "[DI o DA](https://discord.com/channels/123456789012345678/1388866025679880256)\n"
                "[PER o IN](https://discord.com/channels/123456789012345678/1390080013533052949)\n"
                "[QUALCHE / ALCUNI / NESSUNO](https://discord.com/channels/123456789012345678/1390371003414216805)\n"
                "[CI – usi diversi](https://discord.com/channels/123456789012345678/1388241920790237347)\n"
                "[PRONOMI – diretti e indiretti](https://discord.com/channels/123456789012345678/1394735397824758031)\n"
                "[BELLO – tutte le forme](https://discord.com/channels/123456789012345678/1396072250221920276)\n"
                "[COMPARATIVI](https://discord.com/channels/123456789012345678/1393289069009830038)\n"
                "[CHI o CHE](https://discord.com/channels/123456789012345678/1393269447094960209)\n"
                "[CI / DI / NE](https://discord.com/channels/123456789012345678/1393280441221644328)\n"
                "[TRA / FRA / DOPO](https://discord.com/channels/123456789012345678/1390091443678478397)\n"
                "[BUONO o BENE](https://discord.com/channels/123456789012345678/1397860505808535573)"
            ),
            inline=False
        )

        # Embed 2: Esercizi + schrijven + luisteren
        embed2 = discord.Embed(color=discord.Color.blue())

        embed2.add_field(
            name="✍️ Esercizi su carta",
            value=(
                "We hebben ook klassieke invuloefeningen die je zelf op papier of digitaal kan maken.\n"
                "Controleer je antwoorden nadien met het bijhorende commando voor de oplossingen.\n"
                "[Imperfetto](https://discord.com/channels/123456789012345678/1388907175920795658) – `!imperfetto-esercizio` / `!imperfetto-soluzioni`\n"
                "[Passato prossimo](https://discord.com/channels/123456789012345678/1388907630889664522) – `!passato-esercizio` / `!passato-esercizio-soluzioni`"
            ),
            inline=False
        )

        embed2.add_field(
            name="📝 Schrijfoefeningen",
            value=(
                "In deze threads kun je korte teksten of zinnen schrijven. De bot controleert automatisch je spelling en grammatica.\n"
                "[A chi? A cosa?](https://discord.com/channels/123456789012345678/1394729973939699753)\n"
                "[Com'era la situazione](https://discord.com/channels/123456789012345678/1387853018845810891)\n"
                "[Oggi ho fatto](https://discord.com/channels/123456789012345678/1387573784055255263)\n\n"
                "📌 Vrij schrijven? Gebruik [Due Parole](https://discord.com/channels/123456789012345678/1387569943746318386) voor eigen teksten met bot-feedback."
            ),
            inline=False
        )

        embed2.add_field(
            name="🎧 Luistervaardigheid",
            value=(
                "Wekelijkse podcasts met transcript in PDF:\n"
                "📥 [Podcastkanaal](https://discord.com/channels/123456789012345678/1387594096759144508)\n\n"
                "Begrijpend luisteren – luister en beantwoord de vragen:\n"
                "🔊 [Dai accompagni](https://discord.com/channels/123456789012345678/1388473121346027520)\n"
                "🔊 [Spaghetti alla puttanesca](https://discord.com/channels/123456789012345678/1390073410826014903)\n"
                "🔊 [Cristina e la sua famiglia](https://discord.com/channels/123456789012345678/1390410564093743285)\n"
                "🔊 [Cos'hai fatto?](https://discord.com/channels/123456789012345678/1394796805283385454)"
            ),
            inline=False
        )

        # Embed 3: Lezen, muziek, spel en afsluiter
        embed3 = discord.Embed(color=discord.Color.blue())

        embed3.add_field(
            name="📖 Begrijpend lezen",
            value=(
                "Lees korte nieuwsberichten in het Italiaans. Vaak met audio zodat je ook uitspraak kan oefenen.\n"
                "📚 [Nieuws & lettura](https://discord.com/channels/123456789012345678/1395140458493251776)"
            ),
            inline=False
        )

        embed3.add_field(
            name="🎶 Italiaanse muziek delen",
            value=(
                "Deel je favoriete nummers met een YouTube-link.\n"
                "De bot helpt met tekst en vertaling.\n"
                "🎵 [Muziek & vertaling](https://discord.com/channels/123456789012345678/1390448992520765501)"
            ),
            inline=False
        )

        embed3.add_field(
            name="🎮 Giochi – leer via spel!",
            value=(
                "[!wordle](https://discord.com/channels/123456789012345678/1389552706783543307) – Raad het Italiaanse woord\n"
                "[!frasi](https://discord.com/channels/123456789012345678/1395771435632431104) – Vervoeg het juiste werkwoord in 20 zinnen + bonusronde\n"
                "[!verbi](https://discord.com/channels/123456789012345678/1397248870056067113) – Coniugazione: vervoegen op tijd en niveau"
            ),
            inline=False
        )

        embed3.set_footer(text="✨ Elke oefening helpt je weer een stapje verder. Suggesties voor nieuwe onderwerpen zijn altijd welkom. Forza! Continuiamo insieme 💪🇮🇹")

        await kanaal.send(embed=embed1)
        await kanaal.send(embed=embed2)
        await kanaal.send(embed=embed3)
        await ctx.send("✅ Alle overzichtsberichten zijn gepost!")

async def setup(bot):
    await bot.add_cog(OefeningenOverzicht(bot))