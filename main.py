from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

# Top-level Flask instance - Required by Vercel
app = Flask(__name__)

# Configuration
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

# UI Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: sans-serif; background: #000; color: #fff; padding: 20px; }
    .btn { padding: 16px; background: #fff; color: #000; border-radius: 8px; font-weight: bold; width: 100%; border: none; cursor: pointer; }
    table { width: 100%; color: #fff; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 10px; border: 1px solid #333; text-align: left; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment" required style="margin-bottom:10px;">
        <button type="submit" class="btn">SCAN STATEMENT</button>
    </form>
    <div style="color: #ff3333;">{{ error }}</div>
    <div>{{ table_html|safe }}</div>
</body>
</html>
"""

def process_data(image_bytes):
    if not API_KEY: return "", "CRITICAL: API_KEY missing."

    # Encode image to base64
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # Multimodal Payload for Groq Vision models
    payload = {
        "model": "llama-3.2-90b-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all recurring subscriptions as a JSON list. For each, include 's' (Service), 'a' (Amount), 'c' (Strategy). Output ONLY valid JSON, no markdown."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }
        ]
    }
    
    try:
        resp = requests.post(URL, headers=headers, json=payload)
        resp.raise_for_status()
        
        # Parse result
        content = resp.json()['choices'][0]['message']['content'].strip()
        data = json.loads(content)
        
        # Build table
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
