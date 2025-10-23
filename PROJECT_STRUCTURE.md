# 📁 Banking System - Complete Project Structure

## Directory Layout

```
banking-system/
│
├── 📄 app.py                          # Main Flask application (routes, views)
├── 📄 models.py                       # SQLAlchemy database models
├── 📄 auth.py                         # Authentication blueprint (signup/login)
├── 📄 schema.sql                      # PostgreSQL DDL script (tables, triggers, procedures)
│
├── 📄 requirements.txt                # Python dependencies
├── 📄 runtime.txt                     # Python version for deployment
├── 📄 Procfile                        # Heroku/Render deployment config
├── 📄 render.yaml                     # Render.com auto-deployment config
├── 📄 .env.example                    # Environment variables template
├── 📄 .gitignore                      # Git ignore patterns
│
├── 📄 README.md                       # Main project documentation
├── 📄 QUICKSTART.md                   # Fast setup guide (5 minutes)
├── 📄 DEPLOYMENT_GUIDE.md             # Detailed Render deployment steps
├── 📄 TESTING_GUIDE.md                # Comprehensive testing documentation
├── 📄 PROJECT_STRUCTURE.md            # This file
│
└── 📁 templates/                      # HTML templates (Jinja2)
    ├── 📄 base.html                   # Base template with navbar, footer
    ├── 📄 index.html                  # Landing/home page
    ├── 📄 login.html                  # Login form
    ├── 📄 signup.html                 # Registration form
    ├── 📄 dashboard.html              # User dashboard (main page after login)
    ├── 📄 accounts.html               # View all user accounts
    ├── 📄 transfer.html               # Fund transfer form
    ├── 📄 transactions.html           # Transaction history
    ├── 📄 audit_logs.html             # Audit log viewer (trigger-generated)
    ├── 📄 recovery_logs.html          # Recovery log viewer (failed operations)
    ├── 📄 customer_overview.html      # Customer financial overview (view)
    ├── 📄 branch_summary.html         # Branch transaction summary (view)
    ├── 📄 404.html                    # 404 error page
    └── 📄 500.html                    # 500 error page
```

---

## 📝 File Descriptions

### Core Application Files

#### **app.py** (Main Application)
- Flask app initialization
- Database configuration
- Flask-Login setup
- Route definitions:
  - `/` - Home page
  - `/dashboard` - User dashboard
  - `/transfer` - Fund transfer
  - `/simulate_failure` - Failure simulation
  - `/accounts` - Account listing
  - `/transactions` - Transaction history
  - `/audit_logs` - Audit log viewer
  - `/recovery_logs` - Recovery log viewer
  - `/reports/customer_overview` - Customer report
  - `/reports/branch_summary` - Branch report
  - `/api/account/<number>` - Account lookup API
- Error handlers (404, 500)

#### **models.py** (Database Models)
SQLAlchemy ORM models for:
- `Branch` - Bank branches
- `Customer` - Customer accounts (with Flask-Login)
- `Employee` - Branch employees
- `Account` - Bank accounts
- `Transaction` - Financial transactions
- `AuditLog` - Balance change history
- `RecoveryLog` - Failed operation logs

#### **auth.py** (Authentication Blueprint)
- User registration (`/signup`)
- User login (`/login`)
- User logout (`/logout`)
- Password hashing (Werkzeug)
- Form validation

#### **schema.sql** (Database Schema)
Complete PostgreSQL setup:
- **Tables (7)**:
  - branches
  - customers
  - employees
  - accounts (with CHECK constraint)
  - transactions
  - audit_logs
  - recovery_logs
  
- **Trigger**: `log_account_update()` - Auto-logs balance changes
- **Stored Procedure**: `transfer_funds()` - ACID-compliant transfers
- **Views (2)**:
  - customer_financial_overview
  - branch_transaction_summary
  
- **Sample Data**: 3 branches, 3 customers, 5 accounts, 3 employees

---

### Configuration Files

