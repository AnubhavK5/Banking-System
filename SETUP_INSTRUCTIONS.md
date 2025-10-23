# 🔧 Complete Setup Instructions (Fixed)

## The Problem & Solution

**Problem**: The password hash error occurs because the sample data in `schema.sql` uses an incorrect hash format.

**Solution**: Use the `init_db.py` script to generate proper password hashes using Werkzeug (same library Flask uses).

---

## ✅ Correct Setup Procedure

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt
```

### Step 2: Create Database

```bash
# Using createdb command
createdb banking_system

# OR using psql
psql -U postgres
CREATE DATABASE banking_system;
\q
```

### Step 3: Create Tables Only (No Sample Data Yet)

```bash
# Run schema.sql to create tables, triggers, procedures, views
psql -d banking_system -f schema.sql
```

### Step 4: Insert Sample Data with Correct Password Hashes

```bash
# Set your database URL (if not default)
export DATABASE_URL="postgresql://localhost/banking_system"

# Run the initialization script
python init_db.py
```

You should see output like:
```
============================================================
🏦 Banking System - Database Initialization
============================================================
🔗 Connected to database
🔐 Generated password hashes (password: 'password')

🗑️  Clearing existing data...
🏢 Inserting branches...
  ✓ Main Branch (ID: 1)
  ✓ Downtown Branch (ID: 2)
  ✓ Suburban Branch (ID: 3)

👥 Inserting customers...
  ✓ Alice Williams (alice@example.com) - ID: 1
  ✓ Bob Davis (bob@example.com) - ID: 2
  ✓ Charlie Miller (charlie@example.com) - ID: 3

👔 Inserting employees...
  ✓ Emma Wilson - Teller (ID: 1)
  ✓ David Taylor - Manager (ID: 2)
  ✓ Lisa Anderson - Loan Officer (ID: 3)

💰 Inserting accounts...
  ✓ ACC1001 (SAVINGS) - Balance: $5000.00
  ✓ ACC1002 (CHECKING) - Balance: $1500.00
  ✓ ACC2001 (SAVINGS) - Balance: $10000.00
  ✓ ACC3001 (CHECKING) - Balance: $3000.00
  ✓ ACC3002 (SAVINGS) - Balance: $500.00

✅ Database initialized successfully!

📝 Test Credentials:
   Email: alice@example.com | Password: password
   Email: bob@example.com | Password: password
   Email: charlie@example.com | Password: password
============================================================
```

### Step 5: Run the Application

```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

### Step 6: Test Login

1. Open browser: http://localhost:5000
2. Click "Login"
3. Enter:
   - Email: `alice@example.com`
   - Password: `password`
4. Click "Login"

✅ **You should now be logged in!**

---

## 🧪 Easy Way to Test SQL Features

### Option 1: Run the Complete Test Script (Easiest!)

```bash
psql -d banking_system -f test_queries.sql
```

This will automatically test:
- ✅ All tables and data
- ✅ Triggers (audit logging)
- ✅ Stored procedure (successful transfer)
- ✅ Failure simulation (insufficient funds)
- ✅ Database views
- ✅ All constraints
- ✅ Performance (query plans)

**Output is color-coded and easy to read!**

### Option 2: Test Individual Features

Open psql:
```bash
psql -d banking_system
```

Then run these commands:

#### Test 1: View All Data
```sql
-- See all customers
SELECT * FROM customers;

-- See all accounts
SELECT * FROM accounts;

-- See all transactions
SELECT * FROM transactions;
```

#### Test 2: Successful Transfer
```sql
-- Check balances before
SELECT account_number, balance FROM accounts WHERE account_number IN ('ACC1001', 'ACC2001');

-- Do transfer
SELECT transfer_funds(
    (SELECT account_id FROM accounts WHERE account_number = 'ACC1001'),
    (SELECT account_id FROM accounts WHERE account_number = 'ACC2001'),
    100.00
);

-- Check balances after
SELECT account_number, balance FROM accounts WHERE account_number IN ('ACC1001', 'ACC2001');

-- Check audit logs (trigger created these!)
SELECT * FROM audit_logs ORDER BY changed_at DESC LIMIT 2;
```

