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
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: sans-serif; background: #000; color: #fff; padding: 20px; }
    .card { background: #1a1a1a; padding: 15px; border-radius: 12px; margin-bottom: 20px; }
    .stat-val { font-size: 24px; font-weight: bold; color: #FF3B30; }
    .btn { padding: 16px; background: #fff; color: #000; border-radius: 8px; font-weight: bold; width: 100%; border: none; cursor: pointer; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <div class="card">MONTHLY BLEED<div class="stat-val">${{ total }}</div></div>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment" required style="margin-bottom:10px;">
        <button type="submit" class="btn">SCAN STATEMENT</button>
    </form>
    <div>{{ table_html|safe }}</div>
</body>
</html>
"""

def process_data(image_bytes):
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [
            {
                "role": "system", 
                "content": "You are a financial auditor. Identify ONLY recurring subscriptions. IGNORE retail/gas/groceries. Return ONLY a JSON list with 's' (Service), 'a' (Amount), 'c' (Strategy)."
            },
            {
                "role":
