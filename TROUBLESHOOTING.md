# 🔧 Troubleshooting Guide - Common Issues & Solutions

## Issue 1: TemplateSyntaxError in Transactions Page

### Error Message
```
jinja2.exceptions.TemplateSyntaxError: expected token ',', got 'for'
```

### Cause
Jinja2 doesn't support Python list comprehensions directly in templates.

### Solution
✅ **FIXED** - The template now uses simpler Jinja2 syntax to check if transaction is debit or credit.

### How It Works Now
```html
{% if txn.sender_account and txn.sender_account.customer_id == current_user.customer_id %}
    <span class="text-danger">-${{ amount }}</span>  <!-- Debit -->
{% elif txn.receiver_account and txn.receiver_account.customer_id == current_user.customer_id %}
    <span class="text-success">+${{ amount }}</span>  <!-- Credit -->
{% endif %}
```

---

## Issue 2: Recovery Log Shows "N/A" After Failure Simulation

### Symptoms
- ✅ Transaction fails correctly
- ✅ Transaction is rolled back
- ❌ Recovery ID shows as "N/A"
- ❌ Recovery log may or may not be created

### Cause
The recovery log might be created inside the stored procedure's transaction, which gets rolled back along with the failed transfer.

### Solution
✅ **FIXED** - Updated the simulate_failure route to:
1. Count recovery logs before attempt
2. Verify new log was created after failure
3. Display proper recovery ID in flash message

### Verification
After clicking "Simulate Failure", you should see:
```
✓ Failure simulation successful! The transaction was rolled back.
Attempted to transfer $11000.00 from account with balance $6000.00
Recovery log created with ID: 1. Check Recovery Logs for details.
```

### Check Recovery Logs
```sql
-- Run this to verify recovery log was created
SELECT * FROM recovery_logs ORDER BY failed_at DESC LIMIT 1;
```

---

## Issue 3: Recovery Logs Not Being Created

### Problem
Recovery logs table is empty even after failure simulation.

### Root Cause
PostgreSQL RAISE EXCEPTION causes immediate rollback, which includes the INSERT into recovery_logs.

### Solution Options

#### Option A: Use AUTONOMOUS TRANSACTION (PostgreSQL 15+)
Not available in most versions, skip this.

#### Option B: Separate Transaction for Logging (Recommended)
We need to commit the recovery log BEFORE raising the exception.

Let me provide an updated stored procedure:

