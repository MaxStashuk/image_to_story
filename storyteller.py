import ollama
from config import Config


class Storyteller:
    def __init__(self):
        self.model_name = Config.OLLAMA_STORY_MODEL

    def generate_story(self, caption: str, flavor: str, length_setting: str) -> str:
        """Generates a story based on a caption, flavor, and requested length."""
        if flavor.lower() not in Config.VALID_FLAVORS:
            raise ValueError(f"Unsupported flavor '{flavor}'.")

        lengths = Config.LENGTH_MAPPING.get(length_setting.lower(), Config.LENGTH_MAPPING["medium"])
        prompt = self._build_prompt(caption, flavor, lengths["min"], lengths["max"])

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama Storyteller failed: {e}")

    def _build_prompt(self, caption: str, flavor: str, min_w: int, max_w: int) -> str:
        return f"""You are a master novelist. I will provide a brief scene description. 
                    Using that description as your central creative seed, write a compelling {flavor} story.
                    
                    STRICT CONSTRAINTS:
                    1. The story MUST be between {min_w} and {max_w} words long. Do not write a single word more than {max_w} words.
                    2. The language must be {Config.LANGUAGE}.
                    3. Fully lean into the tropes and pacing of a classic {flavor}.
                    
                    Scene Description:
                    {caption}
                    
                    Story:"""