# src/component/ui/audio_controls.py
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QPushButton,
                             QSlider, QLabel, QStyle, QWidget, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import os


class AudioControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_player()

    def setup_ui(self):
        """Create and setup the UI elements"""
        # Main layout
        main_layout = QVBoxLayout()

        # Controls layout
        controls_layout = QHBoxLayout()

        # Create buttons using system icons
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_pause)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.clicked.connect(self.stop)

        self.mute_button = QPushButton()
        self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.mute_button.clicked.connect(self.mute)

        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.volume_changed)

        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.sliderMoved.connect(self.set_position)

        # Time labels
        self.time_label = QLabel("0:00 / 0:00")

        # Create save button using system icon
        self.save_button = QPushButton()
        self.save_button.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_button.clicked.connect(self.save_audio)


        # Add widgets to controls layout
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.mute_button)
        controls_layout.addWidget(self.volume_slider)
        # Add save button to controls layout
        controls_layout.addWidget(self.save_button)

        # Add layouts to main layout
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.progress_slider)
        main_layout.addWidget(self.time_label)

        self.setLayout(main_layout)

    def setup_player(self):
        """Setup media player and connections"""
        self.player = QMediaPlayer()
        self.player.stateChanged.connect(self.update_player_state)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)

        # Update timer for smooth progress bar
        self.update_timer = QTimer()
        self.update_timer.setInterval(1000)  # Update every second
        self.update_timer.timeout.connect(self.update_progress)

    def play_pause(self):
        """Toggle play/pause state"""
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.update_timer.stop()
        else:
            self.player.play()
            self.update_timer.start()

    def stop(self):
        """Stop playback"""
        self.player.stop()
        self.update_timer.stop()
        self.progress_slider.setValue(0)

    def mute(self):
        """Toggle mute state"""
        is_muted = self.player.isMuted()
        self.player.setMuted(not is_muted)
        self.mute_button.setIcon(
            self.style().standardIcon(
                QStyle.SP_MediaVolumeMuted if not is_muted else QStyle.SP_MediaVolume
            )
        )

    def volume_changed(self, value):
        """Handle volume slider changes"""
        self.player.setVolume(value)

    def set_position(self, position):
        """Set playback position from slider"""
        self.player.setPosition(position)

    def position_changed(self, position):
        """Update slider position during playback"""
        self.progress_slider.setValue(position)
        self.update_time_label(position)

    def duration_changed(self, duration):
        """Update slider range when media duration is known"""
        self.progress_slider.setRange(0, duration)
        self.update_time_label(0)

    def update_progress(self):
        """Update progress bar during playback"""
        position = self.player.position()
        self.progress_slider.setValue(position)
        self.update_time_label(position)

    def update_time_label(self, position):
        """Update time label with current/total duration"""
        duration = self.player.duration()

        current = self.format_time(position)
        total = self.format_time(duration)
        self.time_label.setText(f"{current} / {total}")

    def update_player_state(self, state):
        """Update button icons based on player state"""
        if state == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    @staticmethod
    def format_time(ms):
        """Format milliseconds as MM:SS"""
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m}:{s:02d}"

    def load_audio(self, audio_path: str):
        """Load and prepare audio file for playback"""
        try:
            self.current_audio_path = audio_path
            self.player.setMedia(
                QMediaContent(QUrl.fromLocalFile(audio_path))
            )
            return True
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False

    def save_audio(self):
        """Save current audio to user-selected location"""
        try:
            if not hasattr(self, 'current_audio_path'):
                QMessageBox.warning(self, "Error", "No audio loaded to save")
                return

            file_name = QFileDialog.getSaveFileName(
                self,
                "Save Audio File",
                os.path.expanduser("~/Music"),  # Default to Music directory
                "Audio Files (*.wav);;All Files (*)"
            )[0]

            if file_name:
                # Copy the file to new location
                import shutil
                shutil.copy2(self.current_audio_path, file_name)
                QMessageBox.information(self, "Success", "Audio saved successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save audio: {str(e)}")