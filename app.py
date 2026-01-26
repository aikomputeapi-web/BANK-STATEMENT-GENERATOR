#!/usr/bin/env python3
"""
Bank Statement Generator - Web UI
A simple Flask-based frontend for generating bank statements.
"""

import os
import random
import webbrowser
import calendar
from datetime import date, datetime, timedelta
from pathlib import Path
from threading import Timer

from flask import Flask, render_template, request, jsonify, send_file
from faker import Faker

from src.models import (
    AccountHolder, AccountInfo, Address, BankStatement,
    StatementPeriod, StatementSummary
)
from src.transaction_gen import TransactionGenerator
from src.pdf_generator import StatementPDFGenerator

app = Flask(__name__, template_folder='templates_web', static_folder='static')
fake = Faker()

# San Jose area addresses for mock data
MOCK_STREETS = [
    "123 MAIN ST",
    "456 OAK AVE",
    "789 MAPLE DR",
    "1010 TECH BLVD",
    "2020 INNOVATION WAY",
    "555 STARTUP LN",
    "777 VENTURE CT",
    "888 SILICON AVE",
    "999 VALLEY RD",
    "1234 ENTERPRISE DR",
]

MOCK_CITIES = [
    ("SAN JOSE", "CA", "95110"),
    ("SAN JOSE", "CA", "95112"),
    ("SAN JOSE", "CA", "95125"),
    ("SAN JOSE", "CA", "95139"),
    ("SANTA CLARA", "CA", "95050"),
    ("SUNNYVALE", "CA", "94086"),
    ("MOUNTAIN VIEW", "CA", "94040"),
    ("CUPERTINO", "CA", "95014"),
    ("PALO ALTO", "CA", "94301"),
    ("MILPITAS", "CA", "95035"),
]


def get_month_range(year: int, month: int):
    """Get the first and last day of a month."""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day


def get_previous_months(num_months: int):
    """Get date ranges for the previous N complete months."""
    today = date.today()
    
    # Start from the previous month (most recent complete month)
    if today.month == 1:
        year = today.year - 1
        month = 12
    else:
        year = today.year
        month = today.month - 1
    
    months = []
    for i in range(num_months):
        first_day, last_day = get_month_range(year, month)
        months.append((first_day, last_day))
        
        # Go to previous month
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
    
    # Return in chronological order (oldest first)
    return list(reversed(months))


@app.route('/')
def index():
    """Render the main settings page."""
    # Default values (most common/average)
    defaults = {
        'name': '',
        'street': '',
        'city': 'SAN JOSE',
        'state': 'CA',
        'zip': '95110',
        'account_number': generate_account_number(),
        'routing_number': '121042882',  # Wells Fargo CA routing
        'account_type': 'Wells Fargo Everyday Checking',
        'period_mode': '1month',
        'start_date': (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'end_date': date.today().strftime('%Y-%m-%d'),
        'monthly_revenue': 100000,
        'business_type': 'retail',
        'starting_balance_min': 15000,
        'starting_balance_max': 50000,
    }
    return render_template('index.html', defaults=defaults)


@app.route('/generate-mock-data', methods=['POST'])
def generate_mock_data():
    """Generate mock name and address data."""
    name = fake.name().upper()
    street = random.choice(MOCK_STREETS)
    city, state, zip_code = random.choice(MOCK_CITIES)
    
    return jsonify({
        'name': name,
        'street': street,
        'city': city,
        'state': state,
        'zip': zip_code
    })


@app.route('/generate-statement', methods=['POST'])
def generate_statement():
    """Generate bank statement(s) from form data."""
    try:
        data = request.json
        
        # Create account holder
        address = Address(
            street=data['street'].upper(),
            city=data['city'].upper(),
            state=data['state'].upper(),
            zip_code=data['zip']
        )
        account_holder = AccountHolder(name=data['name'].upper(), address=address)
        
        # Create account info
        account_info = AccountInfo(
            account_number=data['account_number'],
            routing_number=data['routing_number'],
            account_type=data['account_type']
        )
        
        # Determine periods based on mode
        period_mode = data['period_mode']
        
        if period_mode == '1month':
            periods = get_previous_months(1)
        elif period_mode == '2months':
            periods = get_previous_months(2)
        elif period_mode == '3months':
            periods = get_previous_months(3)
        elif period_mode == '90days':
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
            periods = [(start_date, end_date)]
        else:  # manual
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            periods = [(start_date, end_date)]
        
        # Generate statement(s)
        pdf_gen = StatementPDFGenerator(output_dir='output')
        generator = TransactionGenerator(
            monthly_revenue=float(data['monthly_revenue']),
            business_type=data['business_type']
        )
        
        # For multi-month, generate separate statements with rolling balance
        if len(periods) > 1:
            statements_info = []
            total_transactions = 0
            total_pages = 0
            
            # Start with random starting balance
            current_balance = round(
                random.uniform(
                    float(data['starting_balance_min']),
                    float(data['starting_balance_max'])
                ), 2
            )
            
            for start_date, end_date in periods:
                period = StatementPeriod(start_date=start_date, end_date=end_date)
                
                transactions, ending_balance = generator.generate_transactions(period, current_balance)
                summary = StatementSummary.from_transactions(transactions, current_balance)
                
                statement = BankStatement(
                    account_holder=account_holder,
                    account_info=account_info,
                    period=period,
                    transactions=transactions,
                    summary=summary
                )
                
                filepath = pdf_gen.generate(statement)
                
                statements_info.append({
                    'filename': os.path.basename(filepath),
                    'period': f"{start_date.strftime('%b %Y')}",
                    'transactions': len(transactions),
                    'pages': statement.page_count
                })
                
                total_transactions += len(transactions)
                total_pages += statement.page_count
                
                # Use ending balance as starting balance for next month
                current_balance = ending_balance
            
            return jsonify({
                'success': True,
                'statements': statements_info,
                'totals': {
                    'total_statements': len(statements_info),
                    'total_transactions': total_transactions,
                    'total_pages': total_pages
                }
            })
        
        else:
            # Single statement
            start_date, end_date = periods[0]
            period = StatementPeriod(start_date=start_date, end_date=end_date)
            
            starting_balance = round(
                random.uniform(
                    float(data['starting_balance_min']),
                    float(data['starting_balance_max'])
                ), 2
            )
            
            transactions, ending_balance = generator.generate_transactions(period, starting_balance)
            summary = StatementSummary.from_transactions(transactions, starting_balance)
            
            statement = BankStatement(
                account_holder=account_holder,
                account_info=account_info,
                period=period,
                transactions=transactions,
                summary=summary
            )
            
            filepath = pdf_gen.generate(statement)
            
            return jsonify({
                'success': True,
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'summary': {
                    'beginning_balance': f'${summary.beginning_balance:,.2f}',
                    'total_deposits': f'${summary.total_deposits:,.2f}',
                    'total_withdrawals': f'${summary.total_withdrawals:,.2f}',
                    'ending_balance': f'${summary.ending_balance:,.2f}',
                    'transaction_count': len(transactions),
                    'pages': statement.page_count
                }
            })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download a generated statement."""
    filepath = Path('output') / filename
    if filepath.exists():
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


def generate_account_number():
    """Generate a random 10-digit account number."""
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])


def open_browser():
    """Open the web browser to the app."""
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    # Open browser after a short delay
    Timer(1.5, open_browser).start()
    print("\n" + "=" * 60)
    print("Bank Statement Generator - Web UI")
    print("=" * 60)
    print("\nStarting server at http://127.0.0.1:5000")
    print("Browser will open automatically...")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=False, port=5000)
