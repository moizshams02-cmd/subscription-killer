from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body style="font-family:sans-serif; background:#000; color:#fff; padding:20px;">
    <h2>Financial Auditor</h2>
    <form id="u">
        <input type="file" id="f" accept="image/*" capture="environment" multiple required>
        <button type="submit" id="b" style="padding:10px; width:100%;">AUDIT BATCH</button>
    </form>
    <div id="r" style="margin-top:20px;"></div>
