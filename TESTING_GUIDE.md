# 🧪 Complete Testing Guide

## Overview
This guide will walk you through testing all DBMS concepts and features of the Banking System.

---

## 1. Testing Authentication System

### 1.1 Sign Up (New User Registration)
**Test Case**: Create a new customer account

**Steps**:
1. Go to `/signup`
2. Fill in the form:
   ```
   First Name: Test
   Last Name: User
   Email: test@example.com
   Password: password123
   Confirm Password: password123
   Phone: 555-9999
   Address: 123 Test Street
   Date of Birth: 2000-01-01
   Branch: Main Branch
   ```
3. Click "Create Account"

**Expected Result**:
- ✅ Success message: "Account created successfully! Please login."
- ✅ Redirect to login page
- ✅ New record in `customers` table

**SQL Verification**:
```sql
SELECT * FROM customers WHERE email = 'test@example.com';
```

### 1.2 Login (Existing User)
**Test Case**: Authenticate with test credentials

**Steps**:
1. Go to `/login`
2. Enter credentials:
   ```
   Email: alice@example.com
   Password: password
   ```
3. Click "Login"

**Expected Result**:
- ✅ Success message: "Welcome back, Alice!"
- ✅ Redirect to dashboard
- ✅ Session cookie created

### 1.3 Password Hashing Verification
**SQL Verification**:
```sql
-- Check that passwords are hashed (not plain text)
SELECT email, password_hash FROM customers LIMIT 5;
-- Should see hashed values starting with $2b$ (bcrypt)
```

---

## 2. Testing Account Management

### 2.1 View Accounts
**Test Case**: Display all user accounts

**Steps**:
1. Login as Alice
2. Navigate to Dashboard or `/accounts`

**Expected Result**:
- ✅ Display all accounts for logged-in user
- ✅ Show account number, type, balance, status
- ✅ Total balance calculation

**SQL Verification**:
```sql
SELECT * FROM accounts WHERE customer_id = 1;
```

---

## 3. Testing Fund Transfer (Stored Procedure)

### 3.1 Successful Transfer
**Test Case**: Transfer funds between accounts

**Steps**:
1. Login as Alice (customer_id: 1)
2. Navigate to `/transfer`
3. Select "From Account": ACC1001 (balance: $5000)
4. Enter "To Account Number": ACC2001
5. Enter "Amount": 500.00
6. Click "Transfer Now"

**Expected Result**:
- ✅ Success message: "Transfer completed successfully!"
- ✅ Sender balance decreased by $500
- ✅ Receiver balance increased by $500
- ✅ New record in `transactions` table
- ✅ Two records in `audit_logs` (one for each account)

**SQL Verification**:
```sql
-- Check balances updated
SELECT account_number, balance FROM accounts WHERE account_number IN ('ACC1001', 'ACC2001');

-- Check transaction recorded
SELECT * FROM transactions WHERE sender_account_id = (SELECT account_id FROM accounts WHERE account_number = 'ACC1001')
ORDER BY transaction_date DESC LIMIT 1;

-- Check audit logs created (trigger fired)
SELECT * FROM audit_logs WHERE account_id IN (
    SELECT account_id FROM accounts WHERE account_number IN ('ACC1001', 'ACC2001')
) ORDER BY changed_at DESC LIMIT 2;
```

### 3.2 Insufficient Funds (Failure Simulation)
**Test Case**: Attempt transfer exceeding balance

**Steps**:
1. Login as any user
2. Navigate to `/transfer`
3. Select sender account with balance $1500
4. Enter receiver account
5. Enter amount: $10,000 (more than balance)
6. Click "Transfer Now"

**Expected Result**:
- ❌ Error message: "Transfer failed: Insufficient funds..."
- ✅ NO balance changes (transaction rolled back)
- ✅ Record in `recovery_logs` table
- ✅ NO record in `transactions` table

**SQL Verification**:
```sql
-- Verify no balance change
SELECT account_number, balance FROM accounts WHERE account_number = 'ACC1002';

-- Check recovery log entry
SELECT * FROM recovery_logs ORDER BY failed_at DESC LIMIT 1;

-- Verify last transaction was NOT this failed transfer
SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT 1;
```

---

## 4. Testing Automatic Failure Simulation

### 4.1 Simulate Failure Button
**Test Case**: Intentionally trigger insufficient funds error

