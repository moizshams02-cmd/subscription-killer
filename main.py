import requests
import json
from flask import Flask, render_template_string, request
from config import API_KEY 

app = Flask(__name__)
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subscription Killer</title>
    <style>
        body { font-family: sans-serif; background: #0A0A0A; color: white; padding: 20px; }
        .container { max-width: 500px; margin: auto; }
        textarea { width: 100%; height: 100px; background: #1C1C1E; color: white; border-radius: 12px; padding: 15px; border: none; }
        button { width: 100%; padding: 18px; background: #FF3B30; color: white; border: none; border-radius: 12px; font-weight: bold; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Subscription Killer</h1>
        <form method="post">
            <textarea name="text_input" placeholder="Paste statement text here..."></textarea>
            <button type="submit">RUN ANALYSIS</button>
        </form>
        {% if result %}<div style="margin-top:20px;"><h3>Results:</h3><pre>{{ result }}</pre></div>{% endif %}
    </div>
</body>
</html>
"""

def analyze_text(text):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"Extract subscription charges from this text: {text}"}]
    }
    response = requests.post(URL, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        text = request.form.get('text_input')
        if text:
            result = analyze_text(text)
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run()
