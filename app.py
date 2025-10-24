from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_required, current_user
from models import db, Customer, Account, Transaction, Branch, AuditLog, RecoveryLog
from auth import auth as auth_blueprint
from sqlalchemy import text
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://localhost/banking_system')

# Fix for Render PostgreSQL URL
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(auth_blueprint)

@login_manager.user_loader
def load_user(customer_id):
    return Customer.query.get(int(customer_id))

# Home route
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    accounts = Account.query.filter_by(customer_id=current_user.customer_id).all()
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter(
        (Transaction.sender_account_id.in_([a.account_id for a in accounts])) |
        (Transaction.receiver_account_id.in_([a.account_id for a in accounts]))
    ).order_by(Transaction.transaction_date.desc()).limit(10).all()
    
    # Calculate total balance
    total_balance = sum(account.balance for account in accounts)
    
    return render_template('dashboard.html', 
                         accounts=accounts, 
                         transactions=recent_transactions,
                         total_balance=total_balance)

# Transfer funds route
@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    accounts = Account.query.filter_by(customer_id=current_user.customer_id, status='ACTIVE').all()
    
    if request.method == 'POST':
        sender_account_id = request.form.get('sender_account_id', type=int)
        receiver_account_number = request.form.get('receiver_account_number')
        amount = request.form.get('amount', type=float)
        
        # Validation
        if not all([sender_account_id, receiver_account_number, amount]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('transfer'))
        
        if amount <= 0:
            flash('Transfer amount must be greater than zero.', 'danger')
            return redirect(url_for('transfer'))
        
        # Check sender account belongs to current user
        sender_account = Account.query.filter_by(
            account_id=sender_account_id,
            customer_id=current_user.customer_id
        ).first()
        
        if not sender_account:
            flash('Invalid sender account.', 'danger')
            return redirect(url_for('transfer'))
        
        # Find receiver account
        receiver_account = Account.query.filter_by(account_number=receiver_account_number).first()
        
        if not receiver_account:
            flash('Receiver account not found.', 'danger')
            return redirect(url_for('transfer'))
        
        if sender_account.account_id == receiver_account.account_id:
            flash('Cannot transfer to the same account.', 'danger')
            return redirect(url_for('transfer'))
        
        # Call stored procedure for transfer
        try:
            result = db.session.execute(
                text('SELECT transfer_funds(:sender, :receiver, :amount)'),
                {
                    'sender': sender_account_id,
                    'receiver': receiver_account.account_id,
                    'amount': amount
                }
            )
            db.session.commit()
            flash('Transfer completed successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            error_message = str(e)
            
            # Log the failure in recovery_logs
            recovery_log = RecoveryLog(
                operation_type='TRANSFER',
                sender_account_id=sender_account_id,
                receiver_account_id=receiver_account.account_id,
                attempted_amount=amount,
                failure_reason=error_message,
                sender_balance_at_failure=sender_account.balance,
                additional_details={
                    'sender_account': sender_account.account_number,
                    'receiver_account': receiver_account.account_number,
                    'user_id': current_user.customer_id
                }
            )
            
            try:
                db.session.add(recovery_log)
                db.session.commit()
            except:
                db.session.rollback()
            
            flash(f'Transfer failed: {error_message}', 'danger')
            return redirect(url_for('transfer'))
    
    return render_template('transfer.html', accounts=accounts)

# Simulate failure route
# Simulate failure route
@app.route('/simulate_failure')
@login_required
def simulate_failure():
    # Get user's first account
    account = Account.query.filter_by(customer_id=current_user.customer_id).first()
    
    if not account:
        flash('You need at least one account to simulate a transfer failure.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Try to transfer more than the account balance
    excessive_amount = float(account.balance) + 5000.00
    
    # Find another account to transfer to
    receiver_account = Account.query.filter(Account.account_id != account.account_id).first()
    
    if not receiver_account:
        flash('No receiver account available for simulation.', 'warning')
        return redirect(url_for('dashboard'))
    
    try:
        # This should fail due to insufficient funds
        result = db.session.execute(
            text('SELECT transfer_funds(:sender, :receiver, :amount)'),
            {
                'sender': account.account_id,
                'receiver': receiver_account.account_id,
                'amount': excessive_amount
            }
        )
        db.session.commit()
        flash('Unexpected success - transfer should have failed!', 'warning')
    except Exception as e:
        db.session.rollback()
        
        # Now manually create recovery log in NEW transaction
        # This ensures it persists even though the transfer rolled back
        recovery_log = RecoveryLog(
            operation_type='TRANSFER',
            sender_account_id=account.account_id,
            receiver_account_id=receiver_account.account_id,
            attempted_amount=excessive_amount,
            failure_reason=f'Insufficient funds. Available: {account.balance}, Required: {excessive_amount}, Shortfall: {excessive_amount - float(account.balance)}',
            sender_balance_at_failure=account.balance,
            additional_details={
                'sender_account': account.account_number,
                'receiver_account': receiver_account.account_number,
                'deficit_amount': float(excessive_amount - float(account.balance)),
                'error_message': str(e)
            }
        )
        
        try:
            db.session.add(recovery_log)
            db.session.commit()
            
            flash('✓ Failure simulation successful! The transaction was rolled back.', 'success')
            flash(f'Attempted to transfer ${excessive_amount:.2f} from account with balance ${account.balance:.2f}', 'info')
            flash(f'Recovery log created with ID: {recovery_log.recovery_id}. Check the table below for details.', 'success')
        except Exception as log_error:
            db.session.rollback()
            flash('✓ Transaction rolled back, but could not create recovery log.', 'warning')
            flash(f'Logging error: {str(log_error)}', 'danger')
    
    return redirect(url_for('recovery_logs'))

# View accounts
@app.route('/accounts')
@login_required
def accounts():
    user_accounts = Account.query.filter_by(customer_id=current_user.customer_id).all()
    return render_template('accounts.html', accounts=user_accounts)

# View transactions
@app.route('/transactions')
@login_required
def transactions():
    user_accounts = Account.query.filter_by(customer_id=current_user.customer_id).all()
    account_ids = [a.account_id for a in user_accounts]
    
    all_transactions = Transaction.query.filter(
        (Transaction.sender_account_id.in_(account_ids)) |
        (Transaction.receiver_account_id.in_(account_ids))
    ).order_by(Transaction.transaction_date.desc()).all()
    
    return render_template('transactions.html', transactions=all_transactions, user_accounts=user_accounts)

# View audit logs
@app.route('/audit_logs')
@login_required
def audit_logs():
    user_accounts = Account.query.filter_by(customer_id=current_user.customer_id).all()
    account_ids = [a.account_id for a in user_accounts]
    
    logs = AuditLog.query.filter(AuditLog.account_id.in_(account_ids)).order_by(AuditLog.changed_at.desc()).all()
    
    return render_template('audit_logs.html', logs=logs)

# View recovery logs (admin view - showing all for demonstration)
@app.route('/recovery_logs')
@login_required
def recovery_logs():
    logs = RecoveryLog.query.order_by(RecoveryLog.failed_at.desc()).all()
    return render_template('recovery_logs.html', logs=logs)

# View customer financial overview
@app.route('/reports/customer_overview')
@login_required
def customer_overview():
    result = db.session.execute(text('SELECT * FROM customer_financial_overview'))
    customers = result.fetchall()
    return render_template('customer_overview.html', customers=customers)

# View branch transaction summary
@app.route('/reports/branch_summary')
@login_required
def branch_summary():
    result = db.session.execute(text('SELECT * FROM branch_transaction_summary'))
    branches = result.fetchall()
    return render_template('branch_summary.html', branches=branches)

# API endpoints for AJAX calls
@app.route('/api/account/<account_number>')
@login_required
def get_account_info(account_number):
    account = Account.query.filter_by(account_number=account_number).first()
    if account:
        return jsonify({
            'success': True,
            'account': {
                'account_number': account.account_number,
                'customer_name': f"{account.customer.first_name} {account.customer.last_name}",
                'account_type': account.account_type,
                'branch': account.branch.branch_name
            }
        })
    return jsonify({'success': False, 'message': 'Account not found'}), 404

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)