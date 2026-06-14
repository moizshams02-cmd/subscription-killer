from flask import Flask, render_template_string, request
import base64
import requests
import json
import os

# Essential: Vercel needs this 'app' defined here to successfully build
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body style="background:#000; color:#fff; padding:20px; font-family:sans-serif;">
    <h2>Financial Auditor</h2>
    <input type="file" id="f" accept="image/*">
    <button onclick="audit()">START AUDIT</button>
    <div id="r"></div>
    <script>
        async function audit() {
            const r = document.getElementById('r');
            r.innerHTML = "Processing...";
            const file = document.getElementById('f').files[0];
            // Shrink image to 400px to avoid "Request too large" errors
            const b = await createImageBitmap(file);
            const c = document.createElement('canvas');
            const s = Math.min(400 / b.width, 1);
            c.width = b.width * s; c.height = b.height * s;
            c.getContext('2d').drawImage(b, 0, 0, c.width, c.height);
            const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.2));
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
                {"role": "system", "content": "Return ONLY a JSON list: [{'s':'desc','a':'amt','c':'date'}]."},
                {"role": "user", "content": "Extract: data:image/jpeg;base64," + b64}
            ]
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {os.environ.get('API_KEY')}", "Content-Type": "application/json"}, 
                             json=payload)
        
        result = resp.json()
        if 'choices' in result:
            content = result['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
            data = json.loads(content)
            return "".join([f"<div>{i.get('s')} | {i.get('a')} | {i.get('c')}</div>" for i in data])
        return "API Error: " + str(result.get('error', 'Unknown'))
    except Exception as e: return "Error: " + str(e)
