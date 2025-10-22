# 🚀 Complete Deployment Guide for Render

## Prerequisites
- GitHub account
- Render account (free tier available)
- All project files ready

---

## Step 1: Prepare Your Repository

### 1.1 Create GitHub Repository
```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Banking System with Failure Simulation"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/banking-system.git
git branch -M main
git push -u origin main
```

### 1.2 Verify Required Files
Ensure these files are in your repository:
- ✅ `app.py`
- ✅ `models.py`
- ✅ `auth.py`
- ✅ `schema.sql`
- ✅ `requirements.txt`
- ✅ `render.yaml`
- ✅ `templates/` folder (with all HTML files)

---

## Step 2: Create PostgreSQL Database on Render

### 2.1 Login to Render
1. Go to [https://render.com](https://render.com)
2. Sign up or login
3. Go to Dashboard

### 2.2 Create New PostgreSQL Database
1. Click **"New +"** button
2. Select **"PostgreSQL"**
3. Fill in details:
   - **Name**: `banking-system-db`
   - **Database**: `banking_system`
   - **User**: `banking_user`
   - **Region**: Choose closest to you
   - **Plan**: Free
4. Click **"Create Database"**
5. Wait 2-3 minutes for provisioning

### 2.3 Save Database Credentials
Once created, you'll see:
- **Internal Database URL** (use this for your app)
- **External Database URL** (use this to connect from your computer)
- Host, Port, Database name, Username, Password

**Copy the Internal Database URL** - you'll need it later!

---

## Step 3: Initialize Database Schema

### Option A: Using External Connection (Recommended)

```bash
# Install psql if not installed (macOS)
brew install postgresql

# Or on Ubuntu/Debian
sudo apt-get install postgresql-client

# Connect to Render database
psql YOUR_EXTERNAL_DATABASE_URL

# Once connected, run the schema
\i schema.sql

# Verify tables created
\dt

# Should show: branches, customers, employees, accounts, transactions, audit_logs, recovery_logs

# Exit
\q
```

### Option B: Using Render Shell

1. Go to your database in Render Dashboard
2. Click **"Connect"** → **"External Connection"**
3. Use the Web Shell option
4. Copy-paste the contents of `schema.sql` in sections
5. Execute each section

---

## Step 4: Deploy Web Service

### 4.1 Create Web Service
1. In Render Dashboard, click **"New +"**
2. Select **"Web Service"**
3. Connect your GitHub repository
4. Select the `banking-system` repository

### 4.2 Configure Service
Fill in the following:

**Basic Settings:**
- **Name**: `banking-system`
- **Region**: Same as database
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Instance Type:**
- Select **"Free"**

### 4.3 Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

1. **DATABASE_URL**
   - Value: Paste your Internal Database URL from Step 2.3
   - **Important**: If it starts with `postgres://`, change it to `postgresql://`

2. **SECRET_KEY**
   - Value: Generate a random string (or click "Generate" if available)
   - Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

3. **PYTHON_VERSION** (optional)
   - Value: `3.11.0`

### 4.4 Deploy
1. Click **"Create Web Service"**
2. Watch the build logs
3. Wait 5-10 minutes for first deployment

---

## Step 5: Verify Deployment

### 5.1 Check Build Logs
Look for:
```
Building...
Installing dependencies from requirements.txt
...
Build successful
Starting service...
Your service is live 🎉
```

### 5.2 Test Your Application
1. Click on the URL provided (e.g., `https://banking-system-xxx.onrender.com`)
2. You should see the home page
3. Try logging in with test credentials:
   - Email: `alice@example.com`
   - Password: `password`

---

## Step 6: Post-Deployment Testing

### 6.1 Test Core Features
1. ✅ **Login**: Use test account
2. ✅ **Dashboard**: View accounts and balance
3. ✅ **Transfer**: Attempt a successful transfer
4. ✅ **Failure Simulation**: Click "Simulate Failure"
5. ✅ **Recovery Logs**: Verify failure was logged
6. ✅ **Audit Logs**: Check balance change tracking
7. ✅ **Reports**: View customer overview and branch summary

### 6.2 Verify Database Objects
Connect to your database and check:

```sql
-- Check tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check trigger
SELECT trigger_name FROM information_schema.triggers 
WHERE trigger_schema = 'public';

-- Check stored procedure
SELECT routine_name FROM information_schema.routines 
WHERE routine_schema = 'public' AND routine_type = 'FUNCTION';

-- Check views
SELECT table_name FROM information_schema.views 
WHERE table_schema = 'public';

-- Test data
SELECT * FROM branches;
SELECT * FROM customers;
SELECT * FROM accounts;
```

---

## Step 7: Troubleshooting Common Issues

### Issue 1: "Application Error" Page
**Cause**: Database connection failed or environment variables missing

**Fix**:
1. Check `DATABASE_URL` is set correctly
2. Verify database is running (Green status in Render)
3. Check logs for specific error
4. Ensure URL starts with `postgresql://` not `postgres://`

### Issue 2: 500 Internal Server Error
**Cause**: Database schema not initialized or Python errors

**Fix**:
1. Verify schema.sql was executed
2. Check application logs for Python errors
3. Try re-running schema.sql

### Issue 3: Login Fails
**Cause**: No test data in database

**Fix**:
```sql
-- Verify customers exist
SELECT * FROM customers;

-- If empty, re-run the INSERT statements from schema.sql
```

### Issue 4: "No such table" Error
**Cause**: Schema not initialized properly

**Fix**:
1. Reconnect to database
2. Run schema.sql again
3. Check for SQL syntax errors in logs

### Issue 5: Build Fails
**Cause**: Missing dependencies or syntax errors

**Fix**:
1. Check requirements.txt has all dependencies
2. Verify Python version compatibility
3. Check application logs for specific error

---

## Step 8: Updating Your Application

### 8.1 Make Changes Locally
```bash
# Edit files
# Test locally first!
python app.py
```

### 8.2 Deploy Updates
```bash
# Commit changes
git add .
git commit -m "Description of changes"
git push origin main
```

### 8.3 Automatic Redeployment
Render will automatically:
1. Detect the push
2. Rebuild the application
3. Deploy the new version (2-5 minutes)

---

## Step 9: Monitoring & Maintenance

### 9.1 View Logs
1. Go to your web service in Render
2. Click **"Logs"** tab
3. Monitor for errors

### 9.2 Check Database Status
1. Go to your database in Render
2. Check **"Metrics"** for:
   - Connection count
   - Storage usage
   - Query performance

### 9.3 Manage Database
```sql
-- View connection count
SELECT count(*) FROM pg_stat_activity;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check recent transactions
SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT 10;

-- Check recovery logs
SELECT * FROM recovery_logs ORDER BY failed_at DESC LIMIT 10;
```

---

## Step 10: Custom Domain (Optional)

### 10.1 Add Custom Domain
1. Go to your web service settings
2. Click **"Custom Domain"**
3. Add your domain (e.g., `banking.yourdomain.com`)
4. Follow DNS configuration instructions
5. Render provides free SSL certificate

---

## Quick Reference

### Important URLs
- **Render Dashboard**: https://dashboard.render.com
- **Your App**: `https://your-service-name.onrender.com`
- **Database**: Via psql or pgAdmin

### Common Commands
```bash
# Connect to database
psql YOUR_EXTERNAL_DATABASE_URL

# View logs
# (Go to Render Dashboard → Service → Logs)

# Restart service
# (Go to Render Dashboard → Service → Manual Deploy → "Clear build cache & deploy")
```

### Support Resources
- Render Docs: https://render.com/docs
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Flask Docs: https://flask.palletsprojects.com/

---

## 🎉 Congratulations!

Your banking system is now live on Render with:
- ✅ PostgreSQL database with full schema
- ✅ Flask web application
- ✅ Automatic HTTPS
- ✅ Free hosting (with limitations)
- ✅ Automatic deployments from GitHub

**Your Live URL**: `https://banking-system-xxx.onrender.com`

Share this URL in your project submission! 🚀