**Steps**:
1. Login as any user
2. Navigate to Dashboard
3. Click "Simulate Failure" button or go to `/simulate_failure`

**Expected Result**:
- ✅ Info message: "Failure simulation successful! The transaction was rolled back."
- ✅ Warning message with error details
- ✅ Info message: "Check the Recovery Logs table..."
- ✅ Automatic redirect to `/recovery_logs`
- ✅ New entry in recovery_logs with:
  - operation_type: 'TRANSFER'
  - failure_reason: 'Insufficient funds...'
  - sender_balance_at_failure: (current balance)
  - attempted_amount: (balance + 5000)

**SQL Verification**:
```sql
-- Check latest recovery log
SELECT 
    recovery_id,
    operation_type,
    sender_account_id,
    receiver_account_id,
    attempted_amount,
    sender_balance_at_failure,
    failure_reason,
    failed_at
FROM recovery_logs 
ORDER BY failed_at DESC 
LIMIT 1;

-- Verify balances unchanged
SELECT account_number, balance FROM accounts 
WHERE account_id = (SELECT sender_account_id FROM recovery_logs ORDER BY failed_at DESC LIMIT 1);
```

---

## 5. Testing Audit Logs (Triggers)

### 5.2 Trigger Behavior Verification
**Test Case**: Ensure trigger only fires on balance changes

**SQL Testing**:
```sql
-- Update account without changing balance (trigger should NOT fire)
UPDATE accounts SET status = 'ACTIVE' WHERE account_number = 'ACC1001';

-- Check audit logs - should be no new entry
SELECT * FROM audit_logs ORDER BY changed_at DESC LIMIT 1;

-- Update account with balance change (trigger SHOULD fire)
UPDATE accounts SET balance = balance + 100 WHERE account_number = 'ACC1001';

-- Check audit logs - should have new entry
SELECT * FROM audit_logs ORDER BY changed_at DESC LIMIT 1;
```

---

## 6. Testing Database Views

### 6.1 Customer Financial Overview View
**Test Case**: Verify aggregated customer data

**Steps**:
1. Navigate to `/reports/customer_overview`
2. View the report

**Expected Result**:
- ✅ Shows all customers with their:
  - Full name
  - Email
  - Branch
  - Total accounts count
  - Total balance (sum of all accounts)
- ✅ Ordered by total balance (highest first)

**SQL Verification**:
```sql
-- Query the view directly
SELECT * FROM customer_financial_overview;

-- Verify calculation manually for one customer
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS full_name,
    COUNT(a.account_id) AS account_count,
    SUM(a.balance) AS total_balance
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id
WHERE c.customer_id = 1
GROUP BY c.customer_id, c.first_name, c.last_name;
```

### 6.2 Branch Transaction Summary View
**Test Case**: Verify branch-level statistics

**Steps**:
1. Navigate to `/reports/branch_summary`
2. View the report

**Expected Result**:
- ✅ Shows all branches with:
  - Branch name and code
  - Total transaction count
  - Total transfer volume
  - Total deposits
  - Total withdrawals
  - Total accounts

**SQL Verification**:
```sql
-- Query the view
SELECT * FROM branch_transaction_summary;

-- Verify calculation for one branch
SELECT 
    b.branch_name,
    COUNT(DISTINCT t.transaction_id) as txn_count,
    SUM(CASE WHEN t.transaction_type = 'TRANSFER' THEN t.amount ELSE 0 END) as transfers
FROM branches b
LEFT JOIN accounts a ON b.branch_id = a.branch_id
LEFT JOIN transactions t ON a.account_id IN (t.sender_account_id, t.receiver_account_id)
WHERE b.branch_id = 1
GROUP BY b.branch_name;
```

---

## 7. Testing Constraints

### 7.1 CHECK Constraint (Balance >= 0)
**Test Case**: Verify balance cannot go negative

**SQL Testing**:
```sql
-- Try to set negative balance (should FAIL)
UPDATE accounts SET balance = -100 WHERE account_number = 'ACC1001';
-- Expected: ERROR: new row for relation "accounts" violates check constraint "chk_balance_non_negative"

-- Verify balance unchanged
SELECT balance FROM accounts WHERE account_number = 'ACC1001';
```

