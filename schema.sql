-- Banking System Database Schema
-- PostgreSQL DDL Script with DBMS Constraints

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS recovery_logs CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS branches CASCADE;

-- 1. Branches Table
CREATE TABLE branches (
    branch_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL UNIQUE,
    branch_code VARCHAR(20) NOT NULL UNIQUE,
    address TEXT NOT NULL,
    phone VARCHAR(20),
    manager_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Customers Table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    branch_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_customer_branch FOREIGN KEY (branch_id) 
        REFERENCES branches(branch_id) ON DELETE RESTRICT,
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- 3. Employees Table
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    position VARCHAR(50) NOT NULL,
    salary NUMERIC(12, 2) CHECK (salary > 0),
    hire_date DATE NOT NULL,
    branch_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_employee_branch FOREIGN KEY (branch_id) 
        REFERENCES branches(branch_id) ON DELETE RESTRICT
);

-- 4. Accounts Table (with CHECK constraint for balance)
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    account_number VARCHAR(20) NOT NULL UNIQUE,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('SAVINGS', 'CHECKING', 'FIXED_DEPOSIT')),
    balance NUMERIC(15, 2) DEFAULT 0.00,
    customer_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'FROZEN')),
    opened_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_account_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id) ON DELETE CASCADE,
    CONSTRAINT fk_account_branch FOREIGN KEY (branch_id) 
        REFERENCES branches(branch_id) ON DELETE RESTRICT,
    CONSTRAINT chk_balance_non_negative CHECK (balance >= 0.00)
);

-- 5. Transactions Table
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('TRANSFER', 'DEPOSIT', 'WITHDRAWAL')),
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    sender_account_id INTEGER,
    receiver_account_id INTEGER,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    status VARCHAR(20) DEFAULT 'COMPLETED' CHECK (status IN ('COMPLETED', 'PENDING', 'FAILED')),
    CONSTRAINT fk_sender_account FOREIGN KEY (sender_account_id) 
        REFERENCES accounts(account_id) ON DELETE SET NULL,
    CONSTRAINT fk_receiver_account FOREIGN KEY (receiver_account_id) 
        REFERENCES accounts(account_id) ON DELETE SET NULL,
    CONSTRAINT chk_different_accounts CHECK (
        (transaction_type = 'TRANSFER' AND sender_account_id IS NOT NULL AND receiver_account_id IS NOT NULL AND sender_account_id != receiver_account_id)
        OR (transaction_type IN ('DEPOSIT', 'WITHDRAWAL'))
    )
);

-- 6. Audit Logs Table
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    old_balance NUMERIC(15, 2),
    new_balance NUMERIC(15, 2),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operation_type VARCHAR(50),
    CONSTRAINT fk_audit_account FOREIGN KEY (account_id) 
        REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- 7. Recovery Logs Table
CREATE TABLE recovery_logs (
    recovery_id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,
    sender_account_id INTEGER,
    receiver_account_id INTEGER,
    attempted_amount NUMERIC(15, 2),
    failure_reason TEXT NOT NULL,
    failed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sender_balance_at_failure NUMERIC(15, 2),
    additional_details JSONB
);

-- Insert Sample Data for Testing

-- Insert Branches
INSERT INTO branches (branch_name, branch_code, address, phone, manager_name) VALUES
('Main Branch', 'BR001', '123 Main Street, New York, NY 10001', '555-0100', 'John Smith'),
('Downtown Branch', 'BR002', '456 Park Avenue, New York, NY 10022', '555-0200', 'Sarah Johnson'),
('Suburban Branch', 'BR003', '789 Oak Street, Brooklyn, NY 11201', '555-0300', 'Michael Brown');

-- Insert Sample Customers
INSERT INTO customers (first_name, last_name, email, password_hash, phone, address, date_of_birth, branch_id) VALUES
('Alice', 'Williams', 'alice@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqL8NvXw9u', '555-1001', '100 First Ave, NY', '1990-05-15', 1),
('Bob', 'Davis', 'bob@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqL8NvXw9u', '555-1002', '200 Second Ave, NY', '1985-08-20', 1),
('Charlie', 'Miller', 'charlie@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqL8NvXw9u', '555-1003', '300 Third Ave, NY', '1992-03-10', 2);

-- Insert Sample Employees
INSERT INTO employees (first_name, last_name, email, phone, position, salary, hire_date, branch_id) VALUES
('Emma', 'Wilson', 'emma.wilson@bank.com', '555-2001', 'Teller', 45000.00, '2020-01-15', 1),
('David', 'Taylor', 'david.taylor@bank.com', '555-2002', 'Manager', 75000.00, '2018-06-01', 1),
('Lisa', 'Anderson', 'lisa.anderson@bank.com', '555-2003', 'Loan Officer', 60000.00, '2019-03-20', 2);

-- Insert Sample Accounts
INSERT INTO accounts (account_number, account_type, balance, customer_id, branch_id) VALUES
('ACC1001', 'SAVINGS', 5000.00, 1, 1),
('ACC1002', 'CHECKING', 1500.00, 1, 1),
('ACC2001', 'SAVINGS', 10000.00, 2, 1),
('ACC3001', 'CHECKING', 3000.00, 3, 2),
('ACC3002', 'SAVINGS', 500.00, 3, 2);

