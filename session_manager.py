import datetime
import logging

# Logger configureren
logger = logging.getLogger(__name__)

# Huidige actieve sessies per gebruiker
# Voorbeeld: {123456789: {"type": "wordle", "start": datetime}}
_active_sessions = {}

def start_session(user_id, session_type):
    """
    Start een sessie van het opgegeven type voor de gebruiker.
    Returnt True als gelukt, False als gebruiker al een sessie heeft lopen.
    """
    if user_id in _active_sessions:
        logger.warning(f"Kan sessie niet starten voor gebruiker {user_id}: reeds actief ({_active_sessions[user_id]['type']})")
        return False
    _active_sessions[user_id] = {
        "type": session_type,
        "start": datetime.datetime.now()
    }
    logger.info(f"Sessie gestart voor gebruiker {user_id}: type = {session_type}")
    return True

def end_session(user_id):
    """
    Beëindigt de sessie van de gebruiker, indien aanwezig.
    """
    if user_id in _active_sessions:
        logger.info(f"Sessie beëindigd voor gebruiker {user_id}")
    else:
        logger.debug(f"Geen actieve sessie om te beëindigen voor gebruiker {user_id}")
    _active_sessions.pop(user_id, None)

def is_user_in_active_session(user_id, session_type=None):
    """
    Controleert of de gebruiker een actieve sessie heeft.
    Optioneel: controleer enkel voor een bepaald sessietype.
    """
    sessie = _active_sessions.get(user_id)
    if not sessie:
        logger.debug(f"Geen actieve sessie voor gebruiker {user_id}")
        return False
    if session_type and sessie["type"] != session_type:
        logger.debug(f"Actieve sessie voor gebruiker {user_id}, maar van ander type ({sessie['type']} ≠ {session_type})")
        return False
    return True

def get_session_info(user_id):
    """
    Geeft info terug over de sessie van een gebruiker (of None als geen sessie).
    """
    return _active_sessions.get(user_id)

def get_active_session_type(user_id):
    """
    Geeft het sessietype terug van een gebruiker (of None).
    """
    sessie = _active_sessions.get(user_id)
    return sessie["type"] if sessie else None

def cleanup_expired_sessions(timeout_minutes=30):
    """
    Verwijdert automatisch sessies die ouder zijn dan de ingestelde timeout.
    """
    now = datetime.datetime.now()
    expired_users = [
        uid for uid, sessie in _active_sessions.items()
        if (now - sessie["start"]).total_seconds() > timeout_minutes * 60
    ]
    for uid in expired_users:
        logger.info(f"Sessie automatisch beëindigd wegens timeout voor gebruiker {uid}")
        _active_sessions.pop(uid)

# Backward compatibility alias
is_busy = is_user_in_active_session