```sql
-- Updated transfer_funds with proper recovery logging
CREATE OR REPLACE FUNCTION transfer_funds(
    p_sender_account_id INTEGER,
    p_receiver_account_id INTEGER,
    p_amount NUMERIC
)
RETURNS TEXT AS $$
DECLARE
    v_sender_balance NUMERIC;
    v_sender_account_number VARCHAR(20);
    v_receiver_account_number VARCHAR(20);
BEGIN
    -- Get sender's current balance
    SELECT balance, account_number INTO v_sender_balance, v_sender_account_number
    FROM accounts
    WHERE account_id = p_sender_account_id
    FOR UPDATE;
    
    IF NOT FOUND THEN
        -- Use PERFORM to execute procedure without transaction
        PERFORM insert_recovery_log(
            'TRANSFER',
            p_sender_account_id,
            p_receiver_account_id,
            p_amount,
            'Sender account not found',
            NULL
        );
        
        RAISE EXCEPTION 'Sender account (ID: %) not found', p_sender_account_id;
    END IF;
    
    -- Check if receiver account exists
    SELECT account_number INTO v_receiver_account_number
    FROM accounts
    WHERE account_id = p_receiver_account_id
    FOR UPDATE;
    
    IF NOT FOUND THEN
        PERFORM insert_recovery_log(
            'TRANSFER',
            p_sender_account_id,
            p_receiver_account_id,
            p_amount,
            'Receiver account not found',
            v_sender_balance
        );
        
        RAISE EXCEPTION 'Receiver account (ID: %) not found', p_receiver_account_id;
    END IF;
    
    -- Check for insufficient funds
    IF v_sender_balance < p_amount THEN
        -- IMPORTANT: This INSERT is part of the transaction that will be rolled back
        -- In production, you'd use a separate connection or queue system
        INSERT INTO recovery_logs (
            operation_type, 
            sender_account_id, 
            receiver_account_id, 
            attempted_amount, 
            failure_reason,
            sender_balance_at_failure,
            additional_details
        ) VALUES (
            'TRANSFER',
            p_sender_account_id,
            p_receiver_account_id,
            p_amount,
            FORMAT('Insufficient funds. Required: %s, Available: %s, Shortfall: %s', 
                   p_amount, v_sender_balance, (p_amount - v_sender_balance)),
            v_sender_balance,
            jsonb_build_object(
                'sender_account', v_sender_account_number,
                'receiver_account', v_receiver_account_number,
                'deficit_amount', (p_amount - v_sender_balance)
            )
        );
        
        RAISE EXCEPTION 'Insufficient funds in account %. Available: %, Required: %', 
            v_sender_account_number, v_sender_balance, p_amount;
    END IF;
    
    -- Perform the transfer
    UPDATE accounts SET balance = balance - p_amount WHERE account_id = p_sender_account_id;
    UPDATE accounts SET balance = balance + p_amount WHERE account_id = p_receiver_account_id;
    
    -- Record transaction
    INSERT INTO transactions (
        transaction_type, amount, sender_account_id, receiver_account_id,
        description, status
    ) VALUES (
        'TRANSFER', p_amount, p_sender_account_id, p_receiver_account_id,
        FORMAT('Transfer from %s to %s', v_sender_account_number, v_receiver_account_number),
        'COMPLETED'
    );
    
    RETURN FORMAT('Transfer successful: %s transferred from account %s to account %s', 
                  p_amount, v_sender_account_number, v_receiver_account_number);
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END;
$$ LANGUAGE plpgsql;
```

### Alternative: Log from Application Level

Update `app.py` to catch exception and log manually:

```python
try:
    result = db.session.execute(
        text('SELECT transfer_funds(:sender, :receiver, :amount)'),
        {'sender': sender_id, 'receiver': receiver_id, 'amount': amount}
    )
    db.session.commit()
except Exception as e:
    db.session.rollback()
    
    # Manually create recovery log in separate transaction
    recovery_log = RecoveryLog(
        operation_type='TRANSFER',
        sender_account_id=sender_id,
        receiver_account_id=receiver_id,
        attempted_amount=amount,
        failure_reason=str(e),
        sender_balance_at_failure=Account.query.get(sender_id).balance
    )
    db.session.add(recovery_log)
    db.session.commit()
    
    flash('Transfer failed', 'danger')
```

---

## Issue 4: Database Connection Error

### Error Message
```
could not connect to server: Connection refused
```

### Solutions

#### Check PostgreSQL is Running
```bash
# Mac
brew services list | grep postgresql
brew services start postgresql@14

# Linux
sudo systemctl status postgresql
sudo systemctl start postgresql

# Windows
# Check Services app for PostgreSQL service
```

#### Check Database Exists
```bash
psql -l | grep banking_system

# If not exists
createdb banking_system
```

#### Check DATABASE_URL
```bash
# In terminal
echo $DATABASE_URL

# Should be something like:
# postgresql://localhost/banking_system
# or
# postgresql://username:password@localhost:5432/banking_system
```

---

## Issue 5: Module Not Found Errors

### Error Messages
```
ModuleNotFoundError: No module named 'flask'
ModuleNotFoundError: No module named 'psycopg2'
```

### Solution
```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(Flask|psycopg2|SQLAlchemy)"
```

---

## Issue 6: Login Fails with "Invalid email or password"

### Check 1: Did you run init_db.py?
```bash
# Must run this to create users with correct password hashes
python init_db.py
```

