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
        self.tra_thread = 1390091443678478397

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
            {"zin": "Non ho ___ voglia di uscire.", "antwoord": "alcuna"},
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
            {"zin": "Non so ___ mi ha consigliato quel ristorante.", "antwoord": "chi"}
        ]

        # CI
        self.ci_domande = [
            {
                "domanda": "— Quale frase usa CI correttamente per indicare un luogo?",
                "opzioni": {"A": "Ci vado spesso in palestra", "B": "Vado spesso ci", "C": "Vado spesso li"},
                "corretta": "A"
            },
            {
                "domanda": "— In quale frase CI sostituisce una cosa già menzionata?",
                "opzioni": {"A": "Pensi a quel problema? Si, ci penso spesso.", "B": "Ci ha chiamato Marco?", "C": "Ci ha dato un libro."},
                "corretta": "A"
            },
            {
                "domanda": "— CI metto due ore per finire. Cosa indica CI in questa frase?",
                "opzioni": {"A": "Il tempo necessario", "B": "Un luogo", "C": "In quella cosa o situazione"},
                "corretta": "A"
            },
            {
                "domanda": "— Quale frase contiene un errore nell’uso di CI?",
                "opzioni": {"A": "Ci sono andato Marco", "B": "Non ci credo", "C": "Ci ho parlato ieri"},
                "corretta": "A"
            },
            {
                "domanda": "— CI vuole pazienza. Cosa significa CI in questa espressione?",
                "opzioni": {"A": "Indica una persona", "B": "Non ha un significato preciso, è impersonale", "C": "Indica il tempo"},
                "corretta": "B"
            },
            {
                "domanda": "— Non so se CI riesco. Cosa indica CI in questa frase?",
                "opzioni": {"A": "Il luogo", "B": "L'azione o il obiettivo", "C": "Una persona"},
                "corretta": "B"
            },
            {
                "domanda": "— Marco CI tiene molto a quella cosa. Cosa significa CI in questa frase?",
                "opzioni": {"A": "È importante", "B": "Marco sta lì", "C": "La possiede quella cosa"},
                "corretta": "A"
            },
            {
                "domanda": "— Quale frase è grammaticalmente corretta?",
                "opzioni": {"A": "Gli ci parlo spesso", "B": "Ci sono parlato", "C": "Ci parlo spesso"},
                "corretta": "C"
            },
            {
                "domanda": "— Scegli l’uso corretto di CI impersonale?",
                "opzioni": {"A": "In Italia ci si saluta con un bacio", "B": "Ci dice sempre la verità", "C": "Ci ho una macchina nuova"},
                "corretta": "A"
            },
            {
                "domanda": "- Quale frase contiene un uso scorretto di CI?",
                "opzioni": {"A": "Ci credo davvero", "B": "Ci piace andare al mare", "C": "Ci fa il letto ogni mattina"},
                "corretta": "C"
            },
            {
                "domanda": "— In quale frase CI è usato in modo impersonale?",
                "opzioni": {"A": "Ci ho messo due ore", "B": "Ci si diverte molto in quel corso", "C": "Ci serve più tempo per finire"},
                "corretta": "B"
            },
            {
                "domanda": "— In quale frase CI è complemento indiretto?",
                "opzioni": {"A": "Ci vediamo domani", "B": "Non ci credo più", "C": "Ci hanno offerto un caffè"},
                "corretta": "C"
            },
            {
                "domanda": "- In quale frase CI significa = a noi??",
                "opzioni": {"A": "Ci ha promesso una risposta entro domani", "B": "Non ci vado più", "C": "Ci siamo visti per caso"},
                "corretta": "A"
            },
            {
                "domanda": "- In quale frase CI indica un luogo?",
                "opzioni": {"A": "Non ci credo nemmeno un po’", "B": "Ci siamo svegliati tardi", "C": "Quando torno a casa, ci metto sempre mezz’ora"},
                "corretta": "C"
            },
            {
                "domanda": "- In quale frase CI sostituisce a qualcosa?",
                "opzioni": {"A": "Non ci vediamo da mesi", "B": "Ci sto pensando da giorni", "C": "Ci chiama ogni mattina"},
                "corretta": "B"
            }
        ]

        # CI, DI, NE
        self.ci_di_ne_zinnen = [
            {"zin": "Vado spesso al cinema, ___ vado anche stasera.", "antwoord": "ci"},
            {"zin": "Quanti libri hai letto quest’anno? ___ ho letti cinque.", "antwoord": "ne"},
            {"zin": "Penso spesso ___ quel giorno.", "antwoord": "di"},
            {"zin": "Hai bisogno ___ aiuto?", "antwoord": "di"},
            {"zin": "È una situazione complicata, ___ parleremo domani.", "antwoord": "ne"},
            {"zin": "Questo gelato è buonissimo! Hai già sentito parlare ___ lui?", "antwoord": "di"},
            {"zin": "È molto difficile, ma ___ provo lo stesso.", "antwoord": "ci"},
            {"zin": "Vado spesso in quel ristorante, ___ vado anche stasera.", "antwoord": "ci"},
            {"zin": "Quante bottiglie d’acqua vuoi? ___ prendo due.", "antwoord": "ne"},
            {"zin": "Hai voglia ___ uscire stasera?", "antwoord": "di"},
            {"zin": "Mi fido ___ te.", "antwoord": "di"},
            {"zin": "Vorrei cambiare lavoro. Che ___ pensi?", "antwoord": "ne"},
            {"zin": "Sono sicuro ___ aver chiuso la porta.", "antwoord": "di"},
            {"zin": "Non c’è bisogno di spiegare tutto, ___ hai già parlato ieri.", "antwoord": "ne"},
            {"zin": "Non voglio parlare ancora ___ quel problema, è troppo delicato.", "antwoord": "di"},
            {"zin": "Domani vado a Milano, vuoi venire ___?", "antwoord": "con me"},
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
            {"zin": "Ho preso una pizza e ________ ho mangiata tutta.", "antwoord": "l'"},
            {"zin": "Hai visto il film che ti ho consigliato? Si, ________ ho visto ieri, ma non mi è piaciuto molto.", "antwoord": "l'"},
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
            {"zin": "Hai scritto il messaggio a Marco? Si, ________ l'ho scritto ieri sera.", "antwoord": "gli"},
            {"zin": "Hai comprato il biglietto per il concerto? Si, ________ ho comprato online.", "antwoord": "l'"},
            {"zin": "Hai già fatto i compiti? Si, ________ ho fatti ieri sera.", "antwoord": "li"}
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
            {"zin": "Il caffè è più forte ___ amaro.", "antwoord": "che"},
            {"zin": "Questo libro è più interessante ___ noioso.", "antwoord": "che"},
            {"zin": "La pasta è meno calorica ___ pane.", "antwoord": "del"},
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

        # TRA/FRA o DOPO
        self.tra_zinnen = [
            {"zin": "Ci vediamo ___ due settimane.", "antwoord": "fra", "alternatieven": ["tra"]},
            {"zin": "Il gatto è nascosto ___ i cuscini.", "antwoord": "tra", "alternatieven": ["fra"]},
            {"zin": "Andremo in vacanza ___ l’esame finale.", "antwoord": "dopo"},
            {"zin": "La festa inizierà ___ 20 minuti.", "antwoord": "fra", "alternatieven": ["tra"]},
            {"zin": "Torniamo a casa ___ il film.", "antwoord": "dopo"},
            {"zin": "Partiremo ___ aver finito di lavorare.", "antwoord": "dopo"},
            {"zin": "C'è un parcheggio ___ la banca e il supermercato.", "antwoord": "tra", "alternatieven": ["fra"]},
            {"zin": "Ci sentiamo ___ cena.", "antwoord": "dopo"},
            {"zin": "L’autobus parte ___ 10 minuti.", "antwoord": "fra", "alternatieven": ["tra"]},
            {"zin": "Devi essere a scuola ___ 8.", "antwoord": "alle"},
            {"zin": "Il libro è ___ quelli che preferisco.", "antwoord": "tra", "alternatieven": ["fra"]},
            {"zin": "Andiamo al cinema ___ cena?", "antwoord": "dopo"},
            {"zin": "Ho un colloquio ___ due giorni.", "antwoord": "fra", "alternatieven": ["tra"]},
            {"zin": "Non so scegliere ___ queste opzioni.", "antwoord": "tra", "alternatieven": ["fra"]},
            {"zin": "Sono arrivato ___ la pioggia.", "antwoord": "dopo"},
            {"zin": "La riunione comincia ___ 5 minuti.", "antwoord": "fra", "alternatieven": ["tra"]},
            {"zin": "Dividi la torta ___ i bambini.", "antwoord": "tra", "alternatieven": ["fra"]},
            {"zin": "Riposati ___ il lavoro.", "antwoord": "dopo"},
            {"zin": "Ci vediamo ___ il concerto?", "antwoord": "dopo"},
            {"zin": "Ha parcheggiato ___ due alberi.", "antwoord": "fra", "alternatieven": ["tra"]}
        ]
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = message.author.id
        thread_id = message.channel.id
        content = normalize(message.content)

        if content == "quiz" and not session_manager.is_user_in_active_session(user_id):
            if thread_id == self.tra_thread:
                try:
                    logger.info(f"Starting TRA/FRA quiz for user {user_id}")
                    await self.start_tra_quiz(message)
                except Exception as e:
                    logger.error(f"Error starting TRA/FRA quiz for user {user_id}: {e}")
            if thread_id == self.di_da_thread:
                try:
                    logger.info(f"Starting DI/DA quiz for user {user_id}")
                    await self.start_di_da_quiz(message)
                except Exception as e:
                    logger.error(f"Error starting DI/DA quiz for user {user_id}: {e}")
            elif thread_id == self.per_in_thread:
                try:
                    logger.info(f"Starting PER/IN quiz for user {user_id}")
                    await self.start_per_in_quiz(message)
                except Exception as e:
                    logger.error(f"Error starting PER/IN quiz for user {user_id}: {e}")
            elif thread_id == self.qualche_thread:
                try:
                    logger.info(f"Starting QUALCHE quiz for user {user_id}")
                    await self.start_qualche_quiz(message)
                except Exception as e:
                    logger.error(f"Error starting QUALCHE quiz for user {user_id}: {e}")
            elif thread_id == self.ci_thread:
                try:
                    logger.info(f"Starting CI quiz for user {user_id}")
                    await self.start_ci_quiz(message)
                except Exception as e:
                    logger.error(f"Error starting CI quiz for user {user_id}: {e}")
            elif thread_id == self.ci_di_ne_thread:
                try:
                    logger.info(f"Starting CI/DI/NE quiz for user {user_id}")
                    await self.start_ci_di_ne_quiz(message)
                except Exception as e:
                    logger.error(f"Error starting CI/DI/NE quiz for user {user_id}: {e}")
            elif thread_id == self.pronomi_thread:
                try:
                    logger.info(f"Starting PRONOMI quiz for user {user_id}")
                    await self.start_pronomi_quiz(message)
                except Exception as e:
                    logger.error(f"Error starting PRONOMI quiz for user {user_id}: {e}")
            elif thread_id == self.bello_thread:
                try:
                    logger.info(f"Starting BELLO quiz for user {user_id}")
                    await self.start_bello_quiz(message)
                except Exception as e:
                    logger.error(f"Error starting BELLO quiz for user {user_id}: {e}")
            elif thread_id == self.comparativi_thread:
                try:
                    logger.info(f"Starting COMPARATIVI quiz for user {user_id}")
                    await self.start_comparativi_quiz(message)
                except Exception as e:
                    logger.error(f"Error starting COMPARATIVI quiz for user {user_id}: {e}")
            elif thread_id == self.chi_che_thread:
                try:
                    logger.info(f"Starting CHI/CHE quiz for user {user_id}")
                    await self.start_chi_che_quiz(message)
                except Exception as e:
                    logger.error(f"Error starting CHI/CHE quiz for user {user_id}: {e}")

    async def start_quiz(self, user, vragen, verwacht, oplossingscommando, intro, check_func=None):
        try:
            session_manager.start_session(user.id, "quiz")
            dm = await user.create_dm()
            await dm.send(intro)
            correcte = 0

            for i, vraag in enumerate(vragen, 1):
                await dm.send(f"{i}. {vraag['zin']}")
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        timeout=60,
                        check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel),
                    )
                    antwoord = normalize(msg.content)

                    if check_func:
                        # Gebruik aangepaste check-functie (zoals check_tra_risposta)
                        if await check_func(dm, vraag, msg.content):
                            correcte += 1
                    else:
                        # Standaardcontrole
                        if normalize(vraag[verwacht]) == antwoord:
                            await dm.send("✅ Corretto!")
                            correcte += 1
                        else:
                            await dm.send(f"❌ Sbagliato! La risposta corretta era: **{vraag[verwacht]}**")

                except asyncio.TimeoutError:
                    await dm.send("⏰ Tempo scaduto per questa domanda.")

            await dm.send(f"\n📊 Hai risposto correttamente a **{correcte}** domande su **{len(vragen)}**.")
            await dm.send(f"✉️ Per vedere tutte le risposte corrette, scrivi il comando **{oplossingscommando}** qui in DM.")
        except discord.Forbidden:
            # Eventuele fallback voor blokkade
            channel = await user.guild.fetch_channel(self.bello_thread)
            await channel.send(f"{user.mention}, non posso inviarti un messaggio privato. Controlla le impostazioni della tua privacy.")
        finally:
            session_manager.end_session(user.id)

    async def start_di_da_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        intro = "🎯 Iniziamo il quiz! Rispondi con DI o DA alle seguenti frasi."
        await self.start_quiz(message.author, self.di_da_zinnen, "antwoord", "!di-soluzioni", intro)

    async def start_per_in_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        intro = "🎯 Iniziamo il quiz! Rispondi con PER o IN alle seguenti frasi."
        await self.start_quiz(message.author, self.per_in_zinnen, "antwoord", "!perin-soluzioni", intro)

    async def start_qualche_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        intro = "🎯 Iniziamo il quiz! Rispondi con QUALCHE, ALCUNI o NESSUNO alle seguenti frasi. Hai 60 secondi per ogni frase"
        await self.start_quiz(message.author, self.qualche_zinnen, "antwoord", "!qualche-soluzioni", intro)

    async def start_bello_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        intro = "🎯 Iniziamo il quiz! Rispondi con BELLO, BELLA, BEI, BEGLI o BELL' alle seguenti frasi. Hai 60 secondi per ogni frase"
        await self.start_quiz(message.author, self.bello_zinnen, "antwoord", "!bello-soluzioni", intro)

    async def start_chi_che_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        intro = "🎯 Iniziamo il quiz! Rispondi con CHI o CHE alle seguenti frasi. Hai 60 secondi per ogni frase."
        await self.start_quiz(message.author, self.chi_che_zinnen, "antwoord", "!chiche-soluzioni", intro)

    async def start_comparativi_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        intro = "🎯 Iniziamo il quiz! Rispondi con DI, CHE, PIÙ, MENO o DELLE seguenti frasi. Hai 60 secondi per ogni frase."
        await self.start_quiz(message.author, self.comparativi_zinnen, "antwoord", "!comparativi-soluzioni", intro)

    async def start_ci_di_ne_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        intro = "🎯 Iniziamo il quiz! Rispondi con CI, DI o NE alle seguenti frasi. Hai 60 secondi per ogni frase."
        await self.start_quiz(message.author, self.ci_di_ne_zinnen, "antwoord", "!cidine-soluzioni", intro)

    async def start_pronomi_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        intro = "🎯 Iniziamo il quiz! Rispondi con il pronome corretto per ogni frase. Hai 60 secondi per ogni frase."
        await self.start_quiz(message.author, self.pronomi_zinnen, "antwoord", "!pronomi-soluzioni", intro)

    async def start_tra_quiz(self, message):
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        intro = "🎯 Iniziamo il quiz! Rispondi con TRA, FRA o DOPO alle seguenti frasi. Hai 60 secondi per ogni frase."
        await self.start_quiz(
            message.author,
            zinnen=self.tra_zinnen,
            antwoord_key="antwoord",
            soluzioni_cmd="!tra-soluzioni",
            intro=intro,
            check_func=self.check_tra_risposta
        )

    async def check_tra_risposta(self, dm, domanda, risposta):
        corretta = False
        risposta = risposta.strip().lower()

        # Voeg alle correcte antwoorden samen: hoofdantwoord + alternatieven
        alle_juist = [domanda["antwoord"]]
        if "alternatieven" in domanda:
            alle_juist += domanda["alternatieven"]

        # Maak alles lowercase voor veilige vergelijking
        alle_juist_lower = [a.lower() for a in alle_juist]

        if risposta in alle_juist_lower:
            corretta = True
            if risposta != domanda["antwoord"].lower():
                await dm.send(f"✅ Corretto! Anche '{risposta}' va bene, ma di solito si dice '{domanda['antwoord']}' per motivi di suono.")
            else:
                await dm.send("✅ Corretto!")
        else:
            await dm.send(f"❌ Sbagliato! La risposta corretta era: **{domanda['antwoord']}**")
        return corretta

    async def start_ci_quiz(self, message):
        user = message.author
        await message.channel.send("\U0001F4E9 Il quiz è partito nei tuoi DM!")
        try:
            session_manager.start_session(user.id, "quiz")
            dm = await user.create_dm()
            await dm.send("🎯 Iniziamo il quiz! Scegli la risposta corretta: A, B o C.")

            corrette = 0
            for i, domanda in enumerate(self.ci_domande, 1):
                testo = domanda["domanda"]
                opzioni = domanda["opzioni"]
                await dm.send(f"{i}. {testo}"
                               f"\nA) {opzioni['A']}\nB) {opzioni['B']}\nC) {opzioni['C']}")
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

    async def stuur_oplossingen(self, ctx, titel, zinnen, speciaal_format=False):
        if not isinstance(ctx.channel, discord.DMChannel):
            try:
                await ctx.author.send(f"📘 Ecco le risposte corrette per il quiz *{titel}*:")
                await ctx.send("✅ Ti ho inviato le soluzioni nei tuoi DM!")
            except discord.Forbidden:
                await ctx.send("⛔ Non riesco a mandarti un DM. Controlla le impostazioni di privacy.")
                return
        else:
            await ctx.send(f"📘 Ecco le risposte corrette per il quiz *{titel}*:")

        for i, z in enumerate(zinnen, 1):
            try:
                zin = z["zin"]
                antwoord = z["antwoord"]
                if speciaal_format:
                    await ctx.author.send(f"{i}. {zin} → **{antwoord}**")
                else:
                    await ctx.author.send(f"{i}. {zin.replace('___', f'**{antwoord}**')}")
            except Exception as e:
                await ctx.author.send(f"{i}. ⚠️ Errore nella frase o risposta mancante. ({e})")

    @commands.command(name="di-soluzioni")
    async def di_soluzioni(self, ctx):
        await self.stuur_oplossingen(ctx, "DI o DA", self.di_da_zinnen)

    @commands.command(name="perin-soluzioni")
    async def perin_soluzioni(self, ctx):
        await self.stuur_oplossingen(ctx, "PER o IN", self.per_in_zinnen)

    @commands.command(name="qualche-soluzioni")
    async def qualche_soluzioni(self, ctx):
        await self.stuur_oplossingen(ctx, "Qualche / Alcuni / Nessuno", self.qualche_zinnen)

    @commands.command(name="bello-soluzioni")
    async def bello_soluzioni(self, ctx):
        await self.stuur_oplossingen(ctx, "Bello", self.bello_zinnen)

    @commands.command(name="chiche-soluzioni")
    async def chiche_soluzioni(self, ctx):
        await self.stuur_oplossingen(ctx, "Chi o Che", self.chi_che_zinnen)

    @commands.command(name="comparativi-soluzioni")
    async def comparativi_soluzioni(self, ctx):
        await self.stuur_oplossingen(ctx, "Comparativi", self.comparativi_zinnen)

    @commands.command(name="cidine-soluzioni")
    async def cidine_soluzioni(self, ctx):
        await self.stuur_oplossingen(ctx, "CI / DI / NE", self.ci_di_ne_zinnen)

    @commands.command(name="pronomi-soluzioni")
    async def pronomi_soluzioni(self, ctx):
        await self.stuur_oplossingen(ctx, "Pronomi diretti e indiretti", self.pronomi_zinnen, speciaal_format=True)

    @commands.command(name="ci-soluzioni")
    async def ci_soluzioni(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel):
            try:
                await ctx.author.send("📘 Ecco le risposte corrette per il quiz *CI*:")
                await ctx.send("✅ Ti ho inviato le soluzioni nei tuoi DM!")
            except discord.Forbidden:
                await ctx.send("⛔ Non riesco a mandarti un DM. Controlla le impostazioni di privacy.")
                return
        else:
            await ctx.send("📘 Ecco le risposte corrette per il quiz *CI*:")

        for i, domanda in enumerate(self.ci_domande, 1):
            try:
                testo = domanda["domanda"]
                opzioni = domanda["opzioni"]
                risposta = domanda["corretta"]
                await ctx.author.send(f"{i}. {testo}\nRisposta corretta: **{risposta}**) {opzioni[risposta]}")
            except Exception as e:
                await ctx.author.send(f"{i}. ⚠️ Errore nella domanda o risposta. ({e})")

    @commands.command(name="tra-soluzioni")
    async def tra_soluzioni(self, ctx):
        await self.stuur_oplossingen(ctx, "TRA/FRA o DOPO", self.tra_zinnen)

async def setup(bot):
    await bot.add_cog(Quiz(bot))