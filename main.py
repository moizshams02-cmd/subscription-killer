from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

# This must be at the top level so Vercel can detect it
app = Flask(__name__)

# --- Configuration ---
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment" required>
        <button type="submit">SCAN STATEMENT</button>
    </form>
    <div>{{ error|safe }}</div>
    <div>{{ table_html|safe }}</div>
</body>
</html>
"""

def process_data(image_bytes):
    if not API_KEY: return "", "CRITICAL: API_KEY missing."
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # Corrected Payload Structure for Groq Vision models
    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract recurring subscriptions as a JSON list. Include 's' (Service), 'a' (Amount), 'c' (Strategy). No markdown code blocks."},
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
