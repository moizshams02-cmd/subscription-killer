import json
import requests
from flask import Flask, render_template_string, request, redirect, url_for, session
from config import API_KEY

app = Flask(__name__)
URL = "https://api.groq.com/openai/v1/chat/completions"
app.secret_key = "enterprise_protection_node_secret_key_ultra"

system_instruction = """
You are the elite AI Brain of the 'Subscription Killer' enterprise dashboard.
Your job is to parse raw text, identify recurring subscription metrics, and ignore standard everyday living expenses.

CRITICAL FORMATTING RULE: You must translate the data into a brand new schema. 
Return a valid JSON object with a 'subscriptions' key containing an array. For every single subscription found, use exactly these keys:
1. 'service_name': Cleaned up name of the service (e.g., 'Netflix').
2. 'cost': The price as a float number only.
3. 'currency_symbol': Detect the symbol used (e.g., '$', '€', '£'). Default to '$' if none found.
4. 'status': Default to 'Active'.
5. 'cancel_method': Step-by-step best cancel method.
"""

def analyze_custom_transactions(raw_text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Analyze these raw transactions: {raw_text}"}
        ],
        "temperature": 0.1
    }
    response = requests.post(URL, headers=headers, json=payload)
    data = response.json()
    ai_reply = data["choices"][0]["message"]["content"]
    return json.loads(ai_reply)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subscription Killer Global</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0A0A0C; color: #ffffff; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 25px; }
        .header h1 { color: #ff3b30; margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.5px; }
        .header p { color: #8e8e93; margin-top: 5px; font-size: 14px; }
        
        .metric-banner { background: linear-gradient(135deg, #1c1c1e 0%, #0A0A0C 100%); border-radius: 16px; padding: 20px; border: 1px solid #2c2c2e; margin-bottom: 25px; display: flex; justify-content: space-around; text-align: center; }
        .metric-val { font-size: 24px; font-weight: bold; color: #ff3b30; margin-top: 5px; }
        .metric-lbl { font-size: 11px; color: #aeaeb2; text-transform: uppercase; letter-spacing: 1px; }

        .input-box { background-color: #1c1c1e; border-radius: 16px; padding: 20px; border: 1px solid #2c2c2e; margin-bottom: 25px; }
        textarea { width: 100%; height: 90px; background-color: #2c2c2e; border: 1px solid #3a3a3c; border-radius: 10px; color: white; padding: 12px; font-family: inherit; box-sizing: border-box; resize: none; font-size: 14px; }
        .scan-btn { width: 100%; background-color: #ff3b30; color: white; border: none; padding: 15px; border-radius: 10px; font-weight: bold; font-size: 16px; margin-top: 12px; cursor: pointer; }
        
        .card { background-color: #1c1c1e; border-radius: 16px; padding: 20px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #2c2c2e; }
        .details h3 { margin: 0 0 6px 0; font-size: 18px; color: #ffffff; }
        .details p { margin: 3px 0; font-size: 13px; color: #aeaeb2; }
        .cost { font-weight: 800; color: #34c759; font-size: 18px; }
        .kill-btn { background-color: transparent; color: #ff3b30; border: 2px solid #ff3b30; padding: 10px 18px; border-radius: 8px; font-weight: bold; font-size: 13px; cursor: pointer; }
        .kill-btn:hover { background-color: #ff3b30; color: white; }
        .no-data { text-align: center; color: #8e8e93; padding: 30px; border: 2px dashed #2c2c2e; border-radius: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💥 Subscription Killer</h1>
            <p>Global AI Financial Isolation Network</p>
        </div>
        
        <div class="metric-banner">
            <div>
                <div class="metric-lbl">Isolated Bleed</div>
                <div class="metric-val">${{ "%.2f"|format(total_monthly) }}</div>
            </div>
            <div style="border-left: 1px solid #3a3a3c; height: 40px; margin-top: 5px;"></div>
            <div>
                <div class="metric-lbl">Your Yearly Saved</div>
                <div class="metric-val" style="color: #34c759;">${{ "%.2f"|format(total_yearly) }}</div>
            </div>
        </div>
        
        <div class="input-box">
            <form method="POST" action="/scan">
                <textarea name="transaction_data" placeholder="Paste bank data here... Secure isolated scanning layer active."></textarea>
                <button type="submit" class="scan-btn">RUN EXTRACTION</button>
            </form>
        </div>
        
        <div id="dashboard">
            <h2 style="font-size: 18px; margin-bottom: 15px; padding-left: 5px;">🔒 Private Storage Rows</h2>
            {% if subs %}
                {% for sub in subs %}
                <div class="card">
                    <div class="details">
                        <h3>🏷️ {{ sub.service_name }}</h3>
                        <p class="cost">{{ sub.currency_symbol }}{{ sub.cost }} <span style="font-size:11px; font-weight:normal; color:#8e8e93;">/month</span></p>
                        <p>⚙️ Session Track: <span style="color:#ff9500;">● Browser Sandbox</span></p>
                        <p>🛠️ Strategy: {{ sub.cancel_method }}</p>
                    </div>
                    <form method="POST" action="/delete/{{ loop.index0 }}" style="margin:0;">
                        <button class="kill-btn" type="submit">TERMINATE</button>
                    </form>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-data">
                    <p>Browser sandbox empty. Input your transaction log streams to isolate leaks.</p>
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    subscriptions_list = session.get("subscriptions", [])
    total_monthly = 0.0
    for sub in subscriptions_list:
        try:
            total_monthly += float(sub.get('cost', 0))
        except:
            pass
    total_yearly = total_monthly * 12
    return render_template_string(HTML_TEMPLATE, subs=subscriptions_list, total_monthly=total_monthly, total_yearly=total_yearly)

@app.route('/scan', methods=['POST'])
def scan():
    user_input = request.form.get('transaction_data', '')
    if user_input.strip():
        try:
            ai_data = analyze_custom_transactions(user_input)
            new_subs = ai_data.get("subscriptions", [])
            if "subscriptions" not in session:
                session["subscriptions"] = []
            current_subs = session["subscriptions"]
            current_subs.extend(new_subs)
            session["subscriptions"] = current_subs
        except Exception as e:
            return f"<h2>AI Pipeline Malfunction: {e}</h2>"
    return redirect(url_for('home'))

@app.route('/delete/<int:sub_id>', methods=['POST'])
def delete(sub_id):
    if "subscriptions" in session:
        current_subs = session["subscriptions"]
        if 0 <= sub_id < len(current_subs):
            current_subs.pop(sub_id)
            session["subscriptions"] = current_subs
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
