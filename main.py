from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body style="font-family:sans-serif; background:#000; color:#fff; padding:20px;">
    <h2>Financial Auditor</h2>
    <form id="u">
        <input type="file" id="f" accept="image/*" required>
        <button type="submit" id="b" style="padding:10px; width:100%;">AUDIT</button>
    </form>
    <div id="r" style="margin-top:20px;"></div>
    <script>
        document.getElementById('u').onsubmit = async (e) => {
            e.preventDefault();
            const b = document.getElementById('b');
            b.disabled = true;
            document.getElementById('r').innerText = "Analyzing... (please wait)";
            
            const file = document.getElementById('f').files[0];
            // Shrink image in browser to keep payload tiny
            const bmp = await createImageBitmap(file);
            const canvas = document.createElement('canvas');
            const scale = Math.min(600 / bmp.width, 1);
            canvas.width = bmp.width * scale; canvas.height = bmp.height * scale;
            canvas.getContext('2d').drawImage(bmp, 0, 0, canvas.width, canvas.height);
            const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.5));
            
            const fd = new FormData();
            fd.append('i', blob);
            
            try {
                const res = await fetch('/', { method: 'POST', body: fd });
                document.getElementById('r').innerHTML = await res.text();
            } catch(e) { document.getElementById('r').innerText = "Error: " + e.message; }
            b.disabled = false;
        };
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET': return render_template_string(HTML_TEMPLATE)
    
    api_key = os.environ.get('API_KEY')
    if not api_key: return "API Key missing."
    
    try:
        img = request.files.get("i")
        b64 = base64.b64encode(img.read()).decode('utf-8')
        
        # Super-lightweight prompt to ensure fast response
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": f"Return JSON list: [{'s':'desc','a':'amt','c':'date'}]. NO EXTRA TEXT. Data: data:image/jpeg;base64,{b64}"}]
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, 
                             json=payload, timeout=9)
        
        raw = resp.json()['choices'][0]['message']['content'].strip()
        data = json.loads(raw.replace('```json', '').replace('```', ''))
        
        return "".join([f"<div>{i.get('s')} | {i.get('a')} | {i.get('c')}</div>" for i in data])
    except Exception as e:
        return f"Process failed: {str(e)}"
