import discord
from discord.ext import commands

class Grammatica(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ================================
    # TOEKOMST - REGELS EN UITZONDERINGEN
    # ================================

    @commands.command(name="futuro-regole")
    async def futuro_regole(self, ctx):
        await ctx.send(
            "📘 **Regole del futuro semplice (verbi regolari):**\n\n"
            "🔹 **-ARE → -ERÒ**\n"
            "✳️ Attenzione: la **\"a\" cambia in \"e\"** nella radice!\n"
            "Esempio: *parlare → parlerò* (non **parlarò**)\n"
            "Esempio: *mangiare → mangerò*\n\n"
            "🔹 **-ERE → -ERÒ**\n"
            "Esempio: *credere → crederò*\n\n"
            "🔹 **-IRE → -IRÒ**\n"
            "Esempio: *partire → partirò*\n\n"
            "📌 Tutte le persone usano le stesse desinenze:\n"
            "- io: **-ò**, tu: **-ai**, lui/lei: **-à**, noi: **-emo**, voi: **-ete**, loro: **-anno**\n\n"
            "💡 *Esempio completo:* **parlare →** parlerò, parlerai, parlerà, parleremo, parlerete, parleranno\n\n"
            "✅ Per i verbi irregolari, vedi `!futuro-irregolari`"
        )

    @commands.command(name="futuro-irregolari")
    async def futuro_irregolari(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – verbi irregolari 🇮🇹**\n\n"
            "🔹 **essere → sar-**, **avere → avr-**, **andare → andr-**\n"
            "🔹 **dovere → dovr-**, **potere → potr-**, **sapere → sapr-**\n"
            "🔹 **vedere → vedr-**, **vivere → vivr-**, **volere → vorr-**\n\n"
            "👉 La **radice cambia**, ma le **desinenze restano**:\n"
            "**-ò, -ai, -à, -emo, -ete, -anno**\n\n"
            "📌 *Esempio:* **essere →** sarò, sarai, sarà, saremo, sarete, saranno"
        )

    # ================================
    # TOEKOMST - ONREGELMATIGE WERKWOORDEN
    # ================================

    @commands.command(name="futuro-andare")
    async def futuro_andare(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – ANDARE 🇮🇹**\n\n"
            "**Radice:** andr-\n"
            "io andrò, tu andrai, lui/lei andrà, noi andremo, voi andrete, loro andranno\n\n"
            "💡 Voorbeeld: *Sabato andremo al cinema.*"
        )

    @commands.command(name="futuro-avere")
    async def futuro_avere(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – AVERE 🇮🇹**\n\n"
            "**Radice:** avr-\n"
            "io avrò, tu avrai, lui/lei avrà, noi avremo, voi avrete, loro avranno\n\n"
            "💡 Voorbeeld: *Avrò tempo domani pomeriggio.*"
        )

    @commands.command(name="futuro-essere")
    async def futuro_essere(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – ESSERE 🇮🇹**\n\n"
            "**Radice:** sar-\n"
            "io sarò, tu sarai, lui/lei sarà, noi saremo, voi sarete, loro saranno\n\n"
            "💡 Voorbeeld: *Domani sarò molto felice.*"
        )

    # ================================
    # TOEKOMST - SPELLINGAANPASSINGEN
    # ================================

    @commands.command(name="futuro-baciare")
    async def futuro_baciare(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – BACIARE 🇮🇹**\n\n"
            "**Stam:** baciar- → *bacerò* (zonder “i”)\n"
            "io bacerò, tu bacerai, lui/lei bacerà, noi baceremo, voi bacerete, loro baceranno\n\n"
            "💡 Voorbeeld: *Ti bacerò sotto le stelle.*"
        )

    @commands.command(name="futuro-mangiare")
    async def futuro_mangiare(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – MANGIARE 🇮🇹**\n\n"
            "**Stam:** mangiar- → *mangerò* (zonder “i”)\n"
            "io mangerò, tu mangerai, lui/lei mangerà, noi mangeremo, voi mangerete, loro mangeranno\n\n"
            "💡 Voorbeeld: *Domani mangerò una pizza napoletana.*"
        )

    @commands.command(name="futuro-pagare")
    async def futuro_pagare(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – PAGARE 🇮🇹**\n\n"
            "**Stam:** pagar- + h → *pagherò*\n"
            "io pagherò, tu pagherai, lui/lei pagherà, noi pagheremo, voi pagherete, loro pagheranno\n\n"
            "💡 Voorbeeld: *Pagherò il conto dopo cena.*"
        )

    @commands.command(name="futuro-giocare")
    async def futuro_giocare(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – GIOCARE 🇮🇹**\n\n"
            "**Stam:** giocar- + h → *giocherò*\n"
            "io giocherò, tu giocherai, lui/lei giocherà, noi giocheremo, voi giocherete, loro giocheranno\n\n"
            "💡 Voorbeeld: *Giocheremo a carte tutta la sera.*"
        )

    @commands.command(name="futuro-guardare")
    async def futuro_guardare(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – GUARDARE 🇮🇹**\n\n"
            "**Stam:** guardar- → *guarderò*\n"
            "io guarderò, tu guarderai, lui/lei guarderà, noi guarderemo, voi guarderete, loro guarderanno\n\n"
            "💡 Voorbeeld: *Guarderemo la partita insieme.*"
        )

    @commands.command(name="futuro-scrivere")
    async def futuro_scrivere(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – SCRIVERE 🇮🇹**\n\n"
            "**Stam:** scriver-\n"
            "io scriverò, tu scriverai, lui/lei scriverà, noi scriveremo, voi scriverete, loro scriveranno\n\n"
            "💡 Voorbeeld: *Scriverò un libro tutto in italiano!*"
        )

    @commands.command(name="futuro-partire")
    async def futuro_partire(self, ctx):
        await ctx.send(
            "📘 **Futuro semplice – PARTIRE 🇮🇹**\n\n"
            "**Stam:** partir-\n"
            "io partirò, tu partirai, lui/lei partirà, noi partiremo, voi partirete, loro partiranno\n\n"
            "💡 Voorbeeld: *Partirò per Roma con il treno delle 8.*"
        )

    # ================================
    # IMPERFETTO – REGELS EN VOORBEELDEN
    # ================================

    @commands.command(name="imperfetto-regole")
    async def imperfetto_regole(self, ctx):
        await ctx.send(
            "📘 **Regelmatige werkwoorden – Imperfetto**\n\n"
            "🔹 **Wanneer gebruik je de imperfetto?**\n"
            "De imperfetto gebruik je om iets te beschrijven dat in het verleden:\n"
            "– herhaald of gewoonlijk gebeurde (vb. elke week, vroeger)\n"
            "– aan de gang was toen iets anders gebeurde\n"
            "– een achtergrond of situatie beschrijft (weer, omgeving, gevoel)\n"
            "– niet afgerond of niet tijdsgebonden is\n\n"
            "Voorbeelden:\n"
            "– Da piccolo andavo sempre al mare.\n"
            "– Mentre cucinavo, ascoltavo la musica.\n"
            "– Faceva caldo e il sole splendeva.\n"
            "– Non stavo bene ieri.\n\n"
            "🔹 **Hoe vervoeg je regelmatige werkwoorden in de imperfetto?**\n"
            "👉 Neem de **infinitief** (zoals *parlare*, *credere*, *dormire*)\n"
            "❌ Laat **-re** vallen\n"
            "✅ Voeg de uitgangen toe:\n\n"
            "**ARE** → parlare → parla-\n"
            "**ERE** → credere → crede-\n"
            "**IRE** → dormire → dormi-\n\n"
            "🧩 **Uitgangen voor alle regelmatige werkwoorden:**\n"
            "- io → **-vo**\n"
            "- tu → **-vi**\n"
            "- lui/lei → **-va**\n"
            "- noi → **-vamo**\n"
            "- voi → **-vate**\n"
            "- loro → **-vano**\n\n"
            "📝 Voorbeeld: *parlare*\n"
            "– io parlavo\n"
            "– tu parlavi\n"
            "– lui/lei parlava\n"
            "– noi parlavamo\n"
            "– voi parlavate\n"
            "– loro parlavano\n\n"
            "📎 Bekijk ook `!imperfetto-irregolari` voor de uitzonderingen."
      )

    @commands.command(name="imperfetto-irregolari")
    async def imperfetto_irregolari(self, ctx):
        await ctx.send(
            "📘 **Onregelmatige werkwoorden – Imperfetto**\n\n"
            "De meeste werkwoorden in de imperfetto zijn regelmatig, \n"
            "maar een paar **veelgebruikte** werkwoorden zijn onregelmatig:\n\n"
            "🟠 **Essere** (zijn)\n"
            "io **ero**\ntu **eri**\nlui/lei **era**\nnoi **eravamo**\nvoi **eravate**\nloro **erano**\n\n"
            "🟠 **Fare** (doen/maken) → stam: face-\n"
            "io **facevo**\ntu **facevi**\nlui/lei **faceva**\nnoi **facevamo**\nvoi **facevate**\nloro **facevano**\n\n"
            "🟠 **Dire** (zeggen) → stam: dice-\n"
            "io **dicevo**\ntu **dicevi**\nlui/lei **diceva**\nnoi **dicevamo**\nvoi **dicevate**\nloro **dicevano**\n\n"
            "🟠 **Bere** (drinken) → stam: beve-\n"
            "io **bevevo**\ntu **bevevi**\nlui/lei **beveva**\nnoi **bevevamo**\nvoi **bevevate**\nloro **bevevano**\n\n"
            "📎 Voor de regels van regelmatige werkwoorden, gebruik `!imperfetto-regole`"
        )

    @commands.command(name="imperfetto-vs-passato")
    async def imperfetto_vs_passato(self, ctx):
        await ctx.send(
            "🧠 **Wanneer gebruik je imperfetto en wanneer passato prossimo?**\n\n"
            "In het Italiaans gebruik je twee verschillende tijden voor het verleden:\n"
            "– de **imperfetto** voor situaties, gewoontes of iets dat bezig was\n"
            "– de **passato prossimo** voor afgeronde, eenmalige acties\n\n"
            "———————————————\n"
            "📘 **IMPERFETTO**\n"
            "———————————————\n"
            "🔹 Gewoontes in het verleden\n"
            "🔹 Situaties / achtergronden\n"
            "🔹 Weer, sfeer, gevoelens\n"
            "🔹 Acties die aan de gang waren\n"
            "🔹 Beschrijvingen zonder duidelijk einde\n\n"
            "🧾 Voorbeelden:\n"
            "– Da bambino andavo al parco.\n"
            "– Faceva freddo e pioveva.\n"
            "– Mentre studiavo, ascoltavo musica.\n\n"
            "———————————————\n"
            "📗 **PASSATO PROSSIMO**\n"
            "———————————————\n"
            "🔸 Eenmalige of specifieke acties\n"
            "🔸 Afgeronde gebeurtenissen\n"
            "🔸 Acties met begin en einde\n"
            "🔸 Wat gebeurde tijdens een andere actie\n\n"
            "🧾 Voorbeelden:\n"
            "– Ieri ho visto Giulia.\n"
            "– Abbiamo mangiato alle 7.\n"
            "– Mentre studiavo, è suonato il telefono.\n\n"
            "---\n\n"
            "📌 **Belangrijke regels om het verschil te begrijpen:**\n\n"
            "🔸 **“Mentre” → gebruik altijd de imperfetto**\n"
            "Gebruik je “mentre” (terwijl), dan beschrijf je meestal een lopende actie of achtergrond.\n"
            "→ *Mentre parlavo, tu scrivevi un messaggio.*\n\n"
            "🔸 **Wanneer een korte actie een langere onderbreekt:**\n"
            "Gebruik dan **imperfetto voor de lange actie** en **passato prossimo voor de korte onderbrekende actie**.\n\n"
            "👉 *Mentre guardavo un film, è suonato il telefono.*\n"
            "(= Terwijl ik een film keek, ging de telefoon plots.)\n\n"
            "📎 Voor vervoegingsregels zie `!imperfetto-regole` en `!passato-regole`"
   )

    @commands.command(name="imperfetto-esempi")
    async def imperfetto_esempi(self, ctx):
        await ctx.send(
               "🗣️ **Voorbeeldzinnen – Imperfetto**\n"
                "Hieronder vind je realistische zinnen waarin de **imperfetto** wordt gebruikt.\n"
                "Let op de situaties: beschrijving, gewoontes, gevoelens of iets dat bezig was.\n\n"
                "🔸 Da piccolo **andavo** sempre al mare con i miei genitori.\n"
                "(Vroeger ging ik altijd naar zee met mijn ouders.)\n\n"
                "🔸 **Faceva** caldo e il sole **splendeva**.\n"
                "(Het was warm en de zon scheen.)\n\n"
                "🔸 **Stavo** male e **avevo** mal di testa tutto il giorno.\n"
                "(Ik voelde me slecht en had de hele dag hoofdpijn.)\n\n"
                "🔸 Mentre **guardavo** un film, **mi è arrivato** un messaggio.\n"
                "(Terwijl ik een film aan het kijken was, kreeg ik een bericht.)\n\n"
                "🔸 A scuola **parlavamo** spesso italiano tra di noi.\n"
                "(Op school spraken we vaak Italiaans onder elkaar.)\n\n"
                "📎 Voor de regels zie `!imperfetto-regole`\n"
                "📎 Voor onregelmatige werkwoorden zie `!imperfetto-irregolari`"
        )

    @commands.command(name="imperfetto-esercizio")
    async def imperfetto_esercizio(self, ctx):
        await ctx.send(
            "✍️ **Oefening – Imperfetto**\n"
            "Vul de juiste vorm van het werkwoord in de **imperfetto** in.\n"
            "Let op of het een regelmatig of onregelmatig werkwoord is!\n\n"
            "**🔹 Deel 1: Basis**\n\n"
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
            "**🔹 Deel 2: Extra oefeningen**\n\n"
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
            "💡 Typ het commando `!imperfetto-soluzioni` voor de oplossingen 📖\n"
            "📎 Zie `!imperfetto-regole` of `!imperfetto-irregolari` voor hulp."
        )

# --- Oplossingen imperfetto: stuur via DM ---
    @commands.command(name="imperfetto-soluzioni")
    async def imperfetto_soluzioni(self, ctx):
        oplossingen = (
            "**📝 Soluzioni – Imperfetto**\n\n"
            "**🔹 Deel 1: Basis**\n"
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
            "**🔹 Deel 2: Extra oefeningen**\n"
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
            await ctx.send("📬 Le soluzioni ti sono state inviate in DM. Controlla la tua inbox!")
        except discord.Forbidden:
            await ctx.send("⚠️ Ik kan je geen privébericht sturen. Controleer je privacy-instellingen in Discord en probeer het opnieuw.")

    # ================================
    # PASSATO PROSSIMO
    # ================================

@bot.command(name='passato-regole')
async def passato_regole(ctx):
    await ctx.send("""📘 **Passato Prossimo – Gebruik & vorming (regelmatige werkwoorden)**

De passato prossimo gebruik je voor **afgeronde handelingen in het verleden**. 
Hier zijn de belangrijkste situaties:

🔹 1. **Recente handeling** 
– *Ho appena finito di studiare.* (Ik ben net klaar met studeren.)

🔹 2. **Lang geleden, maar nog relevant** 
– *Ho conosciuto Giulia nel 2010.* (En we zijn nog steeds bevriend.)

🔹 3. **Deze week / nog bezig** 
– *Questa settimana abbiamo lavorato molto.*

🔹 4. **Afgesloten moment in het verleden** 
– *Ieri sera abbiamo mangiato al ristorante.*

🛠️ **Opbouw van de passato prossimo** 
→ Hulpwerkwoord (**avere** of **essere**) + voltooid deelwoord

🔹 Werkwoorden op -ARE → `-ato` 
– parlare → parlato → *Ho parlato*

🔹 Werkwoorden op -ERE → `-uto` 
– credere → creduto → *Hai creduto*

🔹 Werkwoorden op -IRE → `-ito` 
– dormire → dormito → *Abbiamo dormito*

📎 Zie ook:
– `!passato-verbi-regolari`
– `!passato-irregolari`
– `!passato-essere`
– `!passato-esercizio`
""")


@bot.command(name='passato-verbi-regolari')
async def passato_verbi_regolari(ctx):
    await ctx.send("""📘 **Passato Prossimo – Regelmatige & vaak gebruikte werkwoorden**

🔹 **WERKWOORDEN OP -ARE** (→ -ATO) 
→ hulpwerkwoord: meestal **avere**, tenzij beweging → **essere**

– Ho parlato (parlare)
– Ho telefonato (telefonare)
– Ho pranzato (pranzare)
– Ho trovato (trovare)
– Ho lavato (lavare)
– Ho visitato (visitare)
– Ho camminato (camminare)
– Ho litigato (litigare)
– Ho passato una bella serata
– Sono arrivato/a (arrivare)
– Sono andato/a (andare)
– Sono entrato/a (entrare)
– Sono tornato/a (tornare)
– Sono ritornato/a (ritornare)
– Sono scappato/a (scappare)
– Sono salito/a (salire)
– Sono partito/a (partire)
– Sono uscito/a (uscire)

🔹 **WERKWOORDEN OP -ERE** (→ -UTO) 
– Ho creduto (credere)
– Ho vissuto un’esperienza forte
– Sono vissuto/a in Italia
– Sono cresciuto/a in Belgio

🔹 **WERKWOORDEN OP -IRE** (→ -ITO) 
– Ho dormito (dormire)
– Ho capito (capire)
– Ho seguito il corso (seguire)
– Ho sentito (sentire)

📌 **Let op bij ESSERE** 
→ voltooid deelwoord aanpassen in geslacht & getal
""")


@bot.command(name='passato-irregolari')
async def passato_irregolari(ctx):
    await ctx.send("""📘 **Passato Prossimo – Onregelmatige werkwoorden**

🔹 **Voorbeelden van onregelmatige vormen:**

– fare → **fatto**
– dire → **detto**
– leggere → **letto**
– scrivere → **scritto**
– vedere → **visto**
– prendere → **preso**
– mettere → **messo**
– chiedere → **chiesto**
– rispondere → **risposto**
– aprire → **aperto**
– offrire → **offerto**
– venire → **venuto**
– nascere → **nato**
– morire → **morto**
– scegliere → **scelto**

📌 Let op: sommige gebruiken **essere** en moeten worden aangepast in geslacht/getal
– *Maria è nata.* / *Loro sono venuti.*

📎 Zie ook:
– `!passato-regole`
– `!passato-verbi-regolari`
– `!passato-esercizio`
""")


@bot.command(name='passato-hulpwerkwoorden')
async def passato_hulpwerkwoorden(ctx):
    await ctx.send("""👥 **Welk hulpwerkwoord gebruik je: AVERE of ESSERE?**

✅ **AVERE** → Meestal bij werkwoorden met een lijdend voorwerp
✅ **ESSERE** → Beweging, verandering, reflexieve en onpersoonlijke werkwoorden

🔁 **Verbi riflessivi (altijd met essere)**
⚖️ **Dubbele vormen (avere/essere) afhankelijk van context**

🎯 **Let op bij pronomi diretti vóór avere:**
– *L’ho mangiata.* (pizza → vrouwelijk enkelvoud)
– *Li ho letti.* (libri → mannelijk meervoud)
""")


@bot.command(name='passato-esercizio')
async def passato_esercizio(ctx):
    await ctx.send("""📝 **Oefenzinnen – Passato Prossimo**

Vul het juiste vervoegde werkwoord in:
```plaintext
1. Ieri ________ (mangiare) una pizza.
2. Giulia ________ (andare) al cinema con Marco.
3. Noi ________ (finire) il progetto.
4. Tu ________ (aprire) la finestra?
5. Loro ________ (uscire) molto tardi.
6. Io ________ (leggere) un libro interessante.
7. Voi ________ (visitare) il museo?
8. Il treno ________ (arrivare) alle otto.
9. Mio padre ________ (scrivere) una lettera lunga.
10. Noi non ________ (capire) la spiegazione.
11. La lezione ________ (cominciare) alle 9.
12. ________ (fare) colazione stamattina?
13. I ragazzi ________ (giocare) a calcio tutto il giorno.
14. Mia sorella ________ (mettere) la giacca rossa.
15. Le bambine ________ (nascere) nel 2015.
16. Marco e Paolo ________ (entrare) nella stanza.
17. Io ________ (perdere) le chiavi.
18. L’insegnante ________ (spiegare) bene la grammatica.
19. Voi ________ (vedere) quel film nuovo?
20. Il bambino ________ (piangere) tutta la notte.
21. Tu ________ (dire) la verità?
22. Noi ________ (lavare) la macchina ieri.
23. Lucia ________ (scegliere) un dolce.
24. Io e Mario ________ (partire) alle 6.
25. Voi ________ (chiedere) het conto?
26. La pizza? Io ________ (mangiare) tutta!
27. I libri? Tu non ________ (leggere).
28. Le ragazze? Voi ________ (vedere)?
29. Il film? Noi non ________ (vedere) ancora.
30. La tua lettera? Lui ________ (scrivere) ieri.

📎 Typ !passato-esercizio-soluzioni voor de antwoorden.
“””)

@bot.command(name='passato-esercizio-soluzioni')
async def passato_esercizio_soluzioni(ctx):
    await ctx.author.send("""✅ **Oplossingen – Passato Prossimo**

1. Ieri **ho mangiato** una pizza.  
2. Giulia **è andata** al cinema con Marco.  
3. Noi **abbiamo finito** il progetto.  
4. Tu **hai aperto** la finestra?  
5. Loro **sono usciti** molto tardi.  
6. Io **ho letto** un libro interessante.  
7. Voi **avete visitato** il museo?  
8. Il treno **è arrivato** alle otto.  
9. Mio padre **ha scritto** una lettera lunga.  
10. Noi non **abbiamo capito** la spiegazione.  
11. La lezione **è cominciata** alle 9.  
12. **Hai fatto** colazione stamattina?  
13. I ragazzi **hanno giocato** a calcio tutto de dag.  
14. Mia sorella **ha messo** la giacca rossa.  
15. Le bambine **sono nate** nel 2015.  
16. Marco e Paolo **sono entrati** nella stanza.  
17. Io **ho perso** le chiavi.  
18. L’insegnante **ha spiegato** bene la grammatica.  
19. Voi **avete visto** quel film nuovo?  
20. Il bambino **ha pianto** tutta la notte.  
21. Tu **hai detto** la verità?  
22. Noi **abbiamo lavato** la macchina ieri.  
23. Lucia **ha scelto** un dolce.  
24. Io e Mario **siamo partiti** alle 6.  
25. Voi **avete chiesto** il conto?

🔁 **Extra – met pronomi diretti**  
26. La pizza? Io **l’ho mangiata** tutta!  
27. I libri? Tu non **li hai letti**.  
28. Le ragazze? Voi **le avete viste**?  
29. Il film? Noi non **l’abbiamo visto** ancora.  
30. La tua lettera? Lui **l’ha scritta** ieri.
""")
    await ctx.send("📩 Le soluzioni sono state inviate nella tua inbox (DM)!")

# --- ENCODING FIX ---

# --- ACTIVEREN VAN DE COG ---
async def setup(bot):
    await bot.add_cog(Grammatica(bot))
