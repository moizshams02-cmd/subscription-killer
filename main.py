from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

# 1. MUST BE AT THE TOP LEVEL
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: sans-serif; background: #000; color: #fff; padding: 20px; }
    .btn { padding: 16px; background: #fff; color: #000; border-radius: 8px; font-weight: bold; width: 100%; border: none; cursor: pointer; }
    table { width: 100%; margin-top: 20px; border-collapse: collapse; color: #fff; }
    th, td { border: 1px solid #444; padding: 8px; text-align: left; }
</style>
</head>
<body>
    <h1>Financial Auditor</h1>
    <form id="uploadForm" enctype="multipart/form-data">
        <input type="file" id="fileInput" accept="image/*" multiple required style="margin: 10px 0;">
        <button type="submit" class="btn">AUDIT STATEMENT</button>
    </form>
    <div id="status"></div>
    <div id="results"></div>
    <script>
        document.getElementById('uploadForm').onsubmit = async (e) => {
            e.preventDefault();
            const status = document.getElementById('status');
            status.innerText = "Processing...";
            const files = document.getElementById('fileInput').files;
            const formData = new FormData();
            for (let file of files) {
                const bitmap = await createImageBitmap(file);
                const canvas = document.createElement('canvas');
                const scale = Math.min(800 / bitmap.width, 1);
                canvas.width = bitmap.width * scale;
                canvas.height = bitmap.height * scale;
                canvas.getContext('2d').drawImage(bitmap, 0, 0, canvas.width, canvas.height);
                const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.7));
                formData.append('images', blob, file.name);
            }
            const res = await fetch('/', { method: 'POST', body: formData });
            document.getElementById('results').innerHTML = await res.text();
            status.innerText = "Done!";
        };
    </script>
</body>
</html>
"""

def process_statement(image_file):
    api_key = os.environ.get("API_KEY")
    if not api_key: return "<tr><td>Error: API Key missing</td></tr>"
    
    b64 = base64.b64encode(image_file.read()).decode('utf-8')
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"Extract rows from this statement table. Return JSON list: [{'s': 'desc', 'a': 'amt', 'c': 'date'}]. No markdown. Image: data:image/jpeg;base64,{b64}"}]
    }
    
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, 
                             json=payload)
        content = resp.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', '')
        data = json.loads(content)
        return "".join([f"<tr><td>{item.get('s')}</td><td>{item.get('a')}</td><td>{item.get('c')}</td></tr>" for item in data])
    except Exception as e:
        return f"<tr><td>Error: {str(e)}</td></tr>"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        images = request.files.getlist("images")
        rows = "".join([process_statement(img) for img in images])
        return f"<table><tr><th>Service</th><th>Amount</th><th>Date</th></tr>{rows}</table>"
    return render_template_string(HTML_TEMPLATE)
