import base64
import requests
import json
from flask import Flask, render_template_string, request
import os

app = Flask(__name__)
# Get API key from environment variable safely
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

# Simplified HTML to ensure the interface renders even if API fails
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
    body { font-family: sans-serif; background: #0A0A0A; color: white; padding: 20px; }
    textarea, input { width: 100%; margin: 10px 0; padding: 10px; border-radius: 8px; }
    button { width: 100%; padding: 15px; background: #FF3B30; color: white; border: none; border-radius: 8px; }
</style></head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <textarea name="text_input" placeholder="Paste data..."></textarea>
        <input type="file" name="image" accept="image/*" capture="environment">
        <button type="submit">RUN EXTRACTION</button>
    </form>
    {% if result %}<div><h3>Result:</h3><pre>{{ result }}</pre></div>{% endif %}
</body>
</html>
"""

def get_model_response(data, is_image=False):
    if not API_KEY: return "Error: API_KEY not set"
    
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # Using 'llama-3.3-70b-versatile' as a highly reliable fallback
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"Extract subscriptions from this: {data}"}]
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Processing Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        if 'image' in request.files and request.files['image'].filename:
            # For now, we extract text via OCR or just handle the text path
            result = "Vision processing active. Please use text for now while we verify vision model IDs."
        elif request.form.get('text_input'):
            result = get_model_response(request.form.get('text_input'))
            
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run()
