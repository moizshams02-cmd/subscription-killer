import base64
import requests
import os
from flask import Flask, render_template_string, request

app = Flask(__name__)
# Vercel will automatically pull the API_KEY from your Environment Variables
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
    body { font-family: sans-serif; background: #0A0A0A; color: white; padding: 20px; }
    textarea { width: 100%; height: 100px; padding: 10px; border-radius: 8px; }
    input { width: 100%; margin: 10px 0; }
    button { width: 100%; padding: 15px; background: #FF3B30; color: white; border: none; border-radius: 8px; font-weight: bold; }
</style></head>
<body>
    <h2>Subscription Killer</h2>
    <form method="post" enctype="multipart/form-data">
        <textarea name="text_input" placeholder="Paste data..."></textarea>
        <input type="file" name="image" accept="image/*" capture="environment">
        <button type="submit">RUN EXTRACTION</button>
    </form>
    {% if result %}<div><h3>Result:</h3><pre style="white-space: pre-wrap;">{{ result }}</pre></div>{% endif %}
</body>
</html>
"""

def analyze_image(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": "Extract subscription names and amounts from this statement as a JSON list."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]}]
    }
    response = requests.post(URL, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content'] if response.status_code == 200 else f"Error: {response.text}"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        if 'image' in request.files and request.files['image'].filename:
            result = analyze_image(request.files['image'].read())
        elif request.form.get('text_input'):
            # Fallback to standard LLM if no image
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": request.form.get('text_input')}]}
            res = requests.post(URL, headers=headers, json=payload)
            result = res.json()['choices'][0]['message']['content']
            
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run()
