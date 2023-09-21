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
    items = fetch_data_from_api('item')
    invoices = fetch_data_from_api('invoice')
    payments = fetch_data_from_api('payment')

    num_suppliers = sum(1 for contact in contacts if contact.get('is_supplier'))
    num_customers = sum(1 for contact in contacts if contact.get('is_customer'))
    num_items = len(items)
    num_invoices = len(invoices)
    num_payments = len(payments)

    total_items_in_inventory = sum(item['quantity_on_hand'] for item in items)
    
    total_invoices = sum(invoice['total'] for invoice in invoices)
    total_payments = sum(payment['total'] for payment in payments)

    total_invoices = sum(invoice['total'] for invoice in invoices)
    total_payments = sum(payment['total'] for payment in payments)
    
    total_paid = sum(invoice['total'] - invoice['amount_due'] for invoice in invoices)
    total_outstanding = sum(invoice['amount_due'] for invoice in invoices)
    
    total_received = sum(payment['total'] for payment in payments if payment['is_income'])
    total_to_be_paid = sum(payment['total'] for payment in payments if not payment['is_income'])

    return render_template('index.html', title='Business Analytics Dashboard', 
                            num_suppliers=num_suppliers, num_customers=num_customers,
                            num_items=num_items, num_invoices=num_invoices,
                            num_payments=num_payments, total_invoices=total_invoices,
                            total_payments=total_payments, total_paid=total_paid, 
                            total_outstanding=total_outstanding,
                            total_received=total_received, total_to_be_paid=total_to_be_paid,
                            total_items_in_inventory=total_items_in_inventory)

@app.route('/data_analytics')
def data_analytics():
    return render_template('data_analytics.html', title='Data Analytics')

@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))