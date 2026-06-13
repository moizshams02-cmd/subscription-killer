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
        <button type="submit" id="b" style="padding:10px; width:100%;">START AUDIT</button>
    </form>
    <div id="r" style="margin-top:20px;"></div>
    <script>
        document.getElementById('u').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('b');
            const resDiv = document.getElementById('r');
            btn.disabled = true;
            resDiv.innerText = "Processing image...";
            
            const file = document.getElementById('f').files[0];
            const bmp = await createImageBitmap(file);
            const canvas = document.createElement('canvas');
            const scale = Math.min(400 / bmp.width, 1);
            canvas.width = bmp.width * scale; canvas.height = bmp.height * scale;
            canvas.getContext('2d').drawImage(bmp, 0, 0, canvas.width, canvas.height);
            const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.2));
            
            const fd = new FormData();
            fd.append('i', blob);
            
            try {
                const res = await fetch('/', { method: 'POST', body: fd });
                resDiv.innerHTML = await res.text();
            } catch(e) { resDiv.innerText = "Client Error: " + e.message; }
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
    if not api_key: return "Server Error: API_KEY missing."
    
    try:
        img = request.files.get("i")
        b64 = base64.b64encode(img.read()).decode('utf-8')
        
        # Using a clean dictionary structure that avoids f-string formatting issues
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": "Extract statement rows as a JSON list. Keys: 's' (desc), 'a' (amt), 'c' (date). Example: [{'s':'Gas','a':'50','c':'2026-01-01'}]. Return ONLY the JSON list. No markdown." + " Image: data:image/jpeg;base64," + b64}]
        }
        
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer " + api_key, "Content-Type": "application/json"}, 
                             json=payload, timeout=25)
        
        if resp.status_code != 200:
            return f"API Error {resp.status_code}: {resp.text[:100]}"
            
        content = resp.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        
        # Display results cleanly
        output = "<div style='font-weight:bold;'>Description | Amount | Date</div>"
        for i in data:
            output += f"<div style='border-bottom:1px solid #444; padding:5px;'>{i.get('s','-')} | {i.get('a','-')} | {i.get('c','-')}</div>"
        return output
    except Exception as e:
        return f"Extraction Failed: {str(e)}"
