import discord
from discord.ext import commands
import unicodedata
import re
import asyncio
import session_manager


def normalize(text):
    text = unicodedata.normalize("NFKD", text).lower().strip()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = re.sub(r'[\s’‘`"^\u0300\u0301]', "", text)
    return text


async def confirm_quiz_start(channel):
    await channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")


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
                await message.channel.send("\u274C Hai già una quiz attiva. Completa prima quella prima di iniziarne un'altra.")
                return

            if message.channel.id == 1394735397824758031:
                session_manager.start_session(user_id, "quiz")
                await confirm_quiz_start(message.channel)
                await self.start_pronomi_quiz(message.author)
            elif message.channel.id == 1388866025679880256:
                session_manager.start_session(user_id, "quiz")
                await confirm_quiz_start(message.channel)
                await self.start_di_da_quiz(message.author)
            elif message.channel.id == 1390080013533052949:
                session_manager.start_session(user_id, "quiz")
                await confirm_quiz_start(message.channel)
                await self.start_in_per_quiz(message.author)
            elif message.channel.id == 1390371003414216805:
                session_manager.start_session(user_id, "quiz")
                await confirm_quiz_start(message.channel)
                await self.start_qualche_quiz(message.author)
            elif message.channel.id == 1393269447094960209:
                session_manager.start_session(user_id, "quiz")
                await confirm_quiz_start(message.channel)
                await self.start_che_chi_quiz(message.author)
            elif message.channel.id == 1393280441221644328:
                session_manager.start_session(user_id, "quiz")
                await confirm_quiz_start(message.channel)
                await self.start_ci_di_ne_quiz(message.author)
            elif message.channel.id == 1393289069009830038:
                session_manager.start_session(user_id, "quiz")
                await confirm_quiz_start(message.channel)
                await self.start_comparativi_quiz(message.author)
            elif message.channel.id == 1388241920790237347:
                session_manager.start_session(user_id, "quiz")
                await confirm_quiz_start(message.channel)
                await self.start_ci_quiz(message.author)
            elif message.channel.id == 1396072250221920276:
                session_manager.start_session(user_id, "quiz")
                await confirm_quiz_start(message.channel)
                await self.start_bello_quiz(message.author)
                return

    async def start_pronomi_quiz(self, user):
        questions = [
            ("Hai telefonato a Maria? No, non ________ ho ancora telefonto", "le"),
            ("Puoi chiamare il medico e prendere un appuntamento per domani? Si certo, ________ chiamo tra un secondo.", "lo"),
            ("Devi portare i libri a tua zia? Si, ________ porto io.", "le"),
            ("Ho preso una pizza e ________ ho mangiata tutta", "l'ho"),
            ("Hai visto il film che ti ho consigliato? Si, ________ visto ieri, ma non mi è piacuto molto.", "l'ho"),
            ("Non riesco a trovare le chiavi! ________ sto cercando da due ore!", "le"),
            ("Hai ascoltato la nuova canzone di Taylor Swift? Si, ________ sto ascoltando da due ore!", "la"),
            ("Luca e Paolo ________ hanno invitato a casa loro. Andiamo?", "ci"),
            ("Ho provato a chiamare Marianna ma non ________ ha risposto.", "mi"),
            ("Stavi parlando con Roberto? Si, ________ stavo chiedendo un favore", "gli"),
            ("Ho comprato i pasticcini. ________ porto io alla festa.", "li"),
            ("Dove sono i tuoi amici? Non so, ________ sto aspettando da 5 minuti.", "li"),
            ("Il cane porta la palla al suo padrone. Il cane ________ porta la palla.", "gli"),
            ("I miei zii hanno regalato una vacanza ai miei cugini. I miei zii ________ hanno regalato una vacanza.", "gli"),
            ("Vai da Carlo, ________ serve una mano a portare i pacchi!", "gli")
        ]

        try:
            dm = await user.create_dm()
            await dm.send("\U0001F4DA **Quiz: Pronomi diretti e indiretti**\nScrivi il pronome corretto per ogni frase. Hai 60 secondi per ogni frase. In bocca al lupo!")
            score = 0
            for i, (question, correct) in enumerate(questions, 1):
                await dm.send(f"{i}. {question}")
                try:
                    reply = await self.bot.wait_for("message", timeout=60.0, check=lambda m: m.author == user and m.channel == dm)
                    if normalize(reply.content) == normalize(correct):
                        await dm.send("✅ Corretto!")
                        score += 1
                    else:
                        await dm.send(f"❌ Sbagliato! La risposta giusta era **{correct}**")
                except asyncio.TimeoutError:
                    await dm.send(f"⏰ Tempo scaduto! La risposta giusta era **{correct}**")
            await dm.send(f"\n🏁 Fine del quiz! Risposte corrette: **{score}/{len(questions)}**.\nScrivi `!pronomi-soluzioni` per vedere le soluzioni con spiegazione.")
        except discord.Forbidden:
            await user.send("❌ Non posso mandarti un messaggio privato. Controlla le impostazioni di privacy.")
        finally:
            session_manager.end_session(user.id)

    @commands.command(name="pronomi-soluzioni")
    async def pronome_soluzioni(self, ctx):
        try:
            await ctx.author.send(
                "**🧠 Soluzioni del quiz: Pronomi diretti e indiretti**\n"
                "1. Hai telefonato a Maria? - No, non **le** ho ancora telefonato. *(indiretto: a Maria → le)*\n"
                "2. Puoi chiamare il medico e prendere un appuntamento per domani? - Sì certo, **lo** chiamo tra un secondo. *(diretto: il medico → lo)*\n"
                "3. Devi portare i libri a tua zia? - Sì, **le** do i libri domani. *(indiretto: a tua zia → le)*\n"
                "4. Ho preso una pizza e **l’ho** mangiata tutta. *(diretto: la pizza → la)*\n"
                "5. Hai visto il film? **L’ho** visto ieri. **L’**ho trovato noioso. *(diretto: il film → lo/l’)*\n"
                "6. Non riesco a trovare le chiavi! **Le** sto cercando da due ore! *(diretto: le chiavi → le)*\n"
                "7. Hai ascoltato la nuova canzone? **La** sto ascoltando ora. *(diretto: la canzone → la)*\n"
                "8. Luca e Paolo **ci** hanno invitato a casa loro. *(indiretto plurale: a noi → ci)*\n"
                "9. Ho provato a chiamare Marianna ma non **mi** ha risposto. *(indiretto: a me → mi)*\n"
                "10. Stavi parlando con Roberto? - Sì, **gli** stavo chiedendo un favore. *(indiretto: a lui → gli)*\n"
                "11. Ho comprato i pasticcini. **Li** porto io alla festa. *(diretto: i pasticcini → li)*\n"
                "12. Dove sono i tuoi amici? Non so, **li** sto aspettando. *(diretto: i tuoi amici → li)*\n"
                "13. Il cane porta la palla al suo padrone. - Il cane **gli** porta la palla. *(indiretto: al suo padrone → gli)*\n"
                "14. I miei zii hanno regalato una vacanza ai miei cugini. - I miei zii **gli** hanno regalato una vacanza. *(indiretto: ai miei cugini → gli)*\n"
                "15. Vai da Carlo, **gli** serve una mano a portare i pacchi! *(indiretto: a Carlo → gli)*\n\n"
                "Per rivedere le regole sui pronomi diretti e indiretti, consulta il canale **#grammatica-aiuto**.\n"
                "📝 Wil je deze grammatica nog eens herhalen? Kijk dan in **#grammatica-aiuto** 💪🇮🇹"
            )
            await ctx.send("\U0001F4E9 Le soluzioni sono state inviate nei tuoi DM!")
        except discord.Forbidden:
            await ctx.send("❌ Non riesco a mandarti un DM. Controlla le impostazioni di privacy.")

    async def start_ci_quiz(self, user):
        questions = [
            ("Quale frase usa CI correttamente per indicare un luogo?\nA) Ci vado spesso in palestra\nB) Vado spesso ci\nC) Vado spesso lì", "A"),
            ("Quale frase è corretta?\nA) Non penso più a ci\nB) Non ci penso più\nC) Non penso ci", "B"),
            ("Quale frase è corretta?\nA) Ci credo\nB) Credo ci\nC) Credo a ci", "A"),
            ("Quale frase contiene un errore?\nA) Ci provo sempre\nB) Provo ci sempre\nC) Provo sempre a farlo", "B"),
            ("Scegli l'opzione corretta.\nA) A Roma ci sono stato\nB) Ci Roma sono stato\nC) Ci sono stato a Roma", "C"),
            ("CI può sostituire 'a qualcosa'?\nA) Sì, ci penso spesso\nB) No, mai\nC) Solo con i verbi di moto", "A"),
            ("Qual è la frase corretta?\nA) Penso ci spesso\nB) Ci penso spesso a lei\nC) Ci penso spesso", "C"),
            ("Dove si usa CI correttamente?\nA) Ci voglio bene\nB) Ci credo davvero\nC) Credo ci molto", "B"),
            ("Individua l'uso corretto di CI.\nA) Non ci ho pensato\nB) Non ho pensato ci\nC) Non pensato ci ho", "A"),
            ("Quale frase è corretta?\nA) Ci riesco di solito\nB) Di solito ci riesco\nC) Riesco ci di solito", "B"),
            ("Quale frase contiene un errore?\nA) Pensaci bene\nB) Ci pensi bene\nC) Bene pensaci", "C"),
            ("CI può essere usato con 'pensare'?\nA) Sì, ci penso spesso\nB) No, mai\nC) Solo con nomi propri", "A"),
            ("Qual è la forma corretta?\nA) Non ci faccio caso\nB) Ci non faccio caso\nC) Non faccio caso ci", "A"),
            ("Scegli la frase con CI usato correttamente.\nA) Non ci torno più\nB) Ci torno non più\nC) Torno ci non più", "A"),
            ("Qual è la risposta corretta?\nA) Ci provo sempre\nB) Provo ci sempre\nC) Sempre provo ci", "A")
        ]

        try:
            dm = await user.create_dm()
            await dm.send("\U0001F4DA **Quiz: Uso di CI**\nRispondi con A, B o C. Hai 60 secondi per ogni domanda. In bocca al lupo!")
            score = 0
            for i, (question, correct) in enumerate(questions, 1):
                await dm.send(f"{i}. {question}")
                try:
                    reply = await self.bot.wait_for("message", timeout=60.0, check=lambda m: m.author == user and m.channel == dm and normalize(m.content) in {"a", "b", "c"})
                    if normalize(reply.content) == normalize(correct.lower()):
                        await dm.send("✅ Corretto!")
                        score += 1
                    else:
                        await dm.send(f"❌ Sbagliato! La risposta giusta era **{correct.upper()}**")
                except asyncio.TimeoutError:
                    await dm.send(f"⏰ Tempo scaduto! La risposta giusta era **{correct.upper()}**")
            await dm.send(f"🏁 Hai completato il quiz! Risposte corrette: **{score}/15**. Scrivi `!ci_soluzioni` per vedere le risposte spiegate.")
        except discord.Forbidden:
            await user.send("❌ Non posso inviarti un messaggio privato. Controlla le impostazioni di privacy.")
        finally:
            session_manager.end_session(user.id)

    @commands.command(name="ci_soluzioni")
    async def ci_soluzioni(self, ctx):
        solutions = [
            "1. ❌ C) *Vado spesso lì* → 'lì' è corretto ma non con ci ✅ **A) Ci vado spesso in palestra** è corretta.",
            "2. ✅ B) *Non ci penso più* → 'ci' sostituisce 'a qualcosa'.",
            "3. ✅ A) *Ci credo* → uso corretto con 'credere a qualcosa'.",
            "4. ❌ B) *Provo ci sempre* → 'ci' va prima del verbo. ✅ A) *Ci provo sempre* è corretta.",
            "5. ✅ C) *Ci sono stato a Roma* → struttura corretta con 'ci'.",
            "6. ✅ A) *Sì, ci penso spesso* → uso corretto di 'ci' per sostituire 'a qualcosa'.",
            "7. ✅ C) *Ci penso spesso* → ordine corretto delle parole.",
            "8. ✅ B) *Ci credo davvero* → 'ci' come sostituto di 'a qualcosa'.",
            "9. ✅ A) *Non ci ho pensato* → 'ci' prima dell'ausiliare.",
            "10. ✅ B) *Di solito ci riesco* → posizione corretta di 'ci'.",
            "11. ✅ A) *Pensaci bene* → forma imperativa corretta con 'ci'.",
            "12. ✅ A) *Sì, ci penso spesso* → uso corretto con 'pensare'.",
            "13. ✅ A) *Non ci faccio caso* → espressione fissa corretta.",
            "14. ✅ A) *Non ci torno più* → 'ci' indica luogo, posizione corretta.",
            "15. ✅ A) *Ci provo sempre* → 'ci' sostituisce 'a qualcosa'."
        ]
        try:
            for s in solutions:
                await ctx.author.send(s)
        except discord.Forbidden:
            await ctx.send("❌ Non posso inviarti un messaggio privato. Controlla le impostazioni di privacy.")

    async def start_comparativi_quiz(self, user):
        questions = [
            ("Luca è più simpatico ___ Paolo.", "di"),
            ("Il caffè è più forte ___ amaro.", "che"),
            ("Questo libro è più interessante ___ noioso.", "che"),
            ("La pasta è meno calorica ___ il pane.", "di"),
            ("Questo problema è più urgente ___ complicato.", "che"),
            ("Lei è più sportiva ___ me.", "di"),
            ("Andare al mare è meglio ___ restare in città.", "che"),
            ("Ho meno tempo ___ te.", "di"),
            ("Questo film è il ___ che abbia mai visto.", "peggiore"),
            ("Marta cucina ___ di tutti.", "meglio"),
            ("La birra è ___ del vino, secondo me.", "migliore"),
            ("Hai un fratello ___ o sei figlio unico?", "maggiore"),
            ("Giulia è la sorella ___ .", "minore"),
            ("In questo lavoro, l’esperienza è ___ importante dello stipendio.", "piu"),
            ("Questo esercizio è ___ difficile di quello di ieri.", "piu")
        ]
        await self.run_custom_quiz(user, questions, "I COMPARATIVI", [normalize(a) for a in ["che", "di", "piu", "meno", "meglio", "migliore", "peggiore", "maggiore", "minore"]])

    async def start_che_chi_quiz(self, user):
        questions = [
            ("Non so ______ ha lasciato la porta aperta.", "chi"),
            ("Il ragazzo ______ hai visto ieri è mio cugino.", "che"),
            ("______ arriva tardi deve spiegare il motivo.", "chi"),
            ("È un film ______ mi ha fatto piangere.", "che"),
            ("Non ho capito bene ______ hai invitato.", "chi"),
            ("La ragazza con ______ esco è molto simpatica.", "che"),
            ("______ lavora sodo ottiene risultati.", "chi"),
            ("La canzone ______ stai ascoltando è nuova?", "che"),
            ("Conosco uno ______ parla cinque lingue.", "che"),
            ("C’è qualcuno ______ vuole un caffè?", "chi"),
            ("L’uomo ______ abita qui è un artista.", "che"),
            ("Non ricordo ______ ha detto quella frase.", "chi"),
            ("È una persona ______ non si arrende mai.", "che"),
            ("Non so ______ ha scritto questo libro.", "chi"),
            ("Gli studenti ______ studiano passano l’esame.", "che")
        ]
        await self.run_custom_quiz(user, questions, "CHE o CHI", ["che", "chi"])

    async def start_ci_di_ne_quiz(self, user):
        questions = [
            ("Domani vado a Milano, vuoi venire ___?", "ci"),
            ("Quanti libri hai letto quest’anno? ___ ho letti cinque.", "ne"),
            ("Penso spesso ___ quel giorno.", "di"),
            ("Hai bisogno ___ aiuto?", "di"),
            ("È una situazione complicata, ___ parleremo domani.", "ne"),
            ("Questo gelato è buonissimo! Hai già sentito parlare ___?", "di"),
            ("È molto difficile, ma ___ provo lo stesso.", "ci"),
            ("Vado spesso in quel ristorante, ___ vado anche stasera.", "ci"),
            ("Quante bottiglie d’acqua vuoi? ___ prendo due.", "ne"),
            ("Hai voglia ___ uscire stasera?", "di"),
            ("Mi fido ___ te.", "di"),
            ("Vorrei cambiare lavoro. Che ___ pensi?", "ne"),
            ("Sono sicuro ___ aver chiuso la porta.", "di"),
            ("Non c’è bisogno di spiegare tutto, ___ hai già parlato ieri.", "ne"),
            ("Non voglio parlare ancora ___ quel problema, è troppo delicato.", "di")
        ]
        await self.run_custom_quiz(user, questions, "CI, NE o DI", ["ci", "ne", "di"])

    async def run_custom_quiz(self, user, questions, title, valid_answers):
        try:
            dm = await user.create_dm()
            if title == "I COMPARATIVI":
                istruzioni = "Scrivi la parola corretta tra: **che, di, piu, meno, meglio, migliore, peggiore, maggiore, minore**. Hai 60 secondi per ogni frase. In bocca al lupo!"
            elif title == "CHE o CHI":
                istruzioni = "Scrivi **che** o **chi** secondo il contesto. Hai 60 secondi per ogni frase. In bocca al lupo!"
            elif title == "CI, NE o DI":
                istruzioni = "Scrivi **ci**, **ne** o **di** secondo il contesto. Hai 60 secondi per ogni frase. In bocca al lupo!"
            else:
                istruzioni = "Scrivi la parola corretta secondo il contesto. Hai 60 secondi per ogni frase. In bocca al lupo!"

            await dm.send(f"\U0001F4DA **Quiz: {title}**\n{istruzioni}")
            score = 0
            for idx, (question, answer) in enumerate(questions, start=1):
                await dm.send(f"{idx}/{len(questions)}: {question}")
                try:
                    reply = await self.bot.wait_for(
                        "message",
                        timeout=60.0,
                        check=lambda m: m.author == user and m.channel == dm and normalize(m.content) in valid_answers
                    )
                    if normalize(reply.content) == normalize(answer):
                        await dm.send("\u2705 Corretto!")
                        score += 1
                    else:
                        await dm.send(f"\u274C Sbagliato! Risposta corretta: **{answer}**")
                except asyncio.TimeoutError:
                    await dm.send(f"\u23F0 Tempo scaduto! La risposta giusta era **{answer}**.")
            await dm.send(f"\n\U0001F3C1 Fine del quiz **{title}**! Hai totalizzato **{score}/{len(questions)}** risposte corrette. \U0001F389")
        except discord.Forbidden:
            for thread_id in [
                1388866025679880256,
                1390080013533052949,
                1390371003414216805,
                1393269447094960209,
                1393280441221644328,
                1393289069009830038
            ]:
                channel = self.bot.get_channel(thread_id)
                if channel:
                    await channel.send(f"{user.mention} \u274C Non posso mandarti un messaggio privato. Controlla le impostazioni di privacy.")
                    break
        finally:
            session_manager.end_session(user.id)

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
            session_manager.end_session(user.id)

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
            await dm.send(
                f"📚 **Quiz: {title}**\n"
                "Rispondi scrivendo solo la preposizione corretta (es: `di`, `da`, `in`, `per`, `a`). Hai 60 secondi per ogni frase. Buona fortuna!"
            )

            score = 0
            for q in questions:
                await dm.send(q["question"])
                try:
                    reply = await self.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda m: m.author == user and m.channel == dm
                    )
                    if normalize(reply.content) == normalize(q["answer"]):
                        await dm.send("✅ Corretto!")
                        score += 1
                    else:
                        await dm.send(f"❌ Sbagliato! La risposta giusta era **{q['answer']}**.")
                except asyncio.TimeoutError:
                    await dm.send("⏰ Tempo scaduto! La sessione è stata chiusa per inattività.")
                    return

            await dm.send(f"\n🏁 **Quiz finita!** Hai risposto correttamente a **{score} su {len(questions)}** frasi.")
            await dm.send("Vuoi riprovare? Torna nella thread e scrivi di nuovo `quiz`.")
        except Exception as e:
            print(f"❌ Errore nella quiz ({title}): {e}")
        finally:
            session_manager.end_session(user.id)

