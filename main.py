from flask import Flask, render_template_string, request
import os

# This must be at the top level so Vercel can detect it
app = Flask(__name__)

# --- Your app logic and routes ---
@app.route('/')
def index():
    return "Application is running"

# IMPORTANT: Do not include the 'if __name__ == "__main__": app.run()' block