#### **requirements.txt**
Python dependencies:
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
psycopg2-binary==2.9.9
Werkzeug==3.0.1
python-dotenv==1.0.0
gunicorn==21.2.0
SQLAlchemy==2.0.23
```

#### **runtime.txt**
Specifies Python version for deployment platforms

#### **Procfile**
Deployment command for Heroku/Render:
```
web: gunicorn app:app
```

#### **render.yaml**
Automatic deployment configuration for Render.com:
- Web service settings
- Database connection
- Environment variables

#### **.env.example**
Template for environment variables:
- DATABASE_URL
- SECRET_KEY
- FLASK_ENV

#### **.gitignore**
Excludes from Git:
- Python cache files
- Virtual environments
- .env files
- IDE configurations
- Database files

---

### Documentation Files

#### **README.md**
Main project documentation:
- Overview and features
- Technology stack
- Database schema
- Installation instructions
- Deployment guide
- Testing procedures
- API endpoints
- License

#### **QUICKSTART.md**
Fast setup guide:
- Local setup (5 minutes)
- Render deployment (quick)
- Quick testing
- Verification queries
- Demo script

#### **DEPLOYMENT_GUIDE.md**
Detailed deployment:
- Step-by-step Render setup
- Database initialization
- Environment configuration
- Troubleshooting
- Custom domain setup
- Monitoring

#### **TESTING_GUIDE.md**
Comprehensive testing:
- Feature testing
- DBMS concept verification
- SQL test queries
- Security testing
- Performance testing
- Test checklist

#### **PROJECT_STRUCTURE.md**
This file - complete project layout

---

### Template Files (HTML)

#### **base.html**
Base template with:
- Bootstrap 5 styling
- Responsive navbar
- Flash message display
- Footer
- Common CSS/JS

#### **index.html**
Landing page with:
- Hero section
- Feature highlights
- Call-to-action buttons
- Technology showcase

#### **login.html**
Login form with:
- Email/password fields
- Remember me checkbox
- Link to signup

#### **signup.html**
Registration form with:
- Personal information
- Branch selection
- Password confirmation
- Validation

#### **dashboard.html**
Main user interface:
- Account summary cards
- Total balance
- Recent transactions
- Quick action buttons
- Statistics

#### **accounts.html**
Account listing:
- Account cards
- Balance display
- Account details
- Status indicators

#### **transfer.html**
Fund transfer:
- Account selection
- Receiver lookup (AJAX)
- Amount input
- Transfer button
- Real-time validation

#### **transactions.html**
Transaction history:
- Filterable table
- Transaction details
- Date/time stamps
- Status indicators

#### **audit_logs.html**
Audit log viewer:
- Balance changes
- Old/new balance comparison
- Timestamp tracking
- Account information

#### **recovery_logs.html**
Failed operation logs:
- Failure details
- Attempted amounts
- Balance at failure
- Failure reasons

#### **customer_overview.html**
Customer report (from view):
- Customer list
- Total balances
- Account counts
- Branch information

#### **branch_summary.html**
Branch statistics (from view):
- Transaction counts
- Transfer volumes
- Deposit/withdrawal totals
- Account counts per branch

#### **404.html**
Custom 404 page:
- User-friendly message
- Navigation links

#### **500.html**
Custom 500 page:
- Error message
- Support information

---

## 🎯 Key Features by File

### Transaction Management
- **Files**: `app.py`, `schema.sql` (stored procedure)
- **Demonstrates**: ACID properties, BEGIN/COMMIT/ROLLBACK

### Audit Logging
- **Files**: `schema.sql` (trigger), `audit_logs.html`
- **Demonstrates**: Automatic triggers, data tracking

### Recovery Mechanism
- **Files**: `schema.sql` (stored procedure), `app.py` (simulation), `recovery_logs.html`
- **Demonstrates**: Error handling, failure logging

### Reporting
- **Files**: `schema.sql` (views), `customer_overview.html`, `branch_summary.html`
- **Demonstrates**: Database views, aggregation

### Security
- **Files**: `auth.py`, `models.py`
- **Demonstrates**: Password hashing, authentication, session management

### Constraints
- **Files**: `schema.sql`, `models.py`
- **Demonstrates**: Foreign keys, CHECK, UNIQUE, NOT NULL

---

## 📊 Database Objects Map

| Object Type | Name | File | Purpose |
|------------|------|------|---------|
| Table | branches | schema.sql | Store branch information |
| Table | customers | schema.sql | Store customer accounts |
| Table | employees | schema.sql | Store employee data |
| Table | accounts | schema.sql | Store bank accounts |
| Table | transactions | schema.sql | Store all transactions |
| Table | audit_logs | schema.sql | Store balance changes |
| Table | recovery_logs | schema.sql | Store failed operations |
| Trigger | trg_account_balance_audit | schema.sql | Auto-log balance changes |
| Function | log_account_update() | schema.sql | Trigger function |
| Function | transfer_funds() | schema.sql | Atomic fund transfer |
| View | customer_financial_overview | schema.sql | Customer summaries |
| View | branch_transaction_summary | schema.sql | Branch statistics |

---

## 🔄 Data Flow

### User Registration Flow
```
signup.html → auth.py → models.py (Customer) → PostgreSQL (customers table)
```

### Fund Transfer Flow
```
transfer.html → app.py (/transfer) → PostgreSQL (transfer_funds procedure)
    ↓
