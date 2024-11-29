import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QCheckBox, QComboBox, QVBoxLayout, QPushButton,
                             QHBoxLayout, QFrame, QMessageBox, QTextEdit, QScrollArea)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

# Importation de notre module d'intégration ChatGPT
from llm_integration import LLMIntegration
from llm_integration2 import LLMIntegration2

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
            music_composer = LLMIntegration2()
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
        self.dark_mode = False
        self.streaming_thread = None
        self.initUI()

    def initUI(self):
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
        # self.create_lyrics_section(content_layout)
        # self.create_song_structure_section(content_layout)
        # self.create_chord_progression_section(content_layout)
        self.create_buttons(content_layout)
        # Add a new method to create full composition section
        self.create_full_composition_section(content_layout)

        scroll_area.setWidget(content_frame)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        self.apply_dark_theme()
        self.initialize_llm()

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

    # def create_lyrics_section(self, layout):
    #     lyrics_label = QLabel('Paroles de Chanson Générées')
    #     lyrics_label.setStyleSheet("""
    #         font-weight: bold;
    #         margin-bottom: 5px;
    #     """)
    #
    #     self.lyrics_field = QTextEdit()
    #     self.lyrics_field.setReadOnly(True)
    #     self.lyrics_field.setPlaceholderText('Les paroles de la chanson seront générées ici')
    #
    #     lyrics_layout = QVBoxLayout()
    #     lyrics_layout.addWidget(lyrics_label)
    #     lyrics_layout.addWidget(self.lyrics_field)
    #
    #     layout.addLayout(lyrics_layout)

    # def create_song_structure_section(self, layout):
    #     structure_label = QLabel('Structure de Chanson Générée')
    #     structure_label.setStyleSheet("""
    #         font-weight: bold;
    #         margin-bottom: 5px;
    #     """)
    #
    #     self.structure_field = QTextEdit()
    #     self.structure_field.setReadOnly(True)
    #     self.structure_field.setPlaceholderText('La structure de la chanson sera générée ici')
    #
    #     structure_layout = QVBoxLayout()
    #     structure_layout.addWidget(structure_label)
    #     structure_layout.addWidget(self.structure_field)
    #
    #     layout.addLayout(structure_layout)

    # def create_chord_progression_section(self, layout):
    #     chords_label = QLabel('Progression d\'Accords Générée')
    #     chords_label.setStyleSheet("""
    #         font-weight: bold;
    #         margin-bottom: 5px;
    #     """)
    #
    #     self.chords_field = QTextEdit()
    #     self.chords_field.setReadOnly(True)
    #     self.chords_field.setPlaceholderText('La progression d\'accords sera générée ici')
    #
    #     chords_layout = QVBoxLayout()
    #     chords_layout.addWidget(chords_label)
    #     chords_layout.addWidget(self.chords_field)
    #
    #     layout.addLayout(chords_layout)

    def create_full_composition_section(self, layout):
        full_composition_label = QLabel('Composition Complète Générée')
        full_composition_label.setStyleSheet("""
            font-weight: bold;
            margin-bottom: 5px;
        """)

        self.full_composition_field = QTextEdit()
        self.full_composition_field.setReadOnly(True)
        self.full_composition_field.setPlaceholderText('La composition complète sera générée ici')

        full_composition_layout = QVBoxLayout()
        full_composition_layout.addWidget(full_composition_label)
        full_composition_layout.addWidget(self.full_composition_field)

        layout.addLayout(full_composition_layout)

    def create_buttons(self, layout):
        # self.bouton_generer_lyrics = QPushButton('Générer Paroles de Chanson')
        # self.bouton_generer_lyrics.clicked.connect(self.generer_lyrics)
        # layout.addWidget(self.bouton_generer_lyrics)
        #
        # self.bouton_generer_structure = QPushButton('Générer Structure de Chanson')
        # self.bouton_generer_structure.clicked.connect(self.generer_song_structure)
        # layout.addWidget(self.bouton_generer_structure)
        #
        # self.bouton_generer_chords = QPushButton('Générer Progression d\'Accords')
        # self.bouton_generer_chords.clicked.connect(self.generer_chord_progression)
        # layout.addWidget(self.bouton_generer_chords)
        #
        # self.checkbox = QCheckBox('J\'accepte les conditions')
        # self.checkbox.setStyleSheet("""
        #     margin-top: 10px;
        #     margin-bottom: 10px;
        # """)
        # layout.addWidget(self.checkbox)
        #
        # liste_label = QLabel('Sélectionnez une option')
        # liste_label.setStyleSheet('font-weight: bold;')
        # self.liste_deroulante = QComboBox()
        # self.liste_deroulante.addItems(['Option 1', 'Option 2', 'Option 3'])
        #
        # layout.addWidget(liste_label)
        # layout.addWidget(self.liste_deroulante)
        #
        # bouton_layout = QHBoxLayout()
        # self.bouton_valider = QPushButton('Valider')
        # self.bouton_valider.clicked.connect(self.valider)

        self.bouton_mode = QPushButton('🌙 Mode Sombre')
        self.bouton_mode.clicked.connect(self.toggle_theme)

        # bouton_layout.addWidget(self.bouton_valider)
        # bouton_layout.addWidget(self.bouton_mode)

        # layout.addLayout(bouton_layout)

        # Add full composition button to the existing button creation method
        self.bouton_generer_composition = QPushButton('Générer Composition Complète')
        self.bouton_generer_composition.clicked.connect(self.generer_full_composition)
        layout.addWidget(self.bouton_generer_composition)

    def initialize_llm(self):
        try:
            self.chatgpt_integration = LLMIntegration2()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur de Configuration", str(e))

    def generer_lyrics(self):
        # Récupérer les informations nécessaires
        musicalStyle = self.text_fields[0].text()
        songTheme = self.text_fields[1].text()
        mood = self.text_fields[2].text()
        language = self.text_fields[3].text()

        # Vérifier que les champs ne sont pas vides
        if not musicalStyle or not songTheme or not mood or not language:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs nécessaires")
            return

        # Réinitialiser le champ de lyrics
        self.lyrics_field.clear()

        # Arrêter tout thread de streaming précédent
        if self.streaming_thread and self.streaming_thread.isRunning():
            self.streaming_thread.terminate()

        # Créer et lancer un nouveau thread de streaming
        self.streaming_thread = StreamThread('generate_lyrics', musicalStyle, songTheme, mood, language)
        self.streaming_thread.chunk_ready.connect(self.update_lyrics_streaming)
        self.streaming_thread.stream_complete.connect(self.on_stream_complete)
        self.streaming_thread.start()

    def generer_song_structure(self):
        # Récupérer les informations nécessaires
        musicalStyle = self.text_fields[0].text()
        songTheme = self.text_fields[1].text()
        mood = self.text_fields[2].text()
        language = self.text_fields[3].text()

        # Vérifier que les champs ne sont pas vides
        if not musicalStyle or not songTheme or not mood or not language:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs nécessaires")
            return

        # Réinitialiser le champ de structure
        self.structure_field.clear()

        # Arrêter tout thread de streaming précédent
        if self.streaming_thread and self.streaming_thread.isRunning():
            self.streaming_thread.terminate()

        # Créer et lancer un nouveau thread de streaming
        self.streaming_thread = StreamThread('generate_song_structure', musicalStyle, songTheme, mood, language)
        self.streaming_thread.chunk_ready.connect(self.update_structure_streaming)
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
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs nécessaires")
            return

        # Réinitialiser le champ de chords
        self.chords_field.clear()

        # Arrêter tout thread de streaming précédent
        if self.streaming_thread and self.streaming_thread.isRunning():
            self.streaming_thread.terminate()

        # Créer et lancer un nouveau thread de streaming
        self.streaming_thread = StreamThread('generate_chord_progression', musicalStyle, songTheme, mood, language)
        self.streaming_thread.chunk_ready.connect(self.update_chords_streaming)
        self.streaming_thread.stream_complete.connect(self.on_stream_complete)
        self.streaming_thread.start()

    def generer_full_composition(self):
        # Récupérer les informations nécessaires
        musicalStyle = self.text_fields[0].text()
        songTheme = self.text_fields[1].text()
        mood = self.text_fields[2].text()
        language = self.text_fields[3].text()

        # Vérifier que les champs ne sont pas vides
        if not musicalStyle or not songTheme or not mood or not language:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs nécessaires")
            return

        # Réinitialiser le champ de composition complète
        self.full_composition_field.clear()

        # Arrêter tout thread de streaming précédent
        if self.streaming_thread and self.streaming_thread.isRunning():
            self.streaming_thread.terminate()

        # Créer et lancer un nouveau thread de streaming
        self.streaming_thread = StreamThread('generate_song_composition', musicalStyle, songTheme, mood, language)
        self.streaming_thread.chunk_ready.connect(self.update_full_composition_streaming)
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
            msg.setInformativeText("\n".join([f"{k}: {v}" for k, v in resultats.items()]))
            msg.setWindowTitle("Succès")
            msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    interface = ModernInterface()
    interface.show()
    sys.exit(app.exec_())
