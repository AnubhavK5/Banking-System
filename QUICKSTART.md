# ⚡ Quick Start Guide - Banking System

Get up and running in 5 minutes!

---

## 🚀 Option 1: Local Setup (Fastest for Testing)

### Prerequisites
- Python 3.11+
- PostgreSQL installed and running

### Setup Commands
```bash
# 1. Clone/download the project
cd banking-system

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create database
createdb banking_system

# 5. Initialize database schema
psql -d banking_system -f schema.sql

# 6. Set environment variable
export DATABASE_URL="postgresql://localhost/banking_system"
# Windows: set DATABASE_URL=postgresql://localhost/banking_system

# 7. Run application
python app.py
```

### Access Application
- Open browser: http://localhost:5000
- Login with: alice@example.com / password

---

## 🌐 Option 2: Deploy to Render (Free Hosting)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 2: Create Database on Render
1. Go to https://render.com
2. New → PostgreSQL
3. Name: `banking-system-db`
4. Create Database
5. Copy **Internal Database URL**

### Step 3: Initialize Database
```bash
# Connect using External URL from Render
psql YOUR_EXTERNAL_DATABASE_URL

# Run schema
\i schema.sql

# Verify
\dt
\q
```

### Step 4: Deploy Web Service
1. New → Web Service
2. Connect GitHub repository
3. Settings:
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `gunicorn app:app`
4. Environment Variables:
   - `DATABASE_URL`: (paste Internal URL)
   - `SECRET_KEY`: (generate random string)
5. Create Web Service
6. Wait 5-10 minutes

### Access Application
Your app will be live at: `https://your-app.onrender.com`

---

## 🧪 Quick Testing

### Test Login
```
Email: alice@example.com
Password: password

OR

Email: bob@example.com
Password: password
```

### Test Transfer
1. Login
2. Go to Dashboard → Transfer Funds
3. From: Select any account
4. To: Enter another account number (e.g., ACC2001)
5. Amount: 100.00
6. Transfer Now

### Test Failure Simulation
1. Login
2. Dashboard → Click "Simulate Failure" button
3. View Recovery Logs

### Test Database Concepts
```sql
-- Connect to database
psql -d banking_system

-- View all tables
\dt

-- Check trigger exists
SELECT * FROM information_schema.triggers;

-- Check stored procedure
SELECT * FROM information_schema.routines WHERE routine_type = 'FUNCTION';

-- View audit logs (created by trigger)
SELECT * FROM audit_logs ORDER BY changed_at DESC LIMIT 5;

-- View recovery logs (failed transactions)
SELECT * FROM recovery_logs ORDER BY failed_at DESC LIMIT 5;

-- Query views
SELECT * FROM customer_financial_overview;
SELECT * FROM branch_transaction_summary;

-- Test stored procedure manually
SELECT transfer_funds(1, 2, 50.00);
```

---

## 📁 Project Files Checklist

Make sure you have all these files:

```
banking-system/
├── app.py                      ✓ Main Flask app
├── models.py                   ✓ SQLAlchemy models
├── auth.py                     ✓ Authentication routes
├── schema.sql                  ✓ Database DDL script
├── requirements.txt            ✓ Python dependencies
├── render.yaml                 ✓ Render config (optional)
├── .env.example               ✓ Environment template
├── README.md                   ✓ Documentation
├── DEPLOYMENT_GUIDE.md         ✓ Deployment instructions
├── TESTING_GUIDE.md           ✓ Testing documentation
├── templates/                  ✓ HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── transfer.html
│   ├── accounts.html
│   ├── transactions.html
│   ├── audit_logs.html
│   ├── recovery_logs.html
│   ├── customer_overview.html
│   ├── branch_summary.html
│   ├── 404.html
│   └── 500.html
```

---

## 🎯 Key Features to Demonstrate

### 1. Triggers (Automatic Auditing)
- Make any transfer
- Check Audit Logs page
- See automatic balance change tracking

### 2. Stored Procedures (Fund Transfer)
- All transfers use `transfer_funds()` procedure
- Automatic transaction management
- Rollback on failure

