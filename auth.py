from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Customer, Branch
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        date_of_birth = request.form.get('date_of_birth')
        branch_id = request.form.get('branch_id', type=int)
        
        # Validation
        if not all([email, first_name, last_name, password, confirm_password, branch_id]):
            flash('All required fields must be filled out.', 'danger')
            return redirect(url_for('auth.signup'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.signup'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('auth.signup'))
        
        # Check if user already exists
        existing_user = Customer.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered. Please login instead.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check if branch exists
        branch = Branch.query.get(branch_id)
        if not branch:
            flash('Invalid branch selected.', 'danger')
            return redirect(url_for('auth.signup'))
        
        # Parse date of birth
        dob = None
        if date_of_birth:
            try:
                dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format for date of birth.', 'danger')
                return redirect(url_for('auth.signup'))
        
        # Create new customer
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_customer = Customer(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hashed_password,
            phone=phone,
            address=address,
            date_of_birth=dob,
            branch_id=branch_id,
            is_active=True
        )
        
        try:
            db.session.add(new_customer)
            db.session.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')
            return redirect(url_for('auth.signup'))
    
    # GET request - show signup form
    branches = Branch.query.all()
    return render_template('signup.html', branches=branches)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Validation
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Find user
        customer = Customer.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not customer or not check_password_hash(customer.password_hash, password):
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check if account is active
        if not customer.is_active:
            flash('Your account has been deactivated. Please contact support.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Login the user
        login_user(customer, remember=remember)
        flash(f'Welcome back, {customer.first_name}!', 'success')
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('dashboard'))
    
    # GET request - show login form
    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))