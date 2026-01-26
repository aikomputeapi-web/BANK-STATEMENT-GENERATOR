#!/usr/bin/env python3
"""
Bank Statement Generator - Desktop Application Launcher
Double-click this to run the application with a GUI.
"""

import os
import sys
import webbrowser
import socket
from threading import Timer, Thread
from pathlib import Path

# Ensure we can find our modules
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys._MEIPASS)
    WORKING_DIR = Path(os.path.dirname(sys.executable))
else:
    # Running as script
    BASE_DIR = Path(__file__).parent
    WORKING_DIR = BASE_DIR

os.chdir(WORKING_DIR)
sys.path.insert(0, str(BASE_DIR))

from flask import Flask, render_template, request, jsonify, send_file
from faker import Faker
import random
import calendar
from datetime import date, datetime, timedelta

from src.models import (
    AccountHolder, AccountInfo, Address, BankStatement,
    StatementPeriod, StatementSummary
)
from src.transaction_gen import TransactionGenerator
from src.pdf_generator import StatementPDFGenerator

# Create Flask app
app = Flask(__name__, 
            template_folder=str(BASE_DIR / 'templates_web'), 
            static_folder=str(BASE_DIR / 'static'))
fake = Faker()

# San Jose area addresses for mock data
MOCK_STREETS = [
    "123 MAIN ST", "456 OAK AVE", "789 MAPLE DR", "1010 TECH BLVD",
    "2020 INNOVATION WAY", "555 STARTUP LN", "777 VENTURE CT",
    "888 SILICON AVE", "999 VALLEY RD", "1234 ENTERPRISE DR",
]

MOCK_CITIES = [
    ("SAN JOSE", "CA", "95110"), ("SAN JOSE", "CA", "95112"),
    ("SAN JOSE", "CA", "95125"), ("SAN JOSE", "CA", "95139"),
    ("SANTA CLARA", "CA", "95050"), ("SUNNYVALE", "CA", "94086"),
    ("MOUNTAIN VIEW", "CA", "94040"), ("CUPERTINO", "CA", "95014"),
    ("PALO ALTO", "CA", "94301"), ("MILPITAS", "CA", "95035"),
]


def get_month_range(year: int, month: int):
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day


def get_previous_months(num_months: int):
    today = date.today()
    if today.month == 1:
        year, month = today.year - 1, 12
    else:
        year, month = today.year, today.month - 1
    
    months = []
    for i in range(num_months):
        first_day, last_day = get_month_range(year, month)
        months.append((first_day, last_day))
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
    return list(reversed(months))


@app.route('/')
def index():
    defaults = {
        'name': '', 'street': '', 'city': 'SAN JOSE', 'state': 'CA', 'zip': '95110',
        'account_number': ''.join([str(random.randint(0, 9)) for _ in range(10)]),
        'routing_number': '121042882', 'account_type': 'Wells Fargo Everyday Checking',
        'period_mode': '1month',
        'start_date': (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'end_date': date.today().strftime('%Y-%m-%d'),
        'monthly_revenue': 100000, 'business_type': 'retail',
        'starting_balance_min': 15000, 'starting_balance_max': 50000,
    }
    return render_template('index.html', defaults=defaults)


@app.route('/generate-mock-data', methods=['POST'])
def generate_mock_data():
    name = fake.name().upper()
    street = random.choice(MOCK_STREETS)
    city, state, zip_code = random.choice(MOCK_CITIES)
    return jsonify({'name': name, 'street': street, 'city': city, 'state': state, 'zip': zip_code})


@app.route('/generate-statement', methods=['POST'])
def generate_statement():
    try:
        data = request.json
        
        address = Address(street=data['street'].upper(), city=data['city'].upper(),
                         state=data['state'].upper(), zip_code=data['zip'])
        account_holder = AccountHolder(name=data['name'].upper(), address=address)
        account_info = AccountInfo(account_number=data['account_number'],
                                   routing_number=data['routing_number'],
                                   account_type=data['account_type'])
        
        period_mode = data['period_mode']
        if period_mode == '1month':
            periods = get_previous_months(1)
        elif period_mode == '2months':
            periods = get_previous_months(2)
        elif period_mode == '3months':
            periods = get_previous_months(3)
        elif period_mode == '90days':
            periods = [(date.today() - timedelta(days=90), date.today())]
        else:
            periods = [(datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
                       datetime.strptime(data['end_date'], '%Y-%m-%d').date())]
        
        # Ensure output directory exists
        output_dir = WORKING_DIR / 'output'
        output_dir.mkdir(exist_ok=True)
        
        pdf_gen = StatementPDFGenerator(output_dir=str(output_dir))
        generator = TransactionGenerator(monthly_revenue=float(data['monthly_revenue']),
                                        business_type=data['business_type'])
        
        if len(periods) > 1:
            statements_info = []
            total_transactions = total_pages = 0
            current_balance = round(random.uniform(float(data['starting_balance_min']),
                                                   float(data['starting_balance_max'])), 2)
            
            for start_date, end_date in periods:
                period = StatementPeriod(start_date=start_date, end_date=end_date)
                transactions, ending_balance = generator.generate_transactions(period, current_balance)
                summary = StatementSummary.from_transactions(transactions, current_balance)
                statement = BankStatement(account_holder=account_holder, account_info=account_info,
                                         period=period, transactions=transactions, summary=summary)
                filepath = pdf_gen.generate(statement)
                statements_info.append({'filename': os.path.basename(filepath),
                                       'period': start_date.strftime('%b %Y'),
                                       'transactions': len(transactions), 'pages': statement.page_count})
                total_transactions += len(transactions)
                total_pages += statement.page_count
                current_balance = ending_balance
            
            return jsonify({'success': True, 'statements': statements_info,
                           'totals': {'total_statements': len(statements_info),
                                     'total_transactions': total_transactions, 'total_pages': total_pages}})
        else:
            start_date, end_date = periods[0]
            period = StatementPeriod(start_date=start_date, end_date=end_date)
            starting_balance = round(random.uniform(float(data['starting_balance_min']),
                                                    float(data['starting_balance_max'])), 2)
            transactions, _ = generator.generate_transactions(period, starting_balance)
            summary = StatementSummary.from_transactions(transactions, starting_balance)
            statement = BankStatement(account_holder=account_holder, account_info=account_info,
                                     period=period, transactions=transactions, summary=summary)
            filepath = pdf_gen.generate(statement)
            
            return jsonify({'success': True, 'filename': os.path.basename(filepath),
                           'summary': {'beginning_balance': f'${summary.beginning_balance:,.2f}',
                                      'total_deposits': f'${summary.total_deposits:,.2f}',
                                      'total_withdrawals': f'${summary.total_withdrawals:,.2f}',
                                      'ending_balance': f'${summary.ending_balance:,.2f}',
                                      'transaction_count': len(transactions), 'pages': statement.page_count}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    filepath = WORKING_DIR / 'output' / filename
    if filepath.exists():
        return send_file(str(filepath), as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def open_browser(port):
    webbrowser.open(f'http://127.0.0.1:{port}')


def main():
    port = find_free_port()
    
    print("\n" + "=" * 50)
    print("  Bank Statement Generator - Desktop App")
    print("=" * 50)
    print(f"\n  Server running at: http://127.0.0.1:{port}")
    print("  Opening browser automatically...")
    print("\n  Close this window to stop the application")
    print("=" * 50 + "\n")
    
    Timer(1.0, open_browser, args=[port]).start()
    
    # Run Flask with no reloader (important for PyInstaller)
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)


if __name__ == '__main__':
    main()
