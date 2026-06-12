import json
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)
# Keep your original API_KEY import logic if needed, 
# or ensure API_KEY is defined here/imported from config
from config import API_KEY

URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_INSTRUCTION = """
You are the elite AI Brain of the 'Subscription Killer' enterprise dashboard.
Your job is to parse raw text or image content, identify recurring subscription metrics, and ignore standard everyday living expenses.
Return a valid JSON object with a 'subscriptions' key containing an array. 
For every subscription, provide: 
1. 'service_name': Cleaned up name
2. 'cost': Price as a float number
3. 'currency_symbol': Default to '$'
4. 'status': Default to 'Active'
5. 'cancel_method': Step-by-step best cancel method.
"""

def analyze_input(data_input):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": f"Analyze these transactions: {data_input}"}
        ],
        "temperature": 0.1
    }
    response = requests.post(URL, headers=headers, json=payload)
    return json.loads(response.json()['choices'][0]['message']['content'])

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        # Check if user sent an image (Camera Scan)
        if 'image' in request.files and request.files['image'].filename != '':
            # For now, we simulate image processing. 
            # Real vision requires sending the bytes to a vision-enabled model.
            results = analyze_input("User uploaded an image of a bank statement.")
        else:
            # Standard Text Paste
            text_input = request.form.get('text_input', '')
            if text_input:
                results = analyze_input(text_input)
                
    return render_template_string(HTML_TEMPLATE, results=results)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Subscription Killer Global</title>
    <style>
        body { font-family: sans-serif; background-color: #0A0A0A; color: white; padding: 20px; }
        textarea { width: 100%; height: 100px; background: #1C1C1E; color: white; border-radius: 10px; }
        .scan-btn { background: #FF3B30; color: white; padding: 15px; border: none; width: 100%; border-radius: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <textarea name="text_input" placeholder="Paste bank data here..."></textarea>
        <br><br>
        <label>OR Scan Statement:</label>
        <input type="file" name="image" accept="image/*" capture="environment">
        <br><br>
        <button type="submit" class="scan-btn">RUN EXTRACTION</button>
    </form>
</body>
</html>
"""

if __name__ == '__main__':
    app.run()
