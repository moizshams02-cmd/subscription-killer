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
        <input type="file" id="f" accept="image/*" multiple required>
        <button type="submit" style="padding:10px;">Audit</button>
    </form>
    <div id="r" style="margin-top:20px;"></div>
    <script>
        document.getElementById('u').onsubmit = async (e) => {
            e.preventDefault();
            document.getElementById('r').innerText = "Processing...";
            const fd = new FormData();
            for (let file of document.getElementById('f').files) {
                const b = await createImageBitmap(file);
                const c = document.createElement('canvas');
                // Extremely aggressive resizing to prevent timeouts
                const s = Math.min(600 / b.width, 1);
                c.width = b.width * s; c.height = b.height * s;
                c.getContext('2d').drawImage(b, 0, 0, c.width, c.height);
                const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.5));
                fd.append('i', blob);
            }
            const res = await fetch('/', { method: 'POST', body: fd });
            document.getElementById('r').innerHTML = await res.text();
        };
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET': return render_template_string(HTML_TEMPLATE)
    
    api_key = os.environ.get('API_KEY')
    if not api_key: return "Server Error: API_KEY not set."
    
    results_display = ""
    for img in request.files.getlist("i"):
        try:
            b64 = base64.b64encode(img.read()).decode('utf-8')
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": f"Extract rows. JSON list only: [{'s':'desc','a':'amt','c':'date'}]. NO EXTRA TEXT. Data: data:image/jpeg;base64,{b64}"}]
            }
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                 headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, 
                                 json=payload, timeout=8) # 8 second timeout to avoid Vercel limit
            
            if resp.status_code != 200:
                results_display += f"API Error {resp.status_code}: {resp.text[:50]}...<br>"
                continue
                
            raw = resp.json()['choices'][0]['message']['content'].strip()
            # Extremely aggressive JSON cleaning
            clean = raw[raw.find('['):raw.rfind(']')+1]
            data = json.loads(clean)
            
            for i in data:
                results_display += f"<div>{i.get('s')} | {i.get('a')} | {i.get('c')}</div>"
        except Exception as e:
            results_display += f"Extraction Error: {str(e)}<br>"
            
    return results_display
