def apply_dark_theme(widget):
    # Mode sombre personnalisé
    widget.setStyleSheet("""
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
    widget.bouton_mode.setText('☀️ Mode Clair')

def apply_light_theme(widget):
    # Mode clair personnalisé
    widget.setStyleSheet("""
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
    widget.bouton_mode.setText('🌙 Mode Sombre')