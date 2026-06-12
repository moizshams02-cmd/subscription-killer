from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

app = Flask(__name__)

# Load API key
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: sans-serif; background: #000; color: #fff; padding: 20px; }
    .card { background: #1a1a1a; padding: 15px; border-radius: 12px; }
    .stat-val { font-size: 24px; font-weight: bold; color: #FF3B30; }
    button { width: 100%; padding: 16px; background: #fff; color: #000; border: none; border-radius: 8px; font-weight: bold; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <div class="card">MONTHLY BLEED<div class="stat-val">${{ total }}</div></div>
    <form method="post" enctype="multipart/form-data" style="margin-top:20px;">
        <input type="file" name="image" accept="image/*" style="display:none;" id="f" onchange="this.form.submit()">
        <button type="button" onclick="document.getElementById('f').click()">SCAN STATEMENT</button>
    </form>
    {{ table_html|safe }}
</body>
</html>
"""

def process_image(image_bytes):
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "Extract only recurring subscriptions. Ignore one-time retail/gas/dining. Return JSON with 's', 'a', 'c'."},
            {"role": "user", "content": [{"type": "text", "text": "Extract."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}
        ]
    }
    resp = requests.post(URL, headers=headers, json=payload)
    if resp.status_code == 200:
        data = json.loads(resp.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip())
        total = sum(float(item['a']) for item in data)
        rows = "".join([f"<tr><td>{item['s']}</td><td>{item['a']}</td><td>{item['c']}</td></tr>" for item in data])
        return f"<table>{rows}</table>", f"{total:.2f}"
    return "", "0.00"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'image' in request.files:
        t, tot = process_image(request.files['image'].read())
        return render_template_string(HTML_TEMPLATE, table_html=t, total=tot)
    return render_template_string(HTML_TEMPLATE, table_html="", total="0.00")
