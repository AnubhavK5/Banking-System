# 🏦 Banking System with Failure Simulation & Recovery

A full-stack banking application built with **Flask**, **PostgreSQL**, and **SQLAlchemy** demonstrating advanced DBMS concepts including transactions, triggers, stored procedures, views, failure simulation, and recovery mechanisms.

## 🚀 Features

### Core Banking Features
- ✅ User Authentication (Sign Up / Login with bcrypt)
- ✅ Multi-account management (Savings, Checking, Fixed Deposit)
- ✅ Secure fund transfers between accounts
- ✅ Transaction history tracking
- ✅ Real-time balance updates

### Advanced DBMS Concepts
- ✅ **PostgreSQL Triggers**: Automatic audit logging on balance changes
- ✅ **Stored Procedures**: ACID-compliant fund transfer with transaction control
- ✅ **Database Views**: Customer financial overview and branch summaries
- ✅ **Recovery Logs**: Failed transaction logging for recovery analysis
- ✅ **Failure Simulation**: Intentional failure testing with rollback demonstration
- ✅ **Foreign Key Constraints**: Data integrity across related tables
- ✅ **CHECK Constraints**: Business rule enforcement (e.g., balance >= 0)

## 📊 Database Schema

### Tables (7)
1. **branches** - Bank branch information
2. **customers** - Customer accounts with authentication
3. **employees** - Branch employees
4. **accounts** - Customer bank accounts with balance constraints
5. **transactions** - All financial transactions
6. **audit_logs** - Automatic balance change tracking
7. **recovery_logs** - Failed operation logging for recovery

### Database Objects
- **Trigger**: `log_account_update()` - Automatically logs balance changes
- **Stored Procedure**: `transfer_funds()` - Atomic fund transfers with error handling
- **Views**: 
  - `customer_financial_overview` - Customer account summaries
  - `branch_transaction_summary` - Branch-level transaction statistics

## 🛠️ Technology Stack

- **Backend**: Flask 3.0, Python 3.11
- **Database**: PostgreSQL 14+ with plpgsql
- **ORM**: SQLAlchemy 2.0
- **Authentication**: Flask-Login + Werkzeug (bcrypt)
- **Frontend**: Bootstrap 5, Font Awesome, Vanilla JavaScript
- **Deployment**: Render (Web Service + PostgreSQL)

## 📁 Project Structure

```
banking-system/
├── app.py                  # Main Flask application
├── models.py               # SQLAlchemy models
├── auth.py                 # Authentication blueprint
├── schema.sql              # PostgreSQL DDL script
├── requirements.txt        # Python dependencies
├── render.yaml            # Render deployment config
├── .env.example           # Environment variables template
├── templates/             # HTML templates
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
└── README.md
```

## 🔧 Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- pip

### Installation Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd banking-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database**
```bash
# Create database
createdb banking_system

# Or using psql
psql -U postgres
CREATE DATABASE banking_system;
\q
```

5. **Run the schema script**
```bash
psql -U postgres -d banking_system -f schema.sql
```

6. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

7. **Run the application**
```bash
python app.py
```

Visit `http://localhost:5000`

## 🌐 Deployment on Render

### Method 1: Using render.yaml (Recommended)

1. Push code to GitHub
2. Connect repository to Render
3. Render will automatically:
   - Create PostgreSQL database
   - Deploy web service
   - Set up environment variables

### Method 2: Manual Setup

1. **Create PostgreSQL Database**
   - Go to Render Dashboard
   - New → PostgreSQL
   - Copy the Internal Database URL

2. **Create Web Service**
   - New → Web Service
   - Connect your repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. **Set Environment Variables**
   - `DATABASE_URL`: (Paste database URL)
   - `SECRET_KEY`: (Generate random string)

4. **Initialize Database**
   - Connect to PostgreSQL via psql
   - Run schema.sql script

## 🧪 Testing Failure Simulation

1. Login to your account
2. Navigate to Dashboard
3. Click **"Simulate Failure"** button
4. The system will:
   - Attempt a transfer exceeding your balance
   - Log the failure to `recovery_logs`
   - Rollback the transaction automatically
   - Display confirmation message

5. View the logged failure:
   - Go to Reports → Recovery Logs
   - See detailed failure information

## 🔑 Test Credentials

After running `schema.sql`, use these test accounts:

```
Email: alice@example.com
Password: password

Email: bob@example.com
Password: password

Email: charlie@example.com
Password: password
```

**Note**: All passwords are hashed with bcrypt in the database.

## 📸 Screenshots

### Dashboard
- Account overview with total balance
- Recent transactions
- Quick actions

### Transfer Funds
- Real-time account validation
- Balance checking
- Stored procedure execution

### Recovery Logs
- Failed transaction details
- Failure reasons
- Balance at failure time

### Reports
- Customer financial overview (View)
- Branch transaction summary (View)
- Audit logs (Trigger-generated)

## 🔐 Security Features

- Password hashing with Werkzeug (pbkdf2:sha256)
- Flask-Login session management
- SQL injection prevention via SQLAlchemy ORM
- CSRF protection (Flask built-in)
- Database-level constraints enforcement

## 📚 DBMS Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| **Transactions** | BEGIN/COMMIT/ROLLBACK in stored procedure |
| **Triggers** | Automatic audit logging before updates |
| **Stored Procedures** | transfer_funds() with error handling |
| **Views** | Aggregated reporting queries |
| **Foreign Keys** | Referential integrity across tables |
| **CHECK Constraints** | Balance validation, email format |
| **UNIQUE Constraints** | Email, account number uniqueness |
| **Indexes** | Performance optimization |
| **ACID Properties** | Atomicity via rollback on failure |
| **Recovery Mechanism** | Failed operation logging |

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U postgres -d banking_system
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Render Deployment Issues
- Ensure `DATABASE_URL` starts with `postgresql://` not `postgres://`
- Check build logs for errors
- Verify schema.sql was executed

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/signup` | GET/POST | User registration |
| `/login` | GET/POST | User authentication |
| `/logout` | GET | User logout |
| `/dashboard` | GET | User dashboard |
| `/accounts` | GET | View all accounts |
| `/transfer` | GET/POST | Fund transfer |
| `/transactions` | GET | Transaction history |
| `/audit_logs` | GET | Audit log viewer |
| `/recovery_logs` | GET | Recovery log viewer |
| `/simulate_failure` | GET | Trigger intentional failure |
| `/reports/customer_overview` | GET | Customer financial view |
| `/reports/branch_summary` | GET | Branch statistics view |
| `/api/account/<number>` | GET | Account lookup API |

## 🤝 Contributing

This is an academic project demonstrating DBMS concepts. Feel free to fork and enhance!

## 📄 License

MIT License - Feel free to use for educational purposes.

## 👥 Author

DBMS Project - Banking System with Failure Simulation

---

**Note**: This project is designed for educational purposes to demonstrate advanced database management concepts including transaction management, triggers, stored procedures, and failure recovery mechanisms.