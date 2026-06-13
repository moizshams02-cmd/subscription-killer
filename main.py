from flask import Flask
# REQUIRED: Vercel needs the 'app' instance defined at the top level
app = Flask(__name__)

from flask import render_template_string, request
import base64
import requests
import os
import json

# Configuration
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

# The HTML includes client-side resizing to keep payload under Vercel's 4.5MB limit
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
    <h1>Batch Financial Auditor</h1>
    <form method="post" enctype="multipart/form-data" id="uploadForm">
        <input type="file" name="images" id="fileInput" accept="image/*" multiple required style="margin-bottom:10px;">
        <button type="submit" class="btn">AUDIT BATCH</button>
    </form>
    <div id="status" style="margin-top: 10px;"></div>
    <div>{{ table_html|safe }}</div>
    <script>
        document.getElementById('uploadForm').onsubmit = async (e) => {
            e.preventDefault();
            document.getElementById('status').innerText = "Compressing and uploading...";
            const files = document.getElementById('fileInput').files;
            const formData = new FormData();
            
            for (let file of files) {
                const bitmap = await createImageBitmap(file);
                const canvas = document.createElement('canvas');
                // Resize to max 800px width to keep payload small
                const scale = Math.min(800 / bitmap.width, 1);
                canvas.width = bitmap.width * scale;
                canvas.height = bitmap.height
