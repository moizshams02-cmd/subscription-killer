from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

app = Flask(__name__)

# Configuration
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

# --- UI Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: sans-serif; background: #000; color: #fff; padding: 20px; }
    .btn { padding: 16px; background: #fff; color: #000; border-radius: 8px; font-weight: bold; width: 100%; border: none; cursor: pointer; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment" required>
        <button type="submit" class="btn">SCAN STATEMENT</button>
    </form>
    <div style="color: #FF3B30;">{{ error }}</div>
    <div>{{ table_html|safe }}</div>
</body>
</html>
"""

def process_data(image_bytes):
    api_key = os.environ.get("API_KEY")
    if not api_key: return "", "CRITICAL: API_KEY missing."

    b64 = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # EXACT PAYLOAD STRUCTURE FOR GROQ VISION
    payload = {
        "model": "llama-3.2-90b-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract recurring subscriptions as a JSON list. Keys: s (Service), a (Amount), c (Strategy). No markdown."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }
        ]
    }
    
    try:
        resp = requests.post(URL, headers=headers, json=payload)
        resp.raise_for_status()
        content = resp.json()['choices'][0]['message']['content'].strip()
        data = json.loads(content)
        rows = "".join([f"<tr><td>{item.get('s')}</td><td>{item.get('a')}</td><td>{item.get('c')}</td></tr>" for item in data])
        return f"<table>{rows}</table>", ""
    except Exception as e:
        return "", f"DEBUG ERROR: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'image' in request.files:
        table, err = process_data(request.files['image'].read())
        return render_template_string(HTML_TEMPLATE, table_html=table, error=err)
    return render_template_string(HTML_TEMPLATE, table_html="", error="")
