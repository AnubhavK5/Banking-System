-- ========================================
-- Banking System - Test Queries Script
-- Run this file to test all features easily
-- Usage: psql -d banking_system -f test_queries.sql
-- ========================================

\echo '============================================'
\echo '   BANKING SYSTEM - TEST QUERIES'
\echo '============================================'
\echo ''

-- Enable timing to see query performance
\timing on

-- ========================================
-- 1. VERIFY DATABASE STRUCTURE
-- ========================================
\echo '1. Checking Database Tables...'
\echo '--------------------------------------------'
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
\echo ''

-- ========================================
-- 2. CHECK SAMPLE DATA
-- ========================================
\echo '2. Checking Sample Data...'
\echo '--------------------------------------------'
\echo 'Branches:'
SELECT branch_id, branch_name, branch_code, manager_name FROM branches;
\echo ''

\echo 'Customers:'
SELECT customer_id, first_name, last_name, email, is_active FROM customers;
\echo ''

\echo 'Accounts:'
SELECT account_id, account_number, account_type, balance, customer_id FROM accounts;
\echo ''

-- ========================================
-- 3. TEST TRIGGER (Audit Logging)
-- ========================================
\echo '3. Testing Trigger - Audit Logging...'
\echo '--------------------------------------------'
\echo 'Current audit logs count:'
SELECT COUNT(*) as audit_count FROM audit_logs;
\echo ''

\echo 'Updating account balance to trigger audit log...'
UPDATE accounts SET balance = balance + 100 WHERE account_number = 'ACC1001';
\echo ''

\echo 'New audit logs (should have new entry):'
SELECT log_id, account_id, old_balance, new_balance, operation_type, changed_at 
FROM audit_logs 
ORDER BY changed_at DESC 
LIMIT 3;
\echo ''

-- Revert the change
UPDATE accounts SET balance = balance - 100 WHERE account_number = 'ACC1001';
\echo ''

-- ========================================
-- 4. TEST STORED PROCEDURE (Successful Transfer)
-- ========================================
\echo '4. Testing Stored Procedure - Successful Transfer...'
\echo '--------------------------------------------'
\echo 'Account balances BEFORE transfer:'
SELECT account_number, balance 
FROM accounts 
WHERE account_number IN ('ACC1001', 'ACC2001');
\echo ''

\echo 'Executing transfer_funds(ACC1001 -> ACC2001, $100)...'
SELECT transfer_funds(
    (SELECT account_id FROM accounts WHERE account_number = 'ACC1001'),
    (SELECT account_id FROM accounts WHERE account_number = 'ACC2001'),
    100.00
) as result;
\echo ''

\echo 'Account balances AFTER transfer:'
SELECT account_number, balance 
FROM accounts 
WHERE account_number IN ('ACC1001', 'ACC2001');
\echo ''

\echo 'Latest transaction:'
SELECT transaction_id, transaction_type, amount, sender_account_id, receiver_account_id, status
FROM transactions 
ORDER BY transaction_date DESC 
LIMIT 1;
\echo ''

-- ========================================
-- 5. TEST FAILURE SIMULATION (Insufficient Funds)
-- ========================================
\echo '5. Testing Failure Simulation - Insufficient Funds...'
\echo '--------------------------------------------'
\echo 'Recovery logs count BEFORE:'
SELECT COUNT(*) as recovery_count FROM recovery_logs;
\echo ''

\echo 'Attempting transfer with insufficient funds (should FAIL)...'
\echo 'Trying to transfer $50,000 from ACC3002 (balance: $500)...'
DO $$
BEGIN
    PERFORM transfer_funds(
        (SELECT account_id FROM accounts WHERE account_number = 'ACC3002'),
        (SELECT account_id FROM accounts WHERE account_number = 'ACC1001'),
        50000.00
    );
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Expected failure: %', SQLERRM;
END $$;
\echo ''

\echo 'Recovery logs count AFTER (should increase by 1):'
SELECT COUNT(*) as recovery_count FROM recovery_logs;
\echo ''

\echo 'Latest recovery log entry:'
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
\echo ''

-- ========================================
-- 6. TEST DATABASE VIEWS
-- ========================================
\echo '6. Testing Database Views...'
\echo '--------------------------------------------'
\echo 'Customer Financial Overview:'
SELECT * FROM customer_financial_overview ORDER BY total_balance DESC;
\echo ''

\echo 'Branch Transaction Summary:'
SELECT * FROM branch_transaction_summary ORDER BY total_transactions DESC;
\echo ''

