import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QCheckBox, QComboBox, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QFrame, QMessageBox, QTextEdit)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

# Importation de notre module d'intégration ChatGPT
from chatgpt_integration import ChatGPTIntegration

class StreamThread(QThread):
    """Thread pour gérer le streaming de ChatGPT"""
    chunk_ready = pyqtSignal(str)
    stream_complete = pyqtSignal()
    
    def __init__(self, nom, prenom):
        super().__init__()
        self.nom = nom
        self.prenom = prenom
    
    def run(self):
        try:
            chatgpt = ChatGPTIntegration()
            stream = chatgpt.generate_description(self.nom, self.prenom)
            
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
    
    # [Le reste de votre méthode initUI() reste identique]
    
    def generer_description(self):
        # Récupérer le nom et prénom
        nom = self.text_fields[0].text()
        prenom = self.text_fields[1].text()
        
        # Vérifier que les champs ne sont pas vides
        if not nom or not prenom:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir le nom et le prénom")
            return
        
        # Réinitialiser le champ de description
        self.description_field.clear()
        
        # Arrêter tout thread de streaming précédent
        if self.streaming_thread and self.streaming_thread.isRunning():
            self.streaming_thread.terminate()
        
        # Créer et lancer un nouveau thread de streaming
        self.streaming_thread = StreamThread(nom, prenom)
        self.streaming_thread.chunk_ready.connect(self.update_description_streaming)
        self.streaming_thread.stream_complete.connect(self.on_stream_complete)
        self.streaming_thread.start()
    
    def update_description_streaming(self, chunk):
        # Ajouter le nouveau morceau au texte existant
        current_text = self.description_field.toPlainText()
        self.description_field.setText(current_text + chunk)
        
        # Faire défiler automatiquement vers le bas
        self.description_field.verticalScrollBar().setValue(
            self.description_field.verticalScrollBar().maximum()
        )
    
    def on_stream_complete(self):
        # Vous pouvez ajouter un traitement supplémentaire une fois le streaming terminé
        pass

        
    def initUI(self):
        # Configuration de la fenêtre
        self.setWindowTitle('Application Moderne')
        self.setGeometry(100, 100, 500, 700)
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Frame pour un effet de conteneur
        frame = QFrame()
        frame.setObjectName('mainFrame')
        
        # CORRECTION : Création du frame_layout
        frame_layout = QVBoxLayout()
        
        # Titre
        titre = QLabel('Formulaire de Saisie')
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            margin-bottom: 20px;
        """)
        frame_layout.addWidget(titre)
        
        # Champs de texte avec labels élégants
        def create_input_section(label_text):
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
        
        # Créer les champs de texte
        text_layouts = []
        self.text_fields = []
        for label in ['Nom', 'Prénom', 'Email']:
            layout, field = create_input_section(label)
            text_layouts.append(layout)
            self.text_fields.append(field)
        
        # Ajouter les champs de texte au layout
        for layout in text_layouts:
            frame_layout.addLayout(layout)
        
        # Description ChatGPT
        description_label = QLabel('Description générée')
        description_label.setStyleSheet("""
            font-weight: bold; 
            margin-bottom: 5px;
        """)
        
        self.description_field = QTextEdit()
        self.description_field.setReadOnly(True)
        self.description_field.setPlaceholderText('La description sera générée ici')
        
        # Bouton pour générer la description
        self.bouton_generer = QPushButton('Générer Description')
        self.bouton_generer.clicked.connect(self.generer_description)
        frame_layout.addWidget(self.bouton_generer)
        frame_layout.addWidget(description_label)
        frame_layout.addWidget(self.description_field)
        
        # Checkbox
        self.checkbox = QCheckBox('J\'accepte les conditions')
        self.checkbox.setStyleSheet("""
            margin-top: 10px;
            margin-bottom: 10px;
        """)
        frame_layout.addWidget(self.checkbox)
        
        # Liste déroulante
        liste_label = QLabel('Sélectionnez une option')
        liste_label.setStyleSheet('font-weight: bold;')
        self.liste_deroulante = QComboBox()
        self.liste_deroulante.addItems(['Option 1', 'Option 2', 'Option 3'])
        
        frame_layout.addWidget(liste_label)
        frame_layout.addWidget(self.liste_deroulante)
        
        # Boutons
        bouton_layout = QHBoxLayout()
        
        # Bouton de validation
        self.bouton_valider = QPushButton('Valider')
        self.bouton_valider.clicked.connect(self.valider)
        
        # Bouton de mode sombre
        self.bouton_mode = QPushButton('🌙 Mode Sombre')
        self.bouton_mode.clicked.connect(self.toggle_theme)
        
        bouton_layout.addWidget(self.bouton_valider)
        bouton_layout.addWidget(self.bouton_mode)
        
        frame_layout.addLayout(bouton_layout)
        
        # Appliquer le layout au frame
        frame.setLayout(frame_layout)
        
        # Ajouter le frame au layout principal
        main_layout.addWidget(frame)
        self.setLayout(main_layout)
        
        # Appliquer le style initial (mode clair)
        self.apply_light_theme()
        
        # Initialiser l'intégration ChatGPT
        try:
            self.chatgpt_integration = ChatGPTIntegration()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur de Configuration", str(e))
    
    # def generer_description(self):
    #     # Récupérer le nom et prénom
    #     nom = self.text_fields[0].text()
    #     prenom = self.text_fields[1].text()
        
    #     # Vérifier que les champs ne sont pas vides
    #     if not nom or not prenom:
    #         QMessageBox.warning(self, "Erreur", "Veuillez remplir le nom et le prénom")
    #         return
        
    #     # Lancer le thread pour l'appel à ChatGPT
    #     self.chatgpt_thread = StreamThread(nom, prenom)
    #     self.chatgpt_thread.chunk_ready.connect(self.update_description)
    #     self.chatgpt_thread.start()
    
    # def update_description(self, description):
    #     # Mettre à jour le champ de description
    #     self.description_field.setText(description)

    # [Autres méthodes de la classe originale : toggle_theme, apply_dark_theme, apply_light_theme, valider restent identiques]
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
        
        for i, champ in enumerate(['Nom', 'Prénom', 'Email']):
            if not self.text_fields[i].text():
                erreurs.append(f"Le champ {champ} est obligatoire.")
        
        if not self.checkbox.isChecked():
            erreurs.append("Vous devez accepter les conditions.")
        
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
                'Nom': self.text_fields[0].text(),
                'Prénom': self.text_fields[1].text(),
                'Email': self.text_fields[2].text(),
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