# app.py
import os
import time
from flask import Flask, request, jsonify, render_template_string
from config import Config
from vision import VisionAnalyzer
from storyteller import Storyteller
from audio import AudioGenerator

app = Flask(__name__)
Config.ensure_dirs()

# Initialize our clean backend modules once when server starts
vision_engine = VisionAnalyzer()
story_engine = Storyteller()
audio_engine = AudioGenerator()

# Single-page HTML interface template with custom progress tracking bars
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Story Multimodal Demo</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #f4f6f9; color: #333; }
        .container { background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { margin-top: 0; color: #1a1a1a; text-align: center; }

        /* Drag and Drop Styling */
        #drop-zone { border: 2px dashed #cbd5e1; border-radius: 8px; padding: 40px; text-align: center; background: #f8fafc; cursor: pointer; transition: 0.3s; margin-bottom: 20px; }
        #drop-zone.hover { border-color: #3b82f6; background: #eff6ff; }
        #preview { max-width: 100%; max-height: 300px; display: none; margin: 15px auto; border-radius: 6px; }

        .controls { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        label { font-weight: 600; display: block; margin-bottom: 5px; font-size: 14px; }
        select, button { width: 100%; padding: 12px; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 16px; }
        button { background: #3b82f6; color: white; border: none; cursor: pointer; font-weight: bold; margin-top: 10px; transition: 0.2s; }
        button:hover { background: #2563eb; }
        button:disabled { background: #94a3b8; cursor: not-allowed; }

        /* Progress Bar Styling */
        #loading-container { display: none; margin: 25px 0; background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; }
        .progress-group { margin-bottom: 15px; }
        .progress-group:last-child { margin-bottom: 0; }
        .progress-label { display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 6px; }
        .progress-track { background: #e2e8f0; border-radius: 10px; height: 12px; overflow: hidden; position: relative; }
        .progress-fill { background: #3b82f6; height: 100%; width: 0%; transition: width 0.4s ease; }
        .progress-fill.active { background: repeating-linear-gradient(45deg, #3b82f6, #3b82f6 10px, #60a5fa 10px, #60a5fa 20px); background-size: 28px 28px; animation: progress-bar-stripes 1s linear infinite; }

        @keyframes progress-bar-stripes {
            0% { background-position: 0 0; }
            100% { background-position: 28px 0; }
        }

        .result-box { margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; display: none; }
        audio { width: 100%; margin: 15px 0; }
        .story-text { background: #f8fafc; padding: 15px; border-radius: 6px; border-left: 4px solid #3b82f6; white-space: pre-wrap; font-style: italic; max-height: 300px; overflow-y: auto; }
    </style>
</head>
<body>

<div class="container">
    <h1>Multimodal Story Generator</h1>

    <div id="drop-zone">
        <p id="drop-text">Drag & drop an image here or click to browse</p>
        <input type="file" id="file-input" accept="image/*" style="display: none;">
        <img id="preview" alt="Image preview">
    </div>

    <div class="controls">
        <div>
            <label for="flavor">Story Flavor:</label>
            <select id="flavor">
                <option value="science fiction">Science Fiction</option>
                <option value="thriller">Thriller</option>
                <option value="fairy tale">Fairy Tale</option>
                <option value="romance">Romance</option>
            </select>
        </div>
        <div>
            <label for="length">Target Duration:</label>
            <select id="length">
                <option value="short">Short (~1.5 min)</option>
                <option value="medium" selected>Medium (~2.5 min)</option>
                <option value="long">Long (Max 4 min)</option>
            </select>
        </div>
    </div>

    <button id="generate-btn" disabled>Generate Story & Audio</button>

    <div id="loading-container">
        <div class="progress-group">
            <div class="progress-label"><span id="lbl-vision">1. Vision Recognition</span><span id="pct-vision">0%</span></div>
            <div class="progress-track"><div id="bar-vision" class="progress-fill"></div></div>
        </div>
        <div class="progress-group">
            <div class="progress-label"><span id="lbl-text">2. Creative Text Writing</span><span id="pct-text">0%</span></div>
            <div class="progress-track"><div id="bar-text" class="progress-fill"></div></div>
        </div>
        <div class="progress-group">
            <div class="progress-label"><span id="lbl-audio">3. Text-to-Speech Generation</span><span id="pct-audio">0%</span></div>
            <div class="progress-track"><div id="bar-audio" class="progress-fill"></div></div>
        </div>
    </div>

    <div class="result-box" id="result-box">
        <h3>Image Description Extracted:</h3>
        <p id="result-caption" style="font-weight: 500; color: #475569;"></p>

        <h3>Listen to Story:</h3>
        <audio id="audio-player" controls></audio>

        <h3>Generated Story Text:</h3>
        <div class="story-text" id="story-text"></div>
    </div>
</div>

<script>
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const preview = document.getElementById('preview');
    const dropText = document.getElementById('drop-text');
    const generateBtn = document.getElementById('generate-btn');
    const loadingContainer = document.getElementById('loading-container');
    const resultBox = document.getElementById('result-box');

    let selectedFile = null;

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('hover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('hover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('hover');
        if(e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', (e) => {
        if(e.target.files.length) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) return alert('Please upload an image file.');
        selectedFile = file;
        dropText.style.display = 'none';

        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.style.display = 'block';
        }
        reader.readAsDataURL(file);
        generateBtn.disabled = false;
    }

    // Helper functions to manage visual states of progress tracks
    function updateBar(barId, pctId, percentage, isActive=false) {
        const bar = document.getElementById(barId);
        const text = document.getElementById(pctId);
        bar.style.width = percentage + '%';
        text.innerText = percentage + '%';
        if (isActive) {
            bar.classList.add('active');
        } else {
            bar.classList.remove('active');
        }
    }

    function resetBars() {
        updateBar('bar-vision', 'pct-vision', 0);
        updateBar('bar-text', 'pct-text', 0);
        updateBar('bar-audio', 'pct-audio', 0);
    }

    // Pipeline Execution
    generateBtn.addEventListener('click', async () => {
        if(!selectedFile) return;

        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('flavor', document.getElementById('flavor').value);
        formData.append('length', document.getElementById('length').value);

        // Reset UI states
        resetBars();
        loadingContainer.style.display = 'block';
        resultBox.style.display = 'none';
        generateBtn.disabled = true;

        // Phase 1 Simulation Start: Vision Engine is usually fast (1-3s)
        updateBar('bar-vision', 'pct-vision', 45, true);
        let currentVision = 45;
        const visionInterval = setInterval(() => {
            if (currentVision < 90) {
                currentVision += 5;
                updateBar('bar-vision', 'pct-vision', currentVision, true);
            }
        }, 300);

        try {
            const response = await fetch('/generate', { method: 'POST', body: formData });
            clearInterval(visionInterval);

            const data = await response.json();

            if(data.success) {
                // Complete all stages sequentially to mimic continuous success
                updateBar('bar-vision', 'pct-vision', 100, false);

                // Animate Text Engine completing
                updateBar('bar-text', 'pct-text', 50, true);
                await new Promise(r => setTimeout(r, 600));
                updateBar('bar-text', 'pct-text', 100, false);

                // Animate Audio Engine completing
                updateBar('bar-audio', 'pct-audio', 60, true);
                await new Promise(r => setTimeout(r, 600));
                updateBar('bar-audio', 'pct-audio', 100, false);

                // Render Final Output Objects
                document.getElementById('result-caption').innerText = data.caption;
                document.getElementById('story-text').innerText = data.story;

                const player = document.getElementById('audio-player');
                player.src = `/${data.audio_url}?t=${new Date().getTime()}`;

                resultBox.style.display = 'block';
            } else {
                alert('Pipeline Error: ' + data.error);
                resetBars();
            }
        } catch (err) {
            clearInterval(visionInterval);
            alert('Communication Error: ' + err);
            resetBars();
        } finally {
            generateBtn.disabled = false;
        }
    });
</script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/generate', methods=['POST'])
def generate():
    try:
        image_file = request.files.get('image')
        flavor = request.form.get('flavor')
        length_setting = request.form.get('length')

        if not image_file:
            return jsonify({"success": False, "error": "No image uploaded"}), 400

        image_path = os.path.join(Config.UPLOAD_FOLDER, "temp_input.jpg")
        image_file.save(image_path)

        # 1. Pipeline Segment: BLIP Vision
        caption = vision_engine.extract_caption(image_path)

        # 2. Pipeline Segment: Llama 3.2 Story Writing
        story = story_engine.generate_story(caption, flavor, length_setting)

        # 3. Pipeline Segment: pyttsx3 Audio Generation
        audio_filename = f"output_narrative.wav"
        audio_engine.text_to_file(story, audio_filename)

        audio_url = f"static/audio/{audio_filename}"

        return jsonify({
            "success": True,
            "caption": caption,
            "story": story,
            "audio_url": audio_url
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    print("Starting local demonstration web app on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)