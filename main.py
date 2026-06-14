from flask import Flask, render_template_string, request
import base64
import requests
import json
import os

app = Flask(__name__)

# This updated HTML keeps the user on the page and prevents gallery-nav issues
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
            if(!file) { alert("Please select an image first!"); return; }
            r.innerHTML = "Processing... please wait.";
            
            const b = await createImageBitmap(file);
            const c = document.createElement('canvas');
            const s = 400 / b.width;
            c.width = 400; c.height = b.height * s;
            c.getContext('2d').drawImage(b, 0, 0, 400, b.height * s);
            const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.1));
            
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
            "messages": [{"role": "system", "content": "Return ONLY JSON: [{'s':'desc','a':'amt','c':'date'}]"},
                         {"role": "user", "content": "data:image/jpeg;base64," + b64}]
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {os.environ.get('API_KEY')}", "Content-Type": "application/json"}, 
                             json=payload)
        
        # Clean response to ensure it parses correctly
        content = resp.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        return "".join([f"<div>{i.get('s')} | {i.get('a')} | {i.get('c')}</div>" for i in data])
    except Exception as e: return f"Error: {str(e)}"
