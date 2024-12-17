from src.core.music_composition_experts import MusicCompositionExperts
from PyQt5.QtCore import QThread, pyqtSignal

class AudioGenerationThread(QThread):
    progress_updated = pyqtSignal(int, str)
    generation_complete = pyqtSignal(dict)
    generation_error = pyqtSignal(str)

    def __init__(self, song_generator, formatted_data):
        super().__init__()
        self.song_generator = song_generator
        self.formatted_data = formatted_data
        # Get estimated time from generator
        self.ESTIMATED_GENERATION_TIME = self.song_generator._estimate_generation_time(
            formatted_data)

    def run(self):
        try:
            # Start progress tracking thread
            self.progress_thread = ProgressUpdateThread(
                self.ESTIMATED_GENERATION_TIME)
            self.progress_thread.progress_updated.connect(
                self.handle_progress_update)
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

            message = f"""Generating audio... Estimated time remaining:
            {minutes}m {seconds}s"""
            self.progress_updated.emit(progress, message)

            time.sleep(1)  # Update every second

    def stop(self):
        self.running = False
