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
    <h1>Batch Financial Auditor</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="images" accept="image/*" multiple required style="margin-bottom:10px;">
        <button type="submit" class="btn">AUDIT BATCH</button>
    </form>
    <div style="color: #ff3333; margin-top: 10px;">{{ error }}</div>
    <div>{{ table_html|safe }}</div>
</body>
</html>
"""

def process_batch(image_list):
    api_key = os.environ.get("API_KEY")
    if not api_key: return "", "CRITICAL: API_KEY missing."

    all_results = []
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Process each image in the batch
    for img_file in image_list:
        b64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "user",
                    "content": f"Extract subscriptions as JSON list (keys: s, a, c). No markdown. Image: data:image/jpeg;base64,{b64}"
                }
            ]
        }
        
        try:
            resp = requests.post(URL, headers=headers, json=payload)
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content'].strip()
                all_results.extend(json.loads(content))
        except:
            continue
            
    # Format all results into one table
    rows = "".join([f"<tr><td>{item.get('s', 'N/A')}</td><td>{item.get('a', '0')}</td><td>{item.get('c', 'N/A')}</td></tr>" for item in all_results])
    return f"<table><thead><tr><th>Service</th><th>Amount</th><th>Due Date</th></tr></thead><tbody>{rows}</tbody></table>", ""

@app.route('/', methods=['GET', 'POST'])
def index():
    table, err = "", ""
    if request.method == 'POST':
        # Retrieve the list of files
        images = request.files.getlist("images")
        table, err = process_batch(images)
    return render_template_string(HTML_TEMPLATE, table_html=table, error=err)
