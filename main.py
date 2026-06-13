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
        <button type="submit" style="padding:10px;">Process</button>
    </form>
    <div id="s"></div>
    <div id="r"></div>
    <script>
        document.getElementById('u').onsubmit = async (e) => {
            e.preventDefault();
            document.getElementById('s').innerText = "Compressing/Uploading...";
            const files = document.getElementById('f').files;
            const fd = new FormData();
            for (let file of files) {
                const b = await createImageBitmap(file);
                const c = document.createElement('canvas');
                const scale = Math.min(800 / b.width, 1);
                c.width = b.width * scale; c.height = b.height * scale;
                c.getContext('2d').drawImage(b, 0, 0, c.width, c.height);
                const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.6));
                fd.append('i', blob);
            }
            const res = await fetch('/', { method: 'POST', body: fd });
            document.getElementById('r').innerHTML = await res.text();
            document.getElementById('s').innerText = "Done.";
        };
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        images = request.files.getlist("i")
        results = []
        for img in images:
            b64 = base64.b64encode(img.read()).decode('utf-8')
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": f"Extract table data as JSON list: [{'s':'desc','a':'amt','c':'date'}]. No markdown. Image data: data:image/jpeg;base64,{b64}"}]
            }
            try:
                resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                     headers={"Authorization": f"Bearer {os.environ.get('API_KEY')}", "Content-Type": "application/json"}, 
                                     json=payload)
                data = json.loads(resp.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', ''))
                results.extend(data)
            except: continue
        return "".join([f"<div>{i.get('s')} | {i.get('a')} | {i.get('c')}</div>" for i in results])
    return render_template_string(HTML_TEMPLATE)