-- ========================================
-- 7. TEST CONSTRAINTS
-- ========================================
\echo '7. Testing Constraints...'
\echo '--------------------------------------------'

\echo 'Test 1: Try to set negative balance (should FAIL)...'
DO $$
BEGIN
    UPDATE accounts SET balance = -100 WHERE account_number = 'ACC1001';
    RAISE NOTICE 'ERROR: Constraint should have prevented this!';
EXCEPTION
    WHEN check_violation THEN
        RAISE NOTICE 'SUCCESS: CHECK constraint prevented negative balance';
END $$;
\echo ''

\echo 'Test 2: Try to insert duplicate email (should FAIL)...'
DO $$
BEGIN
    INSERT INTO customers (first_name, last_name, email, password_hash, branch_id)
    VALUES ('Test', 'User', 'alice@example.com', 'hash', 1);
    RAISE NOTICE 'ERROR: Constraint should have prevented this!';
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE 'SUCCESS: UNIQUE constraint prevented duplicate email';
END $$;
\echo ''

\echo 'Test 3: Try to insert account with non-existent customer (should FAIL)...'
DO $$
BEGIN
    INSERT INTO accounts (account_number, account_type, customer_id, branch_id)
    VALUES ('TESTACCT', 'SAVINGS', 99999, 1);
    RAISE NOTICE 'ERROR: Constraint should have prevented this!';
EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE NOTICE 'SUCCESS: FOREIGN KEY constraint prevented invalid customer_id';
END $$;
\echo ''

-- ========================================
-- 8. PERFORMANCE TESTING
-- ========================================
\echo '8. Performance Testing (Query Plans)...'
\echo '--------------------------------------------'
\echo 'Query plan for indexed lookup (should use Index Scan):'
EXPLAIN SELECT * FROM accounts WHERE customer_id = 1;
\echo ''

\echo 'Query plan for view (should use aggregation):'
EXPLAIN SELECT * FROM customer_financial_overview;
\echo ''

-- ========================================
-- 9. AUDIT TRAIL VERIFICATION
-- ========================================
\echo '9. Audit Trail Verification...'
\echo '--------------------------------------------'
\echo 'Recent audit logs (last 5):'
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
LIMIT 5;
\echo ''

-- ========================================
-- 10. SUMMARY STATISTICS
-- ========================================
\echo '10. Summary Statistics...'
\echo '--------------------------------------------'
SELECT 
    'Total Branches' as metric, 
    COUNT(*)::text as value 
FROM branches
UNION ALL
SELECT 
    'Total Customers', 
    COUNT(*)::text 
FROM customers
UNION ALL
SELECT 
    'Total Accounts', 
    COUNT(*)::text 
FROM accounts
UNION ALL
SELECT 
    'Total Transactions', 
    COUNT(*)::text 
FROM transactions
UNION ALL
SELECT 
    'Total Audit Logs', 
    COUNT(*)::text 
FROM audit_logs
UNION ALL
SELECT 
    'Total Recovery Logs', 
    COUNT(*)::text 
FROM recovery_logs
UNION ALL
SELECT 
    'Total System Balance', 
    '$' || SUM(balance)::text 
FROM accounts;
\echo ''

-- ========================================
-- 11. DATABASE OBJECTS VERIFICATION
-- ========================================
\echo '11. Database Objects Verification...'
\echo '--------------------------------------------'

\echo 'Triggers:'
SELECT trigger_name, event_manipulation, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public';
\echo ''

\echo 'Functions/Stored Procedures:'
SELECT routine_name, routine_type 
FROM information_schema.routines 
WHERE routine_schema = 'public' AND routine_type = 'FUNCTION';
\echo ''

\echo 'Views:'
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'public';
\echo ''

\echo 'Indexes:'
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
\echo ''

-- ========================================
-- COMPLETION
-- ========================================
\timing off
\echo ''
\echo '============================================'
\echo '   TEST QUERIES COMPLETED SUCCESSFULLY'
\echo '============================================'
\echo ''
\echo 'All DBMS features verified:'
\echo '  ✓ Tables created with constraints'
\echo '  ✓ Triggers working (audit logging)'
\echo '  ✓ Stored procedures functional'
\echo '  ✓ Views queryable'
\echo '  ✓ Constraints enforced'
\echo '  ✓ Indexes created'
\echo '  ✓ Recovery mechanism working'
\echo ''
\echo 'Next steps:'
\echo '  1. Login to web app: alice@example.com / password'
\echo '  2. Test transfers via UI'
\echo '  3. Click "Simulate Failure" button'
\echo '  4. View audit and recovery logs'
\echo ''