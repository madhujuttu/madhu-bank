<<<<<<<            HEAD
# Madhu Bank — Educational Banking Simulation System

---

## 1. Project Title

**Madhu Bank** — Modern Educational Banking Simulation & Administrative Management Platform.

---

## 2. Project Overview

**Madhu Bank** is a full-stack, enterprise-style educational banking simulation application built with **Python**, **Streamlit**, and **MongoDB**. It replicates the core operational, transactional, security, and administrative workflows of a retail commercial banking platform.

The system features two completely separated and secure portals:
1. **Customer Banking Portal**: Provides user onboarding, multi-factor email verification, credential recovery, savings/current account management, cash deposits, cash withdrawals, peer-to-peer account transfers with atomic rollbacks, 6-digit transaction PIN protection, live transaction statements with CSV export, and account unlock review requests.
2. **Administrative Management Console**: Provides bank administrators with high-level KPI metrics, real-time total deposit tracking, customer account status controls (freeze/unfreeze/delete), audit ledger inspection, automated security alerts (high-value transaction warnings and brute-force lockouts), and customer reactivation request reviews.

---

## 3. What This Project Does

Madhu Bank simulates how real-world financial software operates while remaining easy to run on a local machine for learning and demonstration purposes:

- **Identity & Access Management (IAM)**:
  - Registers users with complex password validation and bcrypt hashing.
  - Issues 10-digit unique banking account numbers upon registration.
  - Enforces mandatory Two-Factor Authentication (2FA) via numeric One-Time Passwords (OTPs) sent over Gmail SMTP.
  - Enforces 5-attempt brute-force protection with automatic 15-minute account lockouts and admin security alert dispatch.
- **Financial Accounting & Double-Entry Ledger**:
  - Handles deposits and withdrawals with atomic MongoDB balance mutations.
  - Executes peer-to-peer transfers with conditional balance verification and automatic compensating rollbacks if any step fails.
  - Enforces an independent 6-digit Transaction PIN on all debit/credit operations.
  - Logs complete audit trails (transaction ID, counterparty details, timestamps, notes, and status).
- **Administrative Operations**:
  - Provides administrators with macro-level insights: Total Bank Reserve, Active Customers, Disabled Accounts, and System Volume.
  - Enables administrators to freeze (disable), unfreeze (activate), or purge customer accounts.
  - Features an administrative approval inbox for reviewing disabled account reactivation requests.
  - Dispatches persistent system alerts for high-value transactions ($\ge \text{₹}50,000$) and security lockouts.

---

## 4. Why This Project Was Created

Traditional banking codebases are either proprietary, closed-source, or excessively complex enterprise systems wrapped in microservices. Madhu Bank was created to bridge the educational gap:

1. **Practical Financial Software Engineering**: Teach beginners and computer science students how financial transactions, balance consistency, and ledger integrity are maintained without data corruption.
2. **Real-World Security Patterns**: Demonstrate how to implement password hashing (bcrypt), transaction PIN validation, Two-Factor Authentication (SMTP OTP), rate-limiting/lockouts, and session management.
3. **NoSQL in Financial Systems**: Show how MongoDB can be configured with strict unique indexes, conditional atomic updates (`$inc`, `$gte`), and compensating transaction patterns for standalone servers.
4. **Modern Interactive UI**: Showcase how Streamlit, combined with custom CSS styling and responsive state management, can render a commercial-grade SaaS banking dashboard.

---

## 5. Project History / Development Background

Based on codebase artifacts, git commit records, and architectural audits:

1. **Initial Prototype (Phase 1)**:
   - Began as a lightweight Streamlit demonstration application (`app.py`) storing user accounts and plain transactions in local MongoDB collections.
   - Authentication was basic username/password validation without multi-factor verification or security PINs.
2. **Security & Financial Hardening (Phase 2)**:
   - Replaced plain text/simple hash storage with **bcrypt** password hashing and policy enforcement in `backend/security.py`.
   - Introduced the `utils/money.py` module to enforce strict decimal precision and minor-unit conversions to prevent floating-point rounding errors.
   - Refactored money transfer logic into `backend/transfer.py` to use conditional queries (`balance: {"$gte": amount}`) and compensating rollbacks so standalone MongoDB instances never leave accounts out of balance.
3. **Enterprise UI & Two-Factor Authentication (Phase 3)**:
   - Added Gmail SMTP integration (`backend/email_otp.py`) delivering 6-digit numeric OTPs for user registration, user login, admin login, and password resets.
   - Introduced the 6-digit Transaction PIN system (`backend/security_pin.py`) to authorize every debit operation.
   - Built a comprehensive Admin Management Console with KPI cards, account freezing/unfreezing, customer review requests, and high-value transaction alerts.
4. **Recent Architectural Fixes (Phase 4)**:
   - Resolved a transaction PIN hash compatibility issue by enabling dual verification (supporting legacy bcrypt PIN hashes as well as SHA256 digests).
   - Solved legacy account lockout by implementing automatic verified email binding during login for accounts created prior to mandatory email verification.
   - Refactored top navigation dropdown callbacks to module-level scope for deterministic Streamlit execution.

---

## 6. Current Project Status

- **Status**: Stable / Fully Functional Educational Simulation.
- **Core Banking Operations**: 100% Implemented and Verified (Deposit, Withdraw, Transfer, Balance, History).
- **Authentication**: 100% Implemented (Bcrypt hashing, Gmail SMTP 2FA OTP, 15-minute brute-force lockout).
- **Security PIN**: 100% Implemented (Dual bcrypt/SHA256 verification).
- **Admin Operations**: 100% Implemented (Account freeze/enable/delete, KPI metrics, review requests, alerts).
- **Automated Tests**: 23/23 Unit & Integration Tests Passing (`pytest tests/`).

---

## 7. Main Features

| Feature Category | Implemented Capabilities |
| :--- | :--- |
| **Authentication & IAM** | Registration, Login, 2FA Email OTP, Forgot Password with Security Question & OTP, 15-min Brute-Force Lockout. |
| **Account & Banking** | Unique 10-digit Account Numbers, Savings & Current accounts, Real-time Balance Checking. |
| **Transaction Processing** | Cash Deposit, Cash Withdrawal, P2P Money Transfer, 6-digit Transaction PIN authorization, Atomic Compensating Rollbacks. |
| **Ledger & Statements** | Complete transaction logging, Search by ID/Party/Note, Filter by Type (Deposit/Withdrawal/Transfer), CSV Statement Export. |
| **Customer Profile** | Customer details card, Profile picture upload & removal (Base64 storage up to 2MB), Email verification & linking, PIN creation/change. |
| **Account Review Workflow** | Disabled account unlock request form for customers; Admin review interface with Approve/Reject actions and reason logging. |
| **Admin Console** | System KPI metrics (Total Reserve, Users, Accounts, Transactions), Account Freeze/Unfreeze/Delete, Search accounts, Audit transactions. |
| **System Alerts** | Automated High-Value Transfer alerts ($\ge \text{₹}50,000$), Security Lockout alerts, Unread badge counters, Acknowledge/Dismiss controls. |

---

## 8. Technology Stack

