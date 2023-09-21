import os
from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def fetch_data_from_api(endpoint):
    api_key = "e6506999-8738-4866-a13f-2a2cfb14ba99"
    headers = {"x-api-key": api_key}
    url = f"https://hackathon.syftanalytics.com/api/{endpoint}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        return []

@app.route('/')
def home():
    contacts = fetch_data_from_api('contacts')

    num_suppliers = sum([1 for contact in contacts if contact.get('is_supplier')])
    num_customers = sum([1 for contact in contacts if contact.get('is_customer')])

    return render_template('index.html', title='Business Dashboard', num_suppliers=num_suppliers, num_customers=num_customers)

@app.route('/data_analytics')
def data_analytics():
    return render_template('data_analytics.html', title='Data Analytics')

@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))