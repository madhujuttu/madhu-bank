# Madhu Bank Audit (Corrected)

## Project overview

This project is a Python-based banking simulation built with Streamlit and MongoDB.
The current repository contains the actual backend modules under the `backend/`
folder, as well as UI code in `app.py` and styling in `frontend/`.

The application follows this flow:

    Streamlit UI -> backend service modules -> MongoDB

This is a layered architecture rather than a single monolithic app, even though
`app.py` still contains a significant amount of UI orchestration and routing.

## Confirmed architecture

### Presentation layer
- `app.py` — main app entry, session state, page routing, and dashboard logic
- `frontend/styles.py` — CSS theme and visual styling
- `frontend/login.py` — login page module (legacy or partial implementation)
- `frontend/register.py` — registration screen helper
- `frontend/deposit.py` — planned deposit UI module
- `frontend/users.py` — user/account UI module placeholder

### Application layer
- `backend/users.py` — registration, login, and user lookup
- `backend/account.py` — deposit/withdrawal and balance operations
- `backend/transfer.py` — transfers, validation, and rollback logic
- `backend/admin.py` — admin login and management operations
- `backend/email_otp.py` — OTP generation, storage, expiry, and SMTP sending
- `backend/password_reset.py` — password reset flow
- `backend/security.py` — password hashing and validation policy
- `backend/security_pin.py` — transaction PIN management
- `backend/account_review_requests.py` — reactivation review workflow
- `backend/transactions.py` — transaction history retrieval

### Data layer
- `backend/database.py` — MongoDB connection, collections, and indexes

### Config and utilities
- `config/settings.py` — environment configuration and SMTP settings
- `security/session.py` — session token helpers
- `security/password.py` — alternate password helper implementation
- `utils/validation.py` — shared validation helpers
- `utils/money.py` — monetary parsing and formatting helpers

## Features confirmed in the current codebase

- User registration
- Username/password login
- Failed-login tracking and lockout logic
- OTP-based email verification flow
- Password reset using stored recovery data
- Deposit and withdrawal processing
- Internal balance transfer logic
- Transaction history storage and retrieval
- Admin account management
- Disabled-account review requests
- Account-number generation and uniqueness checks
- MongoDB indexing and setup
- Streamlit-based banking UI with custom styling

## Findings

### CRITICAL
* Hardcoded admin credentials are present in `backend/admin.py` (`admin` / `admin123`).
  This is not secure for production and is only acceptable in a demo project.
* SMTP configuration is required for OTP delivery and is environment-dependent.
  The app will not send OTPs correctly if Gmail credentials are missing or invalid.

### HIGH
* The app relies on MongoDB being available locally (`mongodb://localhost:27017/`).
  This is acceptable for a local demo but not for deployment.
* Some features are split across multiple modules, while `app.py` still contains a large amount of UI and logic.
  This creates maintenance overhead and makes the design less modular than ideal.
* Security-sensitive flows are partly implemented through app/session state rather than a dedicated server session framework.
  This is fine for a demo, but not a production pattern.

### MEDIUM
* OTPs are stored in memory and are not persisted across app restarts.
  This is acceptable for a demo, but not for a production-grade banking system.
* There are multiple overlapping security helper modules (`backend/security.py`, `security/password.py`, `utils/validation.py`).
  This creates duplication and potential inconsistency.
* Some frontend modules are partial or empty (`frontend/deposit.py`, `frontend/users.py`, `frontend/register.py`), suggesting the project is still in an evolving state.
* The app mixes UI concerns, session management, and business logic in a single file more than a clean layered design would.

### LOW
* Some migration-era files appear stale or incomplete (`migrations/001_migrate_accounts.py` references older modules).
* The codebase contains both legacy and modern patterns, which suggests a transition from an earlier prototype.
* The project is educational and simulation-oriented, not a compliant real-world banking system.

## What is already implemented well

- Clear separation between DB access and business logic in most backend modules
- Use of bcrypt for password hashing
- Conditional balance updates and compensating rollback in transfer logic
- Transaction logging for deposit, withdrawal, and transfer flows
- Index creation for MongoDB collections
- Account-number enforcement and uniqueness checks
- Stronger password validation than a minimal demo would normally use

## What is not production-ready

- No real banking compliance or audit framework
- No proper API security or secure token/session management
- No production-grade deployment configuration
- No real payment network integration
- No strong separation of concerns between UI and business logic
- No user-level permission system beyond simple role checks in the interface

## Deployment status

This project is best described as an educational banking simulation with a working local architecture and a relatively complete demo flow. It is not production-ready and should not be treated as a real financial application.

## Final assessment

The repository is a functional prototype with a usable Flow:

    Streamlit UI -> backend service modules -> MongoDB

It is not missing the backend modules. The main issue is not absence of implementation, but inconsistency and incompleteness across some modules, along with design choices that are acceptable for a demo but not for a production-grade banking product.
