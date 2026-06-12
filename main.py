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
    body { font-family: -apple-system, sans-serif; background: #000; color: #fff; padding: 20px; }
    .stat-box { background: #1a1a1a; padding: 15px; border-radius: 12px; border: 1px solid #333; }
    .stat-val { font-size: 24px; font-weight: bold; color: #FF3B30; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { color: #888; font-size: 11px; text-transform: uppercase; text-align: left; padding: 10px; border-bottom: 1px solid #333; }
    td { padding: 12px 10px; border-bottom: 1px solid #222; font-size: 14px; }
    button { width: 100%; padding: 16px; background: #fff; color: #000; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <div class="stat-box">MONTHLY BLEED<div class="stat-val">${{ total }}</div></div>
    <form method="post" enctype="multipart/form-data" style="margin-top:20px;">
        <input type="file" name="image" accept="image/*">
        <button type="submit">SCAN STATEMENT</button>
    </form>
    {{ table_html|safe }}
</body>
</html>
"""

def process_data(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "You are a financial auditor. Identify ONLY recurring subscriptions. IGNORE gas, restaurants, and retail. Return ONLY JSON list with keys 's' (Service), 'a' (Amount as number), 'c' (Strategy)."},
            {"role": "user", "content": [{"type": "text", "text": "Extract subscriptions."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}
        ]
    }
    response = requests.post(URL, headers=headers, json=payload)
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        total = sum(float(item['a']) for item in data)
        rows = "".join([f"<tr><td>{item['s']}</td><td>${item['a']}</td><td>{item['c']}</td></tr>" for item in data])
        return f"<table><thead><tr><th>Service</th><th>Amount</th><th>Strategy</th></tr></thead><tbody>{rows}</tbody></table>", f"{total:.2f}"
    return "", "0.00"

@app.route('/', methods=['GET', 'POST'])
def index():
    table_html, total = "", "0.00"
    if request.method == 'POST' and 'image' in request.files:
        table_html, total = process_data(request.files['image'].read())
    return render_template_string(HTML_TEMPLATE, table_html=table_html, total=total)
