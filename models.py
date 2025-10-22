from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class Branch(db.Model):
    __tablename__ = 'branches'
    
    branch_id = db.Column(db.Integer, primary_key=True)
    branch_name = db.Column(db.String(100), nullable=False, unique=True)
    branch_code = db.Column(db.String(20), nullable=False, unique=True)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    manager_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customers = db.relationship('Customer', backref='branch', lazy=True)
    employees = db.relationship('Employee', backref='branch', lazy=True)
    accounts = db.relationship('Account', backref='branch', lazy=True)
    
    def __repr__(self):
        return f'<Branch {self.branch_name}>'
    
    def to_dict(self):
        return {
            'branch_id': self.branch_id,
            'branch_name': self.branch_name,
            'branch_code': self.branch_code,
            'address': self.address,
            'phone': self.phone,
            'manager_name': self.manager_name
        }


class Customer(UserMixin, db.Model):
    __tablename__ = 'customers'
    
    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    accounts = db.relationship('Account', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    # Flask-Login required methods
    def get_id(self):
        return str(self.customer_id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_active(self):
        return self.is_active
    
    def __repr__(self):
        return f'<Customer {self.first_name} {self.last_name}>'
    
    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'branch_id': self.branch_id,
            'is_active': self.is_active
        }


class Employee(db.Model):
    __tablename__ = 'employees'
    
    employee_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    position = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Numeric(12, 2))
    hire_date = db.Column(db.Date, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name} - {self.position}>'
    
    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'position': self.position,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'branch_id': self.branch_id,
            'is_active': self.is_active
        }


class Account(db.Model):
    __tablename__ = 'accounts'
    
    account_id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), nullable=False, unique=True)
    account_type = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=False)
    status = db.Column(db.String(20), default='ACTIVE')
    opened_date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sent_transactions = db.relationship('Transaction', 
                                       foreign_keys='Transaction.sender_account_id',
                                       backref='sender_account', 
                                       lazy=True)
    received_transactions = db.relationship('Transaction', 
                                           foreign_keys='Transaction.receiver_account_id',
                                           backref='receiver_account', 
                                           lazy=True)
    audit_logs = db.relationship('AuditLog', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Account {self.account_number} - Balance: {self.balance}>'
    
    def to_dict(self):
        return {
            'account_id': self.account_id,
            'account_number': self.account_number,
            'account_type': self.account_type,
            'balance': float(self.balance) if self.balance else 0.00,
            'customer_id': self.customer_id,
            'branch_id': self.branch_id,
            'status': self.status,
            'opened_date': self.opened_date.isoformat() if self.opened_date else None
        }


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    transaction_id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    sender_account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'))
    receiver_account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='COMPLETED')
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id} - {self.transaction_type} - {self.amount}>'
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'transaction_type': self.transaction_type,
            'amount': float(self.amount) if self.amount else 0.00,
            'sender_account_id': self.sender_account_id,
            'receiver_account_id': self.receiver_account_id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'description': self.description,
            'status': self.status
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)
    old_balance = db.Column(db.Numeric(15, 2))
    new_balance = db.Column(db.Numeric(15, 2))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    operation_type = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<AuditLog {self.log_id} - Account {self.account_id}>'
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'account_id': self.account_id,
            'old_balance': float(self.old_balance) if self.old_balance else 0.00,
            'new_balance': float(self.new_balance) if self.new_balance else 0.00,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
            'operation_type': self.operation_type
        }


class RecoveryLog(db.Model):
    __tablename__ = 'recovery_logs'
    
    recovery_id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(50), nullable=False)
    sender_account_id = db.Column(db.Integer)
    receiver_account_id = db.Column(db.Integer)
    attempted_amount = db.Column(db.Numeric(15, 2))
    failure_reason = db.Column(db.Text, nullable=False)
    failed_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender_balance_at_failure = db.Column(db.Numeric(15, 2))
    additional_details = db.Column(JSONB)
    
    def __repr__(self):
        return f'<RecoveryLog {self.recovery_id} - {self.operation_type}>'
    
    def to_dict(self):
        return {
            'recovery_id': self.recovery_id,
            'operation_type': self.operation_type,
            'sender_account_id': self.sender_account_id,
            'receiver_account_id': self.receiver_account_id,
            'attempted_amount': float(self.attempted_amount) if self.attempted_amount else 0.00,
            'failure_reason': self.failure_reason,
            'failed_at': self.failed_at.isoformat() if self.failed_at else None,
            'sender_balance_at_failure': float(self.sender_balance_at_failure) if self.sender_balance_at_failure else 0.00,
            'additional_details': self.additional_details
        }