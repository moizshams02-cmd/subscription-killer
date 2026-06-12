import base64
import requests
import os
import json
from flask import Flask, render_template_string, request

app = Flask(__name__)
# Ensure API_KEY is set in Vercel Environment Variables
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
    table { width:
