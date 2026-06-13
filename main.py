from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

app = Flask(__name__)

# Minimal HTML to keep the payload size tiny
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body style="font-family:sans-serif; background:#000; color:#fff; padding:20px;">
    <h2>Financial Auditor</h2>
    <form id="u">
        <input type="file" id="f" accept="image/*" multiple required>
        <button type="submit" id="b" style="padding:10px;">AUDIT</button>
    </form>
    <div id="r" style="margin-top:20px;"></div>
    <script>
        document.getElementById('u').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('b');
            const resDiv = document.getElementById('r');
            btn.disabled = true;
            resDiv.innerText = "Analyzing...";
            const fd = new FormData();
            for (let file of document.getElementById('f').files) {
                fd.append('i', file);
            }
            try {
                const res = await fetch('/', { method: 'POST', body: fd });
                resDiv.innerHTML = await res.text();
            } catch(e) { resDiv.innerText = "Error: " + e.message; }
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
    # Limit processing to ONLY the first image to save time/memory
    img = request.files.getlist("i")[0] 
    
    try:
        b64 = base64.b64encode(img.read()).decode('utf-8')
        # Instruct AI to be extremely brief to save token processing time
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": f"Extract rows as simple JSON list: [{'s':'desc','a':'amt','c':'date'}]. No markdown. Image: data:image/jpeg;base64,{b64}"}]
        }
        # Use a short timeout for the API call
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, 
                             json=payload, timeout=7)
        
        data = json.loads(resp.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', ''))
        return "".join([f"<div>{i.get('s')} | {i.get('a')} | {i.get('c')}</div>" for i in data])
    except Exception as e:
        return f"Process failed: {str(e)}"
