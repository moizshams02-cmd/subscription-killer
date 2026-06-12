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
    body { font-family: -apple-system, sans-serif; background: #000; color: #fff; padding: 20px; }
    .stats { display: flex; gap: 10px; margin-bottom: 20px; }
    .stat-box { background: #1a1a1a; padding: 15px; border-radius: 12px; flex: 1; border: 1px solid #333; }
    .stat-val { font-size: 24px; font-weight: bold; color: #FF3B30; }
    .card { background: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; margin-top: 20px;}
    table { width: 100%; border-collapse: collapse; }
    th { color: #888; font-size: 11px; text-transform: uppercase; text-align: left; padding: 10px; border-bottom: 1px solid #333; }
    td { padding: 12px 10px; border-bottom: 1px solid #222; font-size: 14px; vertical-align: top; }
    button { width: 100%; padding: 16px; background: #fff; color: #000; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <div class="stats">
        <div class="stat-box">MONTHLY BLEED<div class="stat-val">${{ total }}</div></div>
    </div>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment">
        <button type="submit">EXECUTE FINANCIAL SCAN</button>
    </form>
    {% if table_html %}
    <div class="card">
        <h3>Detected Subscriptions</h3>
        {{ table_html|safe }}
    </div>
    {% endif %}
</body>
</html>
"""

def process_data(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # ADVANCED FILTER PROMPT: Filters out one-time charges
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages":
