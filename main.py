import base64
import requests
import os
from flask import Flask, render_template_string, request

app = Flask(__name__)
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: -apple-system, sans-serif; background: #000; color: #fff; padding: 20px; }
    .card { background: #1a1a1a; padding: 20px; border-radius: 12px; margin-top: 20px; border: 1px solid #333; }
    table { width: 100%; border-collapse: collapse; }
    th { color: #888; font-size: 11px; text-transform: uppercase; text-align: left; padding: 10px; border-bottom: 1px solid #333; }
    td { padding: 12px 10px; border-bottom: 1px solid #222; font-size: 14px; }
    .price { color: #FF3B30; font-weight: bold; }
    button { width: 100%; padding: 16px; background: #fff; color: #000; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment">
        <button type="submit">SCAN ENTIRE STATEMENT</button>
    </form>
    {% if result %}
    <div class="card">
        <h3>Analysis Result</h3>
        {{ result|safe }}
    </div>
    {% endif %}
</body>
</html>
"""

def analyze_image(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # CRITICAL: Instructing the AI to scan every line and not truncate
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "You are a senior financial auditor. Your task is to scan the ENTIRE provided image for EVERY transaction. List every single item found as an HTML table row. Do not truncate the list. Clean merchant names into professional service names. For each item, provide a 'Service', 'Amount', and 'Cancellation Strategy'."},
            {"role": "user", "content": [
                {"type": "text", "text": "Extract all transactions from this entire document. Return ONLY a comprehensive HTML table. Do not stop until every line is processed."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]
    }
    
    response = requests.post(URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return f"API Error: {response.text}"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST' and 'image' in request.files and request.files['image'].filename:
        result = analyze_image(request.files['image'].read())
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True)
