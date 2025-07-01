import discord
from discord.ext import commands

class Grammatica(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ================================
    # TOEKOMST – REGELS EN UITZONDERINGEN
    # ================================

    @commands.command(name="futuro-regole")
    async def futuro_regole(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Regole del futuro semplice (verbi regolari):**\n\n"
            "\U0001F539 **-ARE → -ERÒ**\n"
            "\u2733\ufe0f Attenzione: la **\"a\" cambia in \"e\"** nella radice!\n"
            "Esempio: *parlare → parlerò* (non **parlarò**)\n"
            "Esempio: *mangiare → mangerò*\n\n"
            "\U0001F539 **-ERE → -ERÒ**\n"
            "Esempio: *credere → crederò*\n\n"
            "\U0001F539 **-IRE → -IRÒ**\n"
            "Esempio: *partire → partirò*\n\n"
            "\U0001F4CC Tutte le persone usano le stesse desinenze:\n"
            "- io: **-ò**, tu: **-ai**, lui/lei: **-à**, noi: **-emo**, voi: **-ete**, loro: **-anno**\n\n"
            "\U0001F4A1 *Esempio completo:* **parlare →** parlerò, parlerai, parlerà, parleremo, parlerete, parleranno\n\n"
            "\u2705 Per i verbi irregolari, vedi `!futuro-irregolari`"
        )

    @commands.command(name="futuro-irregolari")
    async def futuro_irregolari(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – verbi irregolari \U0001F1EE\U0001F1F9**\n\n"
            "\U0001F539 **essere → sar-**, **avere → avr-**, **andare → andr-**\n"
            "\U0001F539 **dovere → dovr-**, **potere → potr-**, **sapere → sapr-**\n"
            "\U0001F539 **vedere → vedr-**, **vivere → vivr-**, **volere → vorr-**\n\n"
            "\U0001F449 La **radice cambia**, ma le **desinenze restano**:\n"
            "**-ò, -ai, -à, -emo, -ete, -anno**\n\n"
            "\U0001F4CC *Esempio:* **essere →** sarò, sarai, sarà, saremo, sarete, saranno"
        )

    @commands.command(name="futuro-andare")
    async def futuro_andare(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – ANDARE \U0001F1EE\U0001F1F9**\n\n"
            "**Radice:** andr-\n"
            "io andrò, tu andrai, lui/lei andrà, noi andremo, voi andrete, loro andranno\n\n"
            "\U0001F4A1 Voorbeeld: *Sabato andremo al cinema.*"
        )

    @commands.command(name="futuro-avere")
    async def futuro_avere(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – AVERE \U0001F1EE\U0001F1F9**\n\n"
            "**Radice:** avr-\n"
            "io avrò, tu avrai, lui/lei avrà, noi avremo, voi avrete, loro avranno\n\n"
            "\U0001F4A1 Voorbeeld: *Avrò tempo domani pomeriggio.*"
        )

    @commands.command(name="futuro-essere")
    async def futuro_essere(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – ESSERE \U0001F1EE\U0001F1F9**\n\n"
            "**Radice:** sar-\n"
            "io sarò, tu sarai, lui/lei sarà, noi saremo, voi sarete, loro saranno\n\n"
            "\U0001F4A1 Voorbeeld: *Domani sarò molto felice.*"
        )

    # ================================
    # TOEKOMST - SPELLINGAANPASSINGEN
    # ================================

    @commands.command(name="futuro-baciare")
    async def futuro_baciare(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – BACIARE \U0001F1EE\U0001F1F9**\n\n"
            "**Stam:** baciar- → *bacerò* (zonder “i”)\n"
            "io bacerò, tu bacerai, lui/lei bacerà, noi baceremo, voi bacerete, loro baceranno\n\n"
            "\U0001F4A1 Voorbeeld: *Ti bacerò sotto le stelle.*"
        )

    @commands.command(name="futuro-mangiare")
    async def futuro_mangiare(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – MANGIARE \U0001F1EE\U0001F1F9**\n\n"
            "**Stam:** mangiar- → *mangerò* (zonder “i”)\n"
            "io mangerò, tu mangerai, lui/lei mangerà, noi mangeremo, voi mangerete, loro mangeranno\n\n"
            "\U0001F4A1 Voorbeeld: *Domani mangerò una pizza napoletana.*"
        )

    @commands.command(name="futuro-pagare")
    async def futuro_pagare(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – PAGARE \U0001F1EE\U0001F1F9**\n\n"
            "**Stam:** pagar- + h → *pagherò*\n"
            "io pagherò, tu pagherai, lui/lei pagherà, noi pagheremo, voi pagherete, loro pagheranno\n\n"
            "\U0001F4A1 Voorbeeld: *Pagherò il conto dopo cena.*"
        )

    @commands.command(name="futuro-giocare")
    async def futuro_giocare(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – GIOCARE \U0001F1EE\U0001F1F9**\n\n"
            "**Stam:** giocar- + h → *giocherò*\n"
            "io giocherò, tu giocherai, lui/lei giocherà, noi giocheremo, voi giocherete, loro giocheranno\n\n"
            "\U0001F4A1 Voorbeeld: *Giocheremo a carte tutta la sera.*"
        )

    @commands.command(name="futuro-guardare")
    async def futuro_guardare(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – GUARDARE \U0001F1EE\U0001F1F9**\n\n"
            "**Stam:** guardar- → *guarderò*\n"
            "io guarderò, tu guarderai, lui/lei guarderà, noi guarderemo, voi guarderete, loro guarderanno\n\n"
            "\U0001F4A1 Voorbeeld: *Guarderemo la partita insieme.*"
        )

    @commands.command(name="futuro-scrivere")
    async def futuro_scrivere(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – SCRIVERE \U0001F1EE\U0001F1F9**\n\n"
            "**Stam:** scriver-\n"
            "io scriverò, tu scriverai, lui/lei scriverà, noi scriveremo, voi scriverete, loro scriveranno\n\n"
            "\U0001F4A1 Voorbeeld: *Scriverò un libro tutto in italiano!*"
        )

    @commands.command(name="futuro-partire")
    async def futuro_partire(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Futuro semplice – PARTIRE \U0001F1EE\U0001F1F9**\n\n"
            "**Stam:** partir-\n"
            "io partirò, tu partirai, lui/lei partirà, noi partiremo, voi partirete, loro partiranno\n\n"
            "\U0001F4A1 Voorbeeld: *Partirò per Roma con il treno delle 8.*"
        )

    # ================================
    # IMPERFETTO – REGELS EN VOORBEELDEN
    # ================================

    @commands.command(name="imperfetto-regole")
    async def imperfetto_regole(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Regelmatige werkwoorden – Imperfetto**\n\n"
            "\U0001F539 **Wanneer gebruik je de imperfetto?**\n"
            "De imperfetto gebruik je om iets te beschrijven dat in het verleden:\n"
            "\u2013 herhaald of gewoonlijk gebeurde (vb. elke week, vroeger)\n"
            "\u2013 aan de gang was toen iets anders gebeurde\n"
            "\u2013 een achtergrond of situatie beschrijft (weer, omgeving, gevoel)\n"
            "\u2013 niet afgerond of niet tijdsgebonden is\n\n"
            "Voorbeelden:\n"
            "\u2013 Da piccolo andavo sempre al mare.\n"
            "\u2013 Mentre cucinavo, ascoltavo la musica.\n"
            "\u2013 Faceva caldo e il sole splendeva.\n"
            "\u2013 Non stavo bene ieri.\n\n"
            "\U0001F539 **Hoe vervoeg je regelmatige werkwoorden in de imperfetto?**\n"
            "\U0001F449 Neem de **infinitief** (zoals *parlare*, *credere*, *dormire*)\n"
            "\u274C Laat **-re** vallen\n"
            "\u2705 Voeg de uitgangen toe:\n\n"
            "**ARE** → parlare → parla-\n"
            "**ERE** → credere → crede-\n"
            "**IRE** → dormire → dormi-\n\n"
            "\U0001F9E9 **Uitgangen voor alle regelmatige werkwoorden:**\n"
            "- io → **-vo**\n"
            "- tu → **-vi**\n"
            "- lui/lei → **-va**\n"
            "- noi → **-vamo**\n"
            "- voi → **-vate**\n"
            "- loro → **-vano**\n\n"
            "\U0001F4DD Voorbeeld: *parlare*\n"
            "\u2013 io parlavo\n"
            "\u2013 tu parlavi\n"
            "\u2013 lui/lei parlava\n"
            "\u2013 noi parlavamo\n"
            "\u2013 voi parlavate\n"
            "\u2013 loro parlavano\n\n"
            "\U0001F4CE Bekijk ook `!imperfetto-irregolari` voor de uitzonderingen."
        )

    @commands.command(name="imperfetto-irregolari")
    async def imperfetto_irregolari(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Onregelmatige werkwoorden – Imperfetto**\n\n"
            "De meeste werkwoorden in de imperfetto zijn regelmatig, \n"
            "maar een paar **veelgebruikte** werkwoorden zijn onregelmatig:\n\n"
            "\U0001F7E0 **Essere** (zijn)\n"
            "io **ero**\ntu **eri**\nlui/lei **era**\nnoi **eravamo**\nvoi **eravate**\nloro **erano**\n\n"
            "\U0001F7E0 **Fare** (doen/maken) → stam: face-\n"
            "io **facevo**\ntu **facevi**\nlui/lei **faceva**\nnoi **facevamo**\nvoi **facevate**\nloro **facevano**\n\n"
            "\U0001F7E0 **Dire** (zeggen) → stam: dice-\n"
            "io **dicevo**\ntu **dicevi**\nlui/lei **diceva**\nnoi **dicevamo**\nvoi **dicevate**\nloro **dicevano**\n\n"
            "\U0001F7E0 **Bere** (drinken) → stam: beve-\n"
            "io **bevevo**\ntu **bevevi**\nlui/lei **beveva**\nnoi **bevevamo**\nvoi **bevevate**\nloro **bevevano**\n\n"
            "\U0001F4CE Voor de regels van regelmatige werkwoorden, gebruik `!imperfetto-regole`"
        )

    @commands.command(name="imperfetto-vs-passato")
    async def imperfetto_vs_passato(self, ctx):
        await ctx.send(
            "\U0001F9E0 **Wanneer gebruik je imperfetto en wanneer passato prossimo?**\n\n"
            "In het Italiaans gebruik je twee verschillende tijden voor het verleden:\n"
            "\u2013 de **imperfetto** voor situaties, gewoontes of iets dat bezig was\n"
            "\u2013 de **passato prossimo** voor afgeronde, eenmalige acties\n\n"
            "———————————————\n"
            "\U0001F4D8 **IMPERFETTO**\n"
            "———————————————\n"
            "\U0001F539 Gewoontes in het verleden\n"
            "\U0001F539 Situaties / achtergronden\n"
            "\U0001F539 Weer, sfeer, gevoelens\n"
            "\U0001F539 Acties die aan de gang waren\n"
            "\U0001F539 Beschrijvingen zonder duidelijk einde\n\n"
            "\U0001F5BE Voorbeelden:\n"
            "\u2013 Da bambino andavo al parco.\n"
            "\u2013 Faceva freddo e pioveva.\n"
            "\u2013 Mentre studiavo, ascoltavo musica.\n\n"
            "———————————————\n"
            "\U0001F4D7 **PASSATO PROSSIMO**\n"
            "———————————————\n"
            "\U0001F538 Eenmalige of specifieke acties\n"
            "\U0001F538 Afgeronde gebeurtenissen\n"
            "\U0001F538 Acties met begin en einde\n"
            "\U0001F538 Wat gebeurde tijdens een andere actie\n\n"
            "\U0001F5BE Voorbeelden:\n"
            "\u2013 Ieri ho visto Giulia.\n"
            "\u2013 Abbiamo mangiato alle 7.\n"
            "\u2013 Mentre studiavo, \u00e8 suonato il telefono.\n\n"
            "---\n\n"
            "\U0001F4CC **Belangrijke regels om het verschil te begrijpen:**\n\n"
            "\U0001F538 **“Mentre” → gebruik altijd de imperfetto**\n"
            "Gebruik je “mentre” (terwijl), dan beschrijf je meestal een lopende actie of achtergrond.\n"
            "→ *Mentre parlavo, tu scrivevi un messaggio.*\n\n"
            "\U0001F538 **Wanneer een korte actie een langere onderbreekt:**\n"
            "Gebruik dan **imperfetto voor de lange actie** en **passato prossimo voor de korte onderbrekende actie**.\n\n"
            "\U0001F449 *Mentre guardavo un film, \u00e8 suonato il telefono.*\n"
            "(= Terwijl ik een film keek, ging de telefoon plots.)\n\n"
            "\U0001F4CE Voor vervoegingsregels zie `!imperfetto-regole` en `!passato-regole`"
        )

    @commands.command(name="imperfetto-esempi")
    async def imperfetto_esempi(self, ctx):
        await ctx.send(
            "\U0001F5E3\uFE0F **Voorbeeldzinnen – Imperfetto**\n"
            "Hieronder vind je realistische zinnen waarin de **imperfetto** wordt gebruikt.\n"
            "Let op de situaties: beschrijving, gewoontes, gevoelens of iets dat bezig was.\n\n"
            "\U0001F538 Da piccolo **andavo** sempre al mare con i miei genitori.\n"
            "(Vroeger ging ik altijd naar zee met mijn ouders.)\n\n"
            "\U0001F538 **Faceva** caldo e il sole **splendeva**.\n"
            "(Het was warm en de zon scheen.)\n\n"
            "\U0001F538 **Stavo** male e **avevo** mal di testa tutto il giorno.\n"
            "(Ik voelde me slecht en had de hele dag hoofdpijn.)\n\n"
            "\U0001F538 Mentre **guardavo** un film, **mi \u00E8 arrivato** un messaggio.\n"
            "(Terwijl ik een film aan het kijken was, kreeg ik een bericht.)\n\n"
            "\U0001F538 A scuola **parlavamo** spesso italiano tra di noi.\n"
            "(Op school spraken we vaak Italiaans onder elkaar.)\n\n"
            "\U0001F4CE Voor de regels zie `!imperfetto-regole`\n"
            "\U0001F4CE Voor onregelmatige werkwoorden zie `!imperfetto-irregolari`"
        )

    @commands.command(name="imperfetto-esercizio")
    async def imperfetto_esercizio(self, ctx):
        await ctx.send(
            "\u270D\uFE0F **Oefening – Imperfetto**\n"
            "Vul de juiste vorm van het werkwoord in de **imperfetto** in.\n"
            "Let op of het een regelmatig of onregelmatig werkwoord is!\n\n"
            "**\U0001F539 Deel 1: Basis**\n\n"
            "1. Quando ero piccolo, ogni estate noi __________ al mare. *(andare)*\n"
            "2. Ieri Maria non __________ bene. *(stare)*\n"
            "3. Che cosa __________ mentre io parlavo? *(fare)*\n"
            "4. A scuola __________ sempre italiano con il professore. *(parlare)*\n"
            "5. Mentre tu __________ la cena, io apparecchiavo la tavola. *(preparare)*\n"
            "6. Il sole __________ e gli uccelli cantavano. *(splendere)*\n"
            "7. Da bambini, __________ sempre presto. *(dormire)*\n"
            "8. Ogni domenica, mio nonno __________ il giornale al parco. *(leggere)*\n"
            "9. Quando ci siamo visti, tu __________ una giacca rossa. *(indossare)*\n"
            "10. I miei genitori __________ molto vino rosso. *(bere)*\n\n"
            "**\U0001F539 Deel 2: Extra oefeningen**\n\n"
            "11. In quel periodo, noi __________ in una casa più piccola. *(vivere)*\n"
            "12. Mentre loro __________, è suonato il telefono. *(mangiare)*\n"
            "13. La maestra ci __________ una storia bellissima. *(raccontare)*\n"
            "14. Mia sorella __________ ore al telefono con le amiche. *(parlare)*\n"
            "15. Non ti __________ mai in quel modo! *(rispondere)*\n"
            "16. I bambini __________ nel giardino quando ha iniziato a piovere. *(giocare)*\n"
            "17. Ogni mattina, lui __________ lo stesso cappotto. *(mettere)*\n"
            "18. Voi __________ di continuo, ma nessuno vi ascoltava. *(gridare)*\n"
            "19. Da giovane, mio padre __________ molto sport. *(fare)*\n"
            "20. Perché non __________ niente? *(dire)*\n\n"
            "\U0001F4A1 Typ het commando `!imperfetto-soluzioni` voor de oplossingen \U0001F4D6\n"
            "\U0001F4CE Zie `!imperfetto-regole` of `!imperfetto-irregolari` voor hulp."
        )

# --- Oplossingen imperfetto: stuur via DM ---
    @commands.command(name="imperfetto-soluzioni")
    async def imperfetto_soluzioni(self, ctx):
        oplossingen = (
            "**\U0001F4DD Soluzioni – Imperfetto**\n\n"
            "**\U0001F539 Deel 1: Basis**\n"
            "1. Quando ero piccolo, ogni estate noi **andavamo** al mare.\n"
            "2. Ieri Maria non **stava** bene.\n"
            "3. Che cosa **facevi** mentre io parlavo?\n"
            "4. A scuola **parlavamo** sempre italiano con il professore.\n"
            "5. Mentre tu **preparavi** la cena, io apparecchiavo la tavola.\n"
            "6. Il sole **splendeva** e gli uccelli cantavano.\n"
            "7. Da bambini, **dormivamo** sempre presto.\n"
            "8. Ogni domenica, mio nonno **leggeva** il giornale al parco.\n"
            "9. Quando ci siamo visti, tu **indossavi** una giacca rossa.\n"
            "10. I miei genitori **bevevano** molto vino rosso.\n\n"
            "**\U0001F539 Deel 2: Extra oefeningen**\n"
            "11. In quel periodo, noi **vivevamo** in una casa più piccola.\n"
            "12. Mentre loro **mangiavano**, è suonato il telefono.\n"
            "13. La maestra ci **raccontava** una storia bellissima.\n"
            "14. Mia sorella **parlava** ore al telefono con le amiche.\n"
            "15. Non ti **rispondevo** mai in quel modo!\n"
            "16. I bambini **giocavano** nel giardino quando ha iniziato a piovere.\n"
            "17. Ogni mattina, lui **metteva** lo stesso cappotto.\n"
            "18. Voi **gridavate** di continuo, ma nessuno vi ascoltava.\n"
            "19. Da giovane, mio padre **faceva** molto sport.\n"
            "20. Perché non **dicevi** niente?"
        )

        try:
            await ctx.author.send(oplossingen)
            await ctx.send("\U0001F4EC Le soluzioni ti sono state inviate in DM. Controlla la tua inbox!")
        except discord.Forbidden:
            await ctx.send("\u26A0\uFE0F Ik kan je geen privébericht sturen. Controleer je privacy-instellingen in Discord en probeer het opnieuw.")

    # ================================
    # PASSATO PROSSIMO
    # ================================
    @commands.command(name="passato-regole")
    async def passato_regole(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Passato Prossimo – Gebruik & vorming (regelmatige werkwoorden)**\n\n"
            "De passato prossimo gebruik je voor **afgeronde handelingen in het verleden**.\n"
            "Hier zijn de belangrijkste situaties:\n\n"
            "\U0001F539 1. **Recente handeling**\n"
            "– *Ho appena finito di studiare.* (Ik ben net klaar met studeren.)\n\n"
            "\U0001F539 2. **Lang geleden, maar nog relevant**\n"
            "– *Ho conosciuto Giulia nel 2010.* (En we zijn nog steeds bevriend.)\n\n"
            "\U0001F539 3. **Deze week / nog bezig**\n"
            "– *Questa settimana abbiamo lavorato molto.*\n\n"
            "\U0001F539 4. **Afgesloten moment in het verleden**\n"
            "– *Ieri sera abbiamo mangiato al ristorante.*\n\n"
            "\U0001FA9A **Opbouw van de passato prossimo**\n"
            "→ Hulpwerkwoord (**avere** of **essere**) + voltooid deelwoord\n\n"
            "\U0001F539 Werkwoorden op -ARE → `-ato`\n"
            "– parlare → parlato → *Ho parlato*\n\n"
            "\U0001F539 Werkwoorden op -ERE → `-uto`\n"
            "– credere → creduto → *Hai creduto*\n\n"
            "\U0001F539 Werkwoorden op -IRE → `-ito`\n"
            "– dormire → dormito → *Abbiamo dormito*\n\n"
            "\U0001F4CE Zie ook:\n"
            "– `!passato-verbi-regolari`\n"
            "– `!passato-irregolari`\n"
            "– `!passato-essere`\n"
            "– `!passato-esercizio`"
        )

    @commands.command(name="passato-verbi-regolari")
    async def passato_verbi_regolari(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Passato Prossimo – Regelmatige & vaak gebruikte werkwoorden**\n\n"
            "\U0001F539 **WERKWOORDEN OP -ARE** (→ -ATO)\n"
            "→ hulpwerkwoord: meestal **avere**, tenzij beweging → **essere**\n\n"
            "– Ho parlato (parlare)\n"
            "– Ho telefonato (telefonare)\n"
            "– Ho pranzato (pranzare)\n"
            "– Ho trovato (trovare)\n"
            "– Ho lavato (lavare)\n"
            "– Ho visitato (visitare)\n"
            "– Ho camminato (camminare)\n"
            "– Ho litigato (litigare)\n"
            "– Ho passato una bella serata\n"
            "– Sono arrivato/a (arrivare)\n"
            "– Sono andato/a (andare)\n"
            "– Sono entrato/a (entrare)\n"
            "– Sono tornato/a (tornare)\n"
            "– Sono ritornato/a (ritornare)\n"
            "– Sono scappato/a (scappare)\n"
            "– Sono salito/a (salire)\n"
            "– Sono partito/a (partire)\n"
            "– Sono uscito/a (uscire)\n\n"
            "\U0001F539 **WERKWOORDEN OP -ERE** (→ -UTO)\n"
            "– Ho creduto (credere)\n"
            "– Ho vissuto un’esperienza forte\n"
            "– Sono vissuto/a in Italia\n"
            "– Sono cresciuto/a in Belgio\n\n"
            "\U0001F539 **WERKWOORDEN OP -IRE** (→ -ITO)\n"
            "– Ho dormito (dormire)\n"
            "– Ho capito (capire)\n"
            "– Ho seguito il corso (seguire)\n"
            "– Ho sentito (sentire)\n\n"
            "\U0001F4CC **Let op bij ESSERE**\n"
            "→ voltooid deelwoord aanpassen in geslacht & getal"
        )

    @commands.command(name="passato-irregolari")
    async def passato_irregolari(self, ctx):
        await ctx.send(
            "\U0001F4D8 **Passato Prossimo – Onregelmatige werkwoorden**\n\n"
            "\U0001F539 **Voorbeelden van onregelmatige vormen:**\n\n"
            "– fare → **fatto**\n"
            "– dire → **detto**\n"
            "– leggere → **letto**\n"
            "– scrivere → **scritto**\n"
            "– vedere → **visto**\n"
            "– prendere → **preso**\n"
            "– mettere → **messo**\n"
            "– chiedere → **chiesto**\n"
            "– rispondere → **risposto**\n"
            "– aprire → **aperto**\n"
            "– offrire → **offerto**\n"
            "– venire → **venuto**\n"
            "– nascere → **nato**\n"
            "– morire → **morto**\n"
            "– scegliere → **scelto**\n\n"
            "\U0001F4CC Let op: sommige gebruiken **essere** en moeten worden aangepast in geslacht/getal\n"
            "– *Maria è nata.* / *Loro sono venuti.*\n\n"
            "\U0001F4CD Zie ook:\n"
            "– `!passato-regole`\n"
            "– `!passato-verbi-regolari`\n"
            "– `!passato-esercizio`"
        )

    @commands.command(name="passato-hulpwerkwoorden")
    async def passato_hulpwerkwoorden(self, ctx):
        await ctx.send(
            "\U0001F465 **Welk hulpwerkwoord gebruik je: AVERE of ESSERE?**\n\n"
            "\u2705 **AVERE** → Meestal bij werkwoorden met een lijdend voorwerp\n"
            "\u2705 **ESSERE** → Beweging, verandering, reflexieve en onpersoonlijke werkwoorden\n\n"
            "\U0001F501 **Verbi riflessivi (altijd met essere)**\n"
            "\u2696\ufe0f **Dubbele vormen (avere/essere) afhankelijk van context**\n\n"
            "\U0001F3AF **Let op bij pronomi diretti vóór avere:**\n"
            "– *L’ho mangiata.* (pizza → vrouwelijk enkelvoud)\n"
            "– *Li ho letti.* (libri → mannelijk meervoud)"
        )

    @commands.command(name="passato-esercizio")
    async def passato_esercizio(self, ctx):
        await ctx.send(
            "\U0001F4DD **Oefenzinnen – Passato Prossimo**\n\n"
            "Vul het juiste vervoegde werkwoord in:\n"
            "```plaintext\n"
            "1. Ieri ________ (mangiare) una pizza.\n"
            "2. Giulia ________ (andare) al cinema con Marco.\n"
            "3. Noi ________ (finire) il progetto.\n"
            "4. Tu ________ (aprire) la finestra?\n"
            "5. Loro ________ (uscire) molto tardi.\n"
            "6. Io ________ (leggere) un libro interessante.\n"
            "7. Voi ________ (visitare) il museo?\n"
            "8. Il treno ________ (arrivare) alle otto.\n"
            "9. Mio padre ________ (scrivere) una lettera lunga.\n"
            "10. Noi non ________ (capire) la spiegazione.\n"
            "11. La lezione ________ (cominciare) alle 9.\n"
            "12. ________ (fare) colazione stamattina?\n"
            "13. I ragazzi ________ (giocare) a calcio tutto il giorno.\n"
            "14. Mia sorella ________ (mettere) la giacca rossa.\n"
            "15. Le bambine ________ (nascere) nel 2015.\n"
            "16. Marco e Paolo ________ (entrare) nella stanza.\n"
            "17. Io ________ (perdere) le chiavi.\n"
            "18. L’insegnante ________ (spiegare) bene la grammatica.\n"
            "19. Voi ________ (vedere) quel film nuovo?\n"
            "20. Il bambino ________ (piangere) tutta la notte.\n"
            "21. Tu ________ (dire) la verità?\n"
            "22. Noi ________ (lavare) la macchina ieri.\n"
            "23. Lucia ________ (scegliere) un dolce.\n"
            "24. Io e Mario ________ (partire) alle 6.\n"
            "25. Voi ________ (chiedere) het conto?\n"
            "26. La pizza? Io ________ (mangiare) tutta!\n"
            "27. I libri? Tu non ________ (leggere).\n"
            "28. Le ragazze? Voi ________ (vedere)?\n"
            "29. Il film? Noi non ________ (vedere) ancora.\n"
            "30. La tua lettera? Lui ________ (scrivere) ieri.\n"
            "```\n\n"
            "\U0001F4DC Typ `!passato-esercizio-soluzioni` voor de antwoorden."
        )

    @commands.command(name="passato-esercizio-soluzioni")
    async def passato_esercizio_soluzioni(self, ctx):
        try:
            await ctx.author.send(
                "\u2705 **Oplossingen – Passato Prossimo**\n\n"
                "1. Ieri **ho mangiato** una pizza.\n"
                "2. Giulia **è andata** al cinema con Marco.\n"
                "3. Noi **abbiamo finito** il progetto.\n"
                "4. Tu **hai aperto** la finestra?\n"
                "5. Loro **sono usciti** molto tardi.\n"
                "6. Io **ho letto** un libro interessante.\n"
                "7. Voi **avete visitato** il museo?\n"
                "8. Il treno **è arrivato** alle otto.\n"
                "9. Mio padre **ha scritto** una lettera lunga.\n"
                "10. Noi non **abbiamo capito** la spiegazione.\n"
                "11. La lezione **è cominciata** alle 9.\n"
                "12. **Hai fatto** colazione stamattina?\n"
                "13. I ragazzi **hanno giocato** a calcio tutto de dag.\n"
                "14. Mia sorella **ha messo** la giacca rossa.\n"
                "15. Le bambine **sono nate** nel 2015.\n"
                "16. Marco e Paolo **sono entrati** nella stanza.\n"
                "17. Io **ho perso** le chiavi.\n"
                "18. L’insegnante **ha spiegato** bene la grammatica.\n"
                "19. Voi **avete visto** quel film nuovo?\n"
                "20. Il bambino **ha pianto** tutta la notte.\n"
                "21. Tu **hai detto** la verità?\n"
                "22. Noi **abbiamo lavato** la macchina ieri.\n"
                "23. Lucia **ha scelto** un dolce.\n"
                "24. Io e Mario **siamo partiti** alle 6.\n"
                "25. Voi **avete chiesto** het conto?\n\n"
                "\U0001F501 **Extra – met pronomi diretti**\n"
                "26. La pizza? Io **l’ho mangiata** tutta!\n"
                "27. I libri? Tu non **li hai letti**.\n"
                "28. Le ragazze? Voi **le avete viste**?\n"
                "29. Il film? Noi non **l’abbiamo visto** ancora.\n"
                "30. La tua lettera? Lui **l’ha scritta** ieri."
            )
            await ctx.send("\U0001F4E9 Le soluzioni sono state inviate nella tua inbox (DM)!")
        except discord.Forbidden:
            await ctx.send("\u26A0\uFE0F Non riesco a inviarti un DM. Controlla le impostazioni della privacy e riprova.")

# --- ENCODING FIX ---

# --- ACTIVEREN VAN DE COG ---
async def setup(bot):
    await bot.add_cog(Grammatica(bot))