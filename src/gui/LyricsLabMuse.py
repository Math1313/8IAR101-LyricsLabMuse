# src/gui/LyricsLabMuse.py
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QVBoxLayout, QPushButton,
                             QFrame, QMessageBox, QTextEdit, QScrollArea)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

import sys

# Importation de notre module d'intégration ChatGPT
from src.core.music_composition_experts import MusicCompositionExperts
from src.core import rag_helper as RagHelper
from src.core.music_composition_export_formatter import MusicCompositionExportFormatter
from audio_generation.audiocraft_generator import FullSongGenerator
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


class ModernInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.song_generator = FullSongGenerator()
        self.media_player = QMediaPlayer()
        self.dark_mode = False
        self.streaming_thread = None
        self.audio_controls = None
        self.initUI()

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

        # Add full composition button to the existing button creation method
        self.bouton_generer_composition = QPushButton(
            'Générer Composition Complète')
        self.bouton_generer_composition.clicked.connect(
            self.generer_full_composition)
        layout.addWidget(self.bouton_generer_composition)

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
        # Récupérer les informations nécessaires
        musicalStyle = self.text_fields[0].text()
        songTheme = self.text_fields[1].text()
        mood = self.text_fields[2].text()
        language = self.text_fields[3].text()
        structure = RagHelper.query_rag(
            self.chatgpt_integration.llm, musicalStyle
        )

        # Vérifier que les champs ne sont pas vides
        if not musicalStyle or not songTheme or not mood or not language:
            QMessageBox.warning(
                self, "Erreur", "Veuillez remplir tous les champs nécessaires")
            return

        # Réinitialiser le champ de structure
        self.structure_field.clear()

        # Arrêter tout thread de streaming précédent
        if self.streaming_thread and self.streaming_thread.isRunning():
            self.streaming_thread.terminate()

        # Créer et lancer un nouveau thread de streaming
        self.streaming_thread = StreamThread(
            'generate_song_structure', musicalStyle, structure, songTheme, mood, language)
        self.streaming_thread.chunk_ready.connect(
            self.update_structure_streaming)
        self.streaming_thread.stream_complete.connect(self.on_stream_complete)
        self.streaming_thread.start()

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
        # Récupérer les informations nécessaires
        musicalStyle = self.text_fields[0].text()
        songTheme = self.text_fields[1].text()
        mood = self.text_fields[2].text()
        language = self.text_fields[3].text()
        structure = RagHelper.query_rag(
            self.chatgpt_integration.llm, musicalStyle
        )

        # Vérifier que les champs ne sont pas vides
        if not musicalStyle or not songTheme or not mood or not language:
            QMessageBox.warning(
                self, "Erreur", "Veuillez remplir tous les champs nécessaires")
            return

        # Réinitialiser le champ de composition complète
        self.full_composition_field.clear()

        # Arrêter tout thread de streaming précédent
        if self.streaming_thread and self.streaming_thread.isRunning():
            self.streaming_thread.terminate()

        # Créer et lancer un nouveau thread de streaming
        self.streaming_thread = StreamThread(
            'generate_song_composition', musicalStyle, structure, songTheme, mood, language)
        self.streaming_thread.chunk_ready.connect(
            self.update_full_composition_streaming)
        self.streaming_thread.stream_complete.connect(self.on_stream_complete)
        self.streaming_thread.start()

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
        try:
            # Get current text from fields
            musical_style = self.text_fields[0].text()
            song_theme = self.text_fields[1].text()
            mood = self.text_fields[2].text()
            language = self.text_fields[3].text()

            if not all([musical_style, song_theme, mood, language]):
                raise ValueError("All fields must be filled")

            composition_data = self.chatgpt_integration.generate_song_composition(
                musical_style, song_theme, mood, language
            )

            formatter = MusicCompositionExportFormatter()
            formatted_data = formatter.generate_audio_export_metadata(
                composition_data.get('lyrics', ''),
                composition_data.get('chord_progression', ''),
                composition_data.get('structure', ''),
                musical_style,
                mood
            )

            result = self.song_generator.generate_full_song(formatted_data)
            self.handle_audio_output(result["instrumental"])

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Audio Generation Error",
                               f"Failed to generate audio: {str(e)}")

    def handle_audio_output(self, audio_path: str):
        try:
            if self.audio_controls.load_audio(audio_path):
                self.audio_controls.play_button.click()
            else:
                QMessageBox.warning(self, "Error", "Failed to load audio file")
        except Exception as e:
            QMessageBox.critical(self, "Audio Playback Error",
                               f"Failed to play audio: {str(e)}")

    def setup_audio(self, layout):
        """Initialize and setup audio controls"""
        self.audio_controls = AudioControls(self)
        layout.addWidget(self.audio_controls)

    def handle_audio_output(self, audio_path: str):
        """Handle the generated audio file"""
        try:
            if self.audio_controls.load_audio(audio_path):
                self.audio_controls.play_button.click()  # Start playing
            else:
                QMessageBox.warning(self, "Error", "Failed to load audio file")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Audio playback failed: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    interface = ModernInterface()
    interface.show()
    sys.exit(app.exec_())