# -------------------- BELLO QUIZ --------------------
BELLO_THREAD_ID = 1395790269350281227

bello_zinnen = [
    {"zin": "___ studente ha fatto una presentazione fantastica.", "antwoord": "bello", "oplossing": "bello studente"},
    {"zin": "Hai visto che ___ idea ha avuto Giulia?", "antwoord": "bell'", "oplossing": "bell'idea"},
    {"zin": "Abbiamo visitato una ___ città in Toscana.", "antwoord": "bella", "oplossing": "bella città"},
    {"zin": "___ amici che hai!", "antwoord": "Begli", "oplossing": "Begli amici"},
    {"zin": "Quella è una ___ occasione da non perdere.", "antwoord": "bella", "oplossing": "bella occasione"},
    {"zin": "È un ___ hotel vicino al mare.", "antwoord": "bell'", "oplossing": "bell'hotel"},
    {"zin": "Abbiamo letto un ___ libro ieri.", "antwoord": "bel", "oplossing": "bel libro"},
    {"zin": "Conosco dei ___ studenti in quella scuola.", "antwoord": "begli", "oplossing": "begli studenti"},
    {"zin": "Che ___ spettacolo abbiamo visto ieri!", "antwoord": "bel", "oplossing": "bel spettacolo"},
    {"zin": "I paesaggi di quella regione sono ___", "antwoord": "belli", "oplossing": "paesaggi belli"},
    {"zin": "È stata una serata davvero ___", "antwoord": "bella", "oplossing": "serata bella"},
    {"zin": "Hanno comprato due ___ orologi italiani.", "antwoord": "begli", "oplossing": "begli orologi"},
    {"zin": "Hai preparato una ___ cena!", "antwoord": "bella", "oplossing": "bella cena"},
    {"zin": "Che ___ zaino hai!", "antwoord": "bello", "oplossing": "bello zaino"},
    {"zin": "Sono dei ___ esempi da seguire.", "antwoord": "begli", "oplossing": "begli esempi"},
]