### 3. Views (Reporting)
- Reports → Customer Overview
- Reports → Branch Summary
- Pre-computed aggregations

### 4. Recovery Mechanism
- Click "Simulate Failure"
- Check Recovery Logs
- See detailed failure information

### 5. Constraints
- Try negative balance (prevented)
- Try duplicate email (prevented)
- Foreign key integrity enforced

---

## 🔍 Verification Queries

Run these to verify everything works:

```sql
-- 1. Check all tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Expected: accounts, audit_logs, branches, customers, employees, recovery_logs, transactions

-- 2. Verify trigger
SELECT trigger_name, event_manipulation, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public';

-- Expected: trg_account_balance_audit on accounts table

-- 3. Verify stored procedure
SELECT routine_name, routine_type 
FROM information_schema.routines 
WHERE routine_schema = 'public';

-- Expected: transfer_funds (FUNCTION), log_account_update (FUNCTION)

-- 4. Verify views
SELECT table_name FROM information_schema.views 
WHERE table_schema = 'public';

-- Expected: customer_financial_overview, branch_transaction_summary

-- 5. Check sample data
SELECT 'Branches' as entity, COUNT(*) as count FROM branches
UNION ALL
SELECT 'Customers', COUNT(*) FROM customers
UNION ALL
SELECT 'Accounts', COUNT(*) FROM accounts
UNION ALL
SELECT 'Employees', COUNT(*) FROM employees;

-- Expected: 3 branches, 3 customers, 5 accounts, 3 employees
```

---

## 🐛 Quick Troubleshooting

### Issue: Can't connect to database
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -d banking_system -c "SELECT 1;"
```

### Issue: Module not found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Table doesn't exist
```bash
# Re-run schema
psql -d banking_system -f schema.sql
```

### Issue: Permission denied
```bash
# Grant permissions
psql -d banking_system -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;"
psql -d banking_system -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;"
```

---

## 📊 Quick Demo Script

Use this for presentations:

```markdown
1. **Show Home Page**
   - Beautiful landing page with features

2. **Sign Up / Login**
   - "Let me login as Alice..."
   - alice@example.com / password

3. **Dashboard**
   - "Here are my accounts with total balance"
   - "Recent transactions shown below"

4. **Transfer Funds**
   - "Let me transfer $500 from ACC1001 to ACC2001"
   - Show successful transfer
   - Return to dashboard - balance updated!

5. **Audit Logs**
   - "Notice the system automatically logged the balance changes"
   - "This is done by a PostgreSQL trigger"

6. **Simulate Failure**
   - "Now let me demonstrate failure handling"
   - Click Simulate Failure button
   - "See how the transaction was rolled back?"

7. **Recovery Logs**
   - "The system logged the failure details"
   - "Shows: amount attempted, balance at failure, reason"

8. **Reports**
   - Customer Overview: "Database view showing aggregated data"
   - Branch Summary: "Another view with transaction statistics"

9. **Database Tour** (if presenting SQL)
   ```sql
   -- Show trigger
   \d accounts
   
   -- Show stored procedure
   \df transfer_funds
   
   -- Show views
   \dv
   
   -- Query audit logs
   SELECT * FROM audit_logs ORDER BY changed_at DESC LIMIT 5;
   ```
```

---

## ✅ Success Criteria

Your project is working if:
- ✅ Can login with test credentials
- ✅ Can view accounts and balances
- ✅ Can perform successful transfer
- ✅ Audit logs show balance changes
- ✅ Failure simulation creates recovery log
- ✅ Views display aggregated data
- ✅ All 7 tables exist
- ✅ Trigger and stored procedure work
- ✅ Constraints are enforced

---

## 🎉 You're Done!

Your banking system is now:
- ✅ Running locally or on Render
- ✅ Database fully initialized
- ✅ All DBMS concepts working
- ✅ Ready for demonstration

**Live URL**: https://your-app.onrender.com
**Local URL**: http://localhost:5000

Need help? Check the full documentation:
- README.md - Complete overview
- DEPLOYMENT_GUIDE.md - Detailed deployment steps
- TESTING_GUIDE.md - Comprehensive testing

Good luck with your project! 🚀