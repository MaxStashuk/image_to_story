# Image-to-story processor
Program that is designed to create a narrated stories, based on context within images.
There's a possibility to have stories with different flavors.

## Utilized stack
1. Python 3.13.13
2. [BLIP 2](https://huggingface.co/docs/transformers/en/model_doc/blip) - for extracting context from the image
3. Ollama 3.2 for story writing.
4. Pyttsx3 - Text to Speech (TTS) library for Python 3.
5. Flask - local web view for the tool

## Prerequisites

1. Clone the repository on your local machine
2. run ```pip install -r requirements.txt``` to downloaded dependencies 
3. Install Ollama from official [website](https://ollama.com/)
4. Install Llama 3.2 by running ```ollama pull llama3.2```