### 7.2 UNIQUE Constraint (Email)
**Test Case**: Prevent duplicate email registration

**Steps**:
1. Try to sign up with existing email: alice@example.com

**Expected Result**:
- ❌ Error message: "Email address already registered"
- ✅ No duplicate record created

**SQL Verification**:
```sql
-- Check email uniqueness
SELECT email, COUNT(*) FROM customers GROUP BY email HAVING COUNT(*) > 1;
-- Should return no rows
```

### 7.3 UNIQUE Constraint (Account Number)
**SQL Testing**:
```sql
-- Try to create duplicate account number (should FAIL)
INSERT INTO accounts (account_number, account_type, customer_id, branch_id)
VALUES ('ACC1001', 'SAVINGS', 2, 1);
-- Expected: ERROR: duplicate key value violates unique constraint "accounts_account_number_key"
```

### 7.4 Foreign Key Constraint
**SQL Testing**:
```sql
-- Try to create account with non-existent customer (should FAIL)
INSERT INTO accounts (account_number, account_type, customer_id, branch_id)
VALUES ('ACC9999', 'SAVINGS', 99999, 1);
-- Expected: ERROR: insert or update on table "accounts" violates foreign key constraint

-- Try to delete branch with existing accounts (should FAIL due to RESTRICT)
DELETE FROM branches WHERE branch_id = 1;
-- Expected: ERROR: update or delete on table "branches" violates foreign key constraint
```

---

## 8. Testing Transaction Integrity (ACID Properties)

### 8.1 Atomicity
**Test Case**: Verify all-or-nothing transaction behavior

**Testing**:
```sql
-- Manual test: Start transaction
BEGIN;

-- Update sender
UPDATE accounts SET balance = balance - 500 WHERE account_number = 'ACC1001';

-- Check interim state
SELECT balance FROM accounts WHERE account_number = 'ACC1001';

-- Rollback
ROLLBACK;

-- Verify balance restored
SELECT balance FROM accounts WHERE account_number = 'ACC1001';
```

### 8.2 Consistency
**Test Case**: Verify database remains in valid state

**Expected Behavior**:
- ✅ All constraints enforced
- ✅ No orphaned records
- ✅ Referential integrity maintained

**SQL Verification**:
```sql
-- Check for orphaned accounts (should return 0)
SELECT COUNT(*) FROM accounts a 
WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.customer_id = a.customer_id);

-- Check for orphaned transactions (should return 0)
SELECT COUNT(*) FROM transactions t
WHERE t.sender_account_id IS NOT NULL 
AND NOT EXISTS (SELECT 1 FROM accounts a WHERE a.account_id = t.sender_account_id);
```

### 8.3 Isolation
**Test Case**: Verify concurrent transaction handling

**Note**: The stored procedure uses `FOR UPDATE` locks to ensure isolation.

**SQL Testing**:
```sql
-- In one session
BEGIN;
SELECT * FROM accounts WHERE account_id = 1 FOR UPDATE;
-- (Don't commit yet)

-- In another session (will wait for lock)
BEGIN;
SELECT * FROM accounts WHERE account_id = 1 FOR UPDATE;
-- This will wait until first session commits/rolls back
```

### 8.4 Durability
**Test Case**: Verify committed transactions persist

**Testing**:
1. Perform a successful transfer
2. Restart the application
3. Verify transaction still exists in database

---

## 9. Testing Recovery Mechanism

### 9.1 Recovery Log Completeness
**Test Case**: Verify all failure details are logged

**Expected Fields in Recovery Log**:
- ✅ operation_type: 'TRANSFER'
- ✅ sender_account_id: ID of sender
- ✅ receiver_account_id: ID of receiver
- ✅ attempted_amount: Amount attempted
- ✅ sender_balance_at_failure: Balance at time of failure
- ✅ failure_reason: Detailed error message
- ✅ failed_at: Timestamp
- ✅ additional_details: JSON with extra info

**SQL Verification**:
```sql
SELECT 
    recovery_id,
    operation_type,
    sender_account_id,
    receiver_account_id,
    attempted_amount,
    sender_balance_at_failure,
    (attempted_amount - sender_balance_at_failure) as shortfall,
    failure_reason,
    additional_details,
    failed_at
FROM recovery_logs
ORDER BY failed_at DESC
LIMIT 5;
```

