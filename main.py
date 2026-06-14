from flask import Flask, render_template_string, request
import base64
import requests
import json
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body style="background:#000; color:#fff; padding:20px; font-family:sans-serif;">
    <h2>Financial Auditor</h2>
    <div style="margin-top:20px;">
        <input type="file" id="f" accept="image/*" style="display:block; margin-bottom:10px;">
        <button onclick="audit()" style="padding:10px 20px; background:#0f0; border:none; cursor:pointer;">START AUDIT</button>
    </div>
    <div id="r" style="margin-top:20px; white-space:pre-wrap;"></div>
    <script>
        async function audit() {
            const file = document.getElementById('f').files[0];
            const r = document.getElementById('r');
            if(!file) { alert("Select an image first!"); return; }
            r.innerHTML = "Auditing...";
            
            const b = await createImageBitmap(file);
            const c = document.createElement('canvas');
            const s = Math.min(600 / b.width, 1);
            c.width = b.width * s; c.height = b.height * s;
            c.getContext('2d').drawImage(b, 0, 0, c.width, c.height);
            const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.5));
            
            const fd = new FormData();
            fd.append('i', blob);
            const res = await fetch('/', { method: 'POST', body: fd });
            r.innerHTML = await res.text();
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET': return render_template_string(HTML_TEMPLATE)
    try:
        b64 = base64.b64encode(request.files.get("i").read()).decode('utf-8')
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "Extract data: desc (s), amount (a), date (c). Return ONLY JSON list: [{'s':'..','a':'..','c':'..'}]."},
                {"role": "user", "content": "data:image/jpeg;base64," + b64}
            ]
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {os.environ.get('API_KEY')}", "Content-Type": "application/json"}, 
                             json=payload)
        
        content = resp.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        
        if not data: return "No data found."
        return "".join([f"<div>{i.get('s','-')} | {i.get('a','-')} | {i.get('c','-')}</div>" for i in data])
    except Exception as e: return f"Error: {str(e)}"