-- Create Indexes for Performance
CREATE INDEX idx_accounts_customer ON accounts(customer_id);
CREATE INDEX idx_accounts_branch ON accounts(branch_id);
CREATE INDEX idx_transactions_sender ON transactions(sender_account_id);
CREATE INDEX idx_transactions_receiver ON transactions(receiver_account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_audit_logs_account ON audit_logs(account_id);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_branch ON customers(branch_id);

-- A. AUDITING TRIGGER

-- Trigger Function: log_account_update()
CREATE OR REPLACE FUNCTION log_account_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert audit record before update happens
    INSERT INTO audit_logs (account_id, old_balance, new_balance, operation_type)
    VALUES (OLD.account_id, OLD.balance, NEW.balance, 'BALANCE_UPDATE');
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach Trigger to accounts table
CREATE TRIGGER trg_account_balance_audit
BEFORE UPDATE ON accounts
FOR EACH ROW
WHEN (OLD.balance IS DISTINCT FROM NEW.balance)
EXECUTE FUNCTION log_account_update();

-- B. ATOMIC TRANSFER STORED PROCEDURE WITH RECOVERY MECHANISM

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
    -- Start transaction control
    -- Get sender's current balance
    SELECT balance, account_number INTO v_sender_balance, v_sender_account_number
    FROM accounts
    WHERE account_id = p_sender_account_id
    FOR UPDATE; -- Lock the row for update
    
    -- Check if sender account exists
    IF NOT FOUND THEN
        -- Log failure to recovery_logs
        INSERT INTO recovery_logs (
            operation_type, 
            sender_account_id, 
            receiver_account_id, 
            attempted_amount, 
            failure_reason,
            sender_balance_at_failure
        ) VALUES (
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
        -- Log failure to recovery_logs
        INSERT INTO recovery_logs (
            operation_type, 
            sender_account_id, 
            receiver_account_id, 
            attempted_amount, 
            failure_reason,
            sender_balance_at_failure
        ) VALUES (
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
        -- Log detailed failure to recovery_logs
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
        
        -- Raise exception to rollback transaction
        RAISE EXCEPTION 'Insufficient funds in account %. Available: %, Required: %', 
            v_sender_account_number, v_sender_balance, p_amount;
    END IF;
    
    -- Perform the transfer (debit sender)
    UPDATE accounts
    SET balance = balance - p_amount
    WHERE account_id = p_sender_account_id;
    
    -- Credit receiver
    UPDATE accounts
    SET balance = balance + p_amount
    WHERE account_id = p_receiver_account_id;
    
    -- Record transaction
    INSERT INTO transactions (
        transaction_type,
        amount,
        sender_account_id,
        receiver_account_id,
        description,
        status
    ) VALUES (
        'TRANSFER',
        p_amount,
        p_sender_account_id,
        p_receiver_account_id,
        FORMAT('Transfer from %s to %s', v_sender_account_number, v_receiver_account_number),
        'COMPLETED'
    );
    
    RETURN FORMAT('Transfer successful: %s transferred from account %s to account %s', 
                  p_amount, v_sender_account_number, v_receiver_account_number);
    
EXCEPTION
    WHEN OTHERS THEN
        -- Log any other unexpected failures
        INSERT INTO recovery_logs (
            operation_type, 
            sender_account_id, 
            receiver_account_id, 
            attempted_amount, 
            failure_reason,
            sender_balance_at_failure
        ) VALUES (
            'TRANSFER',
            p_sender_account_id,
            p_receiver_account_id,
            p_amount,
            SQLERRM,
            v_sender_balance
        );
        
        -- Re-raise the exception to ensure rollback
        RAISE;
END;
$$ LANGUAGE plpgsql;

-- REPORTING VIEWS

-- 1. Customer Financial Overview View
CREATE OR REPLACE VIEW customer_financial_overview AS
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS full_name,
    c.email,
    c.phone,
    b.branch_name,
    COUNT(a.account_id) AS total_accounts,
    COALESCE(SUM(a.balance), 0.00) AS total_balance
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id
LEFT JOIN branches b ON c.branch_id = b.branch_id
WHERE c.is_active = TRUE
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.phone, b.branch_name
ORDER BY total_balance DESC;

-- 2. Branch Transaction Summary View
CREATE OR REPLACE VIEW branch_transaction_summary AS
SELECT 
    b.branch_id,
    b.branch_name,
    b.branch_code,
    COUNT(DISTINCT t.transaction_id) AS total_transactions,
    COALESCE(SUM(CASE WHEN t.transaction_type = 'TRANSFER' THEN t.amount ELSE 0 END), 0) AS total_transfer_volume,
    COALESCE(SUM(CASE WHEN t.transaction_type = 'DEPOSIT' THEN t.amount ELSE 0 END), 0) AS total_deposits,
    COALESCE(SUM(CASE WHEN t.transaction_type = 'WITHDRAWAL' THEN t.amount ELSE 0 END), 0) AS total_withdrawals,
    COUNT(DISTINCT a.account_id) AS total_accounts
FROM branches b
LEFT JOIN accounts a ON b.branch_id = a.branch_id
LEFT JOIN transactions t ON (a.account_id = t.sender_account_id OR a.account_id = t.receiver_account_id)
GROUP BY b.branch_id, b.branch_name, b.branch_code
ORDER BY total_transactions DESC;

-- Grant necessary permissions (adjust as needed for your deployment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;