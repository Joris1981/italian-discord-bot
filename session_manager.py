import datetime

# Huidige actieve sessies per gebruiker
# Voorbeeld: {123456789: {"type": "wordle", "start": datetime}}
_active_sessions = {}

def start_session(user_id, session_type):
    """
    Start een sessie van het opgegeven type voor de gebruiker.
    Returnt True als gelukt, False als gebruiker al een sessie heeft lopen.
    """
    if user_id in _active_sessions:
        return False
    _active_sessions[user_id] = {
        "type": session_type,
        "start": datetime.datetime.now()
    }
    return True

def end_session(user_id):
    """
    Beëindigt de sessie van de gebruiker, indien aanwezig.
    """
    _active_sessions.pop(user_id, None)

def is_user_in_active_session(user_id, session_type=None):
    """
    Controleert of de gebruiker een actieve sessie heeft.
    Optioneel: controleer enkel voor een bepaald sessietype.
    """
    sessie = _active_sessions.get(user_id)
    if not sessie:
        return False
    if session_type:
        return sessie["type"] == session_type
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

# Backward compatibility alias
is_busy = is_user_in_active_session