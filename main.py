from flask import Flask, render_template_string, request
import base64
import requests
import json
import os

# Essential: Top-level definition for Vercel
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body style="font-family:sans-serif; background:#000; color:#fff; padding:20px;">
    <h2 style="color:#0f0;">Financial Auditor</h2>
    <form id="u">
        <input type="file" id="f" accept="image/*" capture="environment" multiple required>
        <button type="submit" id="b" style="padding:15px; width:100%; background:#333; color:#fff; border:none;">AUDIT ALL</button>
    </form>
    <div id="r" style="margin-top:20px;"></div>
    <script>
        document.getElementById('u').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('b');
            const resDiv = document.getElementById('r');
            btn.disabled = true;
            resDiv.innerHTML = "";
            const files = document.getElementById('f').files;
            
            for (let i = 0; i < files.length; i++) {
                if (i > 0) await new Promise(r => setTimeout(r, 2000));
                resDiv.innerHTML += `<div>Processing ${files[i].name}...</div>`;
