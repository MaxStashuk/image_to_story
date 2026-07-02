from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from config import Config


class VisionAnalyzer:
    def __init__(self):
        print("Initializing BLIP Vision Analyzer...")
        self.processor = BlipProcessor.from_pretrained(Config.BLIP_MODEL_NAME)
        self.model = BlipForConditionalGeneration.from_pretrained(Config.BLIP_MODEL_NAME)

    def extract_caption(self, image_path: str) -> str:
        """Reads an image from disk and returns a literal text caption."""
        try:
            raw_image = Image.open(image_path).convert('RGB')
            inputs = self.processor(raw_image, return_tensors="pt")

            # Generate the token ids
            out = self.model.generate(**inputs, max_new_tokens=50)

            # Decode token ids back to readable text
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            raise RuntimeError(f"Vision Engine failed to process image: {e}")