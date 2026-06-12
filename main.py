import json
import requests
import base64
from flask import Flask, render_template_string, request
from config import API_KEY

app = Flask(__name__)
URL = "https://api.groq.com/openai/v1/chat/completions"

# Optimized Mobile-First HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #0A0A0A; color: white; padding: 20px; }
        textarea, .file-input { width: 100%; background: #1C1C1E; color: white; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
        button { width: 100%; padding: 18px; background: #FF3B30; color: white; border: none; border-radius: 12px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <textarea name="text_input" placeholder="Paste data..."></textarea>
        <div class="file-input">
            <label>Scan Statement:</label>
            <input type="file" name="image" accept="image/*" capture="environment">
        </div>
        <button type="submit">RUN EXTRACTION</button>
    </form>
</body>
</html>
"""

def analyze_with_vision(image_bytes):
    # Convert image to base64 for the API
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.2-90b-vision-preview",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": "Extract subscriptions from this statement."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]}]
    }
    return requests.post(URL, headers=headers, json=payload).json()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle Image
        if 'image' in request.files and request.files['image'].filename:
            image_data = request.files['image'].read()
            results = analyze_with_vision(image_data)
            return f"<pre>{json.dumps(results, indent=2)}</pre>"
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run()
