import random

SONG_STRUCTURES = {
    'pop': ['Verse', 'Chorus', 'Verse', 'Chorus', 'Bridge', 'Chorus'],
    'rock': ['Intro', 'Verse', 'Chorus', 'Verse', 'Chorus', 'Solo', 'Chorus'],
    'jazz': ['Intro', 'Verse', 'Interlude', 'Verse', 'Bridge', 'Verse']
}


def generate_song_structure(style):
    """
    Generate a song structure based on the specified musical style.

    Args:
        style (str): The musical style (e.g., 'pop', 'rock', 'jazz').

    Returns:
        list: The song structure as a list of section names.
    """
    if style in SONG_STRUCTURES:
        return SONG_STRUCTURES[style]
    else:
        return ['Verse', 'Chorus', 'Verse', 'Chorus']


def get_section_info(section_name):
    """
    Provide information about a specific song section.

    Args:
        section_name (str): The name of the song section.

    Returns:
        dict: A dictionary with information about the song section.
    """
    section_info = {
        'Verse': {
            'description': 'The main narrative section of the song, where the verses tell the story.',
            'typical_length': '16-32 bars'
        },
        'Chorus': {
            'description': 'The catchy, repetitive section that the audience sings along to.',
            'typical_length': '8-16 bars'
        },
        'Bridge': {
            'description': 'A contrasting section that provides a break from the main melody.',
            'typical_length': '8-16 bars'
        },
        'Intro': {
            'description': 'The opening section that sets the mood and introduces the song.',
            'typical_length': '4-16 bars'
        },
        'Solo': {
            'description': 'A section featuring an instrumental improvisation or performance.',
            'typical_length': '8-32 bars'
        },
        'Interlude': {
            'description': 'A short instrumental section that connects two parts of the song.',
            'typical_length': '4-8 bars'
        }
    }

    return section_info.get(section_name, {'description': 'Unknown section type', 'typical_length': 'Unknown'})