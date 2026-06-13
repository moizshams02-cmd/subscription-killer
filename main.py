from flask import Flask
# REQUIRED: Top-level instance for Vercel
app = Flask(__name__)

from flask import render_template_string, request
import base64
import requests
import os
import json

# Configuration
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

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
        <input type="file" name="image" accept="image/*" capture="environment" required style="margin-bottom:10px;">
        <button type="submit" class="btn">SCAN STATEMENT</button>
    </form>
    <div style="color: #ff3333; margin-top: 10px;">{{ error }}</div>
    <div>{{ table_html|safe }}</div>
</body>
</html>
"""

def process_data(image_bytes):
    api_key = os.environ.get("API_KEY")
    if not api_key: return "", "CRITICAL: API_KEY missing."

    b64 = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Payload fixed: 'content' is now a string to satisfy the validator
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": f"Extract subscriptions from this image as a JSON list (keys: s, a, c). No markdown. Image data: data:image/jpeg;base64,{b64}"
            }
        ]
    }
    
    try:
        resp = requests.post(URL, headers=headers, json=payload)
        if resp.status_code != 200:
            return "", f"API ERROR ({resp.status_code}): {resp.text}"
            
        content = resp.json()['choices'][0]['message']['content'].strip()
        data = json.loads(content)
        
        rows = "".join([f"<tr><td>{item.get('s', 'N/A')}</td><td>{item.get('a', '0')}</td><td>{item.get('c', 'N/A')}</td></tr>" for item in data])
        return f"<table><thead><tr><th>Service</th><th>Amount</th><th>Strategy</th></tr></thead><tbody>{rows}</tbody></table>", ""
    except Exception as e:
        return "", f"DEBUG ERROR: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    table, err = "", ""
    if request.method == 'POST' and 'image' in request.files:
        table, err = process_data(request.files['image'].read())
    return render_template_string(HTML_TEMPLATE, table_html=table, error=err)
