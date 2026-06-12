from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

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
    .stat-val { font-size: 24px; font-weight: bold; color: #FF3B30; }
    .btn-label { display: block; padding: 16px; background: #fff; color: #000; border-radius: 8px; font-weight: bold; text-align: center; cursor: pointer; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <div class="card">MONTHLY BLEED<div class="stat-val">${{ total }}</div></div>
    <form method="post" enctype="multipart/form-data">
        <label for="f" class="btn-label">TAP TO SCAN STATEMENT</label>
        <input type="file" name="image" accept="image/*" capture="environment" id="f" onchange="this.form.submit()" style="display:none;">
    </form>
    {{ table_html|safe }}
</body>
</html>
"""

def process(image_bytes):
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "You are a financial auditor. Identify recurring subscriptions. Ignore one-time purchases. Return ONLY JSON list with keys 's' (Service), 'a' (Amount), 'c' (Strategy)."},
            {"role": "user", "content": [{"type": "text", "text": "Extract."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}
        ]
    }
    resp = requests.post(URL, headers=headers, json=payload)
    if resp.status_code == 200:
        try:
            content = resp.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            total = sum(float(item['a']) for item in data)
            rows = "".join([f"<tr><td>{item['s']}</td><td>${item['a']}</td><td>{item['c']}</td></tr>" for item in data])
            return f"<table>{rows}</table>", f"{total:.2f}"
        except: return "<tr><td>Error</td></tr>", "0.00"
    return "<tr><td>API Error</td></tr>", "0.00"

@app.route('/', methods=['GET', 'POST'])
def index():
    t, tot = "", "0.00"
    if request.method == 'POST' and 'image' in request.files:
        t, tot = process(request.files['image'].read())
    return render_template_string(HTML_TEMPLATE, table_html=t, total=tot)
