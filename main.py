from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: sans-serif; background: #000; color: #fff; padding: 20px; }
    .btn { padding: 16px; background: #fff; color: #000; border-radius: 8px; font-weight: bold; width: 100%; border: none; cursor: pointer; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment" required style="margin-bottom:10px;">
        <button type="submit" class="btn">SCAN STATEMENT</button>
    </form>
    <div style="color: #ff3333; margin-top: 10px;">{{ error }}</div>
    <div>{{ table_html|safe }}</div>
</body>
</html>
"""

def process_data(image_bytes):
    api_key = os.environ.get("API_KEY")
    if not api_key: return "", "CRITICAL ERROR: API_KEY is missing."

    b64 = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Updated to a supported vision model
    payload = {
        "model": "
