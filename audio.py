import os
import pyttsx3
from config import Config


class AudioGenerator:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 145)

        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "EN" in voice.id.upper() or "ENGLISH" in voice.id.upper():
                self.engine.setProperty('voice', voice.id)
                break

    def text_to_file(self, text: str, filename: str) -> str:
        """Converts text directly to an audio file inside the web static folder."""
        Config.ensure_dirs()
        output_path = os.path.join(Config.AUDIO_FOLDER, filename)

        try:
            # Delete file if it exists to overwrite cleanly
            if os.path.exists(output_path):
                os.remove(output_path)

            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            return output_path
        except Exception as e:
            raise RuntimeError(f"Audio Engine failed: {e}")