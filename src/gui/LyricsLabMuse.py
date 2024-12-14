# src/gui/LyricsLabMuse.py
import os
import sys
import time
import logging
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QVBoxLayout, QPushButton,
                             QFrame, QMessageBox, QTextEdit,
                             QScrollArea, QProgressDialog
                             )
# from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from src.core.music_composition_experts import MusicCompositionExperts
from src.core.rag_helper import MusicStructureRAG
from src.core.music_composition_export_formatter import MusicCompositionExportFormatter
from audio_generation.audiocraft_generator import AudiocraftGenerator
from src.gui.components.ui.audio_controls import AudioControls


class StreamThread(QThread):
    """Thread pour gérer le streaming de ChatGPT"""
    chunk_ready = pyqtSignal(str)
    stream_complete = pyqtSignal()

    def __init__(self, function, *args):
        super().__init__()
        self.function = function
        self.args = args

    def run(self):
        try:
            music_composer = MusicCompositionExperts()
            stream = getattr(music_composer, self.function)(*self.args)

            # Parcourir le flux de réponse
            for chunk in stream:
                if chunk:
                    self.chunk_ready.emit(chunk)

            self.stream_complete.emit()
        except Exception as e:
            self.chunk_ready.emit(f"Erreur : {str(e)}")
            self.stream_complete.emit()


class AudioGenerationThread(QThread):
    progress_updated = pyqtSignal(int, str)
    generation_complete = pyqtSignal(dict)
    generation_error = pyqtSignal(str)

    def __init__(self, song_generator, formatted_data):
        super().__init__()
        self.song_generator = song_generator
        self.formatted_data = formatted_data
        self.ESTIMATED_GENERATION_TIME = 300  # 5 minutes in seconds

    def run(self):
        try:
            # Start progress tracking thread
            self.progress_thread = ProgressUpdateThread(self.ESTIMATED_GENERATION_TIME)
            self.progress_thread.progress_updated.connect(self.handle_progress_update)
            self.progress_thread.start()

            # Generate audio
            result = self.song_generator.generate_full_song(
                self.formatted_data,
                progress_callback=self.handle_generation_progress
            )

            # Stop progress thread and emit completion
            self.progress_thread.stop()
            self.progress_thread.wait()
            self.progress_updated.emit(100, "Audio generation complete!")
            self.generation_complete.emit(result)

        except Exception as e:
            if hasattr(self, 'progress_thread'):
                self.progress_thread.stop()
                self.progress_thread.wait()
            self.generation_error.emit(str(e))

    def handle_progress_update(self, progress, message):
        """Handle progress updates from progress thread"""
        self.progress_updated.emit(progress, message)

    def handle_generation_progress(self, percent, message):
        """Handle milestone progress updates from generation"""
        if percent == 100:
            self.progress_thread.stop()
            self.progress_thread.wait()
            self.progress_updated.emit(100, "Audio generation complete!")


class ProgressUpdateThread(QThread):
    progress_updated = pyqtSignal(int, str)

    def __init__(self, estimated_time=300):
        super().__init__()
        self.estimated_time = estimated_time
        self.running = True
        import time
        self.start_time = time.time()

    def run(self):
        import time
        while self.running:
            elapsed_time = time.time() - self.start_time
            progress = min(int((elapsed_time / self.estimated_time) * 100), 99)

            remaining_time = max(self.estimated_time - elapsed_time, 0)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)

            message = f"Generating audio... Estimated time remaining: {minutes}m {seconds}s"
            self.progress_updated.emit(progress, message)

            time.sleep(1)  # Update every second

    def stop(self):
        self.running = False


