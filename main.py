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
        <button type="submit" id="b" style="padding:10px; width:100%;">AUDIT ALL</button>
    </form>
    <div id="r" style="margin-top:20px;"></div>
    <script>
        document.getElementById('u').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('b');
            const resDiv = document.getElementById('r');
            btn.disabled = true;
            resDiv.innerText = "Analyzing batch... (this may take 10-15s)";
            
            const fd = new FormData();
            const files = document.getElementById('f').files;
            for (let i = 0; i < files.length; i++) {
                fd.append('images', files[i]);
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
    results_html = "<h3>Audit Results:</h3>"
    
    for img in request.files.getlist("images"):
        try:
            b64 = base64.b64encode(img.read()).decode('utf-8')
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": f"Extract table rows. Return ONLY a valid JSON list of objects with keys 's', 'a', and 'c'. Example: [{{'s':'desc','a':'amt','c':'date'}}]. Do not wrap in markdown. Image data: data:image/jpeg;base64,{b64}"}]
            }
            
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                 headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, 
                                 json=payload, timeout=25)
            
            content = resp.json()['choices'][0]['message']['content'].strip()
            # Clean potential markdown artifacts
            clean_content = content.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_content)
            
            for item in data:
                results_html += f"<div style='border-bottom:1px solid #444; padding:5px;'>{item.get('s', 'N/A')} | {item.get('a', 'N/A')} | {item.get('c', 'N/A')}</div>"
        except Exception as e:
            results_html += f"<div style='color:red;'>Failed to process an image: {str(e)}</div>"
            
    return results_html
