from flask import Flask, render_template_string, request
import base64
import requests
import json
import os

app = Flask(__name__)

# [The HTML template remains the same as provided previously]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET': return render_template_string(HTML_TEMPLATE)
    api_key = os.environ.get('API_KEY')
    try:
        img = request.files.get("i")
        b64 = base64.b64encode(img.read()).decode('utf-8')
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": "Return JSON list [{'s':'desc','a':'amt','c':'date'}]. Image: data:image/jpeg;base64," + b64}]
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, 
                             json=payload, timeout=25)
        
        response_data = resp.json()
        
        # Robust check for success vs error
        if 'choices' in response_data:
            content = response_data['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
            data = json.loads(content)
            return "".join([f"<div>{i.get('s','-')} | {i.get('a','-')} | {i.get('c','-')}</div>" for i in data])
        else:
            # This will show the actual API error (e.g., rate limit) in your browser
            return f"API Error: {str(response_data.get('error', 'Unknown error'))}"
    except Exception as e:
        return f"Error: {str(e)}"