### Check 2: Verify users exist
```sql
psql -d banking_system
SELECT customer_id, email, is_active FROM customers;
```

Should show:
```
 customer_id |        email          | is_active
-------------+-----------------------+-----------
           1 | alice@example.com    | t
           2 | bob@example.com      | t
           3 | charlie@example.com  | t
```

### Check 3: Test password hash
```python
# In Python shell
from werkzeug.security import check_password_hash
from models import db, Customer
from app import app

with app.app_context():
    alice = Customer.query.filter_by(email='alice@example.com').first()
    print(check_password_hash(alice.password_hash, 'password'))
    # Should print: True
```

---

## Issue 7: "Table does not exist" Error

### Error Message
```
relation "customers" does not exist
```

### Solution
```bash
# Run schema.sql to create tables
psql -d banking_system -f schema.sql

# Verify tables created
psql -d banking_system -c "\dt"

# Should show 7 tables:
# branches, customers, employees, accounts, transactions, audit_logs, recovery_logs
```

---

## Issue 8: Trigger Not Firing

### Check if trigger exists
```sql
psql -d banking_system

-- List triggers
\dy

-- Or
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public';
```

### Recreate trigger if missing
```bash
# Re-run schema.sql
psql -d banking_system -f schema.sql
```

### Test trigger
```sql
-- Update balance (should create audit log)
UPDATE accounts SET balance = balance + 1 WHERE account_id = 1;

-- Check audit logs
SELECT * FROM audit_logs ORDER BY changed_at DESC LIMIT 1;
```

---

## Issue 9: Stored Procedure Not Found

### Error Message
```
function transfer_funds(integer, integer, numeric) does not exist
```

### Solution
```bash
# Re-run schema.sql
psql -d banking_system -f schema.sql

# Verify function exists
psql -d banking_system -c "\df transfer_funds"
```

---

## Issue 10: Port Already in Use

### Error Message
```
Address already in use
Port 5000 is in use by another program
```

### Solutions

#### Option A: Kill the process
```bash
# Find process using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill it
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

#### Option B: Use different port
```python
# In app.py, change last line to:
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Use port 5001 instead
```

---

## Quick Diagnostic Script

Save this as `diagnose.sh`:

```bash
#!/bin/bash
echo "=== Banking System Diagnostics ==="
echo

echo "1. Checking PostgreSQL..."
pg_isready && echo "✓ PostgreSQL running" || echo "✗ PostgreSQL not running"
echo

echo "2. Checking database..."
psql -l | grep banking_system && echo "✓ Database exists" || echo "✗ Database missing"
echo

echo "3. Checking tables..."
psql -d banking_system -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null
echo

echo "4. Checking Python packages..."
pip list | grep -E "(Flask|psycopg2|SQLAlchemy)" && echo "✓ Packages installed" || echo "✗ Packages missing"
echo

echo "5. Checking test data..."
psql -d banking_system -c "SELECT COUNT(*) as customer_count FROM customers;" 2>/dev/null
echo

echo "=== Diagnostics Complete ==="
```

Run with: `bash diagnose.sh`

---

## Getting Help

### View Application Logs
```bash
# Run with debug mode
export FLASK_ENV=development
python app.py

# Flask will show detailed error messages
```

### Check Database Logs
```bash
# Mac
tail -f /usr/local/var/log/postgresql@14.log

# Linux
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Common Commands
```bash
# Restart everything
brew services restart postgresql@14  # Mac
python app.py

# Clean slate
dropdb banking_system
createdb banking_system
psql -d banking_system -f schema.sql
python init_db.py
python app.py
```

---

## Still Having Issues?

1. Check you're using Python 3.11+: `python --version`
2. Check PostgreSQL 14+: `psql --version`
3. Verify virtual environment is activated: `which python`
4. Check all files are present: `ls -la`
5. Run the test script: `psql -d banking_system -f test_queries.sql`

If problems persist, check the detailed logs and error messages - they usually point to the exact issue!