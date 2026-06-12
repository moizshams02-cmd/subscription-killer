from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

# 1. Initialize the app at the top level
app = Flask(__name__)

# 2. Get API key from environment variables
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: -apple-system, sans-serif; background: #000; color: #fff; padding: 20px; }
    .stats { display: flex; gap: 10px; margin-bottom: 20px; }
    .stat-box { background: #1a1a1a; padding: 15px; border-radius: 12px; flex: 1; border: 1px solid #333; }
    .stat-val { font-size: 24px; font-weight: bold; color: #FF3B30; }
    .card { background: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; margin-top: 20px;}
    table { width: 100%; border-collapse: collapse; }
    th { color: #888; font-size: 11px; text-transform: uppercase; text-align: left; padding: 10px; border-bottom: 1px solid #333; }
    td { padding: 12px 10px; border-bottom: 1px solid #222; font-size: 14px; vertical-align: top; }
    button { width: 100%; padding: 16px; background: #fff; color: #000; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <div class="stats">
        <div class="stat-box">MONTHLY BLEED<div class="stat-val">${{ total }}</div></div>
    </div>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment">
        <button type="submit">EXECUTE FINANCIAL SCAN</button>
    </form>
    {% if table_html %}
    <div class="card">
        <h3>Detected Subscriptions</h3>
        {{ table_html|safe }}
    </div>
    {% endif %}
</body>
</html>
"""

def process_data(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "You are a fierce Consumer Advocate. Identify recurring subscriptions. For each, provide: 's' (Service), 'a' (Amount as number), 'c' (Specific cancellation strategy). Return ONLY JSON."},
            {"role": "user", "content": [{"type": "text", "text": "Extract all transactions into a JSON list."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}
        ]
    }
    
    response = requests.post(URL, headers=headers, json=payload)
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        
        total = sum(float(item['a']) for item in data)
        rows = "".join([f"<tr><td>{item['s']}</td><td>${item['a']}</td><td>{item['c']}</td></tr>" for item in data])
        table_html = f"<table><thead><tr><th>Service</th><th>Amount</th><th>Strategy</th></tr></thead><tbody>{rows}</tbody></table>"
        
        return table_html, f"{total:.2f}"
    return "", "0.00"

@app.route('/', methods=['GET', 'POST'])
def index():
    table_html, total = "", "0.00"
    if request.method == 'POST' and 'image' in request.files:
        table_html, total = process_data(request.files['image'].read())
    return render_template_string(HTML_TEMPLATE, table_html=table_html, total=total)
