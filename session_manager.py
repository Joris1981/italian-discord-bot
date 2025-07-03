# session_manager.py

# Huidige actieve gebruikers
active_quiz_users = set()
active_wordle_users = set()

def is_busy(user_id):
    """
    Controleert of gebruiker bezig is met een quiz of wordle.
    """
    return user_id in active_quiz_users or user_id in active_wordle_users

def start_quiz(user_id):
    """
    Start een quiz voor deze gebruiker (enkel als hij vrij is).
    """
    if is_busy(user_id):
        return False
    active_quiz_users.add(user_id)
    return True

def end_quiz(user_id):
    """
    Beëindigt de quiz voor deze gebruiker.
    """
    active_quiz_users.discard(user_id)

def start_wordle(user_id):
    """
    Start een Wordle-spel voor deze gebruiker (enkel als hij vrij is).
    """
    if is_busy(user_id):
        return False
    active_wordle_users.add(user_id)
    return True

def end_wordle(user_id):
    """
    Beëindigt de Wordle voor deze gebruiker.
    """
    active_wordle_users.discard(user_id)

# Alias voor compatibiliteit met oudere imports
is_user_in_active_session = is_busy