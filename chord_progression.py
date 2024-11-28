import random

CHORD_QUALITIES = ['major', 'minor', 'diminished', 'augmented']
CHORD_DEGREES = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']


def generate_chord_progression(lyrics, style, key='C'):
    """
    Generate a chord progression based on the provided lyrics and musical style.

    Args:
        lyrics (str): The lyrics to generate chords for.
        style (str): The musical style (e.g., 'pop', 'rock', 'jazz').
        key (str, optional): The key to generate the chords in. Defaults to 'C'.

    Returns:
        list: A list of chords in the progression.
    """
    # Analyze the lyrics to determine the tonality and mood
    tonality = determine_tonality(lyrics)
    mood = determine_mood(lyrics)

    # Generate a chord progression based on the style and analysis
    chords = []

    if style == 'pop':
        chords = generate_pop_chords(tonality, key)
    elif style == 'rock':
        chords = generate_rock_chords(tonality, key)
    elif style == 'jazz':
        chords = generate_jazz_chords(tonality, mood, key)

    return chords


def determine_tonality(lyrics):
    """
    Determine the tonality of the lyrics (major or minor).
    This is a simplified example and would require more advanced analysis in a real-world application.
    """
    if 'happy' in lyrics.lower() or 'joy' in lyrics.lower():
        return 'major'
    else:
        return 'minor'


def determine_mood(lyrics):
    """
    Determine the mood of the lyrics (e.g., upbeat, melancholic, introspective).
    This is a simplified example and would require more advanced analysis in a real-world application.
    """
    if 'sad' in lyrics.lower() or 'melancholy' in lyrics.lower():
        return 'melancholic'
    elif 'energetic' in lyrics.lower() or 'upbeat' in lyrics.lower():
        return 'upbeat'
    else:
        return 'introspective'


def generate_pop_chords(tonality, key):
    """
    Generate a basic pop chord progression.
    """
    if tonality == 'major':
        return [f'{key}', f'{key}m', f'{key}m', f'{key}']
    else:
        return [f'{key}m', f'{key}°', f'{key}b', f'{key}']


def generate_rock_chords(tonality, key):
    """
    Generate a basic rock chord progression.
    """
    if tonality == 'major':
        return [f'{key}', f'{key}m', f'{key}', f'{key}']
    else:
        return [f'{key}m', f'{key}°', f'{key}b', f'{key}m']


def generate_jazz_chords(tonality, mood, key):
    """
    Generate a basic jazz chord progression.
    """
    chords = []

    if tonality == 'major':
        chords = [f'{key}', f'{key}m7', f'{key}m7', f'{key}7']
    else:
        chords = [f'{key}m7', f'{key}°7', f'{key}b7', f'{key}7']

    if mood == 'melancholic':
        chords.append(f'{key}m7b5')
    elif mood == 'upbeat':
        chords.append(f'{key}maj7')
    else:
        chords.append(f'{key}6')

    return chords