from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

# Required: Vercel needs 'app' to be the entry point
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="font-family:sans-serif; background:#000; color:#fff; padding:20px;">
    <h2>Financial Auditor</h2>
    <form id="uploadForm">
        <input type="file" id="f" accept="image/*" multiple required>
        <button type="submit" id="btn" style="padding:10px; width:100%;">START AUDIT</button>
    </form>
    <div id="status" style="margin-top:10px;"></div>
    <div id="results" style="margin-top:10px;"></div>
    <script>
        document.getElementById('uploadForm').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('btn');
            const status = document.getElementById('status');
            btn.disabled = true;
            status.innerText = "Analyzing... (do not leave page)";
            
            const fd = new FormData();
            for (let file of document.getElementById('f').files) {
                fd.append('images', file);
            }
            
            try {
                const res = await fetch('/', { method: 'POST', body: fd });
                document.getElementById('results').innerHTML = await res.text();
            } catch (err) {
                document.getElementById('results').innerHTML = "Error: " + err.message;
            } finally {
                btn.disabled = false;
                status.innerText = "Finished.";
            }
        };
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET': return render_template_string(HTML_TEMPLATE)
    
    api_key = os.environ.get('API_KEY')
    if not api_key: return "Server Error: API_KEY missing."
    
    output = "<h3>Results:</h3>"
    for img in request.files.getlist("images"):
        try:
            b64 = base64.b64encode(img.read()).decode('utf-8')
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": f"Extract the table. Return ONLY a JSON list of objects: [{'s': 'Description', 'a': 'Amount', 'c': 'Date'}]. No extra text. Data: data:image/jpeg;base64,{b64}"}]
            }
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                 headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, 
                                 json=payload, timeout=20)
            
            data = json.loads(resp.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', ''))
            for item in data:
                output += f"<div style='border:1px solid #444; padding:5px;'>{item.get('s')} | {item.get('a')} | {item.get('c')}</div>"
        except Exception as e:
            output += f"<div>Extraction Error: {str(e)}</div>"
            
    return output
