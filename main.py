from flask import Flask, render_template_string, request
import base64
import requests
import json
import os

# TOP LEVEL: This is required for Vercel to detect the app
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body style="font-family:sans-serif; background:#000; color:#fff; padding:20px;">
    <h2 style="color:#0f0;">Financial Auditor</h2>
    <form id="u">
        <input type="file" id="f" accept="image/*" capture="environment" multiple required>
        <button type="submit" id="b" style="padding:15px; width:100%; background:#333; color:#fff; border:none;">AUDIT ALL</button>
    </form>
    <div id="r" style="margin-top:20px;"></div>
    <script>
        document.getElementById('u').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('b');
            const resDiv = document.getElementById('r');
            btn.disabled = true;
            resDiv.innerHTML = "";
            const files = document.getElementById('f').files;
            
            for (let i = 0; i < files.length; i++) {
                if (i > 0) await new Promise(r => setTimeout(r, 3000)); // 3s cooldown
                resDiv.innerHTML += `<div>Processing ${files[i].name}...</div>`;
                
                // Resizing logic to prevent "Request too large" (413)
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
            "messages": [{"role": "user", "content": "Extract data: [{'s':'desc','a':'amt','c':'date'}]. No markdown. Image: data:image/jpeg;base64," + b64}]
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, 
                             json=payload, timeout=25)
        
        result = resp.json()
        if 'choices' in result:
            content = result['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
            data = json.loads(content)
            return "".join([f"<div>{i.get('s','-')} | {i.get('a','-')} | {i.get('c','-')}</div>" for i in data])
        return "API Error occurred. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"
