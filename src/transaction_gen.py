"""
Mock transaction generator for realistic retail business transactions.
Generates approximately $100k monthly revenue with appropriate expenses.
"""

import random
from datetime import date, timedelta
from typing import List, Tuple
from faker import Faker

from .models import Transaction, TransactionType, StatementPeriod

fake = Faker()


# Deposit templates for retail business
DEPOSIT_TEMPLATES = [
    # POS/Sales deposits
    ("ATM Cash Deposit on {date} {location} {atm_id}", (500, 3000)),
    ("POS Deposit {merchant_id}", (800, 5000)),
    ("Square Inc Deposit", (1500, 8000)),
    ("Stripe Transfer", (2000, 10000)),
    ("PayPal Transfer", (500, 3000)),
    ("Shopify Payments", (1000, 6000)),
    ("Credit Card Settlement", (2000, 8000)),
    ("ACH Credit {company}", (1000, 5000)),
    ("Wire Transfer In", (5000, 15000)),
    ("Mobile Deposit", (200, 1500)),
]

# Withdrawal templates
WITHDRAWAL_TEMPLATES = [
    # Supplier/Inventory payments
    ("Purchase authorized on {date} {supplier} Card {card_id}", (100, 2500)),
    ("ACH Debit {supplier}", (500, 5000)),
    ("Wire Transfer to {supplier}", (2000, 10000)),
    ("Check #{check_num} {supplier}", (500, 3000)),
    
    # Payroll
    ("ADP Payroll", (3000, 8000)),
    ("Gusto Payroll", (2500, 6000)),
    ("Payroll Direct Deposit", (2000, 5000)),
    
    # Rent/Lease
    ("Rent Payment {landlord}", (3000, 8000)),
    ("Commercial Lease Payment", (4000, 10000)),
    
    # Utilities
    ("PG&E Payment", (150, 500)),
    ("Verizon Business", (100, 300)),
    ("Comcast Business", (100, 250)),
    ("Water Utility Payment", (50, 150)),
    
    # Business expenses
    ("Amazon Business", (50, 500)),
    ("Staples Business", (30, 200)),
    ("Office Depot", (25, 150)),
    ("Uber USA 6787 EDI Paymnt {ref}", (10, 100)),
    ("Lyft Ride {location}", (8, 50)),
    
    # Bank fees
    ("Monthly Service Fee", (12, 25)),
    ("Overdraft Fee", (35, 35)),
    ("Wire Transfer Fee", (25, 45)),
    
    # ATM
    ("ATM Withdrawal authorized on {date} {location} {atm_id}", (100, 500)),
    
    # Insurance
    ("Progressive Insurance", (200, 500)),
    ("Hartford Business Insurance", (300, 800)),
    
    # Marketing/Services
    ("Google Ads", (100, 1000)),
    ("Facebook Ads", (50, 500)),
    ("QuickBooks Online", (25, 80)),
    ("Mailchimp", (20, 100)),
]

# Location data
LOCATIONS = [
    "San Jose CA",
    "Santa Clara CA",
    "Sunnyvale CA",
    "Mountain View CA",
    "Cupertino CA",
    "Palo Alto CA",
    "Milpitas CA",
    "Fremont CA",
    "Campbell CA",
    "Los Gatos CA",
]

SUPPLIERS = [
    "Sysco Foods",
    "US Foods",
    "Wholesale Supply Co",
    "Metro Distribution",
    "National Retail Supply",
    "Premier Wholesale",
    "Eastern Distribution",
    "Allied Products Inc",
    "Global Trade LLC",
    "Direct Source Supply",
]

LANDLORDS = [
    "Bay Area Property Management",
    "Silicon Valley Commercial RE",
    "Pacific Coast Properties",
    "CA Commercial Leasing",
]


