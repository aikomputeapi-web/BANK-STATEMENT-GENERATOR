"""
Data models for the bank statement generator.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional
from enum import Enum


class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    
    def format_line1(self) -> str:
        return self.street
    
    def format_line2(self) -> str:
        return f"{self.city} {self.state} {self.zip_code}"
    
    def __str__(self) -> str:
        return f"{self.street}\n{self.city} {self.state} {self.zip_code}"


@dataclass
class AccountHolder:
    name: str
    address: Address


@dataclass
class AccountInfo:
    account_number: str
    routing_number: str
    account_type: str = "Wells Fargo Everyday Checking"


@dataclass
class Transaction:
    date: date
    description: str
    amount: float
    transaction_type: TransactionType
    check_number: Optional[str] = None
    running_balance: float = 0.0
    
    @property
    def is_deposit(self) -> bool:
        return self.transaction_type == TransactionType.DEPOSIT
    
    @property
    def is_withdrawal(self) -> bool:
        return self.transaction_type == TransactionType.WITHDRAWAL
    
    @property
    def deposit_amount(self) -> Optional[float]:
        return self.amount if self.is_deposit else None
    
    @property
    def withdrawal_amount(self) -> Optional[float]:
        return self.amount if self.is_withdrawal else None


@dataclass
class StatementPeriod:
    start_date: date
    end_date: date
    
    @property
    def days(self) -> int:
        return (self.end_date - self.start_date).days
    
    def format_date_range(self) -> str:
        return f"{self.start_date.strftime('%B %d, %Y')} - {self.end_date.strftime('%B %d, %Y')}"


@dataclass
class StatementSummary:
    beginning_balance: float
    total_deposits: float
    total_withdrawals: float
    ending_balance: float
    
    @classmethod
    def from_transactions(cls, transactions: List[Transaction], beginning_balance: float) -> 'StatementSummary':
        total_deposits = sum(t.amount for t in transactions if t.is_deposit)
        total_withdrawals = sum(t.amount for t in transactions if t.is_withdrawal)
        ending_balance = beginning_balance + total_deposits - total_withdrawals
        
        return cls(
            beginning_balance=beginning_balance,
            total_deposits=total_deposits,
            total_withdrawals=total_withdrawals,
            ending_balance=ending_balance
        )


@dataclass
class BankStatement:
    account_holder: AccountHolder
    account_info: AccountInfo
    period: StatementPeriod
    transactions: List[Transaction]
    summary: StatementSummary
    generated_date: date = field(default_factory=date.today)
    
    @property
    def page_count(self) -> int:
        # First page is summary, remaining pages hold ~35 transactions each
        transaction_pages = max(1, (len(self.transactions) + 34) // 35)
        return 1 + transaction_pages