@bot.event
async def on_message(message):
    if message.channel.id == BELLO_THREAD_ID and message.content.lower().strip() == "quiz":
        if is_user_in_active_session(message.author.id):
            return
        if not start_session(message.author.id, "bello_quiz"):
            return
        try:
            dm = await message.author.create_dm()
            await dm.send("🧠 Iniziamo il quiz su **“bello”**! Completa le frasi scegliendo la forma corretta dell’aggettivo.\nRispondi con una sola parola (es: `bel`, `bello`, `bella`, `begli`, `bell'`, `belli`, ...).")

            score = 0
            for i, item in enumerate(bello_zinnen, 1):
                await dm.send(f"**{i}.** {item['zin']}")
                def check(m): return m.author == message.author and isinstance(m.channel, discord.DMChannel)
                try:
                    reply = await bot.wait_for("message", check=check, timeout=60)
                    if reply.content.strip().lower() == item["antwoord"].lower():
                        await dm.send("✅ Corretto!")
                        score += 1
                    else:
                        await dm.send(f"❌ Sbagliato! Risposta corretta: **{item['oplossing']}**")
                except asyncio.TimeoutError:
                    await dm.send(f"⏱ Tempo scaduto! Risposta corretta: **{item['oplossing']}**")

            await dm.send(f"\n📊 Hai risposto correttamente a **{score}** frasi su 15.")
            await dm.send("👉 Per vedere tutte le soluzioni digita `!bello-soluzioni` qui.")

        except Exception as e:
            await message.channel.send("❌ Si è verificato un errore durante il quiz.")
        finally:
            end_session(message.author.id)

# -------------------- BELLO SOLUZIONI --------------------

@bot.command(name="bello-soluzioni")
async def bello_soluzioni(ctx):
    try:
        dm = await ctx.author.create_dm()
        msg = "📘 **Soluzioni del quiz su “bello”**\n\n"
        for i, item in enumerate(bello_zinnen, 1):
            msg += f"**{i}.** {item['oplossing']}\n"
        await dm.send(msg)
        await ctx.send("📩 Le soluzioni ti sono state inviate in DM.")
    except:
        await ctx.send("❌ Impossibile inviare il messaggio in DM.")

async def setup(bot):
    await bot.add_cog(Quiz(bot))