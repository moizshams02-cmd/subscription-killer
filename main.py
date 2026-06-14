from flask import Flask, render_template_string, request
import base64
import requests
import json
import os

# TOP-LEVEL: Required for Vercel to detect the app
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<body style="font-family:sans-serif; background:#000; color:#fff; padding:20px;">
    <h2>Financial Auditor</h2>
    <form id="u">
        <input type="file" id="f" accept="image/*" multiple required>
        <button type="submit" id="b" style="padding:15px; width:100%; background:#0f0; color:#000; border:none;">AUDIT ALL</button>
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
                
                const bmp = await createImageBitmap(files[i]);
                const canvas = document.createElement('canvas');
                const scale = Math.min(600 / bmp.width, 1);
                canvas.width = bmp.width * scale; canvas.height = bmp.height * scale;
                canvas.getContext('2d').drawImage(bmp, 0, 0, canvas.width, canvas.height);
                // Aggressive compression to prevent 413 Errors
                const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.1));
                
                const fd = new FormData();
                fd.append('i', blob);
                const res = await fetch('/', { method: 'POST', body: fd });
                resDiv.innerHTML += await res.text() + "<hr>";
            }
            btn.disabled = false;
        };
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE)
