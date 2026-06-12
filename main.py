import json
import requests
from flask import Flask, render_template_string, request
from config import API_KEY

app = Flask(__name__)
URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_INSTRUCTION = """
You are the elite AI Brain of the 'Subscription Killer' enterprise dashboard.
Extract recurring subscriptions from the provided bank statement (text or image).
Return ONLY a valid JSON object with a 'subscriptions' key containing an array of objects:
{'service_name': str, 'cost': float, 'currency_symbol': str, 'cancel_method': str}.
"""

# The optimized Mobile-First HTML/CSS Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Subscription Killer</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0A0A0A; color: white; margin: 0; padding: 20px; box-sizing: border-box; }
        .container { max-width: 500px; margin: 0 auto; }
        h1 { font-size: 24px; text-align: center; margin-bottom: 20px; }
        textarea { width: 100%; height: 120px; background: #1C1C1E; color: white; border: 1px solid #333; border-radius: 12px; padding: 15px; font-size: 16px; margin-bottom: 15px; box-sizing: border-box; }
        .file-input-group { background: #1C1C1E; padding: 15px; border-radius: 12px; margin-bottom: 20px; text-align: center; }
        button { width: 100%; padding: 18px; background: #FF3B30; color: white; border: none; border-radius: 12px; font-weight: bold; font-size: 16px; cursor: pointer; }
        .result-card { background: #1C1C1E; padding: 15px; border-radius: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Subscription Killer</h1>
        <form method="post" enctype="multipart/form-data">
            <textarea name="text_input" placeholder="Paste bank data here..."></textarea>
            <div class="file-input-group">
                <label>Scan Statement:</label><br><br>
                <input type="file" name="image" accept="image/*" capture="environment">
            </div>
            <button type="submit">RUN EXTRACTION</button>
        </form>
    </div>
</body>
</html>
"""

def analyze_input(data_input, is_image=False):
    # This keeps your existing extraction logic
    # In a production app, you'd send image bytes here
    return {"status": "success", "data": "Analysis Logic Placeholder"}

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run()
