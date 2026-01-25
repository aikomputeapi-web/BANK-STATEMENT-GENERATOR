#!/usr/bin/env python3
"""
Wells Fargo Bank Statement Generator

Generates realistic bank statements with mock transaction data for a retail business.
Edit config.yaml to customize account holder information and statement period.

Usage:
    python generator.py
"""

import random
import yaml
from datetime import date, datetime, timedelta
from pathlib import Path

from src.models import (
    AccountHolder, AccountInfo, Address, BankStatement,
    StatementPeriod, StatementSummary
)
from src.transaction_gen import TransactionGenerator
from src.pdf_generator import StatementPDFGenerator


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def parse_statement_period(config: dict) -> StatementPeriod:
    """Parse statement period from config."""
    period_config = config['statement_period']
    
    if period_config['mode'] == 'auto':
        # Last 90 days
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
    else:
        # Manual dates
        start_date = datetime.strptime(period_config['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(period_config['end_date'], '%Y-%m-%d').date()
    
    return StatementPeriod(start_date=start_date, end_date=end_date)


def create_account_holder(config: dict) -> AccountHolder:
    """Create AccountHolder from config."""
    holder_config = config['account_holder']
    addr_config = holder_config['address']
    
    address = Address(
        street=addr_config['street'],
        city=addr_config['city'],
        state=addr_config['state'],
        zip_code=addr_config['zip']
    )
    
    return AccountHolder(name=holder_config['name'], address=address)


def create_account_info(config: dict) -> AccountInfo:
    """Create AccountInfo from config."""
    acct_config = config['account_info']
    
    return AccountInfo(
        account_number=acct_config['account_number'],
        routing_number=acct_config['routing_number'],
        account_type=acct_config.get('account_type', 'Wells Fargo Business Checking')
    )


def main():
    """Main entry point for statement generation."""
    print("=" * 60)
    print("Wells Fargo Bank Statement Generator")
    print("=" * 60)
    
    # Load configuration
    print("\n[1/5] Loading configuration from config.yaml...")
    config = load_config()
    
    # Parse configuration
    account_holder = create_account_holder(config)
    account_info = create_account_info(config)
    period = parse_statement_period(config)
    
    print(f"      Account Holder: {account_holder.name}")
    print(f"      Account Number: {account_info.account_number}")
    print(f"      Statement Period: {period.start_date} to {period.end_date}")
    
    # Generate starting balance
    business = config['business_profile']
    starting_balance = round(
        random.uniform(
            business['starting_balance_min'],
            business['starting_balance_max']
        ), 
        2
    )
    print(f"\n[2/5] Starting balance: ${starting_balance:,.2f}")
    
    # Generate transactions
    print(f"\n[3/5] Generating transactions for ${business['monthly_revenue']:,}/month retail business...")
    generator = TransactionGenerator(
        monthly_revenue=business['monthly_revenue'],
        business_type=business['business_type']
    )
    
    transactions, ending_balance = generator.generate_transactions(period, starting_balance)
    print(f"      Generated {len(transactions)} transactions")
    
    # Calculate summary
    summary = StatementSummary.from_transactions(transactions, starting_balance)
    print(f"\n[4/5] Statement Summary:")
    print(f"      Beginning Balance: ${summary.beginning_balance:,.2f}")
    print(f"      Total Deposits:    ${summary.total_deposits:,.2f}")
    print(f"      Total Withdrawals: ${summary.total_withdrawals:,.2f}")
    print(f"      Ending Balance:    ${summary.ending_balance:,.2f}")
    
    # Create statement object
    statement = BankStatement(
        account_holder=account_holder,
        account_info=account_info,
        period=period,
        transactions=transactions,
        summary=summary
    )
    
    # Generate PDF
    print(f"\n[5/5] Generating PDF statement...")
    output_dir = config['output']['directory']
    pdf_gen = StatementPDFGenerator(output_dir=output_dir)
    
    filepath = pdf_gen.generate(statement)
    
    print(f"\n{'=' * 60}")
    print(f"✓ Statement generated successfully!")
    print(f"  Output: {filepath}")
    print(f"  Pages:  {statement.page_count}")
    print(f"{'=' * 60}")
    
    return filepath


if __name__ == "__main__":
    main()
