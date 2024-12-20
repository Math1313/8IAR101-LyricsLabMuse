from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QVBoxLayout, QPushButton,
                             QFrame, QMessageBox, QTextEdit,QComboBox,
                             QScrollArea, QProgressDialog, QStyle, QHBoxLayout, QFileDialog
                             )
from PyQt5.QtCore import Qt
import logging
import sys
import os

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")))

from src.gui.components.stream_thread import StreamThread
from src.gui.components.audio_thread import AudioGenerationThread
from src.gui.components.audio_controls import AudioControls
from src.gui.components.themes import apply_dark_theme, apply_light_theme
from src.core.audiocraft_generator import AudiocraftGenerator
from src.core.music_composition_export_formatter import MusicCompositionExportFormatter
from src.core.rag_helper import MusicStructureRAG
from src.core.obscene_filter import ObsceneFilter

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
        self.ObsceneFilter = ObsceneFilter()
        self.MusicExportFormatter = MusicCompositionExportFormatter()
        self.dark_mode = False
        self.streaming_thread = None
        self.audio_controls = None
        self.initUI()

        # TODO test
        # self.media_player = QMediaPlayer()

    def initUI(self):
        try:

            self.setWindowTitle('LyricsLabMuse')
            self.setGeometry(100, 100, 800, 1200)

            # Start the application max size
            # self.showMaximized()
            # Start the app normal
            self.showNormal()

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

            self.create_export_buttons(content_layout)  # Add export buttons

            # Add audio controls here
            self.setup_audio(content_layout)  # Pass the layout as parameter

            scroll_area.setWidget(content_frame)
            main_layout.addWidget(scroll_area)
            self.setLayout(main_layout)

            apply_dark_theme(self)
        except Exception as e:
            QMessageBox.critical(
                self, "UI Initialization Error", f"Failed to initialize UI: {str(e)}")

    
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
            if label == 'Musical Style':
                section_layout, field = self.create_dropdown_section(label)
            else:
                section_layout, field = self.create_input_section(label)
            layout.addLayout(section_layout)
            self.text_fields.append(field)


    def create_dropdown_section(self, label_text):
        section_layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("""
            font-weight: bold;
            margin-bottom: 5px;
        """)
        dropdown = QComboBox()
        dropdown.addItems(['Pop', 'Rock', 'Rap', 'EDM', 'Blues', 'Country', 'Jazz', 'Reggae', 'R&B'])

        section_layout.addWidget(label)
        section_layout.addWidget(dropdown)
        return section_layout, dropdown
    

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

        self.bouton_generer_composition = QPushButton(
            'Générer Composition Complète')
        self.bouton_generer_composition.clicked.connect(
            self.generer_full_composition)

        # Add audio generation button
        self.bouton_generer_audio = QPushButton('Générer Audio')
        self.bouton_generer_audio.clicked.connect(self.generate_audio)

        layout.addWidget(self.bouton_mode)
        layout.addWidget(self.bouton_generer_composition)
        layout.addWidget(self.bouton_generer_audio)


    def get_song_info(self):
        musicalStyle = self.text_fields[0].currentText()
        songTheme = self.text_fields[1].text()
        mood = self.text_fields[2].text()
        language = self.text_fields[3].text()
        
        return musicalStyle, songTheme, mood, language
    

    def generer_full_composition(self):
        """Generate full composition with improved RAG integration"""
        # Récupérer les informations nécessaires
        musicalStyle, songTheme, mood, language = self.get_song_info()

        # Validate inputs
        if not all([musicalStyle, songTheme, mood, language]):
            QMessageBox.warning(
                self, "Error", "Please fill in all empty fields")
            return
        
        # Validate obscene language
        if(any(
            self.ObsceneFilter.is_obscene(item)
            for item in [songTheme, mood, language]
        )):
            QMessageBox.warning(
                self, "Error", "Please avoid using obscene language")
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


    def on_stream_complete(self):
        # Vous pouvez ajouter un traitement supplémentaire une fois le streaming terminé
        pass

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            apply_dark_theme(self)
        else:
            apply_light_theme(self)

    def generate_audio(self):
        """Generate audio in a separate thread with proper error handling and data processing"""
        try:
            # Get input fields and validate
            musical_style = self.text_fields[0].currentText()
            song_theme = self.text_fields[1].text()
            mood = self.text_fields[2].text()
            language = self.text_fields[3].text()

            if not all([musical_style, song_theme, mood, language]):
                raise ValueError("All fields must be filled")

            # Create progress dialog with smaller steps
            self.progress = QProgressDialog(
                "Preparing audio generation...", "Cancel", 0, 100, self)
            self.progress.setWindowTitle("Generating Audio")
            self.progress.setWindowModality(Qt.WindowModal)
            self.progress.setAutoClose(True)
            self.progress.setAutoReset(True)
            self.progress.setMinimumDuration(0)  # Show immediately
            self.progress.setValue(0)
            self.progress.setMinimumWidth(300)

            # Get composition text and validate
            composition_text = self.full_composition_field.toPlainText()
            if not composition_text:
                QMessageBox.warning(
                    self, "Error", "Please generate composition first")
                return

            try:
                # Parse and format data
                parsed_data = self.MusicExportFormatter.parse_composition(composition_text)

                # Log parsed data for debugging
                logging.debug(f"Parsed composition data: {parsed_data}")
                print(parsed_data)
                # Generate audio export metadata
                formatted_data = self.MusicExportFormatter.generate_audio_export_metadata(
                    lyrics=parsed_data.get('lyrics', {}),
                    chord_progression=parsed_data.get('chord_progression', {}),
                    song_structure=parsed_data.get('full_structure', {}),
                    musical_style=musical_style,
                    mood=mood
                )

                # Log formatted data for debugging
                logging.debug(f"Formatted audio metadata: {formatted_data}")

                # Validate formatted data structure
                if not formatted_data.get('music_metadata'):
                    raise ValueError("Missing required music metadata")

            except Exception as e:
                logging.error(f"Data formatting error: {str(e)}")
                QMessageBox.critical(
                    self, "Formatting Error",
                    f"Failed to process composition data: {str(e)}")
                return

            # Create and configure audio generation thread
            self.audio_thread = AudioGenerationThread(
                self.song_generator, formatted_data)

            # Connect signals
            self.audio_thread.progress_updated.connect(
                self.update_generation_progress)
            self.audio_thread.generation_complete.connect(
                self.handle_generation_complete)
            self.audio_thread.generation_error.connect(
                self.handle_generation_error)

            # Connect cancel button
            self.progress.canceled.connect(self.audio_thread.terminate)

            # Start generation
            self.audio_thread.start()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            logging.error(f"Audio generation error: {str(e)}")
            QMessageBox.critical(
                self,
                "Audio Generation Error",
                f"Failed to generate audio: {str(e)}")

    def update_generation_progress(self, percent, message):
        """Update progress dialog"""
        if self.progress is not None:
            # Debug line
            print(f"Debug - Updating progress dialog: {percent}% - {message}")
            self.progress.setLabelText(f"{message}\n{percent}% complete")
            self.progress.setValue(percent)

    def handle_generation_complete(self, result):
        """Handle successful generation"""
        if "instrumental" in result:
            self.handle_audio_output(result["instrumental"])
            QMessageBox.information(
                self, "Generation Complete", "Audio generation completed successfully!")
        else:
            QMessageBox.warning(self, "Generation Error",
                                "No audio was generated")

    def handle_generation_error(self, error_message):
        """Handle generation error"""
        QMessageBox.critical(self, "Generation Error",
                             f"Failed to generate audio: {error_message}")

    def _extract_section(self, composition_text, section_name):
        """Extract a specific section from the composition text"""
        section_marker = f"## {section_name.upper()}"
        if section_marker in composition_text:
            section = composition_text.split(section_marker)[1].split("##")[0]
            return section.strip()
        return ""

    def _extract_lyrics(self, composition_text):
        return self._extract_section(composition_text, "LYRICS")

    def _extract_chords(self, composition_text):
        return self._extract_section(composition_text, "CHORD PROGRESSION")

    def handle_audio_output(self, audio_path: str):
        """Handle the generated audio file"""
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(
                    f"Generated audio file not found at {audio_path}")

            # We need to load this in audio_controls
            if self.audio_controls.load_audio(audio_path):
                self.audio_controls.play_button.click()  # Start playing
            else:
                QMessageBox.warning(self, "Error", "Failed to load audio file")

        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Audio playback failed: {str(e)}")
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

    def create_export_buttons(self, layout):
        """Create export buttons for JSON and TXT formats"""
        export_layout = QHBoxLayout()

        export_label = QLabel("Export Composition:")
        export_layout.addWidget(export_label)

        self.export_json_button = QPushButton('Export to JSON')
        self.export_json_button.setIcon(
            self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.export_json_button.clicked.connect(self.export_to_json)

        self.export_txt_button = QPushButton('Export to TXT')
        self.export_txt_button.setIcon(
            self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.export_txt_button.clicked.connect(self.export_to_txt)

        export_layout.addWidget(self.export_json_button)
        export_layout.addWidget(self.export_txt_button)
        layout.addLayout(export_layout)

    def export_to_json(self):
        """Handle JSON export"""
        try:
            filepath, _ = QFileDialog.getSaveFileName(
                self, 'Save JSON File', '', 'JSON Files (*.json)'
            )

            if filepath:
                composition_text = self.full_composition_field.toPlainText()
                self.MusicExportFormatter.export_to_json(composition_text, filepath)
                QMessageBox.information(
                    self, "Success", "Song exported to JSON successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Export Error",
                                 f"Failed to export to JSON: {str(e)}")

    def export_to_txt(self):
        """Handle TXT export"""
        try:
            filepath, _ = QFileDialog.getSaveFileName(
                self, 'Save Text File', '', 'Text Files (*.txt)'
            )

            if filepath:
                composition_text = self.full_composition_field.toPlainText()
                self.MusicExportFormatter.export_to_txt(composition_text, filepath)
                QMessageBox.information(
                    self, "Success", "Song exported to TXT successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Export Error",
                                 f"Failed to export to TXT: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    interface = ModernInterface()
    interface.show()
    sys.exit(app.exec_())
