from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #000; color: #fff; padding: 20px; }
        .btn { padding: 16px; background: #fff; color: #000; border-radius: 8px; font-weight: bold; width: 100%; border: none; cursor: pointer; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        th, td { border: 1px solid #444; padding: 8px; text-align: left; font-size: 14px; }
    </style>
</head>
<body>
    <h1>Financial Statement Auditor</h1>
    <form id="uploadForm" enctype="multipart/form-data">
        <input type="file" id="fileInput" accept="image/*" multiple required style="margin-bottom:10px;">
        <button type="submit" class="btn">AUDIT STATEMENT</button>
    </form>
    <div id="status"></div>
    <div id="results"></div>
    <script>
        document.getElementById('uploadForm').onsubmit = async (e) => {
            e.preventDefault();
            const status = document.getElementById('status');
            status.innerText = "Analyzing table data...";
            const files = document.getElementById('fileInput').files;
            const formData = new FormData();
            for (let file of files) {
                const bitmap = await createImageBitmap(file);
                const canvas = document.createElement('canvas');
                const scale = Math.min(1000 / bitmap.width, 1);
                canvas.width = bitmap.width * scale;
                canvas.height = bitmap.height * scale;
                canvas.getContext('2d').drawImage(bitmap, 0, 0, canvas.width, canvas.height);
                const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.8));
                formData.append('images', blob, file.name);
            }
            const response = await fetch('/', { method: 'POST', body: formData });
            document.getElementById('results').innerHTML = await response.text();
            status.innerText = "Audit Complete.";
        };
    </script>
</body>
</html>
"""

def process_batch(image_list):
    api_key = os.environ.get("API_KEY")
    if not api_key: return "API Key missing."
    
    all_rows = ""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    URL = "https://api.groq.com/openai/v1/chat/completions"
    
    for img_file in image_list:
        b64 = base64.b64encode(img_file.read()).decode('utf-8')
        # Instructing the AI to be a 'Table Reader'
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{
                "role": "user",
                "content": f"You are a financial auditor. Extract all transactions from this table. Return ONLY a JSON list of objects: [{'s': 'Description', 'a': 'Amount', 'c': 'Date'}]. Do not include headers or filler. If the image is a table, extract every row. Image: data:image/jpeg;base64,{b64}"
            }]
        }
        try:
            resp = requests.post(URL, headers=headers, json=payload)
            data = json.loads(resp.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', ''))
            for item in data:
                all_rows += f"<tr><td>{item.get('s')}</td><td>{item.get('a')}</td><td>{item.get('c')}</td></tr>"
        except: continue
            
    if not all_rows: return "Could not parse table data."
    return f"<table><thead><tr><th>Service</th><th>Amount</th><th>Date</th></tr></thead><tbody>{all_rows}</tbody></table>"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': return process_batch(request.files.getlist("images"))
    return render_template_string(HTML_TEMPLATE)