#### Test 3: Failure Simulation
```sql
-- This should FAIL (insufficient funds)
SELECT transfer_funds(
    (SELECT account_id FROM accounts WHERE account_number = 'ACC3002'),
    (SELECT account_id FROM accounts WHERE account_number = 'ACC1001'),
    50000.00
);

-- Check recovery logs
SELECT * FROM recovery_logs ORDER BY failed_at DESC LIMIT 1;
```

#### Test 4: Database Views
```sql
-- Customer overview
SELECT * FROM customer_financial_overview;

-- Branch summary
SELECT * FROM branch_transaction_summary;
```

### Option 3: Test via Web Interface (Easiest for Demo!)

1. **Login**: alice@example.com / password
2. **Dashboard**: See your accounts
3. **Transfer**: 
   - From: ACC1001
   - To: ACC2001
   - Amount: 500
4. **Click "Simulate Failure"**: Tests recovery mechanism
5. **View Reports**:
   - Audit Logs
   - Recovery Logs
   - Customer Overview
   - Branch Summary

---

## 🎨 ER Diagram

The ER diagram has been created as a Mermaid diagram. You can:

### View Online:
1. Copy the ER diagram code from the artifact
2. Go to https://mermaid.live
3. Paste the code
4. Download as PNG/SVG

### View in VS Code:
1. Install "Markdown Preview Mermaid Support" extension
2. Create a file `ER_DIAGRAM.md`
3. Paste the ER diagram code
4. Click "Preview"

### Export for Documentation:
The ER diagram shows:
- 7 tables with all fields
- Primary keys (PK)
- Foreign keys (FK)
- Unique constraints (UK)
- Relationships between tables
- Cardinality (one-to-many, etc.)

---

## 📊 Complete File Structure

```
banking-system/
├── app.py                      # Main application
├── models.py                   # Database models
├── auth.py                     # Authentication
├── schema.sql                  # Table creation only
├── init_db.py                  # ⭐ NEW: Insert sample data
├── test_queries.sql            # ⭐ NEW: Easy testing
├── requirements.txt
├── .env.example
├── .gitignore
├── Procfile
├── runtime.txt
├── render.yaml
├── README.md
├── QUICKSTART.md
├── DEPLOYMENT_GUIDE.md
├── TESTING_GUIDE.md
├── SETUP_INSTRUCTIONS.md       # ⭐ NEW: This file
├── PROJECT_STRUCTURE.md
├── DEMO_SCRIPT.md
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── signup.html
    ├── dashboard.html
    ├── accounts.html
    ├── transfer.html
    ├── transactions.html
    ├── audit_logs.html
    ├── recovery_logs.html
    ├── customer_overview.html
    ├── branch_summary.html
    ├── 404.html
    └── 500.html
```

---

## 🔥 Quick Commands Cheat Sheet

```bash
# Setup
createdb banking_system
psql -d banking_system -f schema.sql
python init_db.py
python app.py

# Test SQL Features
psql -d banking_system -f test_queries.sql

# Quick Database Access
psql -d banking_system

# Check if tables exist
psql -d banking_system -c "\dt"

# Check if trigger exists
psql -d banking_system -c "\dy"

# Check if functions exist
psql -d banking_system -c "\df"

# View sample data
psql -d banking_system -c "SELECT * FROM customers;"

# Test login
# Browser: http://localhost:5000
# Email: alice@example.com
# Password: password
```

---

## 🐛 Troubleshooting

### Issue: "ValueError: Invalid hash method"
**Solution**: You ran the old schema.sql with bad password hashes.
```bash
# Fix it:
psql -d banking_system -c "TRUNCATE customers CASCADE;"
python init_db.py
```

### Issue: "relation does not exist"
**Solution**: Tables not created.
```bash
psql -d banking_system -f schema.sql
python init_db.py
```

### Issue: "psycopg2 not installed"
**Solution**: Install requirements.
```bash
pip install -r requirements.txt
```