- **Core Programming Language**: Python 3.10 – 3.14 (Tested on Python 3.14.6)
- **Frontend & Web Framework**: [Streamlit](https://streamlit.io/) (v1.63+) with custom CSS styling and responsive layout blocks.
- **Database Engine**: [MongoDB](https://www.mongodb.com/) Community Server (Local standalone instance on port 27017).
- **Database Driver**: [PyMongo](https://pymongo.readthedocs.io/) (v4.10 – v4.17).
- **Security & Cryptography**:
  - `bcrypt`: Password and security answer hashing (salt rounds: 12).
  - `hashlib`: SHA-256 digests for transaction PINs and admin session tokens.
  - `secrets`: Cryptographically secure pseudorandom number generator (CSPRNG) for OTPs, account numbers, and tokens.
- **Email & Communications**: Python standard library `smtplib` and `email.mime` configured for Google Gmail SMTP (Port 587 with TLS).
- **Data Manipulation**: `pandas` for transaction filtering, statement structuring, and CSV generation.
- **Configuration**: `python-dotenv` for loading environment variables from `.env`.
- **Testing Framework**: `pytest` with `pytest-anyio`.

---

## 9. Prerequisites

Before installing and running Madhu Bank, ensure your development machine has:

1. **Operating System**: Windows 10/11, macOS, or Linux.
2. **Python**: Python 3.10 or higher installed. Verify by running:
   ```powershell
   python --version
   ```
3. **MongoDB**: MongoDB Community Server installed and running locally on port `27017`.
   - Download: [MongoDB Community Server](https://www.mongodb.com/try/download/community)
   - Verify service is active via Windows Services or PowerShell:
     ```powershell
     Get-Service MongoDB
     ```
4. **Gmail Account with App Password** (for Email OTPs):
   - A Gmail account with 2-Step Verification enabled.
   - A 16-character **Gmail App Password** generated from [Google Account Security](https://myaccount.google.com/apppasswords).

---

## 10. Complete Project Structure

```text
madhu-bank/
│
├── .streamlit/
│   └── config.toml                  # Streamlit server & theme configuration
│
├── backend/
│   ├── __init__.py                  # Backend package marker
│   ├── account.py                   # Cash deposit, withdrawal, and current balance logic
│   ├── account_review_requests.py   # Reactivation request submission, review, and admin tokens
│   ├── admin.py                     # Administrator authentication and account moderation
│   ├── alerts.py                    # Automated system alerts (lockouts, high-value transfers)
│   ├── database.py                  # PyMongo connection, collections, and index specifications
│   ├── email_otp.py                 # In-memory OTP generation, expiry tracking, and SMTP dispatch
│   ├── password_reset.py            # Password reset execution and validation
│   ├── security.py                  # Password complexity rules and bcrypt hashing helpers
│   ├── security_pin.py              # 6-digit transaction PIN hashing and dual verification
│   ├── transactions.py              # Transaction history queries and statement formatting
│   ├── transfer.py                  # Peer-to-peer transfers with atomic compensating rollbacks
│   └── users.py                     # Customer registration, login status, and lockout logic
│
├── config/
│   ├── __init__.py                  # Config package marker
│   └── settings.py                  # Environment variable ingestion, limits, and SMTP constants
│
├── frontend/
│   ├── assets/                      # Static branding artwork
│   ├── __init__.py                  # Frontend package marker
│   ├── requirements.txt             # Frontend-specific dependency reference
│   └── styles.py                    # Centralized CSS design system (Auth, Customer, Admin)
│
├── migrations/
│   ├── __init__.py                  # Migrations package marker
│   └── 001_migrate_accounts.py      # Historical account numbering backfill script
│
├── tests/
│   ├── __init__.py                  # Tests package marker
│   ├── test_admin.py                # Unit tests for admin credentials and email resolution
│   ├── test_alerts.py               # Unit tests for system alert generation and dispatch
│   ├── test_email_otp.py            # Unit tests for OTP generation and validation
│   ├── test_money.py                # Unit tests for decimal monetary calculations
│   └── test_validation.py           # Unit tests for credentials and transaction PIN hashes
│
├── utils/
│   ├── __init__.py                  # Utilities package marker
│   ├── money.py                     # Decimal precision, formatting, and minor-unit conversions
│   └── validation.py                # Shared regex validation for usernames, notes, and passwords
│
├── .env                             # Environment configuration (secrets, credentials, ports)
├── .gitignore                       # Git exclusion rules
├── app.py                           # Main application entry point, routing, and UI rendering
├── AUDIT.md                         # Architecture audit, security findings, and roadmap
├── logo.png                         # Madhu Bank branding logo
└── requirements-phase1.txt          # Python package dependency manifest
```

---

## 11. Explanation of Every Important File and Folder

### Root Files
- **`app.py`**: The primary executable. Initializes Streamlit configuration, establishes session states, manages authentication flow routing, renders customer pages (Dashboard, Deposit, Withdraw, Transfer, History, Profile), and renders administrative controls.
- **`.env`**: Local configuration file containing sensitive secrets (MongoDB connection string, Gmail SMTP credentials, admin passwords). Never committed to public version control.
- **`requirements-phase1.txt`**: Declares mandatory Python packages (`streamlit`, `pandas`, `pymongo`, `pytest`, `python-dotenv`, `bcrypt`).
- **`logo.png`**: Visual brand mark displayed across top headers and navigation bars.

### `backend/` Folder
- **`database.py`**: Connects to MongoDB via PyMongo (`client["madhu_bank"]`), instantiates collection references, and builds necessary unique/sparse indexes on startup.
- **`users.py`**: Handles user account creation, credential verification, failed login counters, and 15-minute temporary lockout triggers.
- **`security.py`**: Enforces strict password policies (length, uppercase, lowercase, numbers, special characters) and performs bcrypt salting/hashing.
- **`security_pin.py`**: Manages the secondary 6-digit transaction PIN required for debit operations; provides dual verification supporting legacy bcrypt and modern SHA256 hashes.
- **`account.py`**: Executes atomic cash deposits and cash withdrawals against active accounts, writing audit logs to `transactions`.
- **`transfer.py`**: Orchestrates two-legged P2P money transfers using conditional updates and compensating rollbacks if any stage fails.
- **`email_otp.py`**: Generates cryptographically secure 6-digit OTPs, tracks expiry timestamps, and dispatches HTML/plain emails via Gmail SMTP TLS.
- **`password_reset.py`**: Validates security questions and executes password updates in MongoDB.
- **`admin.py`**: Handles administrator authentication (by username or email) and provides moderation functions (freeze, unfreeze, delete, total metrics).
- **`alerts.py`**: Creates persistent audit notifications in `system_alerts` for high-value transfers ($\ge \text{₹}50,000$) and security lockouts.
- **`account_review_requests.py`**: Manages reactivation requests submitted by users whose accounts were disabled.
- **`transactions.py`**: Provides query helpers to fetch customer and bank-wide transaction ledgers.

### `config/` Folder
- **`settings.py`**: Centralizes configuration variables, imports values from `.env`, defines transfer safety limits, and validates SMTP settings.

### `frontend/` Folder
- **`styles.py`**: Supplies the custom CSS theme, injecting brand emerald styles, card geometry, responsive layout rules, and button aesthetics.

### `utils/` Folder
- **`money.py`**: Implements high-precision `Decimal` arithmetic for Indian Rupee (`₹`) calculations, preventing floating-point inaccuracies.
- **`validation.py`**: Supplies regex pattern validators for usernames, notes, and passwords.

### `tests/` Folder
- Contains automated test suites (`test_admin.py`, `test_alerts.py`, `test_email_otp.py`, `test_money.py`, `test_validation.py`) executed via `pytest`.

---

## 12. Installation

Follow these sequential steps to set up Madhu Bank on your local development machine (Windows instructions shown):

### STEP 1: Install Prerequisites
Ensure **Python 3.10+** and **MongoDB Community Server** are installed.

### STEP 2: Clone or Open the Project
Open PowerShell and navigate to the project directory:
```powershell
cd C:\Users\user\OneDrive\Desktop\madhu-bank
```

### STEP 3: Create a Virtual Environment
Isolate project dependencies by creating a dedicated virtual environment:
```powershell
python -m venv env1
```

### STEP 4: Activate the Virtual Environment
Activate the environment in your shell:
```powershell
.\env1\Scripts\Activate.ps1
```
*(If PowerShell displays an Execution Policy restriction, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### STEP 5: Install Python Dependencies
Install all required libraries into your virtual environment:
```powershell
pip install -r requirements-phase1.txt
```
Also install `bcrypt` if not explicitly present in the manifest:
```powershell
pip install bcrypt
```

---

## 13. Environment Setup

Madhu Bank requires an environment file named `.env` in the project root directory.

Create or edit `.env` in the root folder:
```powershell
New-Item -Path .env -ItemType File -Force
```

---

## 14. Environment Variables

Populate `.env` with the following key-value pairs:

```ini
# =========================================================
# DATABASE CONFIGURATION
# =========================================================
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=madhu_bank

# =========================================================
# GMAIL SMTP CONFIGURATION (For 2FA OTP Delivery)
# =========================================================
MADHU_BANK_SMTP_HOST=smtp.gmail.com
MADHU_BANK_SMTP_PORT=587
MADHU_BANK_SMTP_USERNAME=your_gmail_address@gmail.com
MADHU_BANK_SMTP_PASSWORD=your_16_char_app_password
MADHU_BANK_SMTP_FROM=your_gmail_address@gmail.com

# =========================================================
# ADMINISTRATOR CREDENTIALS
# =========================================================
MADHU_BANK_ADMIN_USERNAME=admin
MADHU_BANK_ADMIN_PASSWORD=admin123
MADHU_BANK_ADMIN_EMAIL=your_gmail_address@gmail.com

# =========================================================
# APPLICATION TUNING (Optional)
# =========================================================
MADHU_SESSION_TIMEOUT_SECONDS=900
MADHU_LOGIN_MAX_FAILURES=5
MADHU_LOGIN_LOCKOUT_SECONDS=300
MADHU_CURRENCY=INR
MADHU_ENVIRONMENT=local
```

> [!IMPORTANT]
> **Gmail App Password Instructions**:
> Never enter your primary Google account password in `MADHU_BANK_SMTP_PASSWORD`. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords), generate an App Password for "Mail", and paste the resulting 16-character string into `.env`.

---

## 15. Database Setup

Madhu Bank connects to MongoDB via `backend/database.py`. No manual table creation or schema migration scripts are required because:
1. MongoDB creates the database `madhu_bank` automatically when data is first written.
2. `backend/database.py` automatically checks, creates, and normalizes all collection indexes upon application startup.

---

## 16. MongoDB Setup

Ensure MongoDB service is running locally:

```powershell
# Check MongoDB service status
Get-Service MongoDB

# If stopped, start the service
Start-Service MongoDB
```

To verify the connection using Python:
```powershell
.\env1\Scripts\python.exe -c "from backend.database import db; print('Connected to:', db.name)"
```
Output should be: `Connected to: madhu_bank`.

---

## 17. How the Application Starts

When you launch `streamlit run app.py`:

```text
User executes `streamlit run app.py`
                  ↓
1. Python executes top-level imports in `app.py`
                  ↓
2. `config/settings.py` loads `.env` variables
                  ↓
3. `backend/database.py` connects to MongoDB and builds collection indexes
                  ↓
4. `app.py` checks `st.session_state`:
   - If not logged in: renders Auth View (`login`, `register`, `forgot_password`, or `admin_login`)
   - If logged in as User: renders Customer Layout (Navbar + Customer Pages)
   - If logged in as Admin: renders Administrator Layout (Admin Navbar + Admin Dashboard)
                  ↓
5. Custom CSS from `frontend/styles.py` is injected into the DOM
```

---

## 18. Application Architecture

Madhu Bank adheres to a 3-tier modular architecture:

```text
+--------------------------------------------------------------------------+
|                           PRESENTATION LAYER                             |
|                                (app.py)                                  |
|   +--------------------------+       +-------------------------------+   |
|   |  Customer Banking Portal |       | Administrator Management Portal|   |
|   |  (Dashboard, Deposits,   |       | (KPIs, User Moderation,       |   |
|   |   Transfers, History)    |       |  Alerts, Review Requests)     |   |
|   +--------------------------+       +-------------------------------+   |
|                                  ↑                                       |
|                       Streamlit Session State                            |
+--------------------------------------------------------------------------+
                                   |
                                   v
+--------------------------------------------------------------------------+
|                            APPLICATION LAYER                             |
|                           (backend/ & utils/)                            |
|   +----------------+  +------------------+  +------------------------+   |
|   |   users.py     |  |   transfer.py    |  |     security.py        |   |
|   | (Auth & Lock)  |  | (Compensating tx)|  | (Bcrypt & PIN Hash)    |   |
|   +----------------+  +------------------+  +------------------------+   |
|   +----------------+  +------------------+  +------------------------+   |
|   |   account.py   |  |  email_otp.py    |  |     alerts.py          |   |
|   | (Deposit/Wdl)  |  |  (SMTP Engine)   |  | (Persistent Dispatches)|  |
|   +----------------+  +------------------+  +------------------------+   |
+--------------------------------------------------------------------------+
                                   |
                                   v
+--------------------------------------------------------------------------+
|                               DATA LAYER                                 |
|                        (backend/database.py)                             |
|                           MongoDB Instance                               |
|        [users]  [transactions]  [login_attempts]  [system_alerts]        |
|                 [account_review_requests]  [cards]                       |
+--------------------------------------------------------------------------+
```

---

## 19. How the User System Works

Each customer account has:
- A unique **Username** (alphanumeric, 3–32 characters).
- A 10-digit numeric **Account Number** (generated via CSPRNG `secrets.randbelow` and protected by a unique sparse index).
- An encrypted **Password** hashed using `bcrypt` (12 salt rounds).
- A registered **Email Address** verified via 2FA OTP.
- An optional 6-digit **Transaction PIN** required for debit/credit operations.
- An account **Status**: `Active`, `Pending Verification`, or `Disabled`.

---

## 20. Registration Flow

### What is it?
The onboarding flow where new customers create a bank account with initial zero balance.

### Why is it needed?
Establishes a customer identity, hashes authentication credentials, issues a unique Account Number, and sends an activation OTP.

### Where is it implemented?
- UI: `app.py` in `register_page()` and `register_otp_verification_page()`.
- Backend: `backend/users.py` in `register_user()`.
- Security: `backend/security.py` in `hash_password()`.

### How it works

```text
User fills registration form (Name, Username, Password, DOB, Type, Recovery Q&A, Email)
                                   ↓
Application validates inputs (Regex username, 8+ char complex password)
                                   ↓
Password is hashed via bcrypt.hashpw(password, gensalt())
                                   ↓
Recovery answer is hashed via bcrypt
                                   ↓
Document inserted into `users` collection with status="Pending Verification"
                                   ↓
Unique 10-digit Account Number assigned via ensure_account_number()
                                   ↓
6-digit numeric OTP generated and sent to user email via Gmail SMTP
                                   ↓
User enters OTP on register_otp_verification page
                                   ↓
OTP validated -> User status updated to "Active", email_verified=True
                                   ↓
User redirected to Dashboard as authenticated customer
```

### What happens in the database?
- **Collection**: `users`
- **Fields created**: `name`, `username`, `password`, `dob`, `account_type`, `balance: 0`, `status: "Pending Verification"`, `role: "user"`, `created_at`, `email`, `email_verified: False`, `security_question`, `security_answer_hash`, `account_number`.
- Upon OTP verification: `status` updated to `"Active"`, `email_verified` updated to `True`.

### Important functions
- `register_user(...)`: Validates input and executes insert into `users_collection`.
- `ensure_account_number(username)`: Generates and persists a unique 10-digit number.
- `generate_and_send_otp(email)`: Dispatches the registration verification OTP.

### Error cases
- Duplicate username or email: Blocked with clear conflict error.
- Weak password: Fails regex policy with specific guidance.
- SMTP delivery failure: Error message displayed explaining email delivery failure.

---

## 21. Email Verification / OTP Flow

### What is it?
A Two-Factor Authentication mechanism that issues a 6-digit cryptographic code valid for 5 minutes (300 seconds) to verify email ownership.

### Why is it needed?
Prevents fraudulent registrations, unauthorized logins, and unauthenticated password resets.

### Where is it implemented?
- Backend: `backend/email_otp.py` (`generate_otp`, `send_otp_email`, `validate_otp`).

### How it works

```text
Action requested (Login, Register, Transfer, Forgot Password, PIN Setup)
                                   ↓
generate_otp(6) creates 6-digit numeric string using secrets.randbelow(10)
                                   ↓
SHA-256 hash of OTP stored in memory with creation timestamp and expiry (300s)
                                   ↓
MIME multipart message constructed and sent via smtplib.SMTP (TLS port 587)
                                   ↓
User submits OTP code in Streamlit form
                                   ↓
validate_otp(email, code) checks:
  1. Record exists in OTP_STORE
  2. Current time < expiry time
  3. SHA-256(entered_code) == stored_hash
                                   ↓
If valid, returns True and deletes OTP from memory (single-use protection)
```

---

## 22. Login Flow

### What is it?
The authentication mechanism for returning customers.

### Why is it needed?
Verifies credentials, checks brute-force lockout status, and enforces 2FA email verification.

### Where is it implemented?
- UI: `app.py` in `login_page()` and `login_otp_verification_page()`.
- Backend: `backend/users.py` in `login_with_status()`.

### How it works

```text
User enters Username, Password, and Registered Email
                                   ↓
backend/users.py checks `login_attempts` for active 15-minute lockout
                                   ↓
Bcrypt verifies submitted password against stored hash
  - If mismatch: increments failed_attempts. If >=5, triggers 15-min lockout & alert
                                   ↓
System checks account status:
  - If "Disabled": redirects to disabled_account_review page
  - If "Active": sends 6-digit OTP to user's registered email
                                   ↓
User enters 6-digit OTP on login_otp_verification_page
                                   ↓
OTP validated -> Session state initialized:
  st.session_state.logged_in = True
  st.session_state.username = username
  st.session_state.role = "user"
                                   ↓
Redirects to Customer Dashboard
```

---

## 23. Forgot Password Flow

### What is it?
A multi-step recovery flow allowing users to regain access to their accounts.

### Where is it implemented?
- UI: `app.py` in `forgot_password_page()`.
- Backend: `backend/password_reset.py` in `reset_password()`.

### How it works

```text
User enters Username, Account Number, and Registered Email
                                   ↓
Application verifies records match in MongoDB
                                   ↓
6-digit OTP sent to registered email
                                   ↓
User verifies OTP
                                   ↓
Application presents the user's configured Security Question
                                   ↓
User enters Security Answer -> Verified against bcrypt hash in DB
                                   ↓
User enters New Password -> Validated against complexity policy
                                   ↓
Password updated with new bcrypt hash in `users` collection
                                   ↓
User redirected to Login page with success confirmation
```

---

## 24. Password Security

- **Library**: `bcrypt` (C-optimized implementation).
- **Salt Generation**: `bcrypt.gensalt()` with automatic cryptographic random salt.
- **Complexity Policy**:
  - Minimum 8 characters (10 characters recommended in validation utils).
  - At least one uppercase letter (`[A-Z]`).
  - At least one lowercase letter (`[a-z]`).
  - At least one digit (`[0-9]`).
  - At least one special character (`[^A-Za-z0-9]`).
- **Security Answers**: Hashed using `bcrypt` (without uppercase/special complexity enforcement) to maintain recovery question integrity.

---

## 25. User Dashboard

### What is it?
The primary landing surface for authenticated customers.

### Where is it implemented?
- UI: `app.py` in `dashboard()`.

### Visual Structure & Components
1. **Header Banner**: Greets customer, displays current timestamp and banking mode.
2. **KPI Metric Row**:
   - **Current Balance**: Displays balance formatted in INR (`₹XX,XXX.XX`).
   - **Account Type**: Shows Savings or Current with 10-digit Account Number.
   - **Total Transactions**: Total ledger operations recorded.
   - **Account Status**: Displays active status badge.
3. **Transaction Activity Chart**: Visual bar chart illustrating activity frequency over the last 7 days.
4. **Quick Banking Shortcuts**: Direct navigation buttons to Deposit, Transfer, Withdraw, and Transactions.
5. **Recent Transactions Table**: Shows the 5 most recent deposits, withdrawals, and transfers with counterparty names and status badges.

---

## 26. Account Management

Customers can access their account details via **My Account → Account Overview** (`account_page()` in `app.py`):
- Displays legal Name, Username, Date of Birth, calculated Age, and Category (Major vs Minor).
- Displays Account Number, Account Type, Status, and current ledger balance.
- If an account is disabled, customers can navigate to **Account Review** to file an appeal with the administration team.

---

## 27. Deposit Flow

### What is it?
Simulation of adding funds into a customer's bank account.

### Where is it implemented?
- UI: `app.py` in `deposit_page()`.
- Backend: `backend/account.py` in `deposit_money()`.

### How it works

```text
Customer enters deposit amount and 6-digit Transaction PIN
                                   ↓
System verifies user has configured a Transaction PIN
                                   ↓
verify_transaction_pin() validates PIN against stored hash
                                   ↓
backend/account.py executes atomic balance increment:
  users_collection.update_one(
    {"username": username, "status": "Active"},
    {"$inc": {"balance": amount}}
  )
                                   ↓
Audit transaction inserted into `transactions` collection:
  type: "Deposit", status: "SUCCESS", amount: amount
                                   ↓
UI updates immediately and displays success toast with new balance
```

---

## 28. Withdrawal Flow

### What is it?
Debiting funds from a customer's available balance.

### Where is it implemented?
- UI: `app.py` in `withdraw_page()`.
- Backend: `backend/account.py` in `withdraw_money()`.

### How it works

```text
Customer enters withdrawal amount and 6-digit Transaction PIN
                                   ↓
System verifies entered PIN matches stored hash
                                   ↓
Conditional update executes against MongoDB:
  users_collection.update_one(
    {
      "username": username,
      "status": "Active",
      "balance": {"$gte": amount}
    },
    {"$inc": {"balance": -amount}}
  )
                                   ↓
If modified_count == 1:
  - Audit transaction inserted into `transactions` collection
  - Success toast displayed with updated balance
If modified_count == 0:
  - Operation rejected with "Insufficient balance"
```

---

## 29. Money Transfer Flow

### What is it?
Two-legged peer-to-peer fund transfer between two Madhu Bank customers using their 10-digit Account Numbers.

### Where is it implemented?
- UI: `app.py` in `transfer_page()`.
- Backend: `backend/transfer.py` in `transfer_money()`.

### How it works (Compensating Rollback Architecture)

```text
Customer enters Receiver Account Number, Amount, Note, and 6-digit PIN
                                   ↓
Transaction PIN verified -> 6-digit OTP sent to sender's registered email
                                   ↓
Sender verifies OTP
                                   ↓
backend/transfer.py executes Step 1:
  Debit sender ONLY IF balance >= amount:
  users_collection.find_one_and_update(
    {"account_number": sender_acc, "balance": {"$gte": amount}},
    {"$inc": {"balance": -amount}}
  )
                                   ↓
If debit succeeds, Step 2 executes:
  Credit receiver:
  users_collection.find_one_and_update(
    {"account_number": receiver_acc, "status": "Active"},
    {"$inc": {"balance": amount}}
  )
  *If credit fails -> Automatic Rollback: sender balance credited back*
                                   ↓
Step 3 executes:
  Double-entry ledger records inserted into `transactions`:
  - Record A: Direction="Out", User=Sender, Counterparty=Receiver
  - Record B: Direction="In", User=Receiver, Counterparty=Sender
  *If insert fails -> Full Rollback: receiver debited, sender credited*
                                   ↓
If amount >= ₹50,000:
  High-value system alert dispatched to administrator inbox and email
                                   ↓
Success toast displayed with unique Transfer ID
```

---

## 30. Balance Checking Flow

- Implemented in `balance_page()` in `app.py`.
- Queries MongoDB in real-time using `current_balance(username)`.
- Features an on-screen **"Refresh balance"** trigger to bypass cache and read the latest database state.

---

## 31. Transaction History

- Implemented in `transactions_page()` in `app.py`.
- Retrieves all records for the authenticated customer from `transactions_collection`.
- **Search & Filter**: Real-time substring search across Transaction IDs, Counterparty Names, Notes, and Amounts.
- **Category Filter**: Quickly isolate Deposits, Withdrawals, or Transfers.
- **CSV Statement Export**: Generates and downloads a clean UTF-8 CSV statement named `madhu_bank_statement_<username>.csv`.

---

## 32. Profile Management

- Implemented in `profile_page()` in `app.py`.
- Displays personal details, account number, account category, and registered email address.
- **Profile Picture**: Supports uploading JPG, PNG, and WebP images ($\le 2\text{ MB}$), stored as Base64 strings directly in MongoDB.
- **Email Linking**: Allows legacy users without an email on file to input and verify their email address via OTP.
- **Transaction PIN Management**: Enables customers to set or reset their 6-digit PIN via OTP verification.

---

## 33. Logout Flow

- Implemented in `logout()` in `app.py`.
- Clears all session keys: `logged_in`, `username`, `role`, `account_number`, `pending_*`.
- Resets navigation state to `login` and triggers `st.rerun()`.

---

## 34. Admin Login

- Implemented in `admin_login_page()` in `app.py` and `backend/admin.py`.
- Accepts either the administrative email (`MADHU_BANK_ADMIN_EMAIL`) or username (`admin`).
- Verifies credentials against `.env` and users with `role: "admin"`.
- Dispatches a 6-digit Two-Factor Authentication OTP to the admin email address.
- Upon OTP verification, grants administrative access and routes to `admin_dashboard`.

---

## 35. Admin Dashboard

- Implemented in `admin_dashboard()` in `app.py`.
- Features executive KPI cards:
  - **TOTAL BANK RESERVE**: Aggregate sum of all customer balances.
  - **TOTAL CUSTOMERS**: Total registered accounts.
  - **ACTIVE ACCOUNTS**: Total active accounts.
  - **DISABLED ACCOUNTS**: Accounts frozen by administrator.
  - **TOTAL TRANSACTIONS**: Global ledger volume.
- Displays quick-management panels and recent platform-wide transaction activity.

---

## 36. Admin Features

1. **User Management (`admin_users`)**: Search all accounts by account number, name, or username.
2. **Account Moderation (`admin_accounts`)**:
   - Inspect individual account details.
   - **Freeze/Disable Account**: Sets status to `Disabled` and triggers an account status alert.
   - **Enable Account**: Restores account status to `Active`.
   - **Delete Account**: Removes user record and purges corresponding transactions.
3. **Audit Ledger (`admin_transactions`)**: Global inspection of all deposits, withdrawals, and transfers across the institution.
4. **Requests & Alerts (`admin_requests`)**:
   - Customer review requests tab: Approve (auto-reactivates account) or Reject with notes.
   - System alerts tab: View high-value transfer warnings and security lockout notices with Acknowledge/Dismiss controls.
5. **Platform Reports (`admin_reports`)**: Summary reports of institutional deposits, turnover, and volume.
6. **Admin Settings (`admin_settings`)**: Displays active system configuration, SMTP connectivity, and administrator email targets.

---

## 37. Admin/User Data Flow

```text
Customer Portal                                      Admin Portal
     │                                                    │
     ├─ Deposit / Withdraw / Transfer ───────────────────►│ (Audited in Global Ledger)
     │                                                    │
     ├─ High-Value Transfer (≥ ₹50,000) ─────────────────►│ (Triggers System Alert)
     │                                                    │
     ├─ 5 Failed Logins (Lockout) ───────────────────────►│ (Triggers Security Alert)
     │                                                    │
     ├─ Account Disabled ────────────────────────────────►│ (Review Request Submitted)
     │                                                    │
     │◄────────────────── Re-activates Account ───────────┤ (Admin Approves Review)
     │                                                    │
     │◄────────────────── Freezes Account ────────────────┤ (Admin Disables User)
```

---

## 38. Database Collections

| Collection Name | Purpose |
| :--- | :--- |
| `users` | Stores customer and administrator profile documents, balances, and credentials. |
| `transactions` | Stores double-entry immutable ledger entries for deposits, withdrawals, and transfers. |
| `login_attempts` | Tracks consecutive failed login attempts, timestamps, and 15-minute lockouts. |
| `account_review_requests` | Stores customer appeal requests for disabled account reactivation. |
| `system_alerts` | Stores automated security warnings and high-value transaction notifications. |
| `admin_action_sessions` | Stores temporary admin authorization tokens with TTL auto-expiration. |
| `cards` | Collection reserved for virtual/debit card records. |

---

## 39. Database Fields

### `users` Collection Document Schema
```json
{
  "_id": "ObjectId",
  "name": "Madhu Juttu",
  "username": "madhu",
  "password": "$2b$12$... (bcrypt hash)",
  "dob": "2004-06-06",
  "account_type": "Savings",
  "balance": 102550.0,
  "status": "Active",
  "role": "user",
  "account_number": 5319779851,
  "email": "user@example.com",
  "email_verified": true,
  "transaction_pin_hash": "$2b$12$... or SHA256 hex string",
  "security_question": "What is your primary school name?",
  "security_answer_hash": "$2b$12$... (bcrypt hash)",
  "profile_picture_data": "base64-encoded string (optional)",
  "profile_picture_mime": "image/png (optional)",
  "created_at": "ISODate"
}
```

### `transactions` Collection Document Schema
```json
{
  "_id": "ObjectId",
  "transaction_id": "TX-A1B2C3D4E5F6",
  "account_number": 5319779851,
  "username": "madhu",
  "user_name": "Madhu Juttu",
  "type": "Transfer",
  "direction": "Out",
  "amount": 5000.0,
  "currency": "INR",
  "status": "Completed",
  "counterparty_account_number": 7038280136,
  "counterparty_username": "sagar",
  "counterparty_name": "Sagar Kumar",
  "note": "Rent payment",
  "description": "Transfer to Sagar Kumar (Account Number 7038280136)",
  "date": "2026-09-23T12:00:00+05:30",
  "created_at": "ISODate"
}
```

---

## 40. How Data Is Stored

- **Numbers**: Balances and amounts are stored as finite floats or integers rounded to standard minor-unit decimal precision.
- **Credentials**: Passwords and security answers are salted and hashed using bcrypt before insertion. Plaintext credentials are never written to disk.
- **Dates**: Stored as UTC ISO dates or timezone-aware ISO-8601 strings.
- **Images**: Profile images are validated ($\le 2\text{ MB}$), encoded as ASCII Base64 strings, and stored in the user's document.

---

## 41. How Data Is Retrieved

- Single customer lookups use indexed queries: `users_collection.find_one({"username": username})` or `{"account_number": num}`.
- Ledger histories use indexed sorting: `transactions_collection.find({"username": username}).sort("created_at", -1)`.
- Global metrics use MongoDB aggregation pipelines: `{"$group": {"_id": None, "total": {"$sum": "$balance"}}}`.

---

## 42. How Data Is Updated

- Balance adjustments always use atomic operator expressions (`$inc`) rather than read-modify-write patterns, preventing race conditions.
- Account freezing and status changes use targeted update operators: `{"$set": {"status": "Disabled"}}`.

---

## 43. How Transactions Work Internally

Madhu Bank operates on standalone MongoDB instances without requiring multi-document replica set transactions (`replicaSet`). Ledger consistency is maintained using **Compensating Rollbacks**:

1. **Step 1 (Conditional Sender Debit)**:
   ```python
   updated_sender = users_collection.find_one_and_update(
       {"account_number": sender_number, "balance": {"$gte": amount}},
       {"$inc": {"balance": -amount}},
       return_document=True
   )
   ```
2. **Step 2 (Conditional Receiver Credit)**:
   If sender debit succeeds, receiver is credited. If receiver credit fails, sender is immediately refunded (`$inc: {"balance": amount}`).
3. **Step 3 (Dual Ledger Insert)**:
   Debit and credit transaction records are inserted. If the insert fails, both accounts are rolled back to their initial balances.

---

## 44. Security Features

1. **Bcrypt Password Protection**: Slow cryptographic hash algorithm resistant to GPU-accelerated dictionary attacks.
2. **Mandatory 2FA Email OTP**: All authentication and recovery routes require a 6-digit numeric OTP delivered over TLS.
3. **Secondary Transaction PIN**: Financial debits require an independent 6-digit PIN.
4. **Brute-Force Rate Limiting**: 5 consecutive invalid login attempts lock the account for 15 minutes.
5. **Sanitized User Inputs**: Username regex matching, HTML character escaping, and note length constraints.
6. **No Plaintext Passwords in RAM/Logs**: Passwords excluded from query projections (`{"password": 0}`).

---

## 45. Encryption

- **Transport Encryption**: All OTP email communications use SMTP over TLS (Transport Layer Security) on port 587.
- **Data-at-Rest Protection**: Passwords and security answers are irreversibly transformed using bcrypt hashing with random salts.
- **Transaction PIN Protection**: Hashed using SHA-256 / bcrypt digests.

---

## 46. Password Hashing

```python
import bcrypt

# Hash password
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")

# Verify password
is_valid = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
```

---

## 47. OTP Security

- **CSPRNG Generation**: Generated using `secrets.randbelow(10)`.
- **In-Memory Storage**: OTPs stored in memory and hashed with SHA-256.
- **Short Lifespan**: Automatically invalidated after 300 seconds (5 minutes).
- **Single-Use**: Deleted from memory immediately upon successful validation.

---

## 48. Session Security

- Managed via Streamlit's native `st.session_state`.
- Role verification checks (`st.session_state.role == "admin"`) guard administrative routes.
- Explicit session invalidation on logout clears all sensitive keys from memory.

---

## 49. Input Validation

- **Usernames**: `^[A-Za-z0-9_.-]{3,32}$` (Letters, digits, dots, hyphens, underscores).
- **Amounts**: Must be finite positive numbers ($> 0$).
- **Account Numbers**: Must be exactly 10 digits.
- **Transaction PIN**: Must be exactly 6 digits.

---

## 50. Error Handling

- **Database Errors**: Wrapped in try-except blocks; operations roll back cleanly on failure.
- **SMTP Failures**: Gracefully captured and reported to the UI with diagnostics.
- **Validation Errors**: Clear amber warning banners and red error toasts inform the user without exposing stack traces.

---

## 51. UI Architecture

Built on Streamlit with a clean custom emerald styling system (`frontend/styles.py`):
- **Fixed Top Navigation**: Replaces default vertical sidebars with modern, responsive horizontal navigation menus.
- **Brand Geometry**: Cohesive border radius (10px), subtle elevation shadows, and high-contrast typography.
- **Responsive Viewports**: Supports desktop and mobile viewport resolutions.

---

## 52. User UI Explanation

- **Login / Register**: Clean card layouts with responsive two-column presentation.
- **Dashboard**: High-level KPI metrics, 7-day bar chart, quick action shortcuts, and recent ledger activity.
- **Deposit & Withdraw Pages**: Single-action forms with real-time balance card previews.
- **Transfer Page**: Two-step flow (form submission followed by OTP verification modal).
- **Transactions Page**: Enterprise table with search, category filtering, and CSV download button.
- **Profile Page**: Two-column layout with profile picture uploader, customer information rows, email linking, and PIN management.

---

## 53. Admin UI Explanation

- **Admin Dashboard**: Macro-economic KPI cards (Total Reserves, Customer Count, Active/Disabled ratios).
- **Users**: Searchable customer registry with status badges.
- **Accounts**: Expandable customer cards with direct **Freeze**, **Enable**, and **Delete** buttons.
- **Transactions**: Bank-wide chronological transaction ledger.
- **Requests & Alerts**: Tabbed interface for customer reactivation appeals and security alert notifications.
- **Settings**: Administrative system configuration display.

---

## 54. Navigation Flow

```text
                                [Application Launch]
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
            [Not Logged In]                                 [Logged In]
                   │                                             │
      ┌────────────┼────────────┐                  ┌─────────────┴─────────────┐
      ▼            ▼            ▼                  ▼                           ▼
   [Login]    [Register]   [Admin Login]    [Customer Portal]           [Admin Portal]
      │            │            │                  │                           │
  (2FA OTP)    (2FA OTP)    (2FA OTP)       ├─ Dashboard                ├─ Dashboard
      │            │            │           ├─ My Account               ├─ Users
      └────────────┼────────────┘           ├─ Banking (Dep/Wdl/Xfer)   ├─ Accounts
                   │                        ├─ Transactions             ├─ Transactions
                   ▼                        └─ Profile                  ├─ Requests & Alerts
              [Dashboard]                                               └─ Settings
```

---

## 55. Complete User Journey

1. **Visit Site** $\rightarrow$ Opens `http://localhost:8501`.
2. **Register** $\rightarrow$ Submits details, verifies Email OTP, receives 10-digit Account Number.
3. **Login** $\rightarrow$ Enters username, password, email $\rightarrow$ Verifies 2FA OTP.
4. **Set Transaction PIN** $\rightarrow$ Navigates to Profile $\rightarrow$ Configures 6-digit PIN via OTP.
5. **Deposit Funds** $\rightarrow$ Navigates to Deposit $\rightarrow$ Deposits initial balance.
6. **Transfer Money** $\rightarrow$ Navigates to Transfer $\rightarrow$ Sends funds to peer account via Account Number.
7. **Inspect Statements** $\rightarrow$ Navigates to Transactions $\rightarrow$ Exports CSV file.
8. **Logout** $\rightarrow$ Ends session cleanly.

---

## 56. Complete Admin Journey

1. **Admin Login** $\rightarrow$ Enters admin email (`admin@example.com` or `admin`) and password $\rightarrow$ Verifies Admin OTP.
2. **Inspect System** $\rightarrow$ Views total deposits and platform KPI metrics on Admin Dashboard.
3. **Audit Ledger** $\rightarrow$ Reviews global customer transfers and deposits.
4. **Moderate Account** $\rightarrow$ Freezes suspicious customer account from Accounts tab.
5. **Review Appeals** $\rightarrow$ Inspects customer appeal in Requests tab $\rightarrow$ Approves reactivation.
6. **Logout** $\rightarrow$ Terminates administrative session.

---

## 57. Important Functions and Their Responsibilities

### `backend/account.py`
- `deposit_money(username, amount)`: Atomically increments active balance and writes deposit record.
- `withdraw_money(username, amount)`: Atomically decrements balance if funds are sufficient.
- `current_balance(username)`: Retrieves real-time balance float from MongoDB.

### `backend/transfer.py`
- `transfer_money(sender_acc, receiver_acc, amount, note)`: Executes atomic two-legged fund transfer with compensating rollback.

### `backend/users.py`
- `register_user(...)`: Creates customer document with bcrypt-hashed credentials.
- `login_with_status(username, password)`: Verifies credentials, checks lockout, and identifies active vs disabled accounts.

### `backend/security_pin.py`
- `verify_transaction_pin_hash(pin, stored_hash)`: Dual-hash verification supporting bcrypt and SHA256 PIN hashes.
- `set_transaction_pin(username, pin)`: Hashes and updates a customer's 6-digit PIN.

### `backend/email_otp.py`
- `generate_and_send_otp(email, expires_in_seconds)`: Dispatches 6-digit OTP via Gmail SMTP.
- `validate_otp(email, code)`: Verifies submitted code against in-memory single-use hash.

---

## 58. Important Classes and Their Responsibilities

- **`PasswordPolicyError(ValueError)`** (`backend/security.py`): Raised when a password violates length, case, digit, or special character requirements.
- **`MoneyError(ValueError)`** (`utils/money.py`): Raised when invalid, negative, or non-finite monetary values are processed.

---

## 59. Important Modules and Their Responsibilities

- **`backend.database`**: Central PyMongo database connection and index management.
- **`backend.alerts`**: System notification creation and automated administrative alert dispatch.
- **`config.settings`**: Centralized environment variable ingestion and validation.
- **`frontend.styles`**: Custom CSS design system injection.

---

## 60. Dependencies / Libraries

- **`streamlit`**: Web UI framework and reactive runtime.
- **`pymongo`**: Official MongoDB driver for Python.
- **`bcrypt`**: Cryptographic password and security answer hashing.
- **`pandas`**: Data analysis, filtering, and CSV statement exports.
- **`python-dotenv`**: Environment variable loading from `.env`.
- **`pytest`**: Automated unit and integration testing framework.

---

## 61. `requirements.txt` Explanation

From `requirements-phase1.txt`:
```text
streamlit          # Interactive web UI and application server
pandas             # Data manipulation and CSV export generation
pymongo>=4.10,<5   # MongoDB database driver
pytest             # Test runner and assertions
python-dotenv>=1.0 # Reads environment variables from .env
```

---

## 62. Running the Project

Ensure your virtual environment is active and MongoDB is running:

```powershell
# 1. Activate virtual environment
.\env1\Scripts\Activate.ps1

# 2. Launch Streamlit application
streamlit run app.py
```

The application will start and display your local URL:
```text
Local URL: http://localhost:8501
Network URL: http://192.168.X.X:8501
```

---

## 63. How to Test Each Feature

Execute the automated test suite:
```powershell
.\env1\Scripts\pytest.exe tests/
```

Manual Testing Checklist:
1. **Registration**: Register a new user with a valid Gmail address $\rightarrow$ Verify OTP arrives and activates account.
2. **Login & 2FA**: Log in with created credentials $\rightarrow$ Confirm 2FA OTP arrives and unlocks Dashboard.
3. **Transaction PIN**: Go to Profile $\rightarrow$ Set a 6-digit PIN $\rightarrow$ Verify confirmation.
4. **Deposit**: Deposit ₹5,000 using your PIN $\rightarrow$ Confirm balance increases to ₹5,000.
5. **Transfer**: Transfer ₹1,000 to another Account Number $\rightarrow$ Confirm your balance becomes ₹4,000 and receiver's balance increases.
6. **Withdraw**: Withdraw ₹500 $\rightarrow$ Confirm balance becomes ₹3,500.
7. **Statement**: Go to Transactions $\rightarrow$ Click "Export Statement" $\rightarrow$ Verify CSV file downloads.
8. **Admin Operations**: Log in as admin $\rightarrow$ Freeze account $\rightarrow$ Attempt login as that user to verify redirect to Account Review.

---

## 64. Common Errors

### 1. `pymongo.errors.ServerSelectionTimeoutError`
- **Cause**: MongoDB service is not running locally.
- **Solution**: Run `Start-Service MongoDB` in administrative PowerShell.

### 2. `smtplib.SMTPAuthenticationError`
- **Cause**: Invalid Gmail username or regular password used instead of Gmail App Password.
- **Solution**: Generate a 16-character App Password at [Google Account Security](https://myaccount.google.com/apppasswords) and update `MADHU_BANK_SMTP_PASSWORD` in `.env`.

### 3. `PasswordPolicyError`
- **Cause**: Password does not satisfy complexity requirements.
- **Solution**: Ensure password has at least 8 characters, one uppercase, one lowercase, one number, and one special character (e.g. `Madhu@2026`).

---

## 65. Troubleshooting

| Symptom | Diagnostic Step | Resolution |
| :--- | :--- | :--- |
| OTP emails not arriving | Inspect `.env` credentials | Ensure port is `587`, TLS is enabled, and App Password has no spaces. |
| "Incorrect transaction PIN" | Check stored hash | Reset transaction PIN in Profile via Email OTP. |
| Streamlit port collision | Port 8501 already in use | Run `streamlit run app.py --server.port 8502`. |
| Account locked out | 5 failed login attempts | Wait 15 minutes or unfreeze via Admin Console. |

---

## 66. Development Workflow

1. Create a git branch or backup before modifying code.
2. Make targeted backend changes in `backend/` or UI adjustments in `app.py`.
3. Run the automated test suite to ensure no regressions:
   ```powershell
   .\env1\Scripts\pytest.exe tests/
   ```
4. Test interactive UI workflows in the browser on `http://localhost:8501`.

---

## 67. How a Beginner Can Understand the Code

Follow this 5-step learning sequence:
1. **Start with `config/settings.py`**: Understand how settings and `.env` variables are loaded.
2. **Read `backend/database.py`**: Understand MongoDB connections and collection definitions.
3. **Read `backend/security.py` & `backend/security_pin.py`**: Learn how passwords and PINs are hashed.
4. **Read `backend/account.py` & `backend/transfer.py`**: Learn how atomic ledger updates work.
5. **Inspect `app.py`**: See how Streamlit binds UI inputs to backend functions.

---

## 68. How to Modify Existing Features

Example: Modifying the Brute-Force Lockout Duration:
1. Open `backend/users.py`.
2. Locate line 16: `LOCKOUT_MINUTES = 15`.
3. Change value (e.g., `LOCKOUT_MINUTES = 30`).
4. Save file. Streamlit auto-reloads the changes immediately.

---

## 69. How to Add a New Feature

Example: Adding a "Savings Goal Tracker":
1. Add a new collection helper in `backend/database.py`: `goals_collection = db["goals"]`.
2. Create service methods in a new file `backend/goals.py` (`create_goal`, `get_goals`).
3. Add a page function in `app.py`: `def goals_page(): ...`.
4. Register `goals` in the navigation dictionary in `app.py` (`banking_sidebar()`).

---

## 70. How to Add a New Database Collection

1. Open `backend/database.py`.
2. Define the collection reference:
   ```python
   fixed_deposits_collection = db["fixed_deposits"]
   ```
3. Add appropriate indexes using `_ensure_index`:
   ```python
   _ensure_index(
       fixed_deposits_collection,
       [("username", 1), ("created_at", -1)],
       name="ix_fd_user_created"
   )
   ```
4. Export the collection for backend service use.

---

## 71. How to Add a New Transaction Type

1. Open `backend/account.py`.
2. Create a new transaction recording function (e.g., `record_interest_credit(username, amount)`).
3. Set `type: "Interest Credit"` and `direction: "In"`.
4. Update `transactions_page()` in `app.py` to add `"Interest"` to the category filter options.

---

## 72. How to Add a New Admin Feature

1. Add backend reporting query in `backend/admin.py`.
2. Create UI function in `app.py` (e.g., `def admin_audit_logs(): ...`).
3. Add `("Audit Logs", "admin_audit_logs", ":material/history:")` to `admin_nav` list in `admin_sidebar()`.
4. Add routing condition in `app.py` router block.

---

## 73. Future Improvements

### Short-Term Improvements
- Add PDF statement download alongside existing CSV export.
- Implement pagination for large transaction tables ($> 100$ records).

### Medium-Term Improvements
- Build Recurring Deposits (RD) and Fixed Deposits (FD) simulation engine.
- Implement interest calculation chron jobs for monthly interest credits.

### Long-Term Improvements
- Transition session management to Redis-backed distributed tokens.
- Add multi-currency exchange rate simulation.

---

## 74. Future Security Improvements

- Move OTP storage from local memory (`OTP_STORE`) to a Redis cache with automatic TTL.
- Implement WebAuthn / FIDO2 biometric authentication support.
- Encrypt sensitive database fields at rest using AES-256 (envelope encryption).

---

## 75. Future Database Improvements

- Deploy a 3-node MongoDB Replica Set to utilize native multi-document ACID transactions (`session.start_transaction()`).
- Add database automated backup cron scripts.

---

## 76. Future UI Improvements

- Enable dark mode theme toggle in customer settings.
- Add interactive Plotly financial spending charts by category.

---

## 77. Future Deployment Improvements

- Dockerize application with `docker-compose.yml` (Streamlit + MongoDB containers).
- Configure Nginx reverse proxy with SSL certificate management (Let's Encrypt).

---

## 78. Possible Production Features

*(Features required if transitioning this simulation into a regulated commercial bank)*:
- KYC / AML identity document verification workflows (PAN, Aadhaar, Passport).
- Real payment gateway integration (UPI, IMPS, NEFT, RTGS, SWIFT).
- Core Banking System (CBS) ISO-8583 and ISO-20022 messaging compliance.
- Hardware Security Module (HSM) key management for PIN translation.

---

## 79. Known Limitations

- **Educational Simulation**: Not connected to the real Reserve Bank of India (RBI) or live interbank settlement networks.
- **In-Memory OTP Store**: Restarting the Python process clears active OTPs; users must request a new OTP if the server restarts mid-session.
- **Standalone MongoDB**: Transfer consistency relies on compensating rollbacks rather than distributed 2-phase commit transactions.

---

## 80. Conclusion

**Madhu Bank** demonstrates how modern web frameworks, NoSQL databases, and robust security principles can combine to produce an intuitive, secure, and educational banking platform. By studying its architecture, source code, and transactional workflows, developers and students can master the core foundations of financial software engineering.

=======
# madhu-bank
>>>>>>> 4fe6bd59b105810db07d0997a4d726ab90688469
