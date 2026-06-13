from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

# Vercel requires 'app' at the top level
app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: sans-serif; background: #000; color: #fff; padding: 20px; }
    .card { background: #1a1a1a; padding: 15px; border-radius: 12px; margin-bottom: 20px; }
    .btn { padding: 16px; background: #fff; color: #000; border-radius: 8px; font-weight: bold; width: 100%; border: none; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment" required>
        <button type="submit" class="btn">SCAN STATEMENT</button>
    </form>
    <div>{{ table_html|safe }}</div>
</body>
</html>
"""

def process_data(image_bytes):
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [
            {"role": "system", "content": "You are a financial auditor. Extract ONLY recurring subscriptions. IGNORE one-time purchases like gas or groceries. Return JSON list with 's' (Service), 'a' (Amount), 'c' (Cancellation Strategy)."},
            {"role": "user", "content": [{"type": "text", "text": "Extract."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}
        ]
    }
    resp = requests.post(URL, headers=headers, json=payload)
    if resp.status_code == 200:
        data = json.loads(resp.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip())
        rows = "".join([f"<tr><td>{item['s']}</td><td>{item['a']}</td><td>{item['c']}</td></tr>" for item in data])
        return f"<table>{rows}</table>"
    return "Error: Could not process image."

@app.route('/', methods=['GET', 'POST'])
def index():
    table = ""
    if request.method == 'POST' and 'image' in request.files:
        table = process_data(request.files['image'].read())
    return render_template_string(HTML_TEMPLATE, table_html=table)