### 9.2 Multiple Failure Scenarios
**Test Cases**:

1. **Insufficient Funds**:
   - Trigger: Transfer amount > balance
   - Expected: Logged with detailed shortfall calculation

2. **Non-existent Sender Account**:
   ```sql
   SELECT transfer_funds(99999, 2, 100);
   -- Expected: Error + recovery log entry
   ```

3. **Non-existent Receiver Account**:
   ```sql
   SELECT transfer_funds(1, 99999, 100);
   -- Expected: Error + recovery log entry
   ```

**Verification**:
```sql
-- Check different failure reasons
SELECT DISTINCT failure_reason FROM recovery_logs;
```

---

## 10. Performance Testing

### 10.1 Index Effectiveness
**Test Case**: Verify query performance with indexes

**SQL Testing**:
```sql
-- Explain query plan (should use index)
EXPLAIN ANALYZE SELECT * FROM accounts WHERE customer_id = 1;
-- Look for "Index Scan" in the plan

EXPLAIN ANALYZE SELECT * FROM transactions WHERE sender_account_id = 1;
-- Should use idx_transactions_sender

-- Compare with sequential scan
EXPLAIN ANALYZE SELECT * FROM accounts WHERE address LIKE '%Street%';
-- Will show "Seq Scan" (no index on address)
```

### 10.2 Trigger Performance
**Test Case**: Measure trigger overhead

**SQL Testing**:
```sql
-- Time without trigger (disable temporarily)
ALTER TABLE accounts DISABLE TRIGGER trg_account_balance_audit;

\timing on
UPDATE accounts SET balance = balance + 1 WHERE account_id = 1;
-- Note the time

-- Enable trigger
ALTER TABLE accounts ENABLE TRIGGER trg_account_balance_audit;

UPDATE accounts SET balance = balance + 1 WHERE account_id = 1;
-- Compare the time
\timing off
```

---

## 11. Security Testing

### 11.1 SQL Injection Prevention
**Test Case**: Verify SQLAlchemy prevents SQL injection

**Attempt**:
1. In login form, enter:
   ```
   Email: admin' OR '1'='1
   Password: anything
   ```

**Expected Result**:
- ❌ Login fails (no SQL injection)
- ✅ Query treated as literal string, not SQL code

### 11.2 Password Security
**Test Case**: Verify passwords are not stored in plain text

**SQL Verification**:
```sql
-- Check password storage
SELECT email, password_hash FROM customers LIMIT 3;
-- Should see bcrypt hashes starting with $2b$12$...
-- Should NOT see plain text passwords
```

### 11.3 Session Security
**Test Case**: Verify login required for protected routes

**Steps**:
1. Logout (or use incognito window)
2. Try to access `/dashboard`

**Expected Result**:
- ❌ Access denied
- ✅ Redirect to `/login`
- ✅ Flash message: "Please log in to access this page."

---

## 12. Error Handling Testing

### 12.1 404 Error Page
**Test Case**: Custom 404 page displays

**Steps**:
1. Navigate to `/nonexistent-page`

**Expected Result**:
- ✅ Custom 404 page shown
- ✅ "Page Not Found" message
- ✅ Link to dashboard

### 12.2 500 Error Handling
**Test Case**: Database errors handled gracefully

**Simulation**:
1. Temporarily stop PostgreSQL
2. Try to access dashboard

**Expected Result**:
- ✅ Custom 500 error page
- ✅ User-friendly error message
- ✅ No sensitive information displayed

---

## 13. Comprehensive Test Checklist

### Database Objects
- [ ] All 7 tables created
- [ ] All foreign keys working
- [ ] All CHECK constraints enforced
- [ ] All UNIQUE constraints enforced
- [ ] Trigger `trg_account_balance_audit` firing
- [ ] Stored procedure `transfer_funds()` working
- [ ] View `customer_financial_overview` queryable
- [ ] View `branch_transaction_summary` queryable
- [ ] All indexes created

### Application Features
- [ ] User signup working
- [ ] User login/logout working
- [ ] Password hashing working
- [ ] Dashboard displaying correctly
- [ ] Account list showing
- [ ] Transfer form submitting
- [ ] Successful transfer completing
- [ ] Insufficient funds error handling
- [ ] Transaction history displaying
- [ ] Audit logs showing
- [ ] Recovery logs showing
- [ ] Failure simulation working
- [ ] Customer overview report working
- [ ] Branch summary report working

