from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: sans-serif; background: #000; color: #fff; padding: 20px; }
    .card { background: #1a1a1a; padding: 15px; border-radius: 12px; margin-bottom: 20px; }
    .btn { padding: 16px; background: #fff; color: #000; border-radius: 8px; font-weight: bold; width: 100%; border: none; cursor: pointer; }
    table { width: 100%; color: #fff; border-collapse: collapse; }
    th, td { padding: 8px; border-bottom: 1px solid #333; text-align: left; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*" capture="environment" required style="margin-bottom:10px;">
        <button type="submit" class="btn">SCAN STATEMENT</button>
    </form>
    <div>{{ error|safe }}</div>
    <div>{{ table_html|safe }}</div>
</body>
</html>
"""

def process_data(image_bytes):
