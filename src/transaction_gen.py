"""Transaction generators for business and personal checking statements."""

import calendar
import random
from datetime import date, timedelta
from typing import Dict, List, Optional, Sequence, Tuple

from faker import Faker

from .models import StatementPeriod, Transaction, TransactionType

fake = Faker()

BUSINESS_DEPOSIT_TEMPLATES = [
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

BUSINESS_WITHDRAWAL_TEMPLATES = [
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

PERSONAL_EMPLOYERS = [
    "ACME SYSTEMS INC",
    "PACIFIC HEALTH GROUP",
    "BAY AREA LOGISTICS",
    "SIERRA CONSULTING",
    "VALLEY TECH SERVICES",
    "NORCAL DISTRIBUTION",
]

PERSONAL_DEPOSIT_TEMPLATES = [
    "PAYROLL DIRECT DEP {employer}",
    "ACH CREDIT PAYROLL {employer}",
    "DIRECT DEP {employer}",
]

PERSONAL_FIXED_EXPENSE_TEMPLATES = [
    ("Rent Payment", (1400, 2800)),
    ("PG&E Payment", (90, 220)),
    ("Xfinity Internet", (60, 130)),
    ("AT&T Wireless", (75, 160)),
    ("GEICO Insurance", (110, 240)),
    ("Car Payment", (280, 650)),
    ("Credit Card Payment", (150, 600)),
    ("Planet Fitness", (25, 55)),
    ("Netflix", (16, 24)),
    ("Spotify", (11, 18)),
]

PERSONAL_VARIABLE_WITHDRAWAL_TEMPLATES = [
    ("Safeway Store #{store_id}", (35, 140)),
    ("Trader Joe's #{store_id}", (30, 120)),
    ("Whole Foods Market", (35, 150)),
    ("Costco Wholesale #{store_id}", (80, 240)),
    ("Target T-{store_id}", (25, 130)),
    ("Walmart Supercenter #{store_id}", (25, 140)),
    ("Amazon Marketplace", (18, 180)),
    ("Chevron {location}", (35, 90)),
    ("Shell Oil {location}", (35, 90)),
    ("Uber Trip {location}", (12, 55)),
    ("Lyft Ride {location}", (12, 55)),
    ("DoorDash {merchant}", (18, 65)),
    ("Starbucks Store #{store_id}", (6, 18)),
    ("Chipotle #{store_id}", (12, 28)),
    ("CVS Pharmacy #{store_id}", (12, 65)),
    ("Walgreens #{store_id}", (12, 60)),
    ("Venmo Payment {person}", (20, 140)),
    ("Zelle Transfer {person}", (25, 180)),
    ("ATM Withdrawal {location}", (40, 160)),
    ("Apple Cash {person}", (15, 90)),
]

PERSONAL_MERCHANTS = [
    "Chipotle",
    "Panera",
    "Sweetgreen",
    "DoorDash",
    "Instacart",
]

PERSONAL_CONTACTS = [
    "J. SMITH",
    "A. JOHNSON",
    "M. LEE",
    "D. GARCIA",
    "S. WILSON",
    "R. MARTIN",
]

PERSONAL_MIN_TRANSACTIONS_PER_MONTH = 40
PERSONAL_MAX_TRANSACTIONS_PER_MONTH = 70

PERSONAL_PROFILE_PRESETS = {
    "homebody": {
        "transaction_range": (42, 52),
        "expense_ratio": (0.38, 0.50),
        "digital_ratio": (0.20, 0.34),
        "payday_weekdays": [4],
        "balance_floor": 550,
        "category_weights": {
            "grocery": 5,
            "gas": 2,
            "dining": 2,
            "delivery": 3,
            "retail": 2,
            "pharmacy": 1,
            "digital": 2,
            "coffee": 1,
            "peer_transfer": 1,
            "atm": 1,
            "dry_cleaner": 1,
            "liquor": 1,
            "small_purchase": 1,
        },
        "optional_fixed": ["fitness", "streaming_secondary", "transfer_to_savings"],
    },
    "commuter": {
        "transaction_range": (46, 60),
        "expense_ratio": (0.48, 0.62),
        "digital_ratio": (0.18, 0.30),
        "payday_weekdays": [4, 2],
        "balance_floor": 450,
        "category_weights": {
            "grocery": 3,
            "gas": 4,
            "coffee": 3,
            "rideshare": 2,
            "dining": 2,
            "retail": 2,
            "peer_transfer": 1,
            "atm": 1,
            "dry_cleaner": 1,
            "liquor": 1,
            "small_purchase": 1,
        },
        "optional_fixed": ["car_payment", "fitness", "transfer_to_savings"],
    },
    "student": {
        "transaction_range": (43, 55),
        "expense_ratio": (0.42, 0.56),
        "digital_ratio": (0.32, 0.46),
        "payday_weekdays": [4, 3],
        "balance_floor": 220,
        "category_weights": {
            "grocery": 2,
            "gas": 2,
            "dining": 3,
            "delivery": 3,
            "coffee": 3,
            "rideshare": 2,
            "peer_transfer": 3,
            "retail": 2,
            "digital": 1,
            "atm": 1,
            "liquor": 1,
            "small_purchase": 2,
        },
        "optional_fixed": ["fitness", "transfer_to_savings"],
    },
    "suburban_family": {
        "transaction_range": (52, 68),
        "expense_ratio": (0.54, 0.68),
        "digital_ratio": (0.14, 0.24),
        "payday_weekdays": [4],
        "balance_floor": 700,
        "category_weights": {
            "grocery": 5,
            "wholesale": 2,
            "gas": 4,
            "retail": 3,
            "pharmacy": 2,
            "dining": 2,
            "transfer_out": 2,
            "peer_transfer": 1,
            "atm": 1,
            "dry_cleaner": 1,
            "liquor": 1,
            "small_purchase": 1,
        },
        "optional_fixed": ["car_payment", "fitness", "streaming_secondary", "transfer_to_savings"],
    },
    "higher_income_professional": {
        "transaction_range": (48, 64),
        "expense_ratio": (0.50, 0.64),
        "digital_ratio": (0.26, 0.42),
        "payday_weekdays": [4, 3],
        "balance_floor": 1100,
        "category_weights": {
            "grocery": 3,
            "gas": 2,
            "rideshare": 3,
            "dining": 3,
            "coffee": 2,
            "retail": 3,
            "digital": 2,
            "transfer_out": 2,
            "peer_transfer": 1,
            "pharmacy": 1,
            "dry_cleaner": 1,
            "liquor": 1,
            "small_purchase": 1,
        },
        "optional_fixed": ["car_payment", "fitness", "streaming_secondary", "transfer_to_savings"],
    },
}

PROFILE_AUTO_CHOICES = tuple(PERSONAL_PROFILE_PRESETS.keys())

DIGITAL_PERSONAL_CATEGORIES = {"delivery", "rideshare", "digital", "peer_transfer", "transfer_out"}

BANK_WORDING_PACKS = {
    "wells_fargo": {
        "personal_deposit_templates": [
            "PAYROLL DIRECT DEP {employer}",
            "ACH CREDIT PAYROLL {employer}",
            "DIRECT DEP {employer}",
        ],
        "transfer_out_templates": [
            "ONLINE TRANSFER TO {savings_merchant}",
            "TRANSFER TO {savings_merchant}",
        ],
        "credit_card_templates": [
            "{credit_card_merchant}",
            "ONLINE PAYMENT {credit_card_merchant}",
        ],
        "atm_template": "ATM Withdrawal {location}",
    },
    "generic": {
        "personal_deposit_templates": PERSONAL_DEPOSIT_TEMPLATES,
        "transfer_out_templates": [
            "Transfer to {savings_merchant}",
            "Online Transfer to {savings_merchant}",
        ],
        "credit_card_templates": [
            "{credit_card_merchant}",
        ],
        "atm_template": "ATM Withdrawal {location}",
    },
}

PERSONAL_MERCHANT_POOLS = {
    "grocery": ["Safeway", "Trader Joe's", "Whole Foods Market", "Lucky", "Sprouts Farmers Market"],
    "wholesale": ["Costco Wholesale", "Sam's Club"],
    "big_box": ["Target", "Walmart Supercenter"],
    "retail": ["Amazon Marketplace", "TJ Maxx", "Marshalls", "Old Navy", "Best Buy"],
    "gas": ["Chevron", "Shell Oil", "76", "Arco"],
    "coffee": ["Starbucks", "Peet's Coffee", "Philz Coffee"],
    "pharmacy": ["CVS Pharmacy", "Walgreens"],
    "quick_meal": ["Chipotle", "Panera", "Sweetgreen", "Chick-fil-A"],
    "restaurant": ["The Cheesecake Factory", "Olive Garden", "BJ's Restaurant", "Yard House", "California Pizza Kitchen"],
    "delivery": ["DoorDash", "Uber Eats", "Instacart"],
    "digital": ["Apple.com", "Google One", "Spotify", "Netflix", "Hulu", "YouTube Premium"],
    "fitness": ["Planet Fitness", "24 Hour Fitness", "YMCA Membership"],
    "credit_card": ["CHASE CARD AUTOPAY", "AMEX AUTOPAY", "CITI CARD PAYMENT", "DISCOVER E-PAYMENT"],
    "savings": ["WELLS FARGO SAVINGS", "ALLY SAVINGS", "CAPITAL ONE 360 SAVINGS"],
    "internet": ["Xfinity Internet", "Comcast Xfinity", "AT&T Fiber"],
    "cellphone": ["AT&T Wireless", "Verizon Wireless", "T-Mobile"],
    "insurance": ["GEICO Insurance", "State Farm Insurance", "Progressive Insurance"],
    "housing": ["Rent Payment", "Mortgage Payment"],
    "dry_cleaner": ["One Hour Cleaners", "Sparkle Cleaners", "Town Cleaners", "Village Dry Cleaners"],
    "liquor_store": ["Total Wine & More", "BevMo", "Liquor & Wine", "Bottle Barn"],
    "small_purchase": ["7-Eleven", "ampm", "Quick Stop Market", "Circle K"],
}


class TransactionGenerator:
    """Generates realistic transactions for business and personal accounts."""
    
    def __init__(
        self,
        monthly_revenue: float = 100000,
        business_type: str = "retail",
        account_type: str = "Wells Fargo Everyday Checking",
        personal_profile: str = "auto",
        seed: Optional[str] = None,
    ):
        self.seed = seed if seed not in (None, "") else None
        if self.seed is not None:
            random.seed(str(self.seed))
        self.monthly_revenue = monthly_revenue
        self.business_type = business_type
        self.account_type = account_type
        self.fake = Faker()
        if self.seed is not None:
            self.fake.seed_instance(str(self.seed))
        self.primary_employer = random.choice(PERSONAL_EMPLOYERS)
        self.preferred_rideshare = random.choice(("Uber", "Lyft"))
        self.personal_profile_key = self._resolve_personal_profile(personal_profile)
        self.personal_profile = PERSONAL_PROFILE_PRESETS[self.personal_profile_key]
        self.payday_weekday = random.choice(self.personal_profile["payday_weekdays"])
        self.personal_merchants = self._build_personal_merchants()
        self.personal_contact_pool = random.sample(PERSONAL_CONTACTS, k=min(4, len(PERSONAL_CONTACTS)))
        self.personal_store_labels = self._build_personal_store_labels()
        self.monthly_dining_templates: Dict[Tuple[int, int], List[Tuple[str, Tuple[float, float]]]] = {}
        self.wording_pack_key = self._resolve_wording_pack()
        self.wording_pack = BANK_WORDING_PACKS[self.wording_pack_key]

    @property
    def is_business_account(self) -> bool:
        return "business checking" in self.account_type.lower()
        
    def generate_transactions(
        self, 
        period: StatementPeriod, 
        starting_balance: float
    ) -> Tuple[List[Transaction], float]:
        """
        Generate transactions for the given period.
        Returns tuple of (transactions, ending_balance).
        """
        if self.is_business_account:
            transactions = self._generate_business_transactions(period)
        else:
            transactions = self._generate_personal_transactions(period, starting_balance)

        transactions.sort(key=lambda t: (t.date, t.is_withdrawal))

        balance = starting_balance
        daily_ending_balances = {}
        for txn in transactions:
            if txn.is_deposit:
                balance += txn.amount
            else:
                balance -= txn.amount
            daily_ending_balances[txn.date] = round(balance, 2)

        for txn in transactions:
            txn.running_balance = daily_ending_balances[txn.date]

        # Only show balance on the last transaction of each day
        assigned_dates = set()
        for txn in reversed(transactions):
            if txn.date not in assigned_dates:
                # This is the last transaction for this date (in sorted order)
                assigned_dates.add(txn.date)
            else:
                txn.running_balance = 0.0

        return transactions, round(balance, 2)

    def _generate_business_transactions(self, period: StatementPeriod) -> List[Transaction]:
        transactions = []
        months = max(1, period.days / 30)

        deposits = self._generate_business_deposits(period, months)
        transactions.extend(deposits)

        expense_ratio = random.uniform(0.70, 0.85)
        target_expenses = self.monthly_revenue * months * expense_ratio
        withdrawals = self._generate_business_withdrawals(period, target_expenses)
        transactions.extend(withdrawals)

        return transactions

    def _generate_personal_transactions(
        self,
        period: StatementPeriod,
        starting_balance: float,
    ) -> List[Transaction]:
        month_periods = self._split_period_by_month(period)
        deposits = self._generate_personal_deposits(month_periods)
        adjusted_income_total = sum(t.amount for t in deposits)

        minimum_transaction_count = len(deposits) + self._get_minimum_personal_withdrawal_count(month_periods)
        target_transaction_count = max(
            len(deposits),
            self._get_personal_transaction_target(month_periods),
            minimum_transaction_count,
        )
        target_transaction_count = min(PERSONAL_MAX_TRANSACTIONS_PER_MONTH * max(1, len(month_periods)), target_transaction_count)
        target_withdrawal_count = max(0, target_transaction_count - len(deposits))
        expense_low, expense_high = self.personal_profile["expense_ratio"]
        target_expenses = adjusted_income_total * random.uniform(expense_low, expense_high)
        withdrawals = self._generate_personal_withdrawals(
            period,
            month_periods,
            target_expenses,
            target_withdrawal_count,
        )

        transactions = deposits + withdrawals
        self._stabilize_personal_transactions(transactions, starting_balance, period)
        return transactions
    
    def _generate_business_deposits(self, period: StatementPeriod, months: float) -> List[Transaction]:
        deposits = []
        target_revenue = self.monthly_revenue * months
        current_total = 0
        
        num_deposits = int(random.uniform(25, 35) * months)
        
        while current_total < target_revenue * 0.95 and len(deposits) < num_deposits * 1.5:
            template, (min_amt, max_amt) = random.choice(BUSINESS_DEPOSIT_TEMPLATES)
            
            remaining = target_revenue - current_total
            max_amt = min(max_amt, remaining * 0.3)
            
            if max_amt < min_amt:
                max_amt = min_amt
                
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            days_offset = random.randint(0, period.days)
            txn_date = period.start_date + timedelta(days=days_offset)
            description = self._format_description(template, txn_date)
            
            deposits.append(Transaction(
                date=txn_date,
                description=description,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT
            ))
            
            current_total += amount
        
        return deposits

    def _generate_personal_deposits(
        self,
        month_periods: List[Tuple[date, date]],
    ) -> List[Transaction]:
        deposits = []

        for month_start, month_end in month_periods:
            deposit_dates = self._get_personal_deposit_dates(month_start, month_end)
            deposit_amount = self._get_realistic_personal_paycheck_amount()
            for deposit_date in deposit_dates:
                template = random.choice(self.wording_pack["personal_deposit_templates"])
                description = template.replace("{employer}", self.primary_employer)
                deposits.append(Transaction(
                    date=deposit_date,
                    description=description,
                    amount=deposit_amount,
                    transaction_type=TransactionType.DEPOSIT,
                ))

        return deposits
    
    def _generate_business_withdrawals(self, period: StatementPeriod, target_expenses: float) -> List[Transaction]:
        withdrawals = []
        current_total = 0
        months = max(1, period.days / 30)
        
        fixed_expenses = self._generate_business_fixed_expenses(period, months)
        withdrawals.extend(fixed_expenses)
        current_total = sum(t.amount for t in fixed_expenses)
        
        num_variable = int(random.uniform(40, 60) * months)
        
        while current_total < target_expenses * 0.95 and len(withdrawals) < num_variable + len(fixed_expenses) * 1.5:
            template, (min_amt, max_amt) = random.choice(BUSINESS_WITHDRAWAL_TEMPLATES[:8])
            
            remaining = target_expenses - current_total
            max_amt = min(max_amt, remaining * 0.2)
            
            if max_amt < min_amt:
                break

            if "ATM Withdrawal" in template:
                amount = self._get_atm_withdrawal_amount(min_amt, max_amt)
            else:
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

    def _generate_personal_withdrawals(
        self,
        period: StatementPeriod,
        month_periods: List[Tuple[date, date]],
        target_expenses: float,
        target_count: int,
    ) -> List[Transaction]:
        if target_count == 0:
            return []

        withdrawals = self._generate_personal_fixed_expenses(month_periods)
        if len(withdrawals) > target_count:
            withdrawals = withdrawals[:target_count]

        current_total = sum(t.amount for t in withdrawals)
        remaining_count = target_count - len(withdrawals)
        category_pool = self._get_personal_category_pool()
        category_limits = self._get_personal_category_limits(month_periods)
        required_counts = self._get_personal_required_category_counts(month_periods)
        category_counts: Dict[str, int] = {}
        digital_target = self._get_target_digital_transaction_count(remaining_count)
        digital_count = 0
        atm_dates: List[date] = []

        for index in range(remaining_count):
            category = self._choose_personal_category(
                category_pool,
                category_counts,
                category_limits,
                required_counts,
                digital_count,
                digital_target,
                remaining_count - index,
            )
            if category == "atm":
                txn_date = self._get_personal_atm_date(period, atm_dates)
                atm_dates.append(txn_date)
            else:
                txn_date = self._get_personal_spend_date(period)

            if category == "dining":
                template, (min_amt, max_amt) = self._get_unique_dining_template(txn_date)
            else:
                template, (min_amt, max_amt) = random.choice(self._get_personal_variable_templates_for_category(category))
            remaining_budget = max(target_expenses - current_total, min_amt * (remaining_count - index))
            remaining_slots = remaining_count - index

            if "ATM Withdrawal" in template:
                if remaining_slots == 1:
                    amount = self._get_atm_withdrawal_amount(min_amt, min(max_amt, remaining_budget))
                else:
                    average_budget = remaining_budget / remaining_slots
                    lower_bound = max(min_amt, average_budget * 0.55)
                    upper_bound = min(max_amt, average_budget * 1.45)
                    if lower_bound > upper_bound:
                        lower_bound, upper_bound = min_amt, max_amt
                    amount = self._get_atm_withdrawal_amount(lower_bound, upper_bound)
            elif remaining_slots == 1:
                amount = self._clamp_amount(remaining_budget, min_amt, max_amt)
            else:
                average_budget = remaining_budget / remaining_slots
                lower_bound = max(min_amt, average_budget * 0.55)
                upper_bound = min(max_amt, average_budget * 1.45)
                if lower_bound > upper_bound:
                    lower_bound, upper_bound = min_amt, max_amt
                amount = round(random.uniform(lower_bound, upper_bound), 2)

            description = self._format_personal_description(template, txn_date)
            withdrawals.append(Transaction(
                date=txn_date,
                description=description,
                amount=amount,
                transaction_type=TransactionType.WITHDRAWAL,
            ))
            current_total += amount
            category_counts[category] = category_counts.get(category, 0) + 1
            if category in DIGITAL_PERSONAL_CATEGORIES:
                digital_count += 1

        return withdrawals
    
    def _generate_business_fixed_expenses(self, period: StatementPeriod, months: float) -> List[Transaction]:
        expenses = []
        
        for month_offset in range(int(months) + 1):
            rent_date = period.start_date + timedelta(days=month_offset * 30 + random.randint(1, 5))
            if rent_date <= period.end_date:
                expenses.append(Transaction(
                    date=rent_date,
                    description=f"Rent Payment {random.choice(LANDLORDS)}",
                    amount=round(random.uniform(4000, 7000), 2),
                    transaction_type=TransactionType.WITHDRAWAL
                ))
        
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
        
        for month_offset in range(int(months) + 1):
            ins_date = period.start_date + timedelta(days=month_offset * 30 + random.randint(1, 10))
            if ins_date <= period.end_date:
                expenses.append(Transaction(
                    date=ins_date,
                    description=random.choice(["Progressive Insurance", "Hartford Business Insurance"]),
                    amount=round(random.uniform(300, 600), 2),
                    transaction_type=TransactionType.WITHDRAWAL
                ))
        
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

    def _generate_personal_fixed_expenses(
        self,
        month_periods: List[Tuple[date, date]],
    ) -> List[Transaction]:
        expenses = []

        for month_start, month_end in month_periods:
            monthly_templates = self._build_personal_fixed_templates(month_start, month_end)

            for template, amount_range, day_window in monthly_templates:
                txn_date = self._pick_day_in_window(month_start, month_end, day_window)
                if any(token in template for token in ("{streaming_primary}", "{streaming_secondary}")):
                    amount = float(random.randint(int(amount_range[0]), int(amount_range[1])))
                else:
                    amount = round(random.uniform(amount_range[0], amount_range[1]), 2)
                expenses.append(Transaction(
                    date=txn_date,
                    description=self._format_personal_description(template, txn_date),
                    amount=amount,
                    transaction_type=TransactionType.WITHDRAWAL,
                ))

        return expenses

    def _build_personal_fixed_templates(
        self,
        month_start: date,
        month_end: date,
    ) -> List[Tuple[str, Tuple[float, float], Tuple[int, int]]]:
        templates = [
            ("{housing_payment}", self._get_housing_amount_range(), (1, 5)),
            ("{insurance_merchant}", (115, 245), (3, 10)),
            ("{cellphone_merchant}", (70, 165), (12, 20)),
            ("{internet_merchant}", (60, 145), (14, 22)),
            (random.choice(self.wording_pack["credit_card_templates"]), (140, 620), (20, 28)),
            ("PG&E Payment", (90, 230), (12, 19)),
            ("{streaming_primary}", (12, 25), (5, 12)),
        ]

        optional_map = {
            "car_payment": ("Car Payment", (280, 690), (5, 12)),
            "fitness": ("{fitness_merchant}", (25, 85), (6, 15)),
            "streaming_secondary": ("{streaming_secondary}", (9, 22), (16, 25)),
            "transfer_to_savings": (random.choice(self.wording_pack["transfer_out_templates"]), (120, 650), (15, 27)),
        }

        optional_items = self.personal_profile["optional_fixed"]
        optional_count = min(2, len(optional_items))
        for optional_key in random.sample(optional_items, k=optional_count):
            templates.append(optional_map[optional_key])

        if self.personal_profile_key == "student":
            templates[0] = ("Rent Payment", (850, 1800), (1, 5))
        elif self.personal_profile_key in {"suburban_family", "higher_income_professional"}:
            templates[0] = ("Mortgage Payment", (1900, 3600), (1, 5))

        return templates

    def _split_period_by_month(self, period: StatementPeriod) -> List[Tuple[date, date]]:
        month_periods = []
        current = date(period.start_date.year, period.start_date.month, 1)

        while current <= period.end_date:
            month_end = date(current.year, current.month, calendar.monthrange(current.year, current.month)[1])
            segment_start = max(period.start_date, current)
            segment_end = min(period.end_date, month_end)
            if segment_start <= segment_end:
                month_periods.append((segment_start, segment_end))

            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)

        return month_periods

    def _get_personal_deposit_dates(self, month_start: date, month_end: date) -> List[date]:
        span = max(0, (month_end - month_start).days)
        if span < 14:
            payday = self._first_weekday_on_or_after(month_start, self.payday_weekday)
            return [min(payday, month_end)]

        latest_first_date = month_end - timedelta(days=14)
        first_payday = self._first_weekday_on_or_after(month_start, self.payday_weekday)
        candidates = []
        current = first_payday
        while current <= latest_first_date:
            candidates.append(current)
            current += timedelta(days=7)

        if not candidates:
            payday = self._first_weekday_on_or_after(month_start, self.payday_weekday)
            return [min(payday, month_end)]

        first_date = random.choice(candidates)
        second_date = first_date + timedelta(days=14)
        return [first_date, second_date]

    def _get_realistic_personal_paycheck_amount(self) -> float:
        base_paycheck = self.monthly_revenue / 2
        rounded_paycheck = round(base_paycheck)
        dollar_adjustment = random.randint(11, 87)
        cents = random.randint(11, 93)

        if rounded_paycheck >= 100:
            adjusted_dollars = rounded_paycheck - dollar_adjustment
        else:
            adjusted_dollars = max(1, rounded_paycheck)

        return round(adjusted_dollars + (cents / 100), 2)

    def _resolve_personal_profile(self, personal_profile: str) -> str:
        if personal_profile in PERSONAL_PROFILE_PRESETS:
            return personal_profile
        return random.choice(PROFILE_AUTO_CHOICES)

    def _resolve_wording_pack(self) -> str:
        if "wells fargo" in self.account_type.lower():
            return "wells_fargo"
        return "generic"

    def _build_personal_merchants(self) -> Dict[str, str]:
        if self.personal_profile_key == "homebody":
            grocery_candidates = ["Safeway", "Trader Joe's", "Whole Foods Market"]
            gas_candidates = ["Chevron", "Shell Oil"]
            coffee_candidates = ["Starbucks", "Peet's Coffee"]
        elif self.personal_profile_key == "student":
            grocery_candidates = ["Trader Joe's", "Safeway", "Lucky"]
            gas_candidates = ["Arco", "Chevron"]
            coffee_candidates = ["Starbucks", "Philz Coffee"]
        elif self.personal_profile_key == "suburban_family":
            grocery_candidates = ["Safeway", "Costco Wholesale", "Target"]
            gas_candidates = ["Chevron", "76", "Shell Oil"]
            coffee_candidates = ["Starbucks", "Peet's Coffee"]
        elif self.personal_profile_key == "higher_income_professional":
            grocery_candidates = ["Whole Foods Market", "Trader Joe's", "Sprouts Farmers Market"]
            gas_candidates = ["Chevron", "Shell Oil"]
            coffee_candidates = ["Philz Coffee", "Starbucks", "Peet's Coffee"]
        else:
            grocery_candidates = ["Safeway", "Trader Joe's", "Whole Foods Market", "Lucky"]
            gas_candidates = ["Chevron", "Shell Oil", "76"]
            coffee_candidates = ["Starbucks", "Peet's Coffee", "Philz Coffee"]

        merchants = {
            "grocery_store": random.choice(grocery_candidates),
            "wholesale_store": random.choice(PERSONAL_MERCHANT_POOLS["wholesale"]),
            "big_box_store": random.choice(PERSONAL_MERCHANT_POOLS["big_box"]),
            "retail_merchant": random.choice(PERSONAL_MERCHANT_POOLS["retail"]),
            "gas_brand": random.choice(gas_candidates),
            "coffee_shop": random.choice(coffee_candidates),
            "pharmacy_merchant": random.choice(PERSONAL_MERCHANT_POOLS["pharmacy"]),
            "quick_meal": random.choice(PERSONAL_MERCHANT_POOLS["quick_meal"]),
            "restaurant_merchant": random.choice(PERSONAL_MERCHANT_POOLS["restaurant"]),
            "delivery_merchant": random.choice(PERSONAL_MERCHANT_POOLS["delivery"]),
            "digital_merchant": random.choice(PERSONAL_MERCHANT_POOLS["digital"]),
            "fitness_merchant": random.choice(PERSONAL_MERCHANT_POOLS["fitness"]),
            "credit_card_merchant": random.choice(PERSONAL_MERCHANT_POOLS["credit_card"]),
            "savings_merchant": random.choice(PERSONAL_MERCHANT_POOLS["savings"]),
            "internet_merchant": random.choice(PERSONAL_MERCHANT_POOLS["internet"]),
            "cellphone_merchant": random.choice(PERSONAL_MERCHANT_POOLS["cellphone"]),
            "insurance_merchant": random.choice(PERSONAL_MERCHANT_POOLS["insurance"]),
            "housing_payment": random.choice(PERSONAL_MERCHANT_POOLS["housing"]),
            "dry_cleaner_merchant": random.choice(PERSONAL_MERCHANT_POOLS["dry_cleaner"]),
            "liquor_store_merchant": random.choice(PERSONAL_MERCHANT_POOLS["liquor_store"]),
            "small_purchase_merchant": random.choice(PERSONAL_MERCHANT_POOLS["small_purchase"]),
            "streaming_primary": random.choice(["Netflix", "Hulu", "YouTube Premium", "Disney Plus"]),
            "streaming_secondary": random.choice(["Spotify", "Apple Music", "Max", "Prime Video"]),
            "rideshare": self.preferred_rideshare,
        }
        return merchants

    def _build_personal_store_labels(self) -> Dict[str, str]:
        return {
            "grocery_store_label": self._with_numeric_suffix(self.personal_merchants["grocery_store"], "hash"),
            "wholesale_store_label": self._with_numeric_suffix(self.personal_merchants["wholesale_store"], "hash"),
            "big_box_store_label": self._with_numeric_suffix(self.personal_merchants["big_box_store"], "target"),
            "coffee_shop_label": self._with_numeric_suffix(self.personal_merchants["coffee_shop"], "store"),
            "pharmacy_merchant_label": self._with_numeric_suffix(self.personal_merchants["pharmacy_merchant"], "hash"),
            "quick_meal_label": self._with_numeric_suffix(self.personal_merchants["quick_meal"], "hash"),
            "restaurant_label": self._with_numeric_suffix(self.personal_merchants["restaurant_merchant"], "hash"),
            "gas_brand_label": f"{self.personal_merchants['gas_brand']} {random.choice(LOCATIONS)}",
            "dry_cleaner_label": self.personal_merchants["dry_cleaner_merchant"],
            "liquor_store_label": self.personal_merchants["liquor_store_merchant"],
            "small_purchase_label": self._with_numeric_suffix(self.personal_merchants["small_purchase_merchant"], "hash"),
        }

    def _with_numeric_suffix(self, merchant: str, style: str) -> str:
        location_id = str(random.randint(100, 9999))
        if style == "target":
            return f"{merchant} T-{location_id}"
        if style == "store":
            return f"{merchant} Store #{location_id}"
        return f"{merchant} #{location_id}"

    def _get_personal_category_pool(self) -> List[str]:
        pool = []
        for category, weight in self.personal_profile["category_weights"].items():
            pool.extend([category] * weight)
        return pool

    def _get_personal_category_limits(self, month_periods: List[Tuple[date, date]]) -> Dict[str, int]:
        month_count = max(1, len(month_periods))
        return {
            "atm": month_count if self.personal_profile_key in {"homebody", "student"} else month_count + 1,
            "transfer_out": month_count + 1,
            "digital": month_count + 1,
            "rideshare": month_count + 2,
            "peer_transfer": month_count + 2,
            "dining": month_count * 13,
            "dry_cleaner": month_count,
            "liquor": month_count + 1,
        }

    def _get_personal_required_category_counts(self, month_periods: List[Tuple[date, date]]) -> Dict[str, int]:
        month_count = max(1, len(month_periods))
        return {
            "gas": 2 * month_count,
            "dining": 5 * month_count,
            "dry_cleaner": month_count,
            "liquor": month_count,
            "small_purchase": month_count,
        }

    def _get_minimum_personal_withdrawal_count(self, month_periods: List[Tuple[date, date]]) -> int:
        base_fixed_count = 7 + min(2, len(self.personal_profile["optional_fixed"]))
        required_variable_count = sum(self._get_personal_required_category_counts(month_periods).values())
        return (base_fixed_count * max(1, len(month_periods))) + required_variable_count

    def _get_target_digital_transaction_count(self, variable_count: int) -> int:
        if variable_count <= 0:
            return 0
        low, high = self.personal_profile["digital_ratio"]
        return max(0, min(variable_count, round(variable_count * random.uniform(low, high))))

    def _choose_personal_category(
        self,
        category_pool: List[str],
        category_counts: Dict[str, int],
        category_limits: Dict[str, int],
        required_counts: Dict[str, int],
        digital_count: int,
        digital_target: int,
        remaining_slots: int,
    ) -> str:
        need_digital = max(0, digital_target - digital_count)
        need_required = {
            category: required_counts[category] - category_counts.get(category, 0)
            for category in required_counts
            if category_counts.get(category, 0) < required_counts[category]
        }

        if need_required:
            required_eligible = [
                category for category in category_pool
                if category in need_required
                and category_counts.get(category, 0) < category_limits.get(category, remaining_slots + 5)
            ]
            if required_eligible:
                return random.choice(required_eligible)

        eligible = []

        for category in category_pool:
            if category_counts.get(category, 0) >= category_limits.get(category, remaining_slots + 5):
                continue

            is_digital = category in DIGITAL_PERSONAL_CATEGORIES
            if not is_digital and remaining_slots <= need_digital:
                continue
            if is_digital and digital_count >= digital_target:
                if any(candidate not in DIGITAL_PERSONAL_CATEGORIES for candidate in category_pool):
                    continue

            eligible.append(category)

        if not eligible:
            eligible = [
                category for category in category_pool
                if category_counts.get(category, 0) < category_limits.get(category, remaining_slots + 5)
            ]

        if not eligible:
            eligible = category_pool

        return random.choice(eligible)

    def _get_unique_dining_template(self, txn_date: date) -> Tuple[str, Tuple[float, float]]:
        month_key = (txn_date.year, txn_date.month)
        if month_key not in self.monthly_dining_templates or not self.monthly_dining_templates[month_key]:
            self.monthly_dining_templates[month_key] = self._build_monthly_dining_templates()

        return self.monthly_dining_templates[month_key].pop()

    def _build_monthly_dining_templates(self) -> List[Tuple[str, Tuple[float, float]]]:
        templates: List[Tuple[str, Tuple[float, float]]] = []

        for merchant in PERSONAL_MERCHANT_POOLS["quick_meal"]:
            templates.append((self._with_numeric_suffix(merchant, "hash"), (12, 32)))
            templates.append((f"DoorDash {merchant}", (18, 55)))

        for merchant in PERSONAL_MERCHANT_POOLS["restaurant"]:
            templates.append((self._with_numeric_suffix(merchant, "hash"), (24, 85)))

        random.shuffle(templates)
        return templates

    def _get_personal_variable_templates_for_category(
        self,
        category: str,
    ) -> List[Tuple[str, Tuple[float, float]]]:
        templates = {
            "grocery": [
                ("{grocery_store_label}", (35, 145)),
                ("{grocery_store_label}", (28, 110)),
            ],
            "wholesale": [
                ("{wholesale_store_label}", (90, 260)),
            ],
            "retail": [
                ("{big_box_store_label}", (25, 140)),
                ("{retail_merchant}", (18, 180)),
            ],
            "gas": [
                ("{gas_brand_label}", (35, 90)),
            ],
            "rideshare": [
                ("{rideshare} Trip {location}", (12, 55)),
            ],
            "delivery": [
                ("DoorDash {delivery_merchant}", (18, 65)),
                ("Instacart Grocery Delivery", (30, 120)),
            ],
            "coffee": [
                ("{coffee_shop_label}", (6, 18)),
            ],
            "pharmacy": [
                ("{pharmacy_merchant_label}", (12, 65)),
            ],
            "digital": [
                ("{digital_merchant}", (8, 38)),
                ("Apple.com Bill", (3, 18)),
            ],
            "peer_transfer": [
                ("Venmo Payment {person}", (18, 140)),
                ("Zelle Transfer {person}", (25, 180)),
                ("Apple Cash {person}", (15, 90)),
            ],
            "transfer_out": [(template, (120, 650)) for template in self.wording_pack["transfer_out_templates"]],
            "atm": [
                (self.wording_pack["atm_template"], (40, 160)),
            ],
            "dry_cleaner": [
                ("{dry_cleaner_label}", (14, 42)),
            ],
            "liquor": [
                ("{liquor_store_label}", (18, 68)),
            ],
            "small_purchase": [
                ("{small_purchase_label}", (4, 24)),
                ("{small_purchase_merchant}", (3, 18)),
            ],
        }
        return templates[category]

    def _weighted_choice(self, options: Sequence[str]) -> str:
        return random.choice(list(options))

    def _get_housing_amount_range(self) -> Tuple[float, float]:
        if self.personal_profile_key == "student":
            return (850, 1800)
        if self.personal_profile_key in {"suburban_family", "higher_income_professional"}:
            return (1900, 3600)
        return (1400, 2800)

    def _get_personal_spend_date(self, period: StatementPeriod) -> date:
        if random.random() < 0.65:
            preferred_day = random.choice([4, 5, 6])
            candidate = self._first_weekday_on_or_after(period.start_date, preferred_day)
            if candidate <= period.end_date:
                while candidate + timedelta(days=7) <= period.end_date and random.random() < 0.45:
                    candidate += timedelta(days=7)
                return candidate
        return self._random_date_within_period(period)

    def _get_personal_atm_date(self, period: StatementPeriod, existing_dates: List[date]) -> date:
        candidate = self._first_weekday_on_or_after(period.start_date, random.choice([4, 5]))
        candidates = []
        while candidate <= period.end_date:
            if all(abs((candidate - existing).days) >= 5 for existing in existing_dates):
                candidates.append(candidate)
            candidate += timedelta(days=7)

        if candidates:
            return random.choice(candidates)

        return self._get_personal_spend_date(period)

    def _pick_day_in_window(
        self,
        month_start: date,
        month_end: date,
        window: Tuple[int, int],
    ) -> date:
        start_offset, end_offset = window
        start_candidate = month_start + timedelta(days=max(0, start_offset - 1))
        end_candidate = month_start + timedelta(days=max(0, end_offset - 1))
        if end_candidate > month_end:
            end_candidate = month_end
        if start_candidate > month_end:
            start_candidate = month_end
        if start_candidate > end_candidate:
            start_candidate = end_candidate
        return self._random_date_between(start_candidate, end_candidate)

    def _first_weekday_on_or_after(self, start_date: date, weekday: int) -> date:
        days_ahead = (weekday - start_date.weekday()) % 7
        return start_date + timedelta(days=days_ahead)

    def _stabilize_personal_transactions(
        self,
        transactions: List[Transaction],
        starting_balance: float,
        period: StatementPeriod,
    ) -> None:
        balance_floor = self.personal_profile["balance_floor"]

        for _ in range(3):
            transactions.sort(key=lambda t: (t.date, t.is_withdrawal))
            deposit_dates = [t.date for t in transactions if t.is_deposit]
            balance = starting_balance
            changed = False

            for txn in transactions:
                if txn.is_deposit:
                    balance += txn.amount
                    continue

                projected_balance = balance - txn.amount
                if projected_balance < balance_floor:
                    next_payday = next((deposit_date for deposit_date in deposit_dates if deposit_date > txn.date), None)
                    if next_payday is not None:
                        deferred_date = min(period.end_date, next_payday + timedelta(days=random.randint(0, 2)))
                        if deferred_date > txn.date:
                            txn.date = deferred_date
                            changed = True
                            continue

                    affordable_amount = max(0.0, balance - balance_floor)
                    adjusted_amount = self._adjust_withdrawal_for_balance(txn, affordable_amount)
                    if adjusted_amount is not None and adjusted_amount < txn.amount:
                        txn.amount = adjusted_amount
                        projected_balance = balance - txn.amount
                        changed = True

                balance -= txn.amount

            if not changed:
                break

    def _adjust_withdrawal_for_balance(self, txn: Transaction, affordable_amount: float) -> Optional[float]:
        if affordable_amount <= 0:
            return None

        if "ATM Withdrawal" in txn.description:
            adjusted = self._get_atm_withdrawal_amount(20, min(300, affordable_amount))
            return adjusted if adjusted <= txn.amount else None

        minimum = 8.0
        if any(keyword in txn.description for keyword in ("Rent Payment", "Mortgage Payment", "Car Payment")):
            minimum = min(txn.amount, max(250.0, txn.amount * 0.5))
        elif any(keyword in txn.description for keyword in ("Transfer to", "Online Transfer", "AUTOPAY", "CARD PAYMENT")):
            minimum = min(txn.amount, 40.0)

        if affordable_amount < minimum:
            return None

        return round(min(txn.amount, affordable_amount), 2)

    def _get_atm_withdrawal_amount(self, minimum: float, maximum: float) -> float:
        lower_bound = max(20, int((minimum + 19) // 20) * 20)
        upper_bound = min(300, int(maximum // 20) * 20)

        if upper_bound < lower_bound:
            fallback = min(300, max(20, int(round(minimum / 20)) * 20))
            return float(fallback)

        return float(random.randrange(lower_bound, upper_bound + 20, 20))

    def _get_personal_transaction_target(self, month_periods: List[Tuple[date, date]]) -> int:
        low, high = self.personal_profile["transaction_range"]
        low = max(low, PERSONAL_MIN_TRANSACTIONS_PER_MONTH)
        high = min(max(high, low), PERSONAL_MAX_TRANSACTIONS_PER_MONTH)
        return sum(random.randint(low, high) for _month_start, _month_end in month_periods)

    def _random_date_within_period(self, period: StatementPeriod) -> date:
        days_offset = random.randint(0, max(0, period.days))
        return period.start_date + timedelta(days=days_offset)

    def _random_date_between(self, start_date: date, end_date: date) -> date:
        days_offset = random.randint(0, max(0, (end_date - start_date).days))
        return start_date + timedelta(days=days_offset)

    def _clamp_amount(self, amount: float, minimum: float, maximum: float) -> float:
        return round(max(minimum, min(maximum, amount)), 2)
    
    def _format_description(self, template: str, txn_date: date) -> str:
        description = template
        
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
            description = description.replace("{company}", self.fake.company()[:20])
        if "{ref}" in description:
            ref = f"Ref#{self.fake.bothify('??####??').upper()}"
            description = description.replace("{ref}", ref)
        
        return description

    def _format_personal_description(self, template: str, txn_date: date) -> str:
        description = template

        for placeholder, value in self.personal_merchants.items():
            token = "{" + placeholder + "}"
            if token in description:
                description = description.replace(token, value)
        for placeholder, value in self.personal_store_labels.items():
            token = "{" + placeholder + "}"
            if token in description:
                description = description.replace(token, value)
        if "{location}" in description:
            description = description.replace("{location}", random.choice(LOCATIONS))
        if "{person}" in description:
            description = description.replace("{person}", random.choice(self.personal_contact_pool))

        return description
