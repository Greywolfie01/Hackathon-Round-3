import os
from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

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
contacts = fetch_data_from_api('contacts')
items = fetch_data_from_api('item')
invoices = fetch_data_from_api('invoice')
payments = fetch_data_from_api('payment')

@app.route('/')
def home():

    num_suppliers = sum(1 for contact in contacts if contact.get('is_supplier'))
    num_customers = sum(1 for contact in contacts if contact.get('is_customer'))
    num_items = len(items)
    num_invoices = len(invoices)
    num_payments = len(payments)

    total_items_in_inventory = sum(item['quantity_on_hand'] for item in items)

    # Considering paid status, exchange rate, and currency for the total amount to be received and paid
    total_amount_to_be_received = sum(invoice['amount_due'] * invoice['exchange_rate'] if invoice['is_sale'] and not invoice['paid'] and invoice['currency'] != 'ZAR' else invoice['amount_due'] for invoice in invoices if invoice['is_sale'] and not invoice['paid'])
    total_amount_to_be_paid = sum(invoice['amount_due'] * invoice['exchange_rate'] if not invoice['is_sale'] and not invoice['paid'] and invoice['currency'] != 'ZAR' else invoice['amount_due'] for invoice in invoices if not invoice['is_sale'] and not invoice['paid'])

    # Considering exchange rate and currency for income and expense from invoices
    income_invoices = sum(invoice['total'] * invoice['exchange_rate'] if invoice['is_sale'] and invoice['currency'] != 'ZAR' else invoice['total'] for invoice in invoices if invoice['is_sale'])
    expense_invoices = sum(invoice['total'] * invoice['exchange_rate'] if not invoice['is_sale'] and invoice['currency'] != 'ZAR' else invoice['total'] for invoice in invoices if not invoice['is_sale'])

    # Considering exchange rate and currency for income and expense from payments
    income_payments = sum(payment['total'] if payment['is_income'] else 0 for payment in payments)
    expense_payments = sum(payment['total'] if not payment['is_income'] else 0 for payment in payments)

    return render_template('index.html', title='Business Analytics Dashboard', 
                            num_suppliers=num_suppliers, num_customers=num_customers,
                            num_items=num_items, num_invoices=num_invoices,
                            num_payments=num_payments,
                            total_items_in_inventory=total_items_in_inventory,
                            total_amount_to_be_received=total_amount_to_be_received,
                            total_amount_to_be_paid=total_amount_to_be_paid,
                            income_invoices=income_invoices,
                            expense_invoices=expense_invoices,
                            income_payments=income_payments,
                            expense_payments=expense_payments)

@app.route('/data_analytics')
def data_analytics():

    missing_supplier_emails = 0
    missing_supplier_phones = 0
    missing_customer_emails = 0
    missing_customer_phones = 0

    for contact in contacts:
        if contact['is_supplier']:
            if contact['email'] is None:
                missing_supplier_emails += 1
            if contact['phone'] is None:
                missing_supplier_phones += 1
        if contact['is_customer']:
            if contact['email'] is None:
                missing_customer_emails += 1
            if contact['phone'] is None:
                missing_customer_phones += 1

    low_inventory_items = [item['name'] for item in items if item['quantity_on_hand'] < 30]
    total_items_in_inventory = sum(item['quantity_on_hand'] for item in items)
    total_value_of_inventory = sum(item['quantity_on_hand'] * item['purchase_unit_price'] for item in items)
                
    # Calculate money coming in (revenue)
    revenue_invoices = [invoice for invoice in invoices if invoice['is_sale'] and invoice['paid']]
    
    revenue_values = [invoice['total'] for invoice in revenue_invoices]
    revenue_dates = [invoice['issue_date'] for invoice in revenue_invoices]
    revenue_dates = [date[:10] for date in revenue_dates]

    expense_invoices = [invoice for invoice in invoices if not invoice['is_sale'] and invoice['paid']]
    
    expense_values = [invoice['total'] for invoice in expense_invoices]
    expense_dates = [invoice['issue_date'] for invoice in expense_invoices]
    expense_dates = [date[:10] for date in expense_dates]

    # Filter the data to remove values above 10000
    filtered_revenue_values = [value for value in revenue_values if value <= 10000]
    filtered_expense_values = [value for value in expense_values if value <= 10000]

    # Render the template with the calculated values
    return render_template('data_analytics.html', title='Data Analytics', contacts=contacts, 
                            missing_supplier_emails=missing_supplier_emails, missing_supplier_phones=missing_supplier_phones, 
                            missing_customer_emails=missing_customer_emails, missing_customer_phones=missing_customer_phones,
                            items=items, low_inventory_items=low_inventory_items, total_value_of_inventory=total_value_of_inventory,
                            total_items_in_inventory=total_items_in_inventory, revenue_dates=revenue_dates, revenue_values=revenue_values,
                            expense_values=expense_values, expense_dates=expense_dates, filtered_revenue_values=filtered_revenue_values,
                            filtered_expense_values=filtered_expense_values)


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))