"""
Database Initialization Script
Run this AFTER creating tables with schema.sql to insert test data with proper password hashes
"""

import psycopg2
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/banking_system')

# Fix for Render URLs
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def init_database():
    """Initialize database with test data"""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("🔗 Connected to database")
        
        # Generate password hashes
        password = "password"
        alice_hash = generate_password_hash(password)
        bob_hash = generate_password_hash(password)
        charlie_hash = generate_password_hash(password)
        
        print(f"🔐 Generated password hashes (password: '{password}')")
        
        # Clear existing data (optional - comment out if you want to keep data)
        print("\n🗑️  Clearing existing data...")
        cur.execute("TRUNCATE TABLE recovery_logs, audit_logs, transactions, accounts, employees, customers, branches RESTART IDENTITY CASCADE;")
        
        # Insert Branches
        print("🏢 Inserting branches...")
        cur.execute("""
            INSERT INTO branches (branch_name, branch_code, address, phone, manager_name) VALUES
            ('Main Branch', 'BR001', '123 Main Street, New York, NY 10001', '555-0100', 'John Smith'),
            ('Downtown Branch', 'BR002', '456 Park Avenue, New York, NY 10022', '555-0200', 'Sarah Johnson'),
            ('Suburban Branch', 'BR003', '789 Oak Street, Brooklyn, NY 11201', '555-0300', 'Michael Brown')
            RETURNING branch_id, branch_name;
        """)
        branches = cur.fetchall()
        for branch in branches:
            print(f"  ✓ {branch[1]} (ID: {branch[0]})")
        
        # Insert Customers with hashed passwords
        print("\n👥 Inserting customers...")
        cur.execute("""
            INSERT INTO customers (first_name, last_name, email, password_hash, phone, address, date_of_birth, branch_id) VALUES
            ('Alice', 'Williams', 'alice@example.com', %s, '555-1001', '100 First Ave, NY', '1990-05-15', 1),
            ('Bob', 'Davis', 'bob@example.com', %s, '555-1002', '200 Second Ave, NY', '1985-08-20', 1),
            ('Charlie', 'Miller', 'charlie@example.com', %s, '555-1003', '300 Third Ave, NY', '1992-03-10', 2)
            RETURNING customer_id, first_name, last_name, email;
        """, (alice_hash, bob_hash, charlie_hash))
        customers = cur.fetchall()
        for customer in customers:
            print(f"  ✓ {customer[1]} {customer[2]} ({customer[3]}) - ID: {customer[0]}")
        
        # Insert Employees
        print("\n👔 Inserting employees...")
        cur.execute("""
            INSERT INTO employees (first_name, last_name, email, phone, position, salary, hire_date, branch_id) VALUES
            ('Emma', 'Wilson', 'emma.wilson@bank.com', '555-2001', 'Teller', 45000.00, '2020-01-15', 1),
            ('David', 'Taylor', 'david.taylor@bank.com', '555-2002', 'Manager', 75000.00, '2018-06-01', 1),
            ('Lisa', 'Anderson', 'lisa.anderson@bank.com', '555-2003', 'Loan Officer', 60000.00, '2019-03-20', 2)
            RETURNING employee_id, first_name, last_name, position;
        """)
        employees = cur.fetchall()
        for employee in employees:
            print(f"  ✓ {employee[1]} {employee[2]} - {employee[3]} (ID: {employee[0]})")
        
        # Insert Accounts
        print("\n💰 Inserting accounts...")
        cur.execute("""
            INSERT INTO accounts (account_number, account_type, balance, customer_id, branch_id) VALUES
            ('ACC1001', 'SAVINGS', 5000.00, 1, 1),
            ('ACC1002', 'CHECKING', 1500.00, 1, 1),
            ('ACC2001', 'SAVINGS', 10000.00, 2, 1),
            ('ACC3001', 'CHECKING', 3000.00, 3, 2),
            ('ACC3002', 'SAVINGS', 500.00, 3, 2)
            RETURNING account_id, account_number, account_type, balance;
        """)
        accounts = cur.fetchall()
        for account in accounts:
            print(f"  ✓ {account[1]} ({account[2]}) - Balance: ${account[3]:.2f}")
        
        # Commit all changes
        conn.commit()
        
        print("\n✅ Database initialized successfully!")
        print("\n📝 Test Credentials:")
        print("   Email: alice@example.com | Password: password")
        print("   Email: bob@example.com | Password: password")
        print("   Email: charlie@example.com | Password: password")
        
        # Close connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("🏦 Banking System - Database Initialization")
    print("=" * 60)
    init_database()
    print("=" * 60)