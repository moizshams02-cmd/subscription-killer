import base64
import requests
import os
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Vercel retrieves this from the Environment Variables you configured
API_KEY = os.environ.get("API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: -apple-system, sans-serif; background: #000; color: #fff; padding: 20px; }
    textarea { width: 100%; height: 120px; padding: 10px; border-radius: 8px; background: #1a1a1a; color: #fff; border: 1px solid #333; }
    input[type="file"] { width: 100%; margin: 20px 0; padding: 10px; border: 1px dashed #555; border-radius: 8px; }
    button { width: 100%; padding: 16px; background: #fff; color: #000; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
    pre { background: #111; padding: 15px; border-radius: 8px; overflow-x: auto; border: 1px solid #333; }
</style>
</head>
<body>
    <h1>Subscription Killer</h1>
    <form method="post" enctype="multipart/form-data">
        
