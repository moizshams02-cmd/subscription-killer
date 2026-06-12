import base64
import requests
import os
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Vercel retrieves this from the Environment Variables you configured
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: -apple-system, sans-serif; background: #000; color: #fff; padding: 20px; }
    textarea { width: 100%; height: 120px; padding: 10px; border-radius: 8px; background: #1a1a1a; color: #fff; border: 1px solid #333; }
    input[type="file"] { width: 100%; margin: 20px 0; padding: 10px; border: 1px dashed #555; border-radius: 8px; }
    button { width: 100%; padding: 16px; background: #fff; color: #000; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
    pre { background: #111; padding: 15px; border-radius: 8px; overflow-x: auto; border: 1px solid #333; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <textarea name="text_input" placeholder="Or paste subscription details here..."></textarea>
        <input type="file" name="image" accept="image/*" capture="environment">
        <button type="submit">SCAN STATEMENT</button>
    </form>
    {% if result %}
        <h3>Analysis Result:</h3>
        <pre>{{ result }}</pre>
    {% endif %}
</body>
</html>
"""

def analyze_image(image_bytes):
    if not API_KEY: return "Error: API_KEY not configured in Vercel."
    
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [{
            "role": "user", 
            "content": [
                {"type": "text", "text": "Extract all subscription names and charges from this statement and return them as a JSON list."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }]
    }
    
    response = requests.post(URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return f"API Error: {response.text}"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        if 'image' in request.files and request.files['image'].filename:
            result = analyze_image(request.files['image'].read())
        elif request.form.get('text_input'):
            # Text fallback
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": request.form.get('text_input')}]}
            res = requests.post(URL, headers=headers, json=payload)
            result = res.json()['choices'][0]['message']['content']
            
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True)
