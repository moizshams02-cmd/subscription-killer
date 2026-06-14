from flask import Flask, render_template_string, request
import base64
import requests
import json
import os

# DEFINED AT THE TOP LEVEL: This solves your Build Failed error
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body style="background:#000; color:#fff; padding:20px;">
    <h2>Financial Auditor</h2>
    <form id="u">
        <input type="file" id="f" accept="image/*" multiple required>
        <button type="submit" id="b">START AUDIT</button>
    </form>
    <div id="r"></div>
    <script>
        document.getElementById('u').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('b');
            const resDiv = document.getElementById('r');
            btn.disabled = true;
            const files = document.getElementById('f').files;
            for (let i = 0; i < files.length; i++) {
                resDiv.innerHTML += `<div>Processing ${files[i].name}...</div>`;
                const bmp = await createImageBitmap(files[i]);
                const canvas = document.createElement('canvas');
                const scale = Math.min(600 / bmp.width, 1);
                canvas.width = bmp.width * scale; canvas.height = bmp.height * scale;
                canvas.getContext('2d').drawImage(bmp, 0, 0, canvas.width, canvas.height);
                const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.2));
                const fd = new FormData();
                fd.append('i', blob);
                const res = await fetch('/', { method: 'POST', body: fd });
                resDiv.innerHTML += await res.text() + "<hr>";
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
    api_key = os.environ.get('API_KEY')
    try:
        img = request.files.get("i")
        b64 = base64.b64encode(img.read()).decode('utf-8')
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": "Return JSON list [{'s':'desc','a':'amt','c':'date'}]. No markdown. Image: data:image/jpeg;base64," + b64}]
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}, 
                             json=payload, timeout=25)
        content = resp.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        return "".join([f"<div>{i.get('s')} | {i.get('a')} | {i.get('c')}</div>" for i in data])
    except Exception as e:
        return f"Error: {str(e)}"