class TransactionGenerator:
    """Generates realistic retail business transactions."""
    
    def __init__(self, monthly_revenue: float = 100000, business_type: str = "retail"):
        self.monthly_revenue = monthly_revenue
        self.business_type = business_type
        
    def generate_transactions(
        self, 
        period: StatementPeriod, 
        starting_balance: float
    ) -> Tuple[List[Transaction], float]:
        """
        Generate transactions for the given period.
        Returns tuple of (transactions, ending_balance).
        """
        transactions = []
        months = max(1, period.days / 30)
        
        # Generate deposits (revenue)
        deposits = self._generate_deposits(period, months)
        transactions.extend(deposits)
        
        # Generate withdrawals (expenses) - typically 70-85% of revenue
        expense_ratio = random.uniform(0.70, 0.85)
        target_expenses = self.monthly_revenue * months * expense_ratio
        withdrawals = self._generate_withdrawals(period, target_expenses)
        transactions.extend(withdrawals)
        
        # Sort by date
        transactions.sort(key=lambda t: (t.date, t.is_withdrawal))
        
        # Calculate running balances
        balance = starting_balance
        for txn in transactions:
            if txn.is_deposit:
                balance += txn.amount
            else:
                balance -= txn.amount
            txn.running_balance = round(balance, 2)
        
        return transactions, balance
    
    def _generate_deposits(self, period: StatementPeriod, months: float) -> List[Transaction]:
        """Generate deposit transactions."""
        deposits = []
        target_revenue = self.monthly_revenue * months
        current_total = 0
        
        # Calculate number of deposits (25-35 per month for retail)
        num_deposits = int(random.uniform(25, 35) * months)
        
        while current_total < target_revenue * 0.95 and len(deposits) < num_deposits * 1.5:
            template, (min_amt, max_amt) = random.choice(DEPOSIT_TEMPLATES)
            
            # Adjust amount based on remaining target
            remaining = target_revenue - current_total
            max_amt = min(max_amt, remaining * 0.3)  # Don't exceed 30% of remaining
            
            if max_amt < min_amt:
                max_amt = min_amt
                
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            # Generate random date within period
            days_offset = random.randint(0, period.days)
            txn_date = period.start_date + timedelta(days=days_offset)
            
            # Format description
            description = self._format_description(template, txn_date)
            
            deposits.append(Transaction(
                date=txn_date,
                description=description,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT
            ))
            
            current_total += amount
        
        return deposits
    
    def _generate_withdrawals(self, period: StatementPeriod, target_expenses: float) -> List[Transaction]:
        """Generate withdrawal transactions."""
        withdrawals = []
        current_total = 0
        months = max(1, period.days / 30)
        
        # Fixed monthly expenses
        fixed_expenses = self._generate_fixed_expenses(period, months)
        withdrawals.extend(fixed_expenses)
        current_total = sum(t.amount for t in fixed_expenses)
        
        # Variable expenses to reach target
        num_variable = int(random.uniform(40, 60) * months)
        
        while current_total < target_expenses * 0.95 and len(withdrawals) < num_variable + len(fixed_expenses) * 1.5:
            # Prefer purchase/supplier transactions
            template, (min_amt, max_amt) = random.choice(WITHDRAWAL_TEMPLATES[:8])
            
            remaining = target_expenses - current_total
            max_amt = min(max_amt, remaining * 0.2)
            
            if max_amt < min_amt:
                break
                
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            days_offset = random.randint(0, period.days)
            txn_date = period.start_date + timedelta(days=days_offset)
            
            description = self._format_description(template, txn_date)
            check_number = None
            if "Check #" in description:
                check_number = str(random.randint(1001, 9999))
                description = description.replace("{check_num}", check_number)
            
            withdrawals.append(Transaction(
                date=txn_date,
                description=description,
                amount=amount,
                transaction_type=TransactionType.WITHDRAWAL,
                check_number=check_number
            ))
            
            current_total += amount
        
        return withdrawals
    
    def _generate_fixed_expenses(self, period: StatementPeriod, months: float) -> List[Transaction]:
        """Generate fixed monthly expenses like rent, payroll, utilities."""
        expenses = []
        
        # Rent (once per month)
        for month_offset in range(int(months) + 1):
            rent_date = period.start_date + timedelta(days=month_offset * 30 + random.randint(1, 5))
            if rent_date <= period.end_date:
                expenses.append(Transaction(
                    date=rent_date,
                    description=f"Rent Payment {random.choice(LANDLORDS)}",
                    amount=round(random.uniform(4000, 7000), 2),
                    transaction_type=TransactionType.WITHDRAWAL
                ))
        
        # Payroll (bi-weekly, so ~2 per month)
        payroll_count = int(months * 2)
        for i in range(payroll_count):
            days_offset = int((i + 0.5) * 15)
            if days_offset <= period.days:
                payroll_date = period.start_date + timedelta(days=days_offset)
                expenses.append(Transaction(
                    date=payroll_date,
                    description=random.choice(["ADP Payroll", "Gusto Payroll", "Payroll Direct Deposit"]),
                    amount=round(random.uniform(8000, 15000), 2),
                    transaction_type=TransactionType.WITHDRAWAL
                ))
        
        # Utilities (monthly)
        utilities = [
            ("PG&E Payment", (200, 400)),
            ("Verizon Business", (150, 250)),
            ("Comcast Business", (100, 200)),
        ]
        for month_offset in range(int(months) + 1):
            for util_name, (min_amt, max_amt) in utilities:
                util_date = period.start_date + timedelta(days=month_offset * 30 + random.randint(10, 20))
                if util_date <= period.end_date:
                    expenses.append(Transaction(
                        date=util_date,
                        description=util_name,
                        amount=round(random.uniform(min_amt, max_amt), 2),
                        transaction_type=TransactionType.WITHDRAWAL
                    ))
        
        # Insurance (monthly)
        for month_offset in range(int(months) + 1):
            ins_date = period.start_date + timedelta(days=month_offset * 30 + random.randint(1, 10))
            if ins_date <= period.end_date:
                expenses.append(Transaction(
                    date=ins_date,
                    description=random.choice(["Progressive Insurance", "Hartford Business Insurance"]),
                    amount=round(random.uniform(300, 600), 2),
                    transaction_type=TransactionType.WITHDRAWAL
                ))
        
        # Bank fees (monthly)
        for month_offset in range(int(months) + 1):
            fee_date = period.start_date + timedelta(days=month_offset * 30 + 28)
            if fee_date <= period.end_date:
                expenses.append(Transaction(
                    date=fee_date,
                    description="Monthly Service Fee",
                    amount=round(random.uniform(10, 25), 2),
                    transaction_type=TransactionType.WITHDRAWAL
                ))
        
        return expenses
    
    def _format_description(self, template: str, txn_date: date) -> str:
        """Format a transaction description with random data."""
        description = template
        
        # Replace placeholders
        if "{date}" in description:
            description = description.replace("{date}", txn_date.strftime("%m/%d"))
        if "{location}" in description:
            description = description.replace("{location}", random.choice(LOCATIONS))
        if "{atm_id}" in description:
            atm_id = f"ATM ID 0{random.randint(10000, 99999)}"
            description = description.replace("{atm_id}", atm_id)
        if "{merchant_id}" in description:
            merchant_id = f"M{random.randint(100000, 999999)}"
            description = description.replace("{merchant_id}", merchant_id)
        if "{card_id}" in description:
            card_id = f"{random.randint(1000, 9999)}"
            description = description.replace("{card_id}", card_id)
        if "{supplier}" in description:
            description = description.replace("{supplier}", random.choice(SUPPLIERS))
        if "{landlord}" in description:
            description = description.replace("{landlord}", random.choice(LANDLORDS))
        if "{company}" in description:
            description = description.replace("{company}", fake.company()[:20])
        if "{ref}" in description:
            ref = f"Ref#{fake.bothify('??####??').upper()}"
            description = description.replace("{ref}", ref)
        
        return description
