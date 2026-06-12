import base64
import requests
import json
from flask import Flask, render_template_string, request
from config import API_KEY 

app = Flask(__name__)
URL = "https://api.groq.com/openai/v1/chat/completions"

# ... [Keep your HTML_TEMPLATE from the previous version] ...

def analyze_with_vision(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # Try this specific model ID for Vision
    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": "Extract all recurring subscription charges from this bank statement. Return as JSON."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]}]
    }
    response = requests.post(URL, headers=headers, json=payload)
    
    # Debugging: Print error if it fails
    if response.status_code != 200:
        return f"API Error: {response.text}"
        
    return response.json()['choices'][0]['message']['content']

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        if 'image' in request.files and request.files['image'].filename:
            image_data = request.files['image'].read()
            result = analyze_with_vision(image_data)
        elif request.form.get('text_input'):
            # Fallback to text analysis if image fails
            result = "Vision failed, please use text input or check API key."
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run()
