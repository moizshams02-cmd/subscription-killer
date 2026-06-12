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
    .stat-box { background: #1a1a1a; padding: 15px; border-radius: 12px; border: 1px solid #333; }
    .stat-val { font-size: 24px; font-weight: bold; color: #FF3B30; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { color: #888; font-size: 11px; text-transform: uppercase; text-align: left; padding: 10px; border-bottom: 1px solid #333; }
    td { padding: 12px 10px; border-bottom: 1px solid #222; font-size: 14px; }
    button { width: 100%; padding: 16px; background: #fff; color: #0
