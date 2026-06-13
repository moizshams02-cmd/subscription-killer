from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

# REQUIRED: Top-level Flask instance
app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment">
        <button type="submit">SCAN</button>
    </form>
    <div id="result">{{ result|safe }}</div>
</body>
</html>
"""

def process_image(image_bytes):
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [{"role": "user", "content": [{"type": "text", "text": "Extract subscriptions and amounts as JSON list."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
    }
    # This is a placeholder for your actual API call
    return "Scanning in progress..."

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST' and 'image' in request.files:
        result = process_image(request.files['image'].read())
    return render_template_string(HTML_TEMPLATE, result=result)