├─ Update accounts.balance
├─ Insert into transactions
└─ Trigger → Insert into audit_logs
```

### Failure Simulation Flow
```
app.py (/simulate_failure) → PostgreSQL (transfer_funds procedure)
    ↓
├─ Check balance (insufficient)
├─ Insert into recovery_logs
└─ RAISE EXCEPTION (rollback)
```

---

## 🎨 UI Components

### Color Scheme
- Primary: #2c3e50 (Dark blue)
- Secondary: #3498db (Light blue)
- Success: #27ae60 (Green)
- Danger: #e74c3c (Red)
- Warning: #f39c12 (Orange)
- Info: #16a085 (Teal)

### Layout
- Bootstrap 5 grid system
- Responsive (mobile-friendly)
- Card-based design
- Gradient backgrounds

### Icons
- Font Awesome 6.4.0
- Used throughout for visual clarity

---

## 🚀 Deployment Architecture

### Local Development
```
Python (Flask) ↔ PostgreSQL (Local)
```

### Production (Render)
```
Render Web Service (Gunicorn + Flask)
    ↓
Render PostgreSQL Database
```

---

## 📦 Installation Steps Summary

1. **Clone repository**
2. **Create virtual environment**
3. **Install requirements.txt**
4. **Create PostgreSQL database**
5. **Run schema.sql**
6. **Set DATABASE_URL**
7. **Run app.py**

---

## ✅ File Checklist

Before deployment, ensure you have:

- [x] app.py
- [x] models.py
- [x] auth.py
- [x] schema.sql
- [x] requirements.txt
- [x] runtime.txt
- [x] Procfile
- [x] render.yaml
- [x] .env.example
- [x] .gitignore
- [x] README.md
- [x] QUICKSTART.md
- [x] DEPLOYMENT_GUIDE.md
- [x] TESTING_GUIDE.md
- [x] PROJECT_STRUCTURE.md
- [x] templates/base.html
- [x] templates/index.html
- [x] templates/login.html
- [x] templates/signup.html
- [x] templates/dashboard.html
- [x] templates/accounts.html
- [x] templates/transfer.html
- [x] templates/transactions.html
- [x] templates/audit_logs.html
- [x] templates/recovery_logs.html
- [x] templates/customer_overview.html
- [x] templates/branch_summary.html
- [x] templates/404.html
- [x] templates/500.html

**Total: 29 files**

---

## 🎓 Educational Value

This project demonstrates:
- ✅ Full-stack web development
- ✅ Advanced database concepts
- ✅ Transaction management
- ✅ Trigger programming
- ✅ Stored procedures
- ✅ Database views
- ✅ Error handling & recovery
- ✅ Security best practices
- ✅ Modern UI/UX design
- ✅ Cloud deployment

Perfect for DBMS course projects! 🚀