### Issue: "Cannot connect to database"
**Solution**: PostgreSQL not running.
```bash
# Mac
brew services start postgresql

# Linux
sudo service postgresql start

# Windows
# Start PostgreSQL from Services
```

### Issue: "Database does not exist"
**Solution**: Create it.
```bash
createdb banking_system
```

---

## ✅ Verification Checklist

Run these to verify everything works:

```bash
# 1. Check Python packages
pip list | grep -E "(Flask|psycopg2|SQLAlchemy)"

# 2. Check database exists
psql -l | grep banking_system

# 3. Check tables created
psql -d banking_system -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
# Should return: 7

# 4. Check sample data
psql -d banking_system -c "SELECT COUNT(*) FROM customers;"
# Should return: 3

# 5. Check trigger exists
psql -d banking_system -c "SELECT trigger_name FROM information_schema.triggers WHERE trigger_schema='public';"
# Should show: trg_account_balance_audit

# 6. Check stored procedure exists
psql -d banking_system -c "SELECT routine_name FROM information_schema.routines WHERE routine_schema='public' AND routine_name='transfer_funds';"
# Should show: transfer_funds

# 7. Check views exist
psql -d banking_system -c "SELECT table_name FROM information_schema.views WHERE table_schema='public';"
# Should show: customer_financial_overview, branch_transaction_summary

# 8. Test login
# Start app: python app.py
# Open: http://localhost:5000
# Login: alice@example.com / password
# Should work!
```

---

## 🎯 What to Submit for Your Project

### 1. Source Code
- All Python files (app.py, models.py, auth.py, init_db.py)
- All SQL files (schema.sql, test_queries.sql)
- All HTML templates
- requirements.txt

### 2. Documentation
- README.md (project overview)
- SETUP_INSTRUCTIONS.md (this file)
- ER Diagram (as image or Mermaid code)

### 3. Screenshots
Take screenshots of:
- ✅ Database schema (pgAdmin or \d command)
- ✅ Trigger definition (\d+ accounts)
- ✅ Stored procedure code (\df+ transfer_funds)
- ✅ Views definition (\d+ customer_financial_overview)
- ✅ Successful login page
- ✅ Dashboard with accounts
- ✅ Successful transfer
- ✅ Audit logs page
- ✅ Recovery logs page (after failure simulation)
- ✅ Reports (customer overview, branch summary)

### 4. Live Demo URL
If deployed on Render:
- Provide the live URL
- Include test credentials in documentation

### 5. Video Demo (Optional but Impressive!)
Record a 5-10 minute video showing:
1. Database schema
2. Trigger in action
3. Successful transfer
4. Failure simulation
5. Recovery logs
6. All views

---

## 🎓 Key DBMS Concepts Demonstrated

| Concept | Location | How to Verify |
|---------|----------|---------------|
| **Triggers** | schema.sql | Run test_queries.sql or update any account balance |
| **Stored Procedures** | schema.sql (transfer_funds) | Do a transfer via UI or SQL |
| **Views** | schema.sql | Query customer_financial_overview |
| **Transactions** | transfer_funds procedure | See BEGIN/COMMIT in code |
| **Constraints** | All tables | Try to violate (negative balance, etc.) |
| **Foreign Keys** | All relationships | Try to delete a branch with accounts |
| **Normalization** | Table design | No data redundancy |
| **Indexes** | schema.sql | Run EXPLAIN on queries |
| **Recovery** | recovery_logs table | Click "Simulate Failure" |
| **Audit Trail** | audit_logs + trigger | Every balance change is logged |

---

## 🚀 Ready to Go!

You now have:
- ✅ Working password authentication
- ✅ Easy SQL testing script
- ✅ ER diagram
- ✅ Complete setup instructions
- ✅ Troubleshooting guide

**Next Steps:**
1. Run `init_db.py` to fix password issue
2. Run `test_queries.sql` to test all features
3. Login to web app
4. Take screenshots for documentation
5. Deploy to Render (optional)

Good luck with your project! 🎉