from flask import Flask, render_template_string, request
import base64
import requests
import json
import os

# Essential: Must be at the top level for Vercel to build successfully
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body style="background:#000; color:#fff; padding:20px; font-family:sans-serif;">
    <h2>Financial Auditor</h2>
    <input type="file" id="f" accept="image/*">
    <button onclick="audit()" style="padding:10px; background:#0f0; border:none;">START AUDIT</button>
    <div id="r" style="margin-top:20px;"></div>
    <script>
        async function audit() {
            const r = document.getElementById('r');
            const file = document.getElementById('f').files[0];
            if (!file) { alert("Select a file!"); return; }
            r.innerHTML = "Processing...";
            
            // Resize image to 400px to stop "Request too large" errors
            const b = await createImageBitmap(file);
            const c = document.createElement('canvas');
            const s = Math.min(400 / b.width, 1);
            c.width = b.width * s; c.height = b.height * s;
            c.getContext('2d').drawImage(b, 0, 0, c.width, c.height);
            // Compress to 0.4 quality to stop "Rate limit" errors
            const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.4));
            
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
                {"role": "system", "content": "Extract: desc (s), amount (a), date (c). JSON list only: [{'s':'..','a':'..','c':'..'}]."},
                {"role": "user", "content": "Extract data: data:image/jpeg;base64," + b64}
            ]
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {os.environ.get('API_KEY')}", "Content-Type": "application/json"}, 
                             json=payload)
        
        response_data = resp.json()
        if 'choices' in response_data:
            content = response_data['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
            data = json.loads(content)
            return "".join([f"<div>{i.get('s','-')} | {i.get('a','-')} | {i.get('c','-')}</div>" for i in data])
        return f"API Error: {response_data.get('error', {}).get('message', 'Unknown Error')}"
    except Exception as e: return f"System Error: {str(e)}"
