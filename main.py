import base64
import requests
import json
from flask import Flask, render_template_string, request
from config import API_KEY # Ensure your config.py has API_KEY defined

app = Flask(__name__)
URL = "https://api.groq.com/openai/v1/chat/completions"

# Mobile-responsive HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subscription Killer</title>
    <style>
        body { font-family: -apple-system, sans-serif; background: #0A0A0A; color: white; padding: 20px; }
        .container { max-width: 500px; margin: auto; }
        textarea { width: 100%; height: 100px; background: #1C1C1E; color: white; border-radius: 12px; padding: 15px; border: none; }
        .scan-box { background: #1C1C1E; padding: 20px; border-radius: 12px; margin: 20px 0; text-align: center; }
        button { width: 100%; padding: 18px; background: #FF3B30; color: white; border: none; border-radius: 12px; font-weight: bold; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Subscription Killer</h1>
        <form method="post" enctype="multipart/form-data">
            <textarea name="text_input" placeholder="Paste statement text..."></textarea>
            <div class="scan-box">
                <input type="file" name="image" accept="image/*" capture="environment">
            </div>
            <button type="submit">RUN EXTRACTION</button>
        </form>
        {% if result %}<div style="margin-top:20px;"><h3>Results:</h3><pre>{{ result }}</pre></div>{% endif %}
    </div>
</body>
</html>
"""

def analyze_with_vision(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": "Extract all recurring subscription charges from this bank statement. Return as JSON."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]}]
    }
    response = requests.post(URL, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        if 'image' in request.files and request.files['image'].filename:
            image_data = request.files['image'].read()
            result = analyze_with_vision(image_data)
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run()
