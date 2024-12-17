# tests/test_music_parser.py

import pytest
from src.core.music_parser import MusicParser, MusicParameters, ProductionElements, SongSection


@pytest.fixture
def sample_composition_text():
    return """# Song Composition
Musical Style: Rock
Theme: Freedom
Mood: Energetic
Language: English

## MUSICAL PARAMETERS

[Title]
Breaking Free

[Musical Parameters]
Tempo: 140 BPM
Key: E minor
Time Signature: 4/4
Genre-Specific Feel: Driving
Dynamic Level: High Energy

[Production Elements]
Main Instruments:
- Electric Guitar
- Bass Guitar
- Drums
- Synthesizer

Effects:
- Distortion
- Reverb

[Mix Notes]
Mix Focus: Guitar-driven
Stereo Space: Wide
EQ Focus: Mid-forward

## LYRICS

[Verse 1]
City lights in the distance fade
Running wild, no price to be paid
Every step takes me further away
From the chains of yesterday

[Chorus]
Breaking free, can't you see
This is how it's meant to be
Rising up, breaking through
Nothing left we can't do

## CHORD PROGRESSION

[Verse]
Chord sequence: Em - C - G - D
Duration: 4 bars
Rhythm: Driving eighth notes

[Chorus]
Chord sequence: G - D - Em - C
Duration: 4 bars
Rhythm: Heavy quarter notes

## MELODY

[Verse Melody]
Scale: E Natural Minor
Contour: Rising and falling
Range: E4 to B4
Syncopation: Moderate

[Chorus Melody]
Scale: E Natural Minor
Contour: Upward moving
Range: G4 to E5
Peak Notes: Strong emphasis on B4
"""


def test_parse_musical_parameters(sample_composition_text):
    """Test parsing of musical parameters section"""
    parser = MusicParser()
    result = parser.parse_composition(sample_composition_text)
    params = result['musical_parameters']

    assert isinstance(params, MusicParameters)
    assert params.title == "Breaking Free"
    assert params.tempo == "140"
    assert params.key == "E minor"
    assert params.time_signature == "4/4"
    assert params.genre_specific_feel == "Driving"
    assert params.dynamic_level == "High Energy"


def test_parse_production_elements(sample_composition_text):
    """Test parsing of production elements"""
    parser = MusicParser()
    result = parser.parse_composition(sample_composition_text)
    prod = result['production']

    assert isinstance(prod, ProductionElements)
    assert len(prod.instruments) == 4
    assert "Electric Guitar" in prod.instruments
    assert len(prod.effects) == 2
    assert "Distortion" in prod.effects
    assert prod.mix_focus == "Guitar-driven"
    assert prod.stereo_space == "Wide"
    assert prod.eq_focus == "Mid-forward"


def test_parse_song_sections(sample_composition_text):
    """Test parsing of song sections"""
    parser = MusicParser()
    result = parser.parse_composition(sample_composition_text)
    sections = result['sections']

    # Check Verse 1
    assert "Verse 1" in sections
    verse = sections["Verse 1"]
    assert isinstance(verse, SongSection)
    assert "City lights" in verse.lyrics

    # Check Chorus
    assert "Chorus" in sections
    chorus = sections["Chorus"]
    assert "Breaking free" in chorus.lyrics
    assert "G - D - Em - C" in chorus.chords
    assert "Upward moving" in chorus.melody


def test_parse_metadata(sample_composition_text):
    """Test parsing of metadata"""
    parser = MusicParser()
    result = parser.parse_composition(sample_composition_text)
    metadata = result['metadata']

    assert metadata['musical_style'] == "Rock"
    assert metadata['theme'] == "Freedom"
    assert metadata['mood'] == "Energetic"
    assert metadata['language'] == "English"
    assert 'generated_at' in metadata


def test_empty_composition():
    """Test parsing empty composition"""
    parser = MusicParser()
    result = parser.parse_composition("")

    assert result['metadata'] == {'generated_at': result['metadata']['generated_at']}
    assert isinstance(result['musical_parameters'], MusicParameters)
    assert isinstance(result['production'], ProductionElements)
    assert result['sections'] == {}


def test_partial_composition():
    """Test parsing composition with missing sections"""
    partial_text = """# Song Composition
Musical Style: Rock
Theme: Freedom

## LYRICS

[Verse 1]
Test lyrics
"""

    parser = MusicParser()
    result = parser.parse_composition(partial_text)

    assert result['metadata']['musical_style'] == "Rock"
    assert result['metadata']['theme'] == "Freedom"
    assert "Verse 1" in result['sections']
    assert "Test lyrics" in result['sections']["Verse 1"].lyrics