### DBMS Concepts Demonstrated
- [ ] Transactions (BEGIN/COMMIT/ROLLBACK)
- [ ] Triggers (automatic audit logging)
- [ ] Stored Procedures (transfer_funds)
- [ ] Views (reporting queries)
- [ ] Foreign Keys (referential integrity)
- [ ] CHECK Constraints (business rules)
- [ ] UNIQUE Constraints (data integrity)
- [ ] Indexes (performance optimization)
- [ ] Recovery Logs (failure tracking)
- [ ] ACID Properties (atomicity, consistency, isolation, durability)

---

## 14. Sample Test Data Queries

### Insert Additional Test Data
```sql
-- Add more branches
INSERT INTO branches (branch_name, branch_code, address, phone, manager_name) 
VALUES 
('Test Branch', 'BR999', '999 Test Ave', '555-9999', 'Test Manager');

-- Add test accounts with specific balances for testing
INSERT INTO accounts (account_number, account_type, balance, customer_id, branch_id)
VALUES 
('TESTACCT1', 'SAVINGS', 100.00, 1, 1),
('TESTACCT2', 'CHECKING', 50.00, 1, 1);

-- Perform test transfer
SELECT transfer_funds(
    (SELECT account_id FROM accounts WHERE account_number = 'TESTACCT1'),
    (SELECT account_id FROM accounts WHERE account_number = 'TESTACCT2'),
    25.00
);

-- Verify results
SELECT account_number, balance FROM accounts 
WHERE account_number IN ('TESTACCT1', 'TESTACCT2');
```

---

## 15. Automated Testing Script

Create a file `test_database.sql` for quick testing:

```sql
-- Banking System Test Suite
\echo '=== Starting Test Suite ==='

\echo '\n1. Testing Tables...'
SELECT COUNT(*) as table_count FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

\echo '\n2. Testing Triggers...'
SELECT COUNT(*) as trigger_count FROM information_schema.triggers 
WHERE trigger_schema = 'public';

\echo '\n3. Testing Functions...'
SELECT COUNT(*) as function_count FROM information_schema.routines 
WHERE routine_schema = 'public' AND routine_type = 'FUNCTION';

\echo '\n4. Testing Views...'
SELECT COUNT(*) as view_count FROM information_schema.views 
WHERE table_schema = 'public';

\echo '\n5. Testing Sample Data...'
SELECT COUNT(*) as customer_count FROM customers;
SELECT COUNT(*) as account_count FROM accounts;
SELECT COUNT(*) as transaction_count FROM transactions;

\echo '\n6. Testing Stored Procedure...'
SELECT transfer_funds(1, 2, 10.00);

\echo '\n7. Testing Views...'
SELECT * FROM customer_financial_overview LIMIT 3;
SELECT * FROM branch_transaction_summary LIMIT 3;

\echo '\n=== Test Suite Complete ==='
```

Run with: `psql -d banking_system -f test_database.sql`

---

## Summary

This comprehensive testing guide covers:
- ✅ All core banking features
- ✅ All DBMS concepts (Transactions, Triggers, Procedures, Views)
- ✅ Failure simulation and recovery
- ✅ Security measures
- ✅ Error handling
- ✅ Performance considerations

Use this guide to demonstrate your project works correctly and showcases all required DBMS concepts!1 Automatic Audit Logging
**Test Case**: Verify trigger creates audit logs on balance updates

**Setup**:
1. Note current balance of an account
2. Perform a transfer (as tested in 3.1)

**Expected Result**:
- ✅ Two audit log entries created:
  - One for sender (balance decreased)
  - One for receiver (balance increased)
- ✅ Each log shows:
  - old_balance: previous amount
  - new_balance: updated amount
  - operation_type: 'BALANCE_UPDATE'
  - changed_at: timestamp

**SQL Verification**:
```sql
-- View recent audit logs
SELECT 
    l.log_id,
    a.account_number,
    l.old_balance,
    l.new_balance,
    (l.new_balance - l.old_balance) as change,
    l.operation_type,
    l.changed_at
FROM audit_logs l
JOIN accounts a ON l.account_id = a.account_id
ORDER BY l.changed_at DESC
LIMIT 10;
```

### 5.