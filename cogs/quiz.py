import discord
from discord.ext import commands
import unicodedata
import asyncio
import re
import session_manager
import logging

# Loggingconfiguratie
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize(text):
    text = unicodedata.normalize("NFKD", text).lower().strip()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = re.sub(r'[\s’‘`"^\u0300\u0301]', "", text)
    return text

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.di_da_thread = 1388866025679880256
        self.per_in_thread = 1390080013533052949
        self.qualche_thread = 1390371003414216805
        self.ci_thread = 1388241920790237347
        self.pronomi_thread = 1394735397824758031
        self.bello_thread = 1396072250221920276
        self.comparativi_thread = 1393289069009830038
        self.chi_che_thread = 1393269447094960209
        self.ci_di_ne_thread = 1393280441221644328

        # DI o DA
        self.di_da_zinnen = [
            {"zin": "Vengo ___ Milano.", "antwoord": "da"},
            {"zin": "Sono ___ Napoli.", "antwoord": "di"},
            {"zin": "Vado ___ dentista.", "antwoord": "dal"},
            {"zin": "La chiave ___ macchina.", "antwoord": "della"},
            {"zin": "Parto ___ casa alle otto.", "antwoord": "da"},
            {"zin": "Un amico ___ università.", "antwoord": "dell'"},
            {"zin": "Il profumo ___ mia madre.", "antwoord": "di"},
            {"zin": "Torno ___ Roma domani.", "antwoord": "da"},
            {"zin": "Il libro ___ professore.", "antwoord": "del"},
            {"zin": "La finestra ___ cucina.", "antwoord": "della"},
            {"zin": "La penna ___ Giulia.", "antwoord": "di"},
            {"zin": "Vado ___ Giulia più tardi.", "antwoord": "da"},
            {"zin": "Il cane ___ vicino.", "antwoord": "del"},
            {"zin": "Uscita ___ scuola alle tre.", "antwoord": "da"},
            {"zin": "Il computer ___ ragazzo è rotto.", "antwoord": "del"},
            {"zin": "Questo è il diario ___ Maria", "antwoord": "di"},
            {"zin": "Ho ricevuto una lettera ___ mia cugina", "antwoord": "da"},
            {"zin": "Tornano ___ vacanza domani", "antwoord": "dalla"},
            {"zin": "Torno ___ lavoro alle sei", "antwoord": "dal"},
            {"zin": "La macchina ___ Marco è rossa", "antwoord": "di"}
        ] 
        
        # PER o IN
        self.per_in_zinnen = [
            {"zin": "Studio italiano ___ passione.", "antwoord": "per"},
            {"zin": "Parto ___ Roma domani.", "antwoord": "per"},
            {"zin": "Ho comprato un regalo ___ te.", "antwoord": "per"},
            {"zin": "Vado ___ palestra tre volte a settimana.", "antwoord": "in"},
            {"zin": "Lavoro ___ un’azienda italiana.", "antwoord": "per"},
            {"zin": "Andiamo ___ centro domani?", "antwoord": "in"},
            {"zin": "Questo treno è ___ Milano.", "antwoord": "per"},
            {"zin": "Mi piace viaggiare ___ treno.", "antwoord": "in"},
            {"zin": "Sono ___ ritardo come sempre!", "antwoord": "in"},
            {"zin": "Questa lettera è ___ te.", "antwoord": "per"},
            {"zin": "Ci vediamo ___ classe!", "antwoord": "in"},
            {"zin": "Questo è un corso ___ principianti.", "antwoord": "per"},
            {"zin": "Lui lavora ___ banca.", "antwoord": "in"},
            {"zin": "Ho una sorpresa ___ te!", "antwoord": "per"},
            {"zin": "Sono ___ vacanza in Italia.", "antwoord": "in"},
            {"zin": "È ___ crisi per il lavoro.", "antwoord": "in"},
            {"zin": "Vado a scuola ___ piedi.", "antwoord": "a"},
            {"zin": "Vado al lavoro ___ bicicletta.", "antwoord": "in"},
            {"zin": "Il treno parte ___ Milano alle 8.", "antwoord": "per"},
            {"zin": "Sono ___ piedi da due ore!", "antwoord": "in"}
        ]

        # QUALCHE / ALCUNI / NESSUNO
        self.qualche_zinnen = [
            {"zin": "Ho letto ___ libro interessante.", "antwoord": "qualche"},
            {"zin": "Hai ___ domanda?", "antwoord": "qualche"},
            {"zin": "Ci sono ___ studenti in classe.", "antwoord": "alcuni"},
            {"zin": "Non vedo ___ persona in giardino.", "antwoord": "nessuna"},
            {"zin": "Conosci ___ ragazzo simpatico?", "antwoord": "qualche"},
            {"zin": "Non ho ___ voglia di uscire.", "antwoord": "alcuna"},
            {"zin": "Hai ricevuto ___ notizia?", "antwoord": "qualche"},
            {"zin": "Abbiamo invitato ___ amici alla festa.", "antwoord": "alcuni"},
            {"zin": "Non c’è ___ speranza.", "antwoord": "alcuna"},
            {"zin": "___ volta vado al mare.", "antwoord": "qualche"},
            {"zin": "Non ho incontrato ___ amico lì.", "antwoord": "nessun"},
            {"zin": "Hai ___ minuto per me?", "antwoord": "qualche"},
            {"zin": "Ci sono ___ possibilità di vincere.", "antwoord": "alcune"},
            {"zin": "Non c’è ___ soluzione facile.", "antwoord": "nessuna"},
            {"zin": "___ studenti hanno superato l'esame.", "antwoord": "alcuni"},
            {"zin": "Non ho ___ idea di cosa fare.", "antwoord": "alcuna"},
            {"zin": "Hai visto ___ film interessante?", "antwoord": "qualche"},
            {"zin": "Non c’è ___ motivo di preoccuparsi.", "antwoord": "nessun"},
            {"zin": "___ amici sono partiti in anticipo.", "antwoord": "alcuni"},
            {"zin": "Non c’è ___ problema, tutto è sotto controllo.", "antwoord": "nessun"},
            {"zin": "___ idea è stata accettata.", "antwoord": "qualche"},
            {"zin": "Non conosco ___ con quel nome.", "antwoord": "nessuno"}  
        ]

        # BELLO
        self.bello_zinnen = [
            {"zin": "___ studente ha fatto una presentazione fantastica.", "antwoord": "bello", "oplossing": "bello studente"},
            {"zin": "Hai visto che ___ idea ha avuto Giulia?", "antwoord": "bell'", "oplossing": "bell'idea"},
            {"zin": "Che ___ ragazza!", "antwoord": "bella", "oplossing": "bella ragazza"},
            {"zin": "Sono andato in vacanza in un ___ albergo a cinque stelle.", "antwoord": "bell'", "oplossing": "bell'albergo"},
            {"zin": "Hai comprato dei ___ occhiali da sole.", "antwoord": "begli", "oplossing": "begli occhiali"},
            {"zin": "Che ___ amici che hai!", "antwoord": "begli", "oplossing": "begli amici"},
            {"zin": "Quella è una ___ macchina sportiva.", "antwoord": "bella", "oplossing": "bella macchina"},
            {"zin": "Quel ___ uomo è un attore famoso.", "antwoord": "bell'", "oplossing": "bell'uomo"},
            {"zin": "Questi sono dei ___ regali, grazie!", "antwoord": "bei", "oplossing": "bei regali"},
            {"zin": "Che ___ giornata oggi!", "antwoord": "bella", "oplossing": "bella giornata"},
            {"zin": "Abbiamo visitato un ___ museo in centro.", "antwoord": "bel", "oplossing": "bel museo"},
            {"zin": "Lui ha un ___ sorriso.", "antwoord": "bel", "oplossing": "bel sorriso"},
            {"zin": "Quelle sono delle ___ case antiche.", "antwoord": "belle", "oplossing": "belle case"},
            {"zin": "Guarda che ___ occhi ha!", "antwoord": "begli", "oplossing": "begli occhi"},
            {"zin": "È stato un ___ viaggio.", "antwoord": "bel", "oplossing": "bel viaggio"},
            {"zin": "Hai visto che ___ film interessante?", "antwoord": "bel", "oplossing": "bel film"},
            {"zin": "Quella ___ fontana è davvero bella.", "antwoord": "bella", "oplossing": "bella fontana"},
            {"zin": "Abbiamo fatto una ___ passeggiata al parco.", "antwoord": "bella", "oplossing": "bella passeggiata"},
            {"zin": "Che ___ canzone stai ascoltando?", "antwoord": "bella", "oplossing": "bella canzone"},
            {"zin": "Questo è un ___ libro che ti consiglio di leggere.", "antwoord": "bel", "oplossing": "bel libro"},
            {"zin": "Hai visto che ___ tramonto oggi?", "antwoord": "bel", "oplossing": "bel tramonto"}
        ]

        # CHI o CHE
        self.chi_che_zinnen = [
            {"zin": "Non so ___ ha telefonato.", "antwoord": "chi"},
            {"zin": "Hai visto ___ ha fatto questo disegno?", "antwoord": "chi"},
            {"zin": "Mi chiedo ___ sarà arrivato per primo.", "antwoord": "chi"},
            {"zin": "Non capisco ___ vuoi dire.", "antwoord": "che"},
            {"zin": "So ___ ti piace quel film.", "antwoord": "che"},
            {"zin": "Sai ___ viene alla festa?", "antwoord": "chi"},
            {"zin": "Guarda ___ bel vestito!", "antwoord": "che"},
            {"zin": "Mi domando ___ succederà domani.", "antwoord": "che"},
            {"zin": "Hai scoperto ___ ha scritto quel messaggio?", "antwoord": "chi"},
            {"zin": "È una cosa ___ non si dimentica.", "antwoord": "che"},
            {"zin": "Non so ___ ha lasciato la porta aperta.", "antwoord": "chi"},
            {"zin": "Il ragazzo ___ hai visto ieri è mio cugino.", "antwoord": "che"},
            {"zin": "___ arriva tardi deve spiegare il motivo.", "antwoord": "chi"},
            {"zin": "È un film ___ mi ha fatto piangere.", "antwoord": "che"},
            {"zin": "Non so ___ mi ha mandato quel messaggio.", "antwoord": "chi"},
            {"zin": "La persona ___ ha parlato con te è molto gentile.", "antwoord": "che"},
            {"zin": "Non capisco ___ stai cercando di dire.", "antwoord": "che"},
            {"zin": "Sai ___ ha vinto la gara?", "antwoord": "chi"},
            {"zin": "Non so ___ mi ha rubato il portafoglio.", "antwoord": "chi"},
            {"zin": "Il libro ___ sto leggendo è molto interessante.", "antwoord": "che"},
            {"zin": "Non so ___ mi ha consigliato quel ristorante.", "antwoord": "chi"}
        ]

        # CI
        self.ci_domande = [
            {
                "domanda": "— Quale frase usa CI correttamente per indicare un luogo?",
                "opzioni": {"A": "Ci vado spesso in palestra", "B": "Ne vado spesso", "C": "Lo vado spesso in palestra"},
                "corretta": "A"
            },
            {
                "domanda": "— Quale frase usa CI correttamente per indicare un'azione?",
                "opzioni": {"A": "Ci penso spesso", "B": "Ne penso spesso", "C": "Lo penso spesso"},
                "corretta": "A"
            },
            {
                "domanda": "— Quale frase contiene un errore nell'uso di CI?",
                "opzioni": {"A": "Ci vado spesso in palestra", "B": "Ne vado spesso", "C": "Lo vado spesso in palestra"},
                "corretta": "C"
            },
            {
                "domanda": "— Quale frase è corretta?",
                "opzioni": {"A": "Non penso più a ci", "B": "Non ci penso più", "C": "Non penso ci"},
                "corretta": "B"
            },
            {
                "domanda": "— Quale frase usa CI correttamente per indicare un'azione futura?",
                "opzioni": {"A": "Ci andrò domani", "B": "Ne andrò domani", "C": "Lo andrò domani"},
                "corretta": "A"
            },
            {
                "domanda": "— Quale frase contiene un errore nell'uso di CI?",
                "opzioni": {"A": "Ci credo davvero", "B": "Ne credo davvero", "C": "Lo credo davvero"},
                "corretta": "B"
            },
            {
                "domanda": "— Quale frase usa CI correttamente per indicare un luogo?",
                "opzioni": {"A": "Ci sono stato ieri", "B": "Ne sono stato ieri", "C": "Lo sono stato ieri"},
                "corretta": "A"
            },
            {
                "domanda": "— Quale frase è corretta?",
                "opzioni": {"A": "Ci penso spesso a lei", "B": "Ne penso spesso a lei", "C": "Lo penso spesso a lei"},
                "corretta": "A"
            },
            {
                "domanda": "— Quale frase contiene un errore nell'uso di CI?",
                "opzioni": {"A": "Ci voglio bene", "B": "Ne voglio bene", "C": "Lo voglio bene"},
                "corretta": "B"
            },
            {
                "domanda": "- Quale frase usa CI correttamente per indicare un'azione passata?",
                "opzioni": {"A": "Ci ho pensato ieri", "B": "Ne ho pensato ieri", "C": "Lo ho pensato ieri"},
                "corretta": "A"
            },
            {
                "domanda": "— Quale frase è corretta?",
                "opzioni": {"A": "Ci riesco di solito", "B": "Ne riesco di solito", "C": "Lo riesco di solito"},
                "corretta": "A"
            },
            {
                "domanda": "— Quale frase contiene un errore nell'uso di CI?",
                "opzioni": {"A": "Pensaci bene", "B": "Ne pensi bene", "C": "Lo pensi bene"},
                "corretta": "B"
            },
            {
                "domanda": "- Quale frase usa CI correttamente per indicare un'azione futura?",
                "opzioni": {"A": "Ci torno domani", "B": "Ne torno domani", "C": "Lo torno domani"},
                "corretta": "A"
            },
            {
                "domanda": "- Quale frase è corretta?",
                "opzioni": {"A": "Ci provo sempre", "B": "Ne provo sempre", "C": "Lo provo sempre"},
                "corretta": "A"
            },
            {
                "domanda": "- Individua l'uso corretto di CI",
                "opzioni": {"A": "Ci credo", "B": "Credo a ci", "C": "Credo ci"},
                "corretta": "A"
            }
        ]

        # CI, DI, NE
        self.ci_di_ne_zinnen = [
            {"zin": "Vado spesso al cinema, ___ vado anche stasera.", "antwoord": "ci"},
            {"zin": "Quanti libri hai letto quest’anno? ___ ho letti cinque.", "antwoord": "ne"},
            {"zin": "Penso spesso ___ quel giorno.", "antwoord": "di"},
            {"zin": "Hai bisogno ___ aiuto?", "antwoord": "di"},
            {"zin": "È una situazione complicata, ___ parleremo domani.", "antwoord": "ne"},
            {"zin": "Questo gelato è buonissimo! Hai già sentito parlare ___?", "antwoord": "di"},
            {"zin": "È molto difficile, ma ___ provo lo stesso.", "antwoord": "ci"},
            {"zin": "Vado spesso in quel ristorante, ___ vado anche stasera.", "antwoord": "ci"},
            {"zin": "Quante bottiglie d’acqua vuoi? ___ prendo due.", "antwoord": "ne"},
            {"zin": "Hai voglia ___ uscire stasera?", "antwoord": "di"},
            {"zin": "Mi fido ___ te.", "antwoord": "di"},
            {"zin": "Vorrei cambiare lavoro. Che ___ pensi?", "antwoord": "ne"},
            {"zin": "Sono sicuro ___ aver chiuso la porta.", "antwoord": "di"},
            {"zin": "Non c’è bisogno di spiegare tutto, ___ hai già parlato ieri.", "antwoord": "ne"},
            {"zin": "Non voglio parlare ancora ___ quel problema, è troppo delicato.", "antwoord": "di"},
            {"zin": "Domani vado a Milano, vuoi venire ___?", "antwoord": "ci"},
            {"zin": "Non ho mai visto un film così bello, ___ hai visto?", "antwoord": "ne"},
            {"zin": "Mi piace molto questo libro, ___ hai letto?", "antwoord": "ne"},
            {"zin": "Non ho mai pensato ___ trasferirmi all’estero.", "antwoord": "di"},
            {"zin": "Hai già deciso cosa fare domani? Io non ___ ho ancora deciso.", "antwoord": "ne"}
        ]

        # PRONOMI
        self.pronomi_zinnen = [
            {"zin": "Hai telefonato a Maria? No, non ________ ho ancora telefonto", "antwoord": "le"},
            {"zin": "Puoi chiamare il medico e prendere un appuntamento per domani? Si certo, ________ chiamo tra un secondo.", "antwoord": "lo"},
            {"zin": "Devi portare i libri a tua zia? Si, ________ porto io.", "antwoord": "le"},
            {"zin": "Ho preso una pizza e ________ ho mangiata tutta.", "antwoord": "l'ho"},
            {"zin": "Hai visto il film che ti ho consigliato? Si, ________ visto ieri, ma non mi è piaciuto molto.", "antwoord": "l'ho"},
            {"zin": "Non riesco a trovare le chiavi! ________ sto cercando da due ore!", "antwoord": "le"},
            {"zin": "Hai ascoltato la nuova canzone di Taylor Swift? Si, ________ sto ascoltando da due ore!", "antwoord": "la"},
            {"zin": "Luca e Paolo ________ hanno invitato a casa loro. Andiamo?", "antwoord": "ci"},
            {"zin": "Ho provato a chiamare Marianna ma non ________ ha risposto.", "antwoord": "mi"},
            {"zin": "Stavi parlando con Roberto? Si, ________ stavo chiedendo un favore", "antwoord": "gli"},
            {"zin": "Ho comprato i pasticcini. ________ porto io alla festa.", "antwoord": "li"},       
            {"zin": "Dove sono i tuoi amici? Non so, ________ sto aspettando da 5 minuti.", "antwoord": "li"},
            {"zin": "Il cane porta la palla al suo padrone. Il cane ________ porta la palla.", "antwoord": "gli"},
            {"zin": "I miei zii hanno regalato una vacanza ai miei cugini. I miei zii ________ hanno regalato una vacanza.", "antwoord": "gli"},
            {"zin": "Vai da Carlo, ________ serve una mano a portare i pacchi!", "antwoord": "gli"},
            {"zin": "Hai visto il gatto di Sara? No, non ________ ho visto.", "antwoord": "lo"},
            {"zin": "Hai comprato le uova? Si, ________ ho comprate al mercato.", "antwoord": "le"},
            {"zin": "Hai raccontato la storia ai bambini? Si, ________ l'ho raccontata ieri.", "antwoord": "gliela"},
            {"zin": "Hai dato il regalo a tua sorella? Si, ________ l'ho dato ieri.", "antwoord": "glielo"},
            {"zin": "Hai portato i documenti al tuo capo? Si, ________ li ho portati stamattina.", "antwoord": "glieli"},
            {"zin": "Hai scritto il messaggio a Marco? Si, ________ l'ho scritto ieri sera.", "antwoord": "gli"},
            {"zin": "Hai comprato il biglietto per il concerto? Si, ________ comprato online.", "antwoord": "l'ho"}
        ]

        # COMPARATIVI
        self.comparativi_zinnen = [
            {"zin": "Milano è più grande ___ Bologna.", "antwoord": "di"},
            {"zin": "Lei è meno simpatica ___ sua sorella.", "antwoord": "di"},
            {"zin": "Mi piace più la pasta ___ la pizza.", "antwoord": "che"},
            {"zin": "Correre è più faticoso ___ camminare.", "antwoord": "che"},
            {"zin": "Il treno è meno veloce ___ l’aereo.", "antwoord": "di"},
            {"zin": "Preferisco dormire ___ lavorare.", "antwoord": "che"},
            {"zin": "Il caffè è più amaro ___ tè.", "antwoord": "del"},
            {"zin": "Lui è più alto ___ tutti.", "antwoord": "di"},
            {"zin": "Studiare è più importante ___ uscire.", "antwoord": "che"},
            {"zin": "Questa strada è meno pericolosa ___ quella.", "antwoord": "di"},
            {"zin": "Questo film è meno interessante ___ quello che abbiamo visto ieri.", "antwoord": "di"},
            {"zin": "Luca è più simpatico ___ Paolo.", "antwoord": "di"},
            {"zin": "Il caffè è più forte ___ amaro.", "antwoord": "che"},
            {"zin": "Questo libro è più interessante ___ noioso.", "antwoord": "che"},
            {"zin": "La pasta è meno calorica ___ il pane.", "antwoord": "di"},
            {"zin": "Questo problema è più urgente ___ complicato.", "antwoord": "che"},
            {"zin": "Lei è più sportiva ___ me.", "antwoord": "di"},
            {"zin": "Andare al mare è meglio ___ restare in città.", "antwoord": "che"},
            {"zin": "Ho meno tempo ___ te.", "antwoord": "di"},
            {"zin": "Questo film è il ___ che abbia mai visto.", "antwoord": "peggiore"},
            {"zin": "Marta cucina ___ di tutti.", "antwoord": "meglio"},
            {"zin": "La birra è ___ del vino, secondo me.", "antwoord": "migliore"},
            {"zin": "Hai un fratello ___ o sei figlio unico?", "antwoord": "maggiore"},
            {"zin": "Giulia è la sorella ___ .", "antwoord": "minore"},
            {"zin": "In questo lavoro, l’esperienza è ___ importante dello stipendio.", "antwoord": "più"},
            {"zin": "Questo esercizio è ___ difficile di quello di ieri.", "antwoord": "più"}
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = message.author.id
        thread_id = message.channel.id
        content = normalize(message.content)

        if content == "quiz" and not session_manager.is_user_in_active_session(user_id):
            if thread_id == self.di_da_thread:
                await self.start_di_da_quiz(message)
            elif thread_id == self.per_in_thread:
                await self.start_per_in_quiz(message)
            elif thread_id == self.qualche_thread:
                await self.start_qualche_quiz(message)
            elif thread_id == self.ci_thread:
                await self.start_ci_quiz(message)
            elif thread_id == self.ci_di_ne_thread:
                await self.start_ci_di_ne_quiz(message)
            elif thread_id == self.pronomi_thread:
                await self.start_pronomi_quiz(message)
            elif thread_id == self.bello_thread:
                await self.start_bello_quiz(message)
            elif thread_id == self.comparativi_thread:
                await self.start_comparativi_quiz(message)
            elif thread_id == self.chi_che_thread:
                await self.start_chi_che_quiz(message)

    async def start_quiz(self, user, vragen, verwacht, oplossingscommando):
        try:
            session_manager.start_session(user.id)
            dm = await user.create_dm()
            await dm.send("🎯 Iniziamo il quiz! Rispondi a ciascuna frase inserendo la parola corretta.")
            correcte = 0
            for i, vraag in enumerate(vragen, 1):
                await dm.send(f"{i}. {vraag['zin']}")
                try:
                    msg = await self.bot.wait_for("message", timeout=60, check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel))
                    antwoord = normalize(msg.content)
                    if antwoord == normalize(vraag[verwacht]):
                        await dm.send("✅ Corretto!")
                        correcte += 1
                    else:
                        await dm.send(f"❌ Sbagliato! La risposta corretta era: **{vraag[verwacht]}**")
                except asyncio.TimeoutError:
                    await dm.send("⏰ Tempo scaduto per questa domanda.")

            await dm.send(f"\n📊 Hai risposto correttamente a **{correcte}** domande su **{len(vragen)}**.")
            await dm.send(f"✉️ Per vedere tutte le risposte corrette, scrivi il comando **{oplossingscommando}** qui in DM.")
        except discord.Forbidden:
            channel = await user.guild.fetch_channel(self.bello_thread)
            await channel.send(f"{user.mention}, non posso inviarti un messaggio privato. Controlla le impostazioni della tua privacy.")
        finally:
            session_manager.end_session(user.id)

    async def start_di_da_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        await self.start_quiz(message.author, self.di_da_zinnen, "antwoord", "!di-soluzioni")

    async def start_per_in_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        await self.start_quiz(message.author, self.per_in_zinnen, "antwoord", "!perin-soluzioni")

    async def start_qualche_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        await self.start_quiz(message.author, self.qualche_zinnen, "antwoord", "!qualche-soluzioni")

    async def start_bello_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        await self.start_quiz(message.author, self.bello_zinnen, "antwoord", "!bello-soluzioni")

    async def start_chi_che_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        await self.start_quiz(message.author, self.chi_che_zinnen, "antwoord", "!chiche-soluzioni")

    async def start_comparativi_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        await self.start_quiz(message.author, self.comparativi_zinnen, "antwoord", "!comparativi-soluzioni")

    async def start_ci_di_ne_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        await self.start_quiz(message.author, self.ci_di_ne_zinnen, "antwoord", "!cidine-soluzioni")

    async def start_pronomi_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        await self.start_quiz(message.author, self.pronomi_zinnen, "antwoord", "!pronomi-soluzioni")

    async def start_ci_quiz(self, message):
        user = message.author
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        try:
            session_manager.start_session(user.id)
            dm = await user.create_dm()
            await dm.send("🎯 Iniziamo il quiz! Scegli la risposta corretta: A, B o C.")

            corrette = 0
            for i, domanda in enumerate(self.ci_domande, 1):
                testo = domanda["domanda"]
                await dm.send(f"{i}. {testo}")
                try:
                    msg = await self.bot.wait_for("message", timeout=60, check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel))
                    risposta = msg.content.strip().upper()
                    if risposta == domanda["corretta"]:
                        await dm.send("✅ Corretto!")
                        corrette += 1
                    else:
                        await dm.send(f"❌ Sbagliato! La risposta giusta era: **{domanda['corretta']}**")
                except asyncio.TimeoutError:
                    await dm.send("⏰ Tempo scaduto per questa domanda.")

            await dm.send(f"\n📊 Hai risposto correttamente a **{corrette}** domande su **{len(self.ci_domande)}**.")
            await dm.send("✉️ Per rivedere le domande, scrivi **!ci-soluzioni**.")
        except discord.Forbidden:
            await message.channel.send(f"{user.mention}, non posso inviarti un DM. Controlla le tue impostazioni di privacy.")
        finally:
            session_manager.end_session(user.id)

    @commands.command(name="di-soluzioni")
    async def di_soluzioni(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("📘 Ecco le risposte corrette per il quiz *DI o DA*:")
            for i, z in enumerate(self.di_da_zinnen, 1):
                await ctx.send(f"{i}. {z['zin'].replace('___', f'**{z['antwoord']}**')}")

    @commands.command(name="perin-soluzioni")
    async def perin_soluzioni(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("📘 Ecco le risposte corrette per il quiz *PER o IN*:")
            for i, z in enumerate(self.per_in_zinnen, 1):
                await ctx.send(f"{i}. {z['zin'].replace('___', f'**{z['antwoord']}**')}")

    @commands.command(name="qualche-soluzioni")
    async def qualche_soluzioni(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("📘 Ecco le risposte corrette per il quiz *Qualche / Alcuni / Nessuno*:")
            for i, z in enumerate(self.qualche_zinnen, 1):
                await ctx.send(f"{i}. {z['zin'].replace('___', f'**{z['antwoord']}**')}")

    @commands.command(name="bello-soluzioni")
    async def bello_soluzioni(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("📘 Ecco le risposte corrette per il quiz *Bello*:")
            for i, z in enumerate(self.bello_zinnen, 1):
                await ctx.send(f"{i}. {z['zin'].replace('___', f'**{z['antwoord']}**')}")

    @commands.command(name="chiche-soluzioni")
    async def chiche_soluzioni(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("📘 Ecco le risposte corrette per il quiz *Chi o Che*:")
            for i, z in enumerate(self.chi_che_zinnen, 1):
                await ctx.send(f"{i}. {z['zin'].replace('___', f'**{z['antwoord']}**')}")

    @commands.command(name="comparativi-soluzioni")
    async def comparativi_soluzioni(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("📘 Ecco le risposte corrette per il quiz *Comparativi*:")
            for i, z in enumerate(self.comparativi_zinnen, 1):
                await ctx.send(f"{i}. {z['zin'].replace('___', f'**{z['antwoord']}**')}")

    @commands.command(name="cidine-soluzioni")
    async def cidine_soluzioni(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("📘 Ecco le risposte corrette per il quiz *CI / DI / NE*:")
            for i, z in enumerate(self.ci_di_ne_zinnen, 1):
                await ctx.send(f"{i}. {z['zin'].replace('___', f'**{z['antwoord']}**')}")

    @commands.command(name="pronomi-soluzioni")
    async def pronomi_soluzioni(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("📘 Ecco le risposte corrette per il quiz *Pronomi diretti e indiretti*:")
            for i, z in enumerate(self.pronomi_zinnen, 1):
                await ctx.send(f"{i}. {z['zin']} → **{z['antwoord']}**")

    @commands.command(name="ci-soluzioni")
    async def ci_soluzioni(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("📘 Ecco le risposte corrette per il quiz *CI*:")
            for i, domanda in enumerate(self.ci_domande, 1):
                opzioni = domanda["opzioni"]
                risposta = domanda["corretta"]
                await ctx.send(f"{i}. {domanda['domanda']}\nRisposta corretta: **{risposta}**) {opzioni[risposta]}")

async def setup(bot):
    await bot.add_cog(Quiz(bot))