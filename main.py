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
    <form id="u">
        <input type="file" id="f" accept="image/*" multiple required>
        <button type="submit" id="b" style="padding:10px;">START AUDIT</button>
    </form>
    <div id="r"></div>
    <script>
        document.getElementById('u').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('b');
            const r = document.getElementById('r');
            btn.disabled = true;
            const files = document.getElementById('f').files;
            for (let i = 0; i < files.length; i++) {
                if (i > 0) await new Promise(r => setTimeout(r, 3000));
                r.innerHTML += `<div>Auditing ${files[i].name}...</div>`;
                
                const b = await createImageBitmap(files[i]);
                const c = document.createElement('canvas');
                const s = Math.min(400 / b.width, 1);
                c.width = b.width * s; c.height = b.height * s;
                c.getContext('2d').drawImage(b, 0, 0, c.width, c.height);
                const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.1));
                
                const fd = new FormData();
                fd.append('i', blob);
                const res = await fetch('/', { method: 'POST', body: fd });
                r.innerHTML += await res.text() + "<hr>";
            }
            btn.disabled = false;
        };
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
            "messages": [{"role": "system", "content": "Return ONLY a JSON list: [{'s':'desc','a':'amt','c':'date'}]."},
                         {"role": "user", "content": "Extract data: data:image/jpeg;base64," + b64}]
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {os.environ.get('API_KEY')}", "Content-Type": "application/json"}, 
                             json=payload)
        
        result = resp.json()
        if 'choices' in result:
            content = result['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
            data = json.loads(content)
            return "".join([f"<div>{i.get('s')} | {i.get('a')} | {i.get('c')}</div>" for i in data])
        return f"API Error: {result.get('error', {}).get('message', 'Unknown')}"
    except Exception as e:
        return f"Error: {str(e)}"