class ModernInterface(QWidget):
    def __init__(self):
        super().__init__()
        try:
            self.song_generator = AudiocraftGenerator()
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error",
                                 f"Failed to initialize audio generator: {str(e)}")
            return
        self.rag = MusicStructureRAG()
        self.dark_mode = False
        self.streaming_thread = None
        self.audio_controls = None
        self.initUI()

        # TODO test
        # self.media_player = QMediaPlayer()

    def initUI(self):
        try:

            self.setWindowTitle('LyricsLabMuse')
            self.setGeometry(100, 100, 800, 700)

            # Start the application max size
            self.showMaximized()

            main_layout = QVBoxLayout()

            # Create a scroll area for the entire content
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

            # Create a frame to hold the content
            content_frame = QFrame()
            content_layout = QVBoxLayout(content_frame)

            self.create_title(content_layout)
            self.create_input_sections(content_layout)
            self.create_buttons(content_layout)
            self.create_full_composition_section(content_layout)

            # Add audio controls here
            self.setup_audio(content_layout)  # Pass the layout as parameter

            scroll_area.setWidget(content_frame)
            main_layout.addWidget(scroll_area)
            self.setLayout(main_layout)

            self.apply_dark_theme()
            self.initialize_llm()
        except Exception as e:
            QMessageBox.critical(self, "UI Initialization Error", f"Failed to initialize UI: {str(e)}")

    def create_title(self, layout):
        titre = QLabel('LyricsLabMuse')
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        layout.addWidget(titre)

    def create_input_sections(self, layout):
        self.text_fields = []
        labels = ['Musical Style', 'Song Theme', 'Mood', 'Language']
        for label in labels:
            section_layout, field = self.create_input_section(label)
            layout.addLayout(section_layout)
            self.text_fields.append(field)

    def create_input_section(self, label_text):
        section_layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("""
            font-weight: bold;
            margin-bottom: 5px;
        """)
        input_field = QLineEdit()
        input_field.setPlaceholderText(f'Entrez votre {label_text.lower()}')

        section_layout.addWidget(label)
        section_layout.addWidget(input_field)
        return section_layout, input_field

    def create_full_composition_section(self, layout):
        full_composition_label = QLabel('Composition Complète Générée')
        full_composition_label.setStyleSheet("""
            font-weight: bold;
            margin-bottom: 5px;
        """)

        self.full_composition_field = QTextEdit()
        self.full_composition_field.setReadOnly(True)
        self.full_composition_field.setPlaceholderText(
            'La composition complète sera générée ici')

        full_composition_layout = QVBoxLayout()
        full_composition_layout.addWidget(full_composition_label)
        full_composition_layout.addWidget(self.full_composition_field)

        layout.addLayout(full_composition_layout)

    def create_buttons(self, layout):
        self.bouton_mode = QPushButton('🌙 Mode Sombre')
        self.bouton_mode.clicked.connect(self.toggle_theme)

        self.bouton_generer_composition = QPushButton('Générer Composition Complète')
        self.bouton_generer_composition.clicked.connect(self.generer_full_composition)

        # Add audio generation button
        self.bouton_generer_audio = QPushButton('Générer Audio')
        self.bouton_generer_audio.clicked.connect(self.generate_audio)

        layout.addWidget(self.bouton_mode)
        layout.addWidget(self.bouton_generer_composition)
        layout.addWidget(self.bouton_generer_audio)

    def initialize_llm(self):
        try:
            self.chatgpt_integration = MusicCompositionExperts()
        except Exception as e:
            QMessageBox.critical(self, "LLM Initialization Error",
                                 f"Failed to initialize language model: {str(e)}")
            raise

    def generer_lyrics(self):
        # Récupérer les informations nécessaires
        musicalStyle = self.text_fields[0].text()
        songTheme = self.text_fields[1].text()
        mood = self.text_fields[2].text()
        language = self.text_fields[3].text()

        # Vérifier que les champs ne sont pas vides
        if not musicalStyle or not songTheme or not mood or not language:
            QMessageBox.warning(
                self, "Erreur", "Veuillez remplir tous les champs nécessaires")
            return

        # Réinitialiser le champ de lyrics
        self.lyrics_field.clear()

        # Arrêter tout thread de streaming précédent
        if self.streaming_thread and self.streaming_thread.isRunning():
            self.streaming_thread.terminate()

        # Créer et lancer un nouveau thread de streaming
        self.streaming_thread = StreamThread(
            'generate_lyrics', musicalStyle, songTheme, mood, language)
        self.streaming_thread.chunk_ready.connect(self.update_lyrics_streaming)
        self.streaming_thread.stream_complete.connect(self.on_stream_complete)
        self.streaming_thread.start()

    def generer_song_structure(self):
        """Generate song structure using the improved RAG"""
        # Get necessary information
        musicalStyle = self.text_fields[0].text()
        songTheme = self.text_fields[1].text()
        mood = self.text_fields[2].text()
        language = self.text_fields[3].text()

        # Validate inputs
        if not all([musicalStyle, songTheme, mood, language]):
            QMessageBox.warning(
                self, "Error", "Please fill in all required fields")
            return

        # Get structure using new RAG
        try:
            structure = self.rag.query_rag(musicalStyle)

            # Reset the structure field
            self.structure_field.clear()

            # Stop any existing streaming thread
            if self.streaming_thread and self.streaming_thread.isRunning():
                self.streaming_thread.terminate()

            # Create and start new streaming thread
            self.streaming_thread = StreamThread(
                'generate_song_structure',
                musicalStyle,
                structure,  # Pass the RAG-generated structure
                songTheme,
                mood,
                language
            )
            self.streaming_thread.chunk_ready.connect(
                self.update_structure_streaming)
            self.streaming_thread.stream_complete.connect(self.on_stream_complete)
            self.streaming_thread.start()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Structure Generation Error",
                f"Failed to generate song structure: {str(e)}"
            )

    def generer_chord_progression(self):
        # Récupérer les informations nécessaires
        musicalStyle = self.text_fields[0].text()
        songTheme = self.text_fields[1].text()
        mood = self.text_fields[2].text()
        language = self.text_fields[3].text()

        # Vérifier que les champs ne sont pas vides
        if not musicalStyle or not songTheme or not mood or not language:
            QMessageBox.warning(
                self, "Erreur", "Veuillez remplir tous les champs nécessaires")
            return

        # Réinitialiser le champ de chords
        self.chords_field.clear()

        # Arrêter tout thread de streaming précédent
        if self.streaming_thread and self.streaming_thread.isRunning():
            self.streaming_thread.terminate()

        # Créer et lancer un nouveau thread de streaming
        self.streaming_thread = StreamThread(
            'generate_chord_progression', musicalStyle, songTheme, mood, language)
        self.streaming_thread.chunk_ready.connect(self.update_chords_streaming)
        self.streaming_thread.stream_complete.connect(self.on_stream_complete)
        self.streaming_thread.start()

    def generer_full_composition(self):
        """Generate full composition with improved RAG integration"""
        # Get necessary information
        musicalStyle = self.text_fields[0].text()
        songTheme = self.text_fields[1].text()
        mood = self.text_fields[2].text()
        language = self.text_fields[3].text()

        # Validate inputs
        if not all([musicalStyle, songTheme, mood, language]):
            QMessageBox.warning(
                self, "Error", "Please fill in all required fields")
            return

        try:
            # Get structure using new RAG
            structure = self.rag.query_rag(musicalStyle)

            # Reset the composition field
            self.full_composition_field.clear()

            # Stop any existing streaming thread
            if self.streaming_thread and self.streaming_thread.isRunning():
                self.streaming_thread.terminate()

            # Create and start new streaming thread
            self.streaming_thread = StreamThread(
                'generate_song_composition',
                musicalStyle,
                structure,  # Pass the RAG-generated structure
                songTheme,
                mood,
                language
            )
            self.streaming_thread.chunk_ready.connect(
                self.update_full_composition_streaming)
            self.streaming_thread.stream_complete.connect(
                self.on_stream_complete)
            self.streaming_thread.start()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Composition Generation Error",
                f"Failed to generate composition: {str(e)}"
            )

    def update_full_composition_streaming(self, chunk):
        # Ajouter le nouveau morceau au texte existant
        current_text = self.full_composition_field.toPlainText()
        self.full_composition_field.setText(current_text + chunk)

        # Faire défiler automatiquement vers le bas
        self.full_composition_field.verticalScrollBar().setValue(
            self.full_composition_field.verticalScrollBar().maximum()
        )

    def update_lyrics_streaming(self, chunk):
        # Ajouter le nouveau morceau au texte existant
        current_text = self.lyrics_field.toPlainText()
        self.lyrics_field.setText(current_text + chunk)

        # Faire défiler automatiquement vers le bas
        self.lyrics_field.verticalScrollBar().setValue(
            self.lyrics_field.verticalScrollBar().maximum()
        )

    def update_structure_streaming(self, chunk):
        # Ajouter le nouveau morceau au texte existant
        current_text = self.structure_field.toPlainText()
        self.structure_field.setText(current_text + chunk)

        # Faire défiler automatiquement vers le bas
        self.structure_field.verticalScrollBar().setValue(
            self.structure_field.verticalScrollBar().maximum()
        )

    def update_chords_streaming(self, chunk):
        # Ajouter le nouveau morceau au texte existant
        current_text = self.chords_field.toPlainText()
        self.chords_field.setText(current_text + chunk)

        # Faire défiler automatiquement vers le bas
        self.chords_field.verticalScrollBar().setValue(
            self.chords_field.verticalScrollBar().maximum()
        )

    def on_stream_complete(self):
        # Vous pouvez ajouter un traitement supplémentaire une fois le streaming terminé
        pass

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self):
        # Mode sombre personnalisé
        self.setStyleSheet("""
            QWidget {
                background-color: #2C3E50;
                color: #ECF0F1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QLabel { color: #ECF0F1; }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #2C3E50;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QCheckBox { color: #ECF0F1; }
        """)
        self.bouton_mode.setText('☀️ Mode Clair')

    def apply_light_theme(self):
        # Mode clair personnalisé
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                color: #333;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QLabel { color: #333; }
            QLineEdit, QComboBox, QTextEdit {
                background-color: white;
                color: #333;
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QCheckBox { color: #333; }
        """)
        self.bouton_mode.setText('🌙 Mode Sombre')

    def valider(self):
        # Validation des champs
        erreurs = []

        if not self.checkbox.isChecked():
            erreurs.append("Vous devez accepter les conditions.")

        if self.liste_deroulante.currentIndex() == -1:
            erreurs.append("Vous devez sélectionner une option.")

        if erreurs:
            # Afficher les erreurs
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Erreurs de validation")
            msg.setInformativeText("\n".join(erreurs))
            msg.setWindowTitle("Validation")
            msg.exec_()
        else:
            # Récupérer les valeurs
            resultats = {
                'Conditions': self.checkbox.isChecked(),
                'Option': self.liste_deroulante.currentText()
            }

            # Afficher un message de succès
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Formulaire Validé")
            msg.setInformativeText(
                "\n".join([f"{k}: {v}" for k, v in resultats.items()]))
            msg.setWindowTitle("Succès")
            msg.exec_()

    def generate_audio(self):
        """Generate audio in a separate thread"""
        try:
            # Get input fields and validate
            musical_style = self.text_fields[0].text()
            song_theme = self.text_fields[1].text()
            mood = self.text_fields[2].text()
            language = self.text_fields[3].text()

            if not all([musical_style, song_theme, mood, language]):
                raise ValueError("All fields must be filled")

            # Create progress dialog with smaller steps
            self.progress = QProgressDialog("Preparing audio generation...", "Cancel", 0, 100, self)
            self.progress.setWindowTitle("Generating Audio")
            self.progress.setWindowModality(Qt.WindowModal)
            self.progress.setAutoClose(True)
            self.progress.setAutoReset(True)
            self.progress.setMinimumDuration(0)  # Show immediately
            self.progress.setValue(0)

            # Make the progress dialog wider
            self.progress.setMinimumWidth(300)

            # Get and validate composition data
            composition_text = self.full_composition_field.toPlainText()
            if not composition_text:
                QMessageBox.warning(self, "Error", "Please generate composition first")
                return

            # Parse and format data
            parsed_data = self._parse_composition_data(composition_text)
            formatter = MusicCompositionExportFormatter()
            formatted_data = formatter.generate_audio_export_metadata(
                lyrics=parsed_data['lyrics'],
                chord_progression=parsed_data['chord_progression'],
                song_structure=parsed_data['full_structure'],
                musical_style=musical_style,
                mood=mood
            )

            # Update musical parameters
            if 'music_metadata' not in formatted_data:
                formatted_data['music_metadata'] = {}
            formatted_data['music_metadata'].update({
                'tempo_bpm': parsed_data.get('musical_parameters', {}).get('Tempo', '120').split()[0],
                'primary_key': parsed_data.get('musical_parameters', {}).get('Key', 'C'),
            })

            # Create and configure audio generation thread
            self.audio_thread = AudioGenerationThread(self.song_generator, formatted_data)

            # Connect signals
            self.audio_thread.progress_updated.connect(self.update_generation_progress)
            self.audio_thread.generation_complete.connect(self.handle_generation_complete)
            self.audio_thread.generation_error.connect(self.handle_generation_error)

            # Connect cancel button
            self.progress.canceled.connect(self.audio_thread.terminate)

            # Start generation
            self.audio_thread.start()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Audio Generation Error", f"Failed to generate audio: {str(e)}")
            logging.error(f"Audio generation error: {str(e)}")

    def update_generation_progress(self, percent, message):
        """Update progress dialog"""
        if self.progress is not None:
            print(f"Debug - Updating progress dialog: {percent}% - {message}")  # Debug line
            self.progress.setLabelText(f"{message}\n{percent}% complete")
            self.progress.setValue(percent)

    def handle_generation_complete(self, result):
        """Handle successful generation"""
        if "instrumental" in result:
            self.handle_audio_output(result["instrumental"])
            QMessageBox.information(self, "Generation Complete", "Audio generation completed successfully!")
        else:
            QMessageBox.warning(self, "Generation Error", "No audio was generated")

    def handle_generation_error(self, error_message):
        """Handle generation error"""
        QMessageBox.critical(self, "Generation Error", f"Failed to generate audio: {error_message}")

    def _extract_lyrics(self, composition_text):
        """Extract lyrics from composition text"""
        # Add logic to extract lyrics section from composition text
        if "## LYRICS" in composition_text:
            lyrics_section = composition_text.split("## LYRICS")[1].split("##")[0]
            return lyrics_section.strip()
        return ""

    def _extract_chords(self, composition_text):
        """Extract chord progression from composition text"""
        # Add logic to extract chord section from composition text
        if "## CHORD PROGRESSION" in composition_text:
            chord_section = composition_text.split("## CHORD PROGRESSION")[1].split("##")[0]
            return chord_section.strip()
        return ""

    def _extract_lyrics(self, composition_text):
        """Extract lyrics from composition text"""
        # Add logic to extract lyrics section from composition text
        if "## LYRICS" in composition_text:
            lyrics_section = composition_text.split("## LYRICS")[1].split("##")[0]
            return lyrics_section.strip()
        return ""

    def _extract_chords(self, composition_text):
        """Extract chord progression from composition text"""
        # Add logic to extract chord section from composition text
        if "## CHORD PROGRESSION" in composition_text:
            chord_section = composition_text.split("## CHORD PROGRESSION")[1].split("##")[0]
            return chord_section.strip()
        return ""

    def handle_audio_output(self, audio_path: str):
        """Handle the generated audio file"""
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Generated audio file not found at {audio_path}")

            if self.audio_controls.load_audio(audio_path):
                self.audio_controls.play_button.click()  # Start playing
            else:
                QMessageBox.warning(self, "Error", "Failed to load audio file")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Audio playback failed: {str(e)}")
            logging.error(f"Audio playback error: {str(e)}")

    def setup_audio(self, layout):
        """Initialize and setup audio controls"""
        try:
            self.audio_controls = AudioControls(self)
            layout.addWidget(self.audio_controls)
        except Exception as e:
            QMessageBox.critical(self, "Audio Setup Error",
                                 f"Failed to initialize audio controls: {str(e)}")
            logging.error(f"Audio controls setup error: {str(e)}")

    def _parse_composition_data(self, composition_text: str) -> dict:
        """
        Parse the full composition text to extract all musical elements
        """
        sections = {}
        current_section = None
        current_content = []

        # Split by sections
        for line in composition_text.split('\n'):
            if line.startswith('##'):
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                    current_content = []
                # Start new section
                current_section = line.replace('#', '').strip()
            elif current_section:
                current_content.append(line)

        # Add final section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)

        # Extract specific parameters
        musical_params = {}
        if "MUSICAL PARAMETERS" in sections:
            params_text = sections["MUSICAL PARAMETERS"]
            for line in params_text.split('\n'):
                if ":" in line:
                    key, value = line.split(':', 1)
                    musical_params[key.strip()] = value.strip()

        return {
            'musical_parameters': musical_params,
            'lyrics': sections.get("LYRICS", ""),
            'chord_progression': sections.get("CHORD PROGRESSION", ""),
            'melody': sections.get("MELODY", ""),
            'full_structure': sections.get("COMPLETE SONG STRUCTURE", "")
        }


if __name__ == '__main__':
    app = QApplication(sys.argv)
    interface = ModernInterface()
    interface.show()
    sys.exit(app.exec_())
