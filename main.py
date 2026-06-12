from flask import Flask, render_template_string, request
import base64
import requests
import os
import json

# REQUIRED: This must be in the global scope (not inside any function)
app = Flask(__name__)

# --- Rest of your functions (process_data, etc.) ---
# ...
# NOTE: REMOVE the if __name__ == '__main__': block at the bottom
