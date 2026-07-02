import os

class Config:
    BLIP_MODEL_NAME = "Salesforce/blip-image-captioning-base"
    OLLAMA_STORY_MODEL = "llama3.2"
    LANGUAGE = "English"

    VALID_FLAVORS = ["fairy tale", "thriller", "romance", "science fiction"]

    # Map friendly UI lengths to specific word limits
    LENGTH_MAPPING = {
        "short": {"min": 150, "max": 200},  # ~1 to 1.5 minutes of audio
        "medium": {"min": 300, "max": 400},  # ~2 to 3 minutes of audio
        "long": {"min": 450, "max": 500}  # ~3.5 to 4 minutes of audio
    }

    # Web directories
    STATIC_DIR = "static"
    UPLOAD_FOLDER = os.path.join(STATIC_DIR, "uploads")
    AUDIO_FOLDER = os.path.join(STATIC_DIR, "audio")

    @classmethod
    def ensure_dirs(cls):
        """Ensures directories exist for web assets."""
        for folder in [cls.UPLOAD_FOLDER, cls.AUDIO_FOLDER]:
            if not os.path.exists(folder):
                os.makedirs(folder)