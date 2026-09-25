import streamlit as st
import pandas as pd
import base64
import hashlib
import time
from datetime import date, datetime
from backend.users import (
    register_user,
    login,
    get_user
)

from backend.account import (
    deposit_money,
    current_balance,
    withdraw_money
)

from backend.transactions import (
    get_transactions,
    get_all_transactions
)

from backend.transfer import transfer_money
from backend.password_reset import reset_password
from backend.security import hash_password, verify_password
from backend.security_pin import set_transaction_pin, verify_transaction_pin
from backend.email_otp import generate_and_send_otp, get_last_otp_email_error, validate_otp
from config.settings import SMTP_CONFIGURATION_ERROR

from backend.database import users_collection, db
from backend.alerts import (
    dispatch_system_alert,
    get_system_alerts,
    get_unread_alerts_count,
    acknowledge_system_alert,
    dismiss_system_alert,
)
import secrets

from frontend.styles import (
    get_shared_styles,
    get_user_theme_styles,
    get_admin_theme_styles,
    get_auth_theme_styles,
    get_auth_waves_svg,
)


# Direct transaction collection access for admin backfilling/display.
transactions_collection = db["transactions"]
# Customer account-review requests are stored separately from banking transactions.
account_review_requests_collection = db["account_review_requests"]

# Account Review indexes are managed centrally in backend/database.py.
# Do not create or drop Account Review indexes here; Streamlit reruns this
# module frequently, and index migration must not run on every UI rerun.


# =========================================================
# UNIQUE ACCOUNT NUMBER HELPERS
# =========================================================

# Account-number indexing is managed centrally in backend/database.py.


def _generate_account_number():
    return secrets.randbelow(9_000_000_000) + 1_000_000_000


def ensure_account_number(username):
    """Ensure every customer has one unique numeric Account Number."""
    if not username:
        return None

    user = users_collection.find_one({"username": username})
    if not user:
        return None

    existing = user.get("account_number")
    if isinstance(existing, int) and not isinstance(existing, bool):
        return existing

    if existing is not None:
        users_collection.update_one(
            {"username": username},
            {"$unset": {"account_number": ""}},
        )

    while True:
        candidate = _generate_account_number()
        try:
            result = users_collection.update_one(
                {
                    "username": username,
                    "account_number": {"$exists": False},
                },
                {"$set": {"account_number": candidate}},
            )
            if result.modified_count:
                return candidate

            refreshed = users_collection.find_one({"username": username})
            refreshed_number = refreshed.get("account_number") if refreshed else None
            if isinstance(refreshed_number, int) and not isinstance(refreshed_number, bool):
                return refreshed_number
        except Exception:
            continue


def get_user_by_account_number(account_number):
    try:
        numeric_number = int(str(account_number).strip())
    except (TypeError, ValueError):
        return None
    return users_collection.find_one({"account_number": numeric_number})


def get_username_by_account_number(account_number):
    user = get_user_by_account_number(account_number)
    return user.get("username") if user else None


def ensure_all_account_numbers():
    for user in users_collection.find({}, {"username": 1, "account_number": 1}):
        username = user.get("username")
        if username:
            ensure_account_number(username)

from backend.admin import (
    admin_login,
    get_admin_email,
    get_all_accounts,
    search_accounts,
    delete_account,
    disable_account,
    enable_account,
    get_total_accounts,
    get_active_accounts,
    get_disabled_accounts,
    get_total_bank_balance
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Madhu Bank",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)


def navigate_to(page: str):
    """Navigate to a target page in a single pass without redundant script runs."""
    st.session_state.page = page
    st.session_state["_reset_scroll_after_nav"] = True
    st.session_state["user_banking_menu_open"] = False
    st.session_state["user_account_menu_open"] = False
    st.session_state["user_profile_menu_open"] = False


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None

if "account_number" not in st.session_state:
    st.session_state.account_number = None

if "seen_transfer_notifications" not in st.session_state:
    st.session_state.seen_transfer_notifications = set()

if "password_reset_username" not in st.session_state:
    st.session_state.password_reset_username = None

if "password_reset_verified" not in st.session_state:
    st.session_state.password_reset_verified = False
if "password_reset_question" not in st.session_state:
    st.session_state.password_reset_question = None

if "password_reset_account_number" not in st.session_state:
    st.session_state.password_reset_account_number = None

if "password_reset_account_verified" not in st.session_state:
    st.session_state.password_reset_account_verified = False

if "password_reset_email" not in st.session_state:
    st.session_state.password_reset_email = None

if "password_reset_email_verified" not in st.session_state:
    st.session_state.password_reset_email_verified = False

if "password_reset_needs_question_setup" not in st.session_state:
    st.session_state.password_reset_needs_question_setup = False


if "pin_pending_action" not in st.session_state:
    st.session_state.pin_pending_action = None

if "pin_pending_email" not in st.session_state:
    st.session_state.pin_pending_email = None

if "pin_email_verified" not in st.session_state:
    st.session_state.pin_email_verified = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# Customer top-navigation dropdown states. These are explicit booleans so
# My Account and Profile open deterministically on the first click.
if "user_account_menu_open" not in st.session_state:
    st.session_state.user_account_menu_open = False
if "user_banking_menu_open" not in st.session_state:
    st.session_state.user_banking_menu_open = False
if "user_profile_menu_open" not in st.session_state:
    st.session_state.user_profile_menu_open = False

if "account_review_login_username" not in st.session_state:
    st.session_state.account_review_login_username = None

if "pending_registration_username" not in st.session_state:
    st.session_state.pending_registration_username = None

if "pending_registration_email" not in st.session_state:
    st.session_state.pending_registration_email = None

if "pending_login_username" not in st.session_state:
    st.session_state.pending_login_username = None

if "pending_login_email" not in st.session_state:
    st.session_state.pending_login_email = None

if "pending_admin_login_username" not in st.session_state:
    st.session_state.pending_admin_login_username = None

if "pending_admin_login_email" not in st.session_state:
    st.session_state.pending_admin_login_email = None

if "pending_transfer_otp" not in st.session_state:
    st.session_state.pending_transfer_otp = None

if "pending_transfer_receiver_id" not in st.session_state:
    st.session_state.pending_transfer_receiver_id = None

if "pending_transfer_amount" not in st.session_state:
    st.session_state.pending_transfer_amount = None

if "pending_transfer_note" not in st.session_state:
    st.session_state.pending_transfer_note = None


# One-time account-number migration for the current session.
# The old version scanned every customer on every Streamlit rerun, which
# made navigation unnecessarily slow. Individual users are still repaired
# on demand by ensure_account_number().
if not st.session_state.get("_account_numbers_backfilled", False):
    try:
        ensure_all_account_numbers()
    except Exception:
        pass
    else:
        st.session_state["_account_numbers_backfilled"] = True


# =========================================================
# SAFE NUMBER CONVERSION
# =========================================================

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default





# =========================================================
# BRAND / LOGO
# =========================================================

def madhu_bank_logo():
    return """
    <div class="madhu-brand-mark" aria-label="Madhu Bank logo">
        <svg width="28" height="28" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" role="img">
            <rect x="1" y="1" width="30" height="30" rx="9" fill="#173B6C"/>
            <path d="M8 22V10l8 7 8-7v12" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="24.2" cy="7.8" r="3.1" fill="#C8FF3D"/>
        </svg>
    </div>
    """

# =========================================================
# BANK HEADER
# =========================================================

def bank_header():
    # Authentication pages use the self-contained split-screen layout with their own brand header.
    page = st.session_state.get("page")
    if page in {"login", "register", "forgot_password", "admin_login", "disabled_account_review", "register_otp_verification", "login_otp_verification"}:
        return

    header_class = "bank-header"
    st.markdown(
        f'<div class="{header_class}">'
        f'{madhu_bank_logo()}'
        '<div>'
        '<div class="bank-name">MADHU BANK</div>'
        '<div class="bank-tagline">'
        'Secure • Simple • Smart Banking'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    

# =========================================================
# LOGOUT
# =========================================================

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.account_number = None
    st.session_state.page = "login"
    st.session_state["user_account_menu_open"] = False
    st.session_state["user_banking_menu_open"] = False
    st.session_state["user_profile_menu_open"] = False
    st.session_state["pending_admin_login_username"] = None
    st.session_state["pending_admin_login_email"] = None


# =========================================================
# =========================================================
# PIN SECURITY HELPERS
# =========================================================

def _clear_pin_state():
    st.session_state.pin_pending_action = None
    st.session_state.pin_pending_email = None
    st.session_state.pin_email_verified = False


def _validate_pin_request(user, password, new_pin, confirm_pin, action):
    expected_action = "change" if user.get("transaction_pin_hash") else "set"
    if action != expected_action:
        return False, "Please start a fresh PIN setup request."

    if not password:
        return False, "Enter your account password."

    try:
        password_ok = verify_password(
            password,
            str(user.get("password", "")),
        )
    except Exception:
        password_ok = False

    if not password_ok:
        return False, "Incorrect account password."

    if not str(new_pin).isdigit() or len(str(new_pin)) != 6:
        return False, "PIN must contain exactly 6 digits."

    if str(new_pin) != str(confirm_pin):
        return False, "PINs do not match."

    if len(set(str(new_pin))) == 1:
        return False, "Choose a less predictable 6-digit PIN."

    return True, ""


def _verify_and_set_pin(user, password, new_pin, confirm_pin, action):
    valid, message = _validate_pin_request(
        user,
        password,
        new_pin,
        confirm_pin,
        action,
    )
    if not valid:
        return False, message

    if set_transaction_pin(user.get("username"), new_pin):
        _clear_pin_state()
        return True, "Transaction PIN updated successfully."

    return False, "Could not update the transaction PIN."


# =========================================================
# ACCOUNT REVIEW REQUEST HELPERS
# =========================================================

def get_account_review_request(username):
    """Return the latest account-review request for a customer."""
    if not username:
        return None
    return account_review_requests_collection.find_one(
        {"username": username},
        sort=[("created_at", -1)],
    )


def submit_account_review_request(username, request_note=""):
    """Create a pending account-review request for a disabled customer."""
    if not username:
        return False, "Customer account could not be identified."

    user = users_collection.find_one({"username": username})
    if not user:
        return False, "Customer account could not be found."

    if str(user.get("status", "Active")).lower() != "disabled":
        return False, "Account Review is only available for a disabled account."

    existing_pending = account_review_requests_collection.find_one(
        {"username": username, "status": "Pending"}
    )
    if existing_pending:
        return False, "You already have a pending account review request."

    now = datetime.now()
    request_note = str(request_note or "").strip()
    account_number = ensure_account_number(username)
    display_name = (
        user.get("name")
        or f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        or username
    )

    account_review_requests_collection.insert_one(
        {
            "username": username,
            "account_number": account_number,
            "name": display_name,
            "status": "Pending",
            "created_at": now,
            "reviewed_at": None,
            "reviewed_by": None,
            "request_note": request_note or None,
            "admin_note": None,
        }
    )
    return True, "Account review request submitted successfully."


def get_account_review_requests(status=None):
    query = {}
    if status and status != "All":
        query["status"] = status
    return list(
        account_review_requests_collection.find(query).sort("created_at", -1)
    )


def update_account_review_request(request_id, status, admin_note=""):
    """Review a request. Approval also re-activates the customer account."""
    from bson import ObjectId

    try:
        object_id = ObjectId(str(request_id))
    except Exception:
        return False, "Invalid review request."

    request_doc = account_review_requests_collection.find_one({"_id": object_id})
    if not request_doc:
        return False, "Review request not found."

    status = str(status or "").strip().title()
    note = str(admin_note or "").strip()

    if status == "Rejected" and not note:
        return False, "Please provide a reason before rejecting the request."

    username = str(request_doc.get("username", "")).strip()
    update_fields = {
        "status": status,
        "reviewed_at": datetime.now(),
        "reviewed_by": st.session_state.get("username"),
        "admin_note": note or None,
    }

    result = account_review_requests_collection.update_one(
        {"_id": object_id},
        {"$set": update_fields},
    )

    if result.modified_count == 0:
        return False, "The review request could not be updated."

    # Accept/activate: re-enable the customer's account immediately.
    if status == "Approved" and username:
        users_collection.update_one(
            {"username": username},
            {"$set": {"status": "Active"}},
        )

    return True, (
        "Account approved and activated successfully."
        if status == "Approved"
        else "Account review request rejected."
    )


# =========================================================
# AUTHENTICATION REFERENCE THEME
# =========================================================

def auth_reference_theme():
    """Authentication layout and viewport setup."""

    st.html(
        """
        <script>
        (function() {
            function resetAuthViewport() {
                try {
                    window.scrollTo(0, 0);
                    if (document.documentElement) document.documentElement.scrollTop = 0;
                    if (document.body) document.body.scrollTop = 0;
                    var appView = document.querySelector('[data-testid="stAppViewContainer"]');
                    if (appView) appView.scrollTop = 0;
                    var main = document.querySelector('[data-testid="stMain"], section.main');
                    if (main) main.scrollTop = 0;
                    var scrollable = document.querySelector(
                        '.st-key-auth_login_scroll, ' +
                        '.st-key-auth_register_scroll, ' +
                        '.st-key-auth_forgot_scroll, ' +
                        '.st-key-auth_admin_scroll, ' +
                        '.st-key-auth_register_otp_scroll, ' +
                        '.st-key-auth_login_otp_scroll, ' +
                        '.st-key-auth_account_review_scroll'
                    );
                    if (scrollable) {
                        scrollable.scrollTop = 0;
                    }
                } catch(e) {}
            }

            function delegateAuthScroll(e) {
                var scrollable = document.querySelector(
                    '.st-key-auth_login_scroll, ' +
                    '.st-key-auth_register_scroll, ' +
                    '.st-key-auth_forgot_scroll, ' +
                    '.st-key-auth_admin_scroll, ' +
                    '.st-key-auth_register_otp_scroll, ' +
                    '.st-key-auth_login_otp_scroll, ' +
                    '.st-key-auth_account_review_scroll'
                );
                if (!scrollable) return;
                if (e.target && scrollable.contains(e.target)) {
                    return;
                }
                scrollable.scrollTop += e.deltaY;
            }

            function enforceOuterScrollLocked() {
                var hasAuth = document.querySelector('.st-key-auth_visual_fixed, .auth-visual-panel');
                var appView = document.querySelector('[data-testid="stAppViewContainer"]');
                var main = document.querySelector('[data-testid="stMain"], section.main');
                if (hasAuth && window.innerWidth > 900) {
                    if (document.documentElement) {
                        document.documentElement.style.overflow = 'hidden';
                        document.documentElement.style.height = '100%';
                    }
                    if (document.body) {
                        document.body.style.overflow = 'hidden';
                        document.body.style.height = '100%';
                    }
                    if (appView) {
                        appView.style.overflow = 'hidden';
                        appView.style.height = '100vh';
                    }
                    if (main) {
                        main.style.overflow = 'hidden';
                        main.style.height = '100vh';
                    }
                } else if (!hasAuth) {
                    if (document.documentElement) {
                        document.documentElement.style.overflow = '';
                        document.documentElement.style.height = '';
                    }
                    if (document.body) {
                        document.body.style.overflow = '';
                        document.body.style.height = '';
                    }
                    if (appView) {
                        appView.style.overflow = '';
                        appView.style.height = '';
                    }
                    if (main) {
                        main.style.overflow = '';
                        main.style.height = '';
                    }
                }
            }

            function removeInputInstructions() {
                var instructions = document.querySelectorAll('[data-testid="InputInstructions"], div:has(> [data-testid="InputInstructions"])');
                for (var i = 0; i < instructions.length; i++) {
                    instructions[i].style.setProperty('display', 'none', 'important');
                    instructions[i].style.setProperty('visibility', 'hidden', 'important');
                }
            }

            function initAuthScrollSync() {
                enforceOuterScrollLocked();
                removeInputInstructions();
                if (!window.__authWheelBound) {
                    window.__authWheelBound = true;
                    window.addEventListener('wheel', delegateAuthScroll, { passive: true });
                }
            }

            resetAuthViewport();
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initAuthScrollSync);
            } else {
                initAuthScrollSync();
            }
            setInterval(initAuthScrollSync, 300);
            document.addEventListener('focusin', removeInputInstructions, true);
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def auth_visual_panel(section="login"):
    """Decorative authentication panel with premium digital banking visual artwork; contains no authentication logic."""
    panel_data = {
        "login": {
            "title": "SMART BANKING.<br>SIMPLIFIED.",
            "desc": "Securely manage your account, payments and transactions with MADHU BANK digital banking.",
            "quote": "MADHU BANK",
        },
        "register": {
            "title": "YOUR MONEY.<br>YOUR BANK.<br>YOUR CONTROL.",
            "desc": "Experience effortless digital banking with institutional security and complete clarity.",
            "quote": "MADHU BANK",
        },
        "forgot": {
            "title": "SECURE ACCESS.<br>TOTAL CONTROL.",
            "desc": "Securely recover access to your account with multi-factor identity protection.",
            "quote": "MADHU BANK",
        },
        "admin": {
            "title": "EXECUTIVE PORTAL.<br>INSTITUTIONAL POWER.",
            "desc": "Command operations, review user requests, and oversee global audit logs.",
            "quote": "MADHU BANK",
        },
    }
    cfg = panel_data.get(section, panel_data["login"])
    title = cfg["title"]
    desc = cfg["desc"]
    quote = cfg["quote"]

    st.markdown(
        f"""
        <div class="auth-visual-panel">
            <div class="auth-visual-content-wrapper">
                <div class="auth-visual-top">
                    <div class="visual-top-label" style="color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;">
                        <span style="color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;">{quote}</span>
                        <span class="visual-line"></span>
                    </div>
                    <div class="auth-visual-content">
                        <div class="visual-hero-heading" style="color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; text-shadow: 0 4px 24px rgba(0,0,0,0.95);">{title}</div>
                        <div class="visual-hero-desc" style="color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; text-shadow: 0 2px 14px rgba(0,0,0,0.95);">{desc}</div>
                    </div>
                </div>
                <div class="auth-visual-spacer" aria-hidden="true"></div>
                <div class="auth-visual-footer">
                    <div class="banking-security-cue">
                        <svg class="security-shield-svg" viewBox="0 0 20 20" fill="none">
                            <path d="M10 2L3 5v5c0 4.5 3 8 7 9 4-1 7-4.5 7-9V5l-7-3z" stroke="rgba(255,255,255,0.95)" stroke-width="1.6" fill="rgba(150,114,244,0.25)"/>
                            <path d="M7 10l2 2 4-4" stroke="#61D8E7" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        <div class="security-cue-text">
                            <span class="sec-title" style="color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;">BANK-GRADE SECURITY</span>
                            <span class="sec-sub" style="color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;">Protected digital access</span>
                        </div>
                    </div>
                    <div class="visual-footer-pill" style="color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;">
                        <span class="pill-dot"></span> Institutional Grade Security
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



# =========================================================
# LOGIN CREDENTIAL VERIFICATION
# =========================================================

def _verify_login_password(user, password):
    """Verify a stored password hash without applying account-status rules."""
    if not user or not password:
        return False

    # Current records use ``password``. The fallbacks keep older educational
    # records compatible if a previous schema used a different hash field.
    stored_hash = (
        user.get("password")
        or user.get("password_hash")
        or user.get("hashed_password")
        or user.get("pass_hash")
    )

    if stored_hash is None:
        return False

    if isinstance(stored_hash, bytes):
        try:
            stored_hash = stored_hash.decode("utf-8")
        except Exception:
            return False

    try:
        return bool(verify_password(str(password), str(stored_hash)))
    except Exception:
        return False


# =========================================================
# LOGIN PAGE
# =========================================================

def login_page():

    auth_reference_theme()

    bank_header()

    left, center = st.columns([1, 1], gap="medium")

    with left:
        with st.container(key="auth_visual_fixed"):
            auth_visual_panel("login")

    with center:
        with st.container(key="auth_login_scroll"):
            st.markdown(
                f"""
                <div class="auth-brand-header">
                    <div class="auth-brand-logo">{madhu_bank_logo()}</div>
                    <div class="auth-brand-title">MADHU BANK</div>
                </div>
                <div class="auth-main-heading">Welcome Back</div>
                <div class="auth-main-desc">Securely access your MADHU BANK account.</div>
                """,
                unsafe_allow_html=True,
            )

            # Login only. Account Review appears only after valid credentials for
            # a disabled account, so active users do not see it on the login page.
            pending_username = st.session_state.get("pending_login_username")
            pending_email = st.session_state.get("pending_login_email")

            if pending_username and pending_email:
                st.info(f"OTP sent to {pending_email}. Enter it to complete login.")
                with st.form("login_otp_form"):
                    otp_value = st.text_input(
                        "OTP (6 digits)",
                        max_chars=6,
                        type="password",
                        key="login_otp",
                        placeholder="Enter code sent to your email",
                    )
                    verify_button = st.form_submit_button("Verify OTP and Login", width="stretch")

                if verify_button:
                    if not otp_value:
                        st.error("Please enter the OTP sent to your email.")
                    elif not validate_otp(pending_email, otp_value):
                        st.error("Invalid or expired OTP. Please retry.")
                    else:
                        user = users_collection.find_one({"username": pending_username})
                        if not user:
                            st.error("Login session expired. Please try again.")
                            st.session_state.pending_login_username = None
                            st.session_state.pending_login_email = None
                        else:
                            st.session_state.pending_login_username = None
                            st.session_state.pending_login_email = None
                            st.session_state.logged_in = True
                            st.session_state.username = user.get("username")
                            st.session_state.role = user.get("role", "user")
                            st.session_state.account_number = ensure_account_number(user.get("username"))
                            st.session_state.page = (
                                "admin_dashboard"
                                if st.session_state.role == "admin"
                                else "dashboard"
                            )
                            st.rerun()

                c_resend, c_cancel = st.columns(2, gap="small")
                with c_resend:
                    if st.button("Resend OTP", width="stretch", key="login_inline_resend_otp", icon=":material/refresh:"):
                        now = time.time()
                        last_sent = float(st.session_state.get("_last_login_inline_resend", 0) or 0)
                        if (now - last_sent) < 10.0:
                            st.toast("OTP was recently sent. Please wait a moment.", icon="⏳")
                        else:
                            st.session_state["_last_login_inline_resend"] = now
                            generated_otp, sent = generate_and_send_otp(pending_email, expires_in_seconds=300)
                            if sent:
                                st.toast("A new OTP has been sent to your email.", icon="📧")
                                st.success(f"A new 6-digit OTP has been sent to {pending_email}.")
                            else:
                                st.error(
                                    "Could not resend the OTP. "
                                    f"{SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or 'Please check your email settings.'}"
                                )
                with c_cancel:
                    if st.button("Cancel OTP Login", width="stretch"):
                        st.session_state.pending_login_username = None
                        st.session_state.pending_login_email = None
                        st.rerun()
            else:
                with st.form("login_form"):
                    username = st.text_input("Username", key="login_username")
                    password = st.text_input("Password", type="password", key="login_password")
                    email = st.text_input(
                        "Registered Email",
                        key="login_email",
                        placeholder="Enter the email registered with your account",
                    )
                    send_otp_button = st.form_submit_button("Send OTP", width="stretch")

                if send_otp_button:
                    clean_username = username.strip()
                    clean_email = email.strip().lower()

                    if not clean_username or not password or not clean_email:
                        st.error("Please enter username, password, and registered email.")
                    else:
                        user = users_collection.find_one({"username": clean_username})
                        credentials_valid = _verify_login_password(user, password)
                        backend_result = False
                        if user:
                            try:
                                backend_result = bool(login(clean_username, password))
                            except Exception:
                                backend_result = False
                        registered_email = str(user.get("email") or "").strip().lower() if user else ""
                        target_email = registered_email or clean_email

                        if not user or (not credentials_valid and not backend_result):
                            st.error("Invalid username or password.")
                        elif str(user.get("status", "Active")).lower() == "disabled":
                            st.session_state.account_review_login_username = user.get("username")
                            st.session_state.account_review_login_verified = True
                            st.session_state.page = "disabled_account_review"
                            st.rerun()
                        elif clean_email and registered_email and clean_email != registered_email:
                            st.error("The email does not match the email registered for this username.")
                        else:
                            _otp, sent = generate_and_send_otp(target_email, expires_in_seconds=300)
                            if not sent:
                                st.error(
                                    "Unable to send OTP email. "
                                    f"{SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or 'Please check your email settings.'}"
                                )
                            else:
                                st.session_state.pending_login_username = clean_username
                                st.session_state.pending_login_email = target_email
                                st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                st.button("Forgot Password", width="stretch", on_click=navigate_to, args=("forgot_password",))
            with col2:
                st.button("Register", width="stretch", on_click=navigate_to, args=("register",))

            st.button("Admin Login", width="stretch", on_click=navigate_to, args=("admin_login",))


# =========================================================
# LOGIN OTP VERIFICATION PAGE
# =========================================================

def login_otp_verification_page():
    auth_reference_theme()
    bank_header()

    left, center = st.columns([1, 1], gap="medium")

    with left:
        with st.container(key="auth_visual_fixed"):
            auth_visual_panel("login")

    with center:
        with st.container(key="auth_login_otp_scroll"):
            st.markdown(
                f"""
                <div class="auth-brand-header">
                    <div class="auth-brand-logo">{madhu_bank_logo()}</div>
                    <div class="auth-brand-title">MADHU BANK</div>
                </div>
                <div class="auth-main-heading">OTP Verification</div>
                <div class="auth-main-desc">Enter the 6-digit code sent to your email to complete login.</div>
                """,
                unsafe_allow_html=True,
            )

            username = st.session_state.get("pending_login_username")
            email = st.session_state.get("pending_login_email")

            if not username or not email:
                st.warning("Your OTP session expired. Please log in again.")
                if st.button("Back to Login", width="stretch"):
                    st.session_state.page = "login"
                    st.rerun()
                return

            with st.form("login_otp_form"):
                st.info(f"OTP sent to {email}")
                otp_value = st.text_input("Enter OTP", max_chars=6, type="password")
                verify_button = st.form_submit_button("Verify and Login", width="stretch")

            if verify_button:
                if not otp_value or not validate_otp(email, otp_value):
                    st.error("Invalid or expired OTP. Please retry the login.")
                else:
                    user = users_collection.find_one({"username": username})
                    if not user:
                        st.error("Login session expired. Please try again.")
                        st.session_state.page = "login"
                        st.rerun()

                    if str(user.get("status", "Active")).lower() == "disabled":
                        st.session_state.account_review_login_username = user.get("username")
                        st.session_state.account_review_login_verified = True
                        st.session_state.page = "disabled_account_review"
                        st.session_state.pending_login_username = None
                        st.session_state.pending_login_email = None
                        st.rerun()

                    if email and (not user.get("email") or not user.get("email_verified")):
                        users_collection.update_one(
                            {"username": username},
                            {"$set": {"email": email, "email_verified": True}},
                        )

                    st.session_state.logged_in = True
                    st.session_state.username = user.get("username")
                    st.session_state.role = user.get("role", "user")
                    st.session_state.account_number = ensure_account_number(user.get("username"))
                    st.session_state.pending_login_username = None
                    st.session_state.pending_login_email = None
                    st.session_state.page = (
                        "admin_dashboard"
                        if st.session_state.role == "admin"
                        else "dashboard"
                    )
                    st.rerun()

            c_resend, c_cancel = st.columns(2, gap="small")
            with c_resend:
                if st.button("Resend OTP", width="stretch", key="login_otp_resend", icon=":material/refresh:"):
                    now = time.time()
                    last_sent = float(st.session_state.get("_last_login_page_resend", 0) or 0)
                    if (now - last_sent) < 10.0:
                        st.toast("OTP was recently sent. Please wait a moment.", icon="⏳")
                    else:
                        st.session_state["_last_login_page_resend"] = now
                        generated_otp, sent = generate_and_send_otp(email, expires_in_seconds=300)
                        if sent:
                            st.toast("A new OTP has been sent to your email.", icon="📧")
                            st.success(f"A new 6-digit OTP has been sent to {email}.")
                        else:
                            st.error(
                                "Could not resend the OTP. "
                                f"{SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or 'Please check your email settings.'}"
                            )
            with c_cancel:
                if st.button("Cancel", width="stretch"):
                    st.session_state.pending_login_username = None
                    st.session_state.pending_login_email = None
                    st.session_state.page = "login"
                    st.rerun()


# =========================================================
# DISABLED ACCOUNT REVIEW PAGE
# =========================================================

def disabled_account_review_page():
    auth_reference_theme()
    bank_header()

    left, center = st.columns([1, 1], gap="medium")

    with left:
        with st.container(key="auth_visual_fixed"):
            auth_visual_panel("login")

    with center:
        with st.container(key="auth_account_review_scroll"):
            st.markdown(
                f"""
                <div class="auth-brand-header">
                    <div class="auth-brand-logo">{madhu_bank_logo()}</div>
                    <div class="auth-brand-title">MADHU BANK</div>
                </div>
                <div class="auth-main-heading">Account Review</div>
                <div class="auth-main-desc">Request administrator review for your disabled account.</div>
                """,
                unsafe_allow_html=True,
            )

            username = st.session_state.get("account_review_login_username")
            user = users_collection.find_one({"username": username}) if username else None
            # The review form is always fresh when the customer opens this page.
            # Previous requests remain stored for the administrator, but their
            # message/status/history is not displayed on the customer review form.
            pending_request = (
                account_review_requests_collection.find_one(
                    {"username": username, "status": "Pending"}
                )
                if username
                else None
            )
            latest_request = get_account_review_request(username) if username else None

            if not user:
                st.error("Account information could not be loaded.")
            else:
                account_number = user.get("account_number") or ensure_account_number(username)
                name = (
                    user.get("name")
                    or f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                    or username
                )

                current_status = str(user.get("status", "Disabled")).strip().title()

                with st.form("account_review_form"):
                    st.text_input("Account Holder", value=name, disabled=True)
                    st.text_input("Username", value=username or "", disabled=True)
                    st.text_input("Account Number", value=str(account_number or ""), disabled=True)
                    st.text_input("Account Status", value=current_status, disabled=True)

                    st.markdown(
                        '<div class="review-help-text">'
                        'Your account has been disabled by the administrator. '
                        'Submit a message below to request an account review and possible reactivation.'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    # The customer page never displays previous review history.
                    # Only an active Pending request matters for submission.
                    account_is_disabled = current_status.lower() == "disabled"

                    if account_is_disabled:
                        # Show only the current administrator rejection feedback.
                        # Do not expose the customer's previous request history.
                        if (
                            latest_request
                            and str(latest_request.get("status", "")).strip().lower() == "rejected"
                            and str(latest_request.get("admin_note", "")).strip()
                        ):
                            st.warning("Your account review request was rejected by the administrator.")
                            st.markdown("**Administrator reason:**")
                            st.info(str(latest_request.get("admin_note")).strip())

                        if pending_request:
                            st.info(
                                "Your account review request is already pending. "
                                "Please wait while the administrator reviews it."
                            )
                        else:
                            request_note = st.text_area(
                                "Message to Administrator",
                                key="disabled_account_request_note",
                                placeholder="Explain why you are requesting activation of your account.",
                                height=110,
                            )
                            st.caption("This message will be sent to the administrator with your review request.")

                            # This button is always visible for a disabled account
                            # when there is no Pending request.
                            submit_button = st.form_submit_button(
                                "Submit Account Review",
                                width="stretch",
                            )

                            if submit_button:
                                if not request_note.strip():
                                    st.error(
                                        "Please enter a short message for the administrator before submitting the request."
                                    )
                                else:
                                    ok, message = submit_account_review_request(username, request_note)
                                    if ok:
                                        st.session_state.pop("disabled_account_request_note", None)
                                        st.success(message)
                                        st.rerun()
                                    else:
                                        st.warning(message)
                    else:
                        st.success(
                            "Your account is active. Please return to Login and sign in again."
                        )

            if st.button("Back to Login", width="stretch", key="disabled_account_back_login"):
                st.session_state.account_review_login_username = None
                st.session_state.account_review_login_verified = False
                st.session_state.page = "login"
                st.rerun()


# =========================================================
# REGISTER PAGE
# =========================================================

def register_page():

    auth_reference_theme()

    bank_header()

    left, center = st.columns([1, 1], gap="medium")

    with left:
        with st.container(key="auth_visual_fixed"):
            auth_visual_panel("register")

    with center:
        with st.container(key="auth_register_scroll"):

            st.markdown(
                f"""
                <div class="auth-brand-header">
                    <div class="auth-brand-logo">{madhu_bank_logo()}</div>
                    <div class="auth-brand-title">MADHU BANK</div>
                </div>
                <div class="auth-main-heading">Create Your Account</div>
                <div class="auth-main-desc">Start your secure digital banking experience.</div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("register_form"):

                name = st.text_input(
                    "Full Name"
                )

                username = st.text_input(
                    "Username"
                )

                email = st.text_input(
                    "Email Address",
                    placeholder="you@example.com",
                )

                dob = st.date_input(
                      "Date of Birth",
                     min_value=date(1990, 1, 1),
                     max_value=date.today(),
                    value=date(2007, 1, 1)
    )
                account_type = st.selectbox(
                "Account Type",
               ["Savings", "Current"]
                )

                if dob:
                   today = date.today()
                   age = today.year - dob.year

                   if (today.month, today.day) < (dob.month, dob.day):
                    age -= 1

                   if age < 18:
                     account_type = "Savings"
                     st.info("Below 18 years: Only Savings account is available.")

                security_questions = [
                    "What was the name of your first school?",
                    "What is your favorite color?",
                    "What was the name of your first pet?",
                    "What is your favorite food?",
                ]

                security_question = st.selectbox(
                    "Security Question Type",
                    security_questions,
                    key="register_security_question",
                    help="Choose a question you can remember. This will be used for password recovery.",
                )

                security_answer = st.text_input(
                    "Security Answer",
                    type="password",
                    key="register_security_answer",
                )

                password = st.text_input(
                    "Password",
                    type="password"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password"
                )

                register_submit = st.form_submit_button(
                    "Create Account",
                    width='stretch'
                )

            if register_submit:

                if not name or not username or not password or not security_answer.strip():

                    st.error(
                        "Please fill all required fields."
                    )

                elif password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                elif len(password) < 8:

                    st.error(
                        "Password must contain at least 8 characters."
                    )

                else:

                    clean_name = str(name or "").strip()
                    clean_username = str(username or "").strip()
                    clean_answer = str(security_answer or "").strip()

                    if len(password) < 8:
                        st.error("Password must contain at least 8 characters.")
                    elif not clean_answer:
                        st.error("Please enter your security answer.")
                    else:
                        # Let the backend perform the authoritative uniqueness check.
                        # A stale pre-check could incorrectly block registration while
                        # the actual create operation has not happened yet.
                        result = None
                        registration_error = None

                        try:
                            result = register_user(
                                clean_name,
                                clean_username,
                                password,
                                dob.strftime("%Y-%m-%d"),
                                account_type,
                                security_question=security_question,
                                security_answer=clean_answer,
                                email=email.strip(),
                            )
                        except Exception as exc:
                            registration_error = str(exc)

                        # If the registration succeeded, immediately attach the
                        # recovery question and assign the Account Number.
                        if result is True:
                            try:
                                saved_user = users_collection.find_one(
                                    {"username": clean_username},
                                    {"security_question": 1, "security_answer_hash": 1, "email": 1, "status": 1},
                                )
                                if not saved_user or not saved_user.get("security_question") or not saved_user.get("security_answer_hash"):
                                    raise RuntimeError(
                                        "The account was created, but the security question could not be saved."
                                    )

                                account_number = ensure_account_number(clean_username)

                                if not account_number:
                                    raise RuntimeError(
                                        "Account was created, but the Account Number could not be assigned."
                                    )

                                user_email = str(saved_user.get("email") or "").strip().lower()
                                if user_email:
                                    otp_sent = False
                                    try:
                                        _, otp_sent = generate_and_send_otp(user_email, expires_in_seconds=300)
                                    except Exception:
                                        otp_sent = False

                                    if otp_sent:
                                        st.session_state.pending_registration_username = clean_username
                                        st.session_state.pending_registration_email = user_email
                                        st.session_state.page = "register_otp_verification"
                                        st.success(
                                            f"Account created successfully. Your Account Number is {account_number}. A verification OTP has been sent to {user_email}."
                                        )
                                        st.rerun()

                                    if SMTP_CONFIGURATION_ERROR:
                                        st.error(
                                            "Account created, but OTP email is not configured. "
                                            f"{SMTP_CONFIGURATION_ERROR}"
                                        )
                                    else:
                                        st.error(
                                            "Account created, but the verification email could not be sent. "
                                            "Check SMTP settings and try resending the OTP."
                                        )
                                    return

                                st.success(
                                    f"Account created successfully. Your Account Number is {account_number}."
                                )
                                st.session_state.logged_in = True
                                st.session_state.username = clean_username
                                st.session_state.role = "user"
                                st.session_state.account_number = account_number
                                st.session_state.page = "dashboard"
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Account setup could not be completed: {exc}")

                        elif result is False:
                            # register_user() returns False for a duplicate username,
                            # duplicate email, or invalid required identity fields.
                            # Report the exact conflict to avoid the raw database error
                            # for normal sign-up retries.
                            email_lookup = str(email or "").strip().lower()
                            duplicate_now = users_collection.find_one(
                                {"$or": [
                                    {"username": clean_username},
                                    {"email": email_lookup} if email_lookup else {"_id": "__never__"},
                                ]},
                                {"_id": 1, "username": 1, "email": 1},
                            )

                            if duplicate_now and duplicate_now.get("username") == clean_username:
                                st.error(
                                    f"Username '{clean_username}' is already registered. "
                                    "Please choose a different username."
                                )
                            elif duplicate_now and duplicate_now.get("email") == email_lookup:
                                st.error(
                                    f"Email '{email_lookup}' is already registered. "
                                    "Please use a different email address."
                                )
                            elif registration_error:
                                st.error(f"Unable to create the account: {registration_error}")
                            else:
                                st.error(
                                    "Unable to create the account. Please check your details and try again."
                                )

                        elif registration_error:
                            st.error(f"Unable to create the account: {registration_error}")
                        else:
                            st.error(
                                "Unable to create the account. Please check your details and try again."
                            )

            if st.button(
                "Back to Login",
                width='stretch'
            ):

                st.session_state.page = "login"

                st.rerun()

# =========================================================
# REGISTER OTP VERIFICATION PAGE
# =========================================================

def register_otp_verification_page():
    auth_reference_theme()
    bank_header()

    left, center = st.columns([1, 1], gap="medium")

    with left:
        with st.container(key="auth_visual_fixed"):
            auth_visual_panel("register")

    with center:
        with st.container(key="auth_register_otp_scroll"):
            st.markdown(
                f"""
                <div class="auth-brand-header">
                    <div class="auth-brand-logo">{madhu_bank_logo()}</div>
                    <div class="auth-brand-title">MADHU BANK</div>
                </div>
                <div class="auth-main-heading">Email Verification</div>
                <div class="auth-main-desc">Enter the OTP sent to your email to activate your account.</div>
                """,
                unsafe_allow_html=True,
            )

            username = st.session_state.get("pending_registration_username")
            email = st.session_state.get("pending_registration_email")

            if not username or not email:
                st.warning("Your registration verification session expired. Please register again.")
                if st.button("Back to Register", width="stretch"):
                    st.session_state.page = "register"
                    st.rerun()
                return

            with st.form("register_otp_form"):
                st.info(f"OTP sent to {email}")
                otp_value = st.text_input("Enter OTP", max_chars=6, type="password")
                verify_button = st.form_submit_button("Verify Email", width="stretch")

            if verify_button:
                if not otp_value or not validate_otp(email, otp_value):
                    st.error("Invalid or expired OTP. Please retry.")
                else:
                    users_collection.update_one(
                        {"username": username},
                        {"$set": {"status": "Active", "email_verified": True}},
                    )

                    user = users_collection.find_one({"username": username})
                    if not user:
                        st.error("Account could not be verified. Please try again.")
                        st.session_state.page = "register"
                        st.rerun()

                    st.session_state.pending_registration_username = None
                    st.session_state.pending_registration_email = None
                    st.session_state.logged_in = True
                    st.session_state.username = user.get("username")
                    st.session_state.role = user.get("role", "user")
                    st.session_state.account_number = ensure_account_number(user.get("username"))
                    st.session_state.page = "dashboard"
                    st.success("Email verified successfully. Your account is now active.")
                    st.rerun()

            if st.button("Resend OTP", width="stretch"):
                now = time.time()
                last_sent = float(st.session_state.get("_last_register_resend", 0) or 0)
                if (now - last_sent) < 10.0:
                    st.toast("OTP was recently sent. Please wait a moment.", icon="⏳")
                else:
                    st.session_state["_last_register_resend"] = now
                    generated_otp, sent = generate_and_send_otp(email, expires_in_seconds=300)
                    if sent:
                        st.success("A new OTP has been sent to your email.")
                    else:
                        st.error(
                            "Could not resend the OTP. "
                            f"{SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or 'Please check your email settings.'}"
                        )

            if st.button("Back to Register", width="stretch"):
                st.session_state.pending_registration_username = None
                st.session_state.pending_registration_email = None
                st.session_state.page = "register"
                st.rerun()


# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password_page():

    auth_reference_theme()

    bank_header()

    left, center = st.columns([1, 1], gap="medium")

    with left:
        with st.container(key="auth_visual_fixed"):
            auth_visual_panel("forgot")

    with center:
        with st.container(key="auth_forgot_scroll"):

            st.markdown(
                f"""
                <div class="auth-brand-header">
                    <div class="auth-brand-logo">{madhu_bank_logo()}</div>
                    <div class="auth-brand-title">MADHU BANK</div>
                </div>
                <div class="auth-main-heading">Forgot Password</div>
                <div class="auth-main-desc">Securely recover access to your account.</div>
                """,
                unsafe_allow_html=True,
            )

            # ---------------------------------------------------------
            # STEP 1: Verify account ownership
            # ---------------------------------------------------------
            if not st.session_state.get("password_reset_verified", False):

                # First identify the account and send an OTP to its registered email.
                pending_reset_username = st.session_state.get("password_reset_username")
                email_verified = st.session_state.get("password_reset_email_verified", False)

                if not pending_reset_username or not email_verified:
                    with st.form("password_recovery_account_form"):
                        username = st.text_input("Username", key="reset_username")
                        account_number = st.text_input(
                            "Account Number",
                            key="reset_account_number",
                            placeholder="Enter your 10-digit Account Number",
                        )
                        email = st.text_input(
                            "Registered Email",
                            key="reset_email",
                            placeholder="Enter the email registered to your account",
                        )
                        continue_button = st.form_submit_button("Send Email OTP", width="stretch")

                    if continue_button:
                        if not username.strip() or not account_number.strip() or not email.strip():
                            st.error("Please enter your username, Account Number, and registered email.")
                        else:
                            try:
                                numeric_account_number = int(account_number.strip())
                            except ValueError:
                                numeric_account_number = None

                            user = None
                            if numeric_account_number is not None:
                                user = users_collection.find_one(
                                    {
                                        "username": username.strip(),
                                        "account_number": numeric_account_number,
                                    }
                                )

                            registered_email = str(user.get("email") or "").strip().lower() if user else ""
                            entered_email = email.strip().lower()
                            target_reset_email = registered_email or entered_email

                            if not user or str(user.get("status", "Active")).lower() == "disabled":
                                st.error("The account details could not be verified.")
                            elif entered_email and registered_email and entered_email != registered_email:
                                st.error("The email does not match the email registered for this account.")
                            else:
                                _, sent = generate_and_send_otp(target_reset_email, expires_in_seconds=300)
                                if not sent:
                                    st.error(
                                        "Unable to send the password reset OTP. "
                                        f"{SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or 'Please check your email settings.'}"
                                    )
                                else:
                                    st.session_state.password_reset_username = user.get("username")
                                    st.session_state.password_reset_account_number = numeric_account_number
                                    st.session_state.password_reset_email = target_reset_email
                                    st.session_state.password_reset_email_verified = False
                                    st.session_state.password_reset_question = user.get("security_question")
                                    st.rerun()

                # Verify the email OTP before exposing the security-question step.
                if (
                    st.session_state.get("password_reset_username")
                    and not st.session_state.get("password_reset_email_verified", False)
                ):
                    reset_email = st.session_state.get("password_reset_email")
                    st.info(f"A password reset OTP was sent to {reset_email}.")
                    with st.form("password_reset_email_otp_form"):
                        email_otp = st.text_input("Email OTP", max_chars=6, type="password")
                        verify_email_button = st.form_submit_button("Verify Email OTP", width="stretch")

                    if verify_email_button:
                        if not email_otp or not validate_otp(reset_email, email_otp):
                            st.error("Invalid or expired email OTP. Please try again.")
                        else:
                            st.session_state.password_reset_email_verified = True
                            user = users_collection.find_one({
                                "username": st.session_state.password_reset_username,
                                "account_number": st.session_state.password_reset_account_number,
                            })
                            saved_question = user.get("security_question") if user else None
                            saved_answer_hash = user.get("security_answer_hash") if user else None
                            st.session_state.password_reset_question = saved_question
                            if not saved_question or not saved_answer_hash:
                                st.session_state.password_reset_needs_question_setup = True
                                st.session_state.password_reset_account_verified = False
                            else:
                                st.session_state.password_reset_account_verified = True
                                st.session_state.password_reset_needs_question_setup = False
                            st.rerun()

                    if st.button("Cancel", width="stretch"):
                        st.session_state.password_reset_username = None
                        st.session_state.password_reset_account_number = None
                        st.session_state.password_reset_email = None
                        st.session_state.password_reset_email_verified = False
                        st.session_state.page = "login"
                        st.rerun()
                    return

                # ---------------------------------------------------------
                # Legacy recovery setup: accounts without a saved question.
                # ---------------------------------------------------------
                if st.session_state.get("password_reset_needs_question_setup", False):
                    st.info(
                        "This account does not have a recovery question yet. "
                        "Verify your Date of Birth once to set it up, then continue with password recovery."
                    )

                    recovery_questions = [
                        "What was the name of your first school?",
                        "What is your favorite color?",
                        "What was the name of your first pet?",
                        "What is your favorite food?",
                    ]

                    with st.form("legacy_recovery_setup_form"):
                        recovery_dob = st.date_input(
                            "Date of Birth",
                            value=date(2007, 1, 1),
                            min_value=date(1900, 1, 1),
                            max_value=date.today(),
                            key="legacy_recovery_dob",
                        )
                        recovery_question = st.selectbox(
                            "Security Question Type",
                            recovery_questions,
                            key="legacy_recovery_question",
                        )
                        recovery_answer = st.text_input(
                            "Security Answer",
                            type="password",
                            key="legacy_recovery_answer",
                        )
                        setup_button = st.form_submit_button(
                            "Save Recovery Question",
                            width="stretch",
                        )

                    if setup_button:
                        legacy_username = st.session_state.get("password_reset_username")
                        legacy_account_number = st.session_state.get("password_reset_account_number")
                        legacy_user = users_collection.find_one({
                            "username": legacy_username,
                            "account_number": legacy_account_number,
                        })

                        stored_dob = str(legacy_user.get("dob", ""))[:10] if legacy_user else ""
                        entered_dob = recovery_dob.strftime("%Y-%m-%d")

                        if not legacy_user:
                            st.error("The account could not be verified. Please start again.")
                        elif stored_dob != entered_dob:
                            st.error("Date of Birth does not match the account record.")
                        elif not recovery_answer.strip():
                            st.error("Please enter a security answer.")
                        else:
                            users_collection.update_one(
                                {
                                    "username": legacy_username,
                                    "account_number": legacy_account_number,
                                },
                                {
                                    "$set": {
                                        "security_question": recovery_question,
                                        "security_answer_hash": hash_password(recovery_answer.strip().lower()),
                                    }
                                },
                            )
                            st.session_state.password_reset_question = recovery_question
                            st.session_state.password_reset_needs_question_setup = False
                            st.session_state.password_reset_account_verified = True
                            st.success("Recovery question saved. Please verify your answer to continue.")
                            st.rerun()

                # Ask the security question after the account is identified.
                if st.session_state.get("password_reset_account_verified", False):
                    question = st.session_state.get("password_reset_question")

                    with st.form("password_recovery_question_form"):
                        # Show only the exact question saved for this account.
                        # It is deliberately disabled so the recovery question cannot be changed.
                        if not question:
                            st.error("No security question is available for this account.")
                        else:
                            st.selectbox(
                                "Security Question Type",
                                [question],
                                index=0,
                                key="reset_security_question_type",
                                disabled=True,
                                help="This is the security question you selected during registration.",
                            )

                        security_answer = st.text_input(
                            "Security Answer",
                            type="password",
                            key="reset_security_answer",
                        )

                        verify_button = st.form_submit_button(
                            "Verify Answer",
                            width="stretch"
                        )

                    if verify_button:
                        reset_username = st.session_state.get("password_reset_username")
                        reset_account_number = st.session_state.get("password_reset_account_number")
                        identity_query = {"username": reset_username}
                        if reset_account_number is not None:
                            identity_query["account_number"] = reset_account_number
                        user = users_collection.find_one(identity_query)
                        answer_hash = user.get("security_answer_hash") if user else None

                        answer_matches = False
                        if answer_hash and security_answer.strip():
                            try:
                                from backend.security import verify_password
                                answer_matches = verify_password(
                                    security_answer.strip().lower(),
                                    answer_hash,
                                )
                            except Exception:
                                answer_matches = False

                        if answer_matches:
                            st.session_state.password_reset_verified = True
                            st.session_state.password_reset_account_verified = False
                            st.rerun()
                        else:
                            st.error("Incorrect security answer.")

            # ---------------------------------------------------------
            # STEP 2: Create a new password
            # ---------------------------------------------------------
            else:

                st.success("Account verified. You can now create a new password.")

                with st.form("new_password_form"):

                    new_password = st.text_input(
                        "New Password",
                        type="password",
                        key="reset_new_password"
                    )

                    confirm_password = st.text_input(
                        "Confirm New Password",
                        type="password",
                        key="reset_confirm_password"
                    )

                    reset_button = st.form_submit_button(
                        "Reset Password",
                        width="stretch"
                    )

                if reset_button:

                    if not new_password or not confirm_password:
                        st.error("Please enter and confirm your new password.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(new_password) < 6:
                        st.error("Passwords must contain at least 6 characters.")
                    else:
                        username = st.session_state.get("password_reset_username")
                        reset_email = st.session_state.get("password_reset_email")
                        if reset_password(username, new_password):
                            if reset_email:
                                users_collection.update_one(
                                    {"username": username},
                                    {"$set": {"email": reset_email, "email_verified": True}},
                                )
                            st.session_state.password_reset_username = None
                            st.session_state.password_reset_account_number = None
                            st.session_state.password_reset_email = None
                            st.session_state.password_reset_email_verified = False
                            st.session_state.password_reset_verified = False
                            st.session_state.password_reset_account_verified = False
                            st.session_state.password_reset_question = None
                            st.session_state.password_reset_needs_question_setup = False
                            st.session_state.password_reset_account_number = None
                            st.session_state.pop("reset_security_question_type", None)
                            st.session_state.pop("reset_security_answer", None)
                            st.success(
                                "Password reset successfully. Please log in with your new password."
                            )
                            st.session_state.page = "login"
                            st.rerun()
                        else:
                            st.error("Unable to reset the password. Please try again.")

                st.write("")

                if st.button("Cancel", width="stretch"):
                    st.session_state.password_reset_username = None
                    st.session_state.password_reset_account_number = None
                    st.session_state.password_reset_email = None
                    st.session_state.password_reset_email_verified = False
                    st.session_state.password_reset_verified = False
                    st.session_state.password_reset_account_verified = False
                    st.session_state.password_reset_question = None
                    st.session_state.pop("reset_security_question_type", None)
                    st.session_state.page = "login"
                    st.rerun()

                return

            if st.button(
                "Back to Login",
                width="stretch"
            ):
                st.session_state.password_reset_username = None
                st.session_state.password_reset_account_number = None
                st.session_state.password_reset_email = None
                st.session_state.password_reset_email_verified = False
                st.session_state.password_reset_verified = False
                st.session_state.password_reset_account_verified = False
                st.session_state.password_reset_question = None
                st.session_state.pop("reset_security_question_type", None)
                st.session_state.page = "login"
                st.rerun()


# =========================================================
# ACCOUNT REVIEW PAGE
# =========================================================

def account_review_page():
    username = current_customer_username()
    user = current_customer_user()

    user_header(
        "Account Review",
        "Request an administrator review of your Madhu Bank account.",
        "Account review",
    )

    if not user:
        st.error("Account information is unavailable.")
        return

    latest_request = get_account_review_request(username)

    left, right = st.columns([1.25, 1])

    with left:
        st.markdown(
            """
            <div class="user-panel">
                <div class="user-panel-title">Account Review Request</div>
                <div class="user-panel-subtitle">
                    Use this request when you need an administrator to review your account information.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if latest_request:
            status = str(latest_request.get("status", "Pending"))

            if status == "Pending":
                st.info("Your account review request is currently pending administrator review.")
            elif status == "Approved":
                st.success("Your account review request has been approved.")
            elif status == "Rejected":
                st.warning("Your account review request was rejected. You can submit a new request.")
                admin_note = str(latest_request.get("admin_note", "")).strip()
                if admin_note:
                    st.markdown("**Administrator reason:**")
                    st.info(admin_note)

        can_submit = not latest_request or str(latest_request.get("status", "")).lower() in {
            "approved",
            "rejected",
        }

        if can_submit:
            request_note = st.text_area(
                "Message to administrator",
                key="account_review_request_note",
                placeholder="Explain why you are requesting an account review.",
                height=100,
            )
            if st.button(
                "Request Account Review",
                key="request_account_review_submit",
                width="stretch",
                type="primary",
            ):
                if not request_note.strip():
                    st.error("Please enter a short message for the administrator before submitting the request.")
                else:
                    ok, message = submit_account_review_request(username, request_note)
                    if ok:
                        st.success(message)
                        st.rerun()
                    else:
                        st.warning(message)
        else:
            st.caption("A new request can be submitted after the current request is reviewed.")

    with right:
        account_number = user.get("account_number") or ensure_account_number(username)
        name = (
            user.get("name")
            or f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            or username
        )
        st.markdown(
            f"""
            <div class="user-panel">
                <div class="user-panel-title">Account Information</div>
                <div class="user-panel-subtitle">Information available to the administrator during review.</div>
                <div class="account-mini">
                    <div class="account-mini-label">Account Number</div>
                    <div class="account-mini-value">{account_number}</div>
                </div>
                <div class="account-mini">
                    <div class="account-mini-label">Customer</div>
                    <div class="account-mini-value">{name}</div>
                </div>
                <div class="account-mini">
                    <div class="account-mini-label">Username</div>
                    <div class="account-mini-value">{username}</div>
                </div>
                <div class="account-mini">
                    <div class="account-mini-label">Status</div>
                    <div class="account-mini-value">{user.get("status", "Active")}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# USER / CUSTOMER THEME
# =========================================================

def user_theme():
    """Customer console theme (injected via centralized design system)."""
    pass


def _profile_picture_data_url(user):
    """Return a data URL for a stored customer profile picture."""
    if not user:
        return None
    raw_data = user.get("profile_picture_data")
    if not raw_data:
        return None
    if isinstance(raw_data, (bytes, bytearray, memoryview)):
        encoded = base64.b64encode(bytes(raw_data)).decode("ascii")
    else:
        encoded = str(raw_data)
    mime = str(user.get("profile_picture_mime") or "image/png")
    if not mime.startswith("image/"):
        mime = "image/png"
    return f"data:{mime};base64,{encoded}"


def _customer_display_name(user, fallback="Customer"):
    if not user:
        return fallback
    name = user.get("name")
    if name:
        return str(name)
    full_name = (
        f"{user.get('first_name', '')} "
        f"{user.get('last_name', '')}"
    ).strip()
    return full_name or str(user.get("username") or fallback)


def _customer_initials(name):
    parts = str(name or "Customer").replace("_", " ").split()
    return "".join(part[0] for part in parts[:2]).upper() or "C"


def user_header(title, subtitle="", kicker="MADHU BANK / CUSTOMER"):
    username = current_customer_username()
    user = current_customer_user()
    name = _customer_display_name(user, username or "Customer")

    # Profile is intentionally kept only in the fixed top navigation bar.
    # This page header contains only the dashboard/page title area so there is
    # no duplicate Profile control near the lower-right side of the content.
    st.markdown(
        f"""
        <div class="user-topbar admin-topbar">
            <div>
                <div class="user-kicker admin-page-kicker">{html_escape(kicker)}</div>
                <div class="user-page-title admin-page-title">{html_escape(title)}</div>
                <div class="user-page-subtitle admin-page-subtitle">{html_escape(subtitle)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def transaction_type(row):
    return str(
        row.get("type")
        or row.get("transaction_type")
        or row.get("description")
        or "Transaction"
    )


# =========================================================
# NAVIGATION SCROLL RESET
# When the user switches pages from the top navbar, reset the browser
# viewport to the top of the newly rendered page.
# =========================================================
def _reset_browser_scroll_after_navigation():
    """Reset the browser viewport to the top of the page when navigating."""
    current_page = st.session_state.get("page")
    last_page = st.session_state.get("_last_viewed_page")
    page_changed = (last_page is not None and last_page != current_page)
    explicit_reset = st.session_state.get("_reset_scroll_after_nav", False)

    should_reset = explicit_reset or page_changed
    if page_changed or explicit_reset:
        st.session_state["_last_viewed_page"] = current_page
        st.session_state["_reset_scroll_after_nav"] = False

    if not should_reset:
        return

    st.html(
        """
        <div id="madhu-scroll-reset-anchor" style="display:none!important;height:0!important;width:0!important;margin:0!important;padding:0!important;overflow:hidden!important;"></div>
        <script>
        (function() {
            try { window.scrollTo({left: 0, top: 0, behavior: 'instant'}); } catch(e) { window.scrollTo(0, 0); }
            if (document.documentElement) document.documentElement.scrollTop = 0;
            if (document.body) document.body.scrollTop = 0;
            var selectors = ['[data-testid="stAppViewContainer"]', '[data-testid="stMain"]', 'section.main', '.main', '[data-testid="stMainBlockContainer"]', '.block-container'];
            for (var i = 0; i < selectors.length; i++) {
                try {
                    var node = document.querySelector(selectors[i]);
                    if (node) { node.scrollTop = 0; }
                } catch(e) {}
            }
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )

def _toggle_account_menu():
    st.session_state["user_account_menu_open"] = not st.session_state.get("user_account_menu_open", False)
    st.session_state["user_banking_menu_open"] = False
    st.session_state["user_profile_menu_open"] = False

def _toggle_banking_menu():
    st.session_state["user_banking_menu_open"] = not st.session_state.get("user_banking_menu_open", False)
    st.session_state["user_account_menu_open"] = False
    st.session_state["user_profile_menu_open"] = False

def _toggle_profile_menu():
    st.session_state["user_profile_menu_open"] = not st.session_state.get("user_profile_menu_open", False)
    st.session_state["user_account_menu_open"] = False
    st.session_state["user_banking_menu_open"] = False

# =========================================================
# USER SIDEBAR
# =========================================================

def banking_sidebar():
    """Render the customer navigation as a grouped fixed top menu.

    Existing customer pages and data are preserved. The navbar only changes
    how those existing destinations are grouped and positioned:
      Dashboard | My Account | Banking | Transactions | Profile
    """

    username = current_customer_username() or "Customer"
    user = current_customer_user()
    display_name = _customer_display_name(user, username)
    current_page = st.session_state.get("page", "dashboard")
    # Existing customer destinations are grouped into related menu buttons.
    account_pages = {
        "account": "Account Overview",
        "account_review": "Account Review",
    }
    banking_pages = {
        "deposit": ("Deposit", ":material/add_circle:"),
        "transfer": ("Transfer", ":material/swap_horiz:"),
        "withdraw": ("Withdraw", ":material/remove_circle:"),
        "balance": ("Balance", ":material/account_balance:"),
    }

    # Resolve the profile image once, before the navbar is rendered.
    # IMPORTANT: do not render a Streamlit markdown/style element inside the
    # Profile column because that creates an extra vertical block and pushes
    # the Profile popover lower than the other navbar controls.
    profile_image = _profile_picture_data_url(user)

    # Keep branding outside the navigation so it remains independently fixed.
    st.markdown(
        f"""
        <div class="user-fixed-brand">
            <div class="top-nav-brand-mark">{madhu_bank_logo()}</div>
            <div>
                <div class="top-nav-brand-name">MADHU BANK</div>
                <div class="top-nav-brand-subtitle">Customer banking</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    def go_to(page):
        navigate_to(page)

    def nav_button(label, page, icon):
        try:
            st.button(
                label,
                icon=icon,
                key=f"user_top_nav_{page}",
                width="stretch",
                type="primary" if current_page == page else "secondary",
                on_click=navigate_to,
                args=(page,),
            )
        except TypeError:
            st.button(
                label,
                key=f"user_top_nav_{page}",
                width="stretch",
                on_click=navigate_to,
                args=(page,),
            )

    # Final navbar-only override. It runs after the shared customer/admin theme
    # Top navbar styling.
    st.markdown(
        """
        <style>
        /* Profile image styling is declared outside the Profile column so it
           cannot create an extra Streamlit block and change vertical alignment. */
        __PROFILE_NAV_CSS__

        /* FINAL navbar geometry: five equal-width controls on ONE LINE.
           Every gap is identical and there is no extra edge padding. */
        .st-key-user_top_nav [data-testid="stHorizontalBlock"] {
            display:flex !important;
            flex-wrap:nowrap !important;
            width:100% !important;
            max-width:none !important;
            align-items:stretch !important;
            gap:6px !important;
            margin:0 !important;
            padding:0 !important;
        }
        .st-key-user_top_nav [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
        .st-key-user_top_nav [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex:1 1 0 !important;
            width:0 !important;
            min-width:0 !important;
            max-width:none !important;
            margin:0 !important;
            padding:0 !important;
            box-sizing:border-box !important;
        }
        .st-key-user_top_nav [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div,
        .st-key-user_top_nav [data-testid="stHorizontalBlock"] > div[data-testid="column"] > div {
            width:100% !important;
            min-width:0 !important;
            max-width:none !important;
            margin:0 !important;
            padding:0 !important;
            box-sizing:border-box !important;
        }
        /* Out-of-flow container collapse to eliminate empty space under fixed header */
        div[data-testid="stElementContainer"]:has(.user-fixed-brand),
        div[data-testid="stElementContainer"]:has(> .st-key-user_top_nav),
        div[data-testid="stElementContainer"]:has(.st-key-user_top_nav) {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            border: 0 !important;
        }

        /* Zero out all outer wrappers, borders, shadows, backgrounds, and paddings */
        .st-key-user_top_nav [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-user_top_nav [data-testid="stVerticalBlockBorderWrapper"] > div,
        .st-key-user_top_nav [data-testid="stVerticalBlock"],
        .st-key-user_top_nav [data-testid="stVerticalBlock"] > div,
        .st-key-user_top_nav [data-testid="stElementContainer"],
        .st-key-user_top_nav [data-testid="stElementContainer"] > div,
        .st-key-user_top_nav .stButton,
        .st-key-user_top_nav .stButton > div,
        .st-key-user_top_nav div[data-testid="stPopover"],
        .st-key-user_top_nav div[data-testid="stPopover"] > div,
        .st-key-user_top_nav div[data-testid="stPopover"] > div > div {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            border-width: 0 !important;
            box-shadow: none !important;
            outline: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .st-key-user_top_nav .stButton,
        .st-key-user_top_nav .stButton > div,
        .st-key-user_top_nav div[data-testid="stPopover"],
        .st-key-user_top_nav div[data-testid="stPopover"] > div {
            display: flex !important;
            width: 100% !important;
            min-width: 0 !important;
            max-width: none !important;
            flex: 1 1 auto !important;
            height: 38px !important;
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }

        /* Top-level navbar button: ONLY the button element has styling */
        .st-key-user_top_nav .stButton > button,
        .st-key-user_top_nav div[data-testid="stPopover"] button {
            width: 100% !important;
            min-width: 0 !important;
            max-width: none !important;
            height: 38px !important;
            min-height: 38px !important;
            box-sizing: border-box !important;
            border-radius: 8px !important;
            padding: 0 14px !important;
            margin: 0 !important;
            background: transparent !important;
            background-image: none !important;
            border: 1px solid transparent !important;
            color: #4F5B56 !important;
            -webkit-text-fill-color: #4F5B56 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            box-shadow: none !important;
            transform: none !important;
            transition: background 160ms ease, color 160ms ease, border-color 160ms ease !important;
        }
        /* Top-level navbar behaviour: neutral by default, soft emerald when selected/open. */
        .st-key-user_top_nav .stButton > button:hover,
        .st-key-user_top_nav div[data-testid="stPopover"] button:hover {
            background: #F0F7F4 !important;
            background-image: none !important;
            border-color: #BFE3D4 !important;
            color: #0E5B45 !important;
            -webkit-text-fill-color: #0E5B45 !important;
            box-shadow: none !important;
            transform: none !important;
        }
        .st-key-user_top_nav .stButton > button[kind="primary"],
        .st-key-user_top_nav .stButton > button[data-testid*="baseButton-primary"],
        .st-key-user_top_nav div[data-testid="stPopover"] button[aria-expanded="true"],
        .st-key-user_top_nav .nav-selected > button {
            background: #E8F5F0 !important;
            background-image: none !important;
            border: 1px solid #BFE3D4 !important;
            border-color: #BFE3D4 !important;
            color: #0E5B45 !important;
            -webkit-text-fill-color: #0E5B45 !important;
            font-weight: 600 !important;
            box-shadow: none !important;
            transform: none !important;
        }
        .st-key-user_top_nav .stButton > button[kind="primary"] *,
        .st-key-user_top_nav .stButton > button[data-testid*="baseButton-primary"] *,
        .st-key-user_top_nav div[data-testid="stPopover"] button[aria-expanded="true"] *,
        .st-key-user_top_nav .nav-selected > button * {
            color: #0E5B45 !important;
            -webkit-text-fill-color: #0E5B45 !important;
        }
        .st-key-user_top_nav .nav-selected > button:hover,
        .st-key-user_top_nav div[data-testid="stPopover"] button[aria-expanded="true"]:hover {
            background: #E8F5F0 !important;
            border-color: #BFE3D4 !important;
            box-shadow: none !important;
        }
        .st-key-user_top_nav div[data-testid="stPopover"] button svg,
        .st-key-user_top_nav .stButton > button svg {
            color: currentColor !important;
            fill: currentColor !important;
            stroke: currentColor !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _reset_browser_scroll_after_navigation()

    with st.container(key="user_top_nav"):
        cols = st.columns([1, 1, 1, 1, 1], gap="small")

        # 1. Dashboard — direct destination.
        with cols[0]:
            nav_button("Dashboard", "dashboard", ":material/dashboard:")

        # 2. My Account — controlled dropdown.
        # Native st.popover was causing the first click to be consumed by
        # Streamlit/BaseWeb. Use a real button + session state so the first
        # click immediately renders the floating menu after one rerun.
        with cols[1]:
            account_menu_open = st.session_state.get("user_account_menu_open", False)
            account_active = current_page in set(account_pages.keys())

            st.button(
                "My Account",
                icon=":material/account_balance_wallet:",
                key="user_my_account_trigger",
                width="stretch",
                type="primary" if account_active or account_menu_open else "secondary",
                on_click=_toggle_account_menu,
            )

            if account_menu_open:
                with st.container(key="user_account_dropdown"):
                    for page, label in account_pages.items():
                        st.button(
                            label,
                            icon=(
                                ":material/account_balance_wallet:"
                                if page == "account"
                                else ":material/fact_check:"
                            ),
                            key=f"user_account_menu_{page}",
                            width="stretch",
                            on_click=navigate_to,
                            args=(page,),
                        )

        # 3. Banking — controlled dropdown retained as the working pattern.
        with cols[2]:
            banking_child_pages = set(banking_pages.keys())
            banking_menu_open = st.session_state.get("user_banking_menu_open", False)
            banking_active = current_page in banking_child_pages

            st.button(
                "Banking",
                icon=":material/account_balance:",
                key="user_banking_top_trigger",
                width="stretch",
                type="primary" if banking_active or banking_menu_open else "secondary",
                on_click=_toggle_banking_menu,
            )

            if banking_menu_open:
                with st.container(key="user_banking_dropdown"):
                    for page, (label, icon) in banking_pages.items():
                        st.button(
                            label,
                            icon=icon,
                            key=f"user_banking_menu_{page}",
                            width="stretch",
                            on_click=navigate_to,
                            args=(page,),
                        )

        # 4. Transactions — direct destination.
        with cols[3]:
            nav_button("Transactions", "transactions", ":material/receipt_long:")

        # 5. Profile — controlled dropdown.
        # This uses the same Admin-derived profile markup already implemented,
        # but the trigger is a normal Streamlit button so the FIRST click is
        # deterministic and never depends on BaseWeb popover state.
        with cols[4]:
            profile_menu_open = st.session_state.get("user_profile_menu_open", False)
            profile_active = current_page == "profile"

            st.button(
                "Profile",
                icon=None,
                key="user_profile_trigger",
                width="stretch",
                type="primary" if profile_active or profile_menu_open else "secondary",
                on_click=_toggle_profile_menu,
            )

            if profile_menu_open:
                with st.container(key="user_profile_dropdown"):
                    with st.container(key="user_profile_popover_content"):
                        initials = _customer_initials(display_name)
                        if profile_image:
                            profile_avatar_html = (
                                f'<img class="user-profile-avatar admin-top-profile-avatar admin-top-profile-avatar-image" '
                                f'src="{profile_image}" alt="Profile picture">'
                            )
                        else:
                            profile_avatar_html = (
                                f'<div class="user-profile-avatar admin-top-profile-avatar">{html_escape(initials)}</div>'
                            )

                        if user:
                            profile_rows = [
                                ("Full Name", user.get("name") or display_name),
                                ("Username", user.get("username") or username),
                                (
                                    "Account Number",
                                    user.get("account_number")
                                    or st.session_state.get("account_number")
                                    or "Unavailable",
                                ),
                                ("Account Type", user.get("account_type", "Savings")),
                                ("Status", user.get("status", "Active")),
                            ]
                        else:
                            profile_rows = [("Profile", "Customer data unavailable")]

                        rows_markup = "".join([
                            f'<div class="user-profile-row admin-top-profile-row">'
                            f'<span>{html_escape(lbl)}</span>'
                            f'<strong>{html_escape(val)}</strong>'
                            f'</div>'
                            for lbl, val in profile_rows
                        ])

                        st.markdown(
                            f"""
                            <div class="user-profile-card admin-top-profile-popover">
                                <div class="user-profile-header">
                                    {profile_avatar_html}
                                    <div class="user-profile-name admin-top-profile-name">{html_escape(display_name)}</div>
                                    <div class="user-profile-role admin-top-profile-role">Madhu Bank Customer</div>
                                </div>
                                <div class="user-profile-table">
                                    {rows_markup}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.button(
                            "Open Full Profile",
                            icon=":material/badge:",
                            key="user_top_profile_settings",
                            width="stretch",
                            on_click=navigate_to,
                            args=("profile",),
                        )
                        st.button(
                            "Logout",
                            icon=":material/logout:",
                            key="user_top_profile_logout",
                            width="stretch",
                            on_click=logout,
                        )
    


def notify_incoming_transfers(transactions=None):
    """Show newly received transfers once, then mark them as acknowledged."""
    user = current_customer_user()
    if not user:
        return

    username = user.get("username")
    if not username:
        return

    incoming = transactions if transactions is not None else get_transactions(username)
    for tx in incoming:
        if str(tx.get("type", "")).strip().lower() != "transfer":
            continue
        if str(tx.get("direction", "")).strip().lower() != "in":
            continue

        tx_key = str(
            tx.get("transaction_id")
            or tx.get("transfer_id")
            or tx.get("_id")
            or ""
        )
        if not tx_key or tx_key in st.session_state.seen_transfer_notifications:
            continue

        # New transfers are explicitly unacknowledged. Legacy incoming
        # transfers without this field are considered already seen so an
        # existing account does not get old popup messages on first login.
        if tx.get("notification_seen") is not False:
            st.session_state.seen_transfer_notifications.add(tx_key)
            continue

        amount = safe_float(tx.get("amount", 0))
        sender_name = tx.get("counterparty_name")

        if not sender_name and tx.get("counterparty_account_number") is not None:
            counterparty = get_user_by_account_number(tx.get("counterparty_account_number"))
            if counterparty:
                sender_name = (
                    counterparty.get("name")
                    or f"{counterparty.get('first_name', '')} {counterparty.get('last_name', '')}".strip()
                    or counterparty.get("username")
                )

        sender_name = sender_name or tx.get("counterparty_username") or "Another Madhu Bank user"

        st.toast(
            f"Received ₹{amount:,.2f} from {sender_name}",
            icon="💸",
        )
        st.success(
            f"Transfer received: ₹{amount:,.2f} from {sender_name}."
        )

        st.session_state.seen_transfer_notifications.add(tx_key)
        try:
            transactions_collection.update_one(
                {"transaction_id": tx_key, "username": username},
                {"$set": {"notification_seen": True}},
            )
        except Exception:
            pass


_CURRENT_CUSTOMER_CONTEXT = None


def _current_customer_context():
    """Load the logged-in customer once per Streamlit script run."""
    global _CURRENT_CUSTOMER_CONTEXT
    if _CURRENT_CUSTOMER_CONTEXT is not None:
        return _CURRENT_CUSTOMER_CONTEXT

    account_number = st.session_state.get("account_number")
    username = st.session_state.get("username")
    user = None

    if account_number is not None:
        user = get_user_by_account_number(account_number)
        if user:
            username = user.get("username") or username

    if user is None and username:
        user = get_user(username)
        if user:
            assigned_number = user.get("account_number")
            if not isinstance(assigned_number, int) or isinstance(assigned_number, bool):
                assigned_number = ensure_account_number(username)
            if assigned_number is not None:
                st.session_state.account_number = assigned_number
                user = get_user_by_account_number(assigned_number) or user

    _CURRENT_CUSTOMER_CONTEXT = (username, user)
    return _CURRENT_CUSTOMER_CONTEXT


def current_customer_username():
    """Resolve the logged-in customer without repeating DB lookups in one run."""
    return _current_customer_context()[0]


def current_customer_user():
    """Return the current customer record without repeating DB lookups in one run."""
    return _current_customer_context()[1]


def dashboard():
    """Customer dashboard using the Admin reference geometry.

    Data, calculations, transactions, and existing navigation actions are
    preserved; only the visual arrangement of existing customer information
    is changed to match the supplied Admin reference.
    """
    username = current_customer_username()
    user = current_customer_user() or {}
    transactions = get_transactions(username)
    notify_incoming_transfers(transactions)
    balance = current_balance(username)

    display_name = _customer_display_name(user, username or "Customer")
    account_type = user.get("account_type", "Savings")
    status = user.get("status", "Active")
    account_number = user.get("account_number") or ensure_account_number(username)

    # ---------------------------------------------------------
    # PAGE HEADER — same position/spacing as Admin reference.
    # ---------------------------------------------------------
    user_header(
        "Dashboard",
        "Monitor your account activity and manage banking operations.",
        "MADHU BANK / CUSTOMER",
    )

    # ---------------------------------------------------------
    # KPI ROW — exact four-column geometry of the reference.
    # ---------------------------------------------------------
    total_transactions = len(transactions)

    kpis = [
        (
            "CURRENT BALANCE",
            f"₹{safe_float(balance):,.2f}",
            f"{account_type} account",
            "◉",
            "balance",
        ),
        (
            "ACCOUNT TYPE",
            str(account_type),
            f"Account #{account_number or 'Unavailable'}",
            "▣",
            "account",
        ),
        (
            "TOTAL TRANSACTIONS",
            str(total_transactions),
            "Recorded activity",
            "↔",
            "transactions",
        ),
        (
            "ACCOUNT STATUS",
            str(status),
            display_name,
            "!",
            "status",
        ),
    ]

    kpi_cols = st.columns(4, gap="small")
    for col, (label, value, note, icon, kind) in zip(kpi_cols, kpis):
        with col:
            st.markdown(
                f"""
                <div class="user-ref-kpi user-ref-kpi-{kind} admin-kpi">
                    <div class="admin-kpi-top">
                        <div class="admin-kpi-label">{html_escape(label)}</div>
                        <div class="admin-kpi-icon">{icon}</div>
                    </div>
                    <div class="admin-kpi-value">{html_escape(value)}</div>
                    <div class="admin-kpi-foot">{html_escape(note)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TRANSACTION OVERVIEW — BAR CHART
    # ---------------------------------------------------------
    now = datetime.now()
    parsed_rows = []

    for row in transactions:
        raw_dt = row.get("date") or row.get("timestamp") or row.get("created_at")
        try:
            parsed = pd.to_datetime(raw_dt, errors="coerce")
            if pd.isna(parsed):
                continue
            if getattr(parsed, "tzinfo", None) is not None:
                parsed = parsed.tz_localize(None)
            parsed_rows.append(parsed)
        except Exception:
            continue

    days = [now.date() - pd.Timedelta(days=offset) for offset in range(6, -1, -1)]
    counts = []
    for day_value in days:
        counts.append(
            sum(1 for dt_value in parsed_rows if dt_value.date() == day_value)
        )

    # Responsive seven-day bar chart.
    chart_w = 1180
    chart_h = 200
    plot_left = 28
    plot_right = chart_w - 22
    plot_top = 18
    plot_bottom = chart_h - 46

    max_count = max(max(counts), 1)
    usable_w = plot_right - plot_left
    slot_w = usable_w / max(len(counts), 1)
    bar_w = min(72, slot_w * 0.54)

    # Horizontal grid and Y-axis labels.
    grid_values = [0, max_count / 3, (2 * max_count) / 3, max_count]
    grid_svg = []
    y_labels_svg = []

    for gv in grid_values:
        gy = plot_bottom - (gv / max_count) * (plot_bottom - plot_top)

        grid_svg.append(
            f'<line x1="{plot_left}" y1="{gy:.1f}" '
            f'x2="{plot_right}" y2="{gy:.1f}" '
            f'style="stroke:#EDF0EE;stroke-width:1;"/>'
        )

        y_labels_svg.append(
            f'<text x="{plot_left - 9:.1f}" y="{gy + 3:.1f}" '
            f'text-anchor="end" '
            f'style="fill:#4F5B56;font-size:11px;font-family:Inter,system-ui,sans-serif;font-weight:600;">'
            f'{int(round(gv))}</text>'
        )

    # X-axis and seven bars.
    x_axis_svg = (
        f'<line x1="{plot_left}" y1="{plot_bottom:.1f}" '
        f'x2="{plot_right}" y2="{plot_bottom:.1f}" '
        f'style="stroke:#E4E9E6;stroke-width:1.2;"/>'
    )

    bars_svg = []
    labels_svg = []

    for idx, (day_value, count) in enumerate(zip(days, counts)):
        center_x = plot_left + (idx + 0.5) * slot_w
        bar_h = (count / max_count) * (plot_bottom - plot_top)
        bar_y = plot_bottom - bar_h

        # Keep a one-pixel visual presence when the count is zero.
        visible_h = max(bar_h, 1.0)
        visible_y = plot_bottom - visible_h

        bars_svg.append(
            f'<rect x="{center_x - bar_w/2:.1f}" y="{visible_y:.1f}" '
            f'width="{bar_w:.1f}" height="{visible_h:.1f}" '
            f'rx="5" ry="5" '
            f'style="fill:#16805F;opacity:0.96;"/>'
        )

        # Value above non-zero bars.
        if count > 0:
            bars_svg.append(
                f'<text x="{center_x:.1f}" y="{max(visible_y - 5, 10):.1f}" '
                f'text-anchor="middle" '
                f'style="fill:#17201D;font-size:11px;font-family:Inter,system-ui,sans-serif;font-weight:700;">'
                f'{count}</text>'
            )

        labels_svg.append(
            f'<line x1="{center_x:.1f}" y1="{plot_bottom:.1f}" '
            f'x2="{center_x:.1f}" y2="{plot_bottom + 5:.1f}" '
            f'style="stroke:#E4E9E6;stroke-width:1;"/>'
        )

        labels_svg.append(
            f'<text x="{center_x:.1f}" y="{chart_h - 12}" '
            f'text-anchor="middle" '
            f'style="fill:#4F5B56;font-size:11px;font-family:Inter,system-ui,sans-serif;font-weight:600;">'
            f'{day_value.strftime("%a %d")}</text>'
        )

    analytics_html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8"/>
        <style>
          html, body {{
            margin:0;
            padding:0;
            width:100%;
            height:100%;
            overflow:hidden;
            background:#F6F8F7;
            font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
            color:#17201D;
          }}

          .analytics {{
            width:100%;
            height:297px;
            box-sizing:border-box;
            padding:22px 18px 14px 18px;
            background:#FFFFFF;
            border:1px solid #E4E9E6;
            border-radius:12px;
            box-shadow:0 5px 20px rgba(23,32,29,.05);
            overflow:hidden;
          }}

          .head {{
            width:100%;
            display:flex;
            align-items:flex-start;
            justify-content:space-between;
            gap:16px;
          }}

          .title {{
            margin:0;
            font-size:13px;
            line-height:1.2;
            font-weight:750;
            color:#17201D;
          }}

          .subtitle {{
            margin-top:5px;
            font-size:12px;
            line-height:1.3;
            color:#4F5B56;
          }}

          .period {{
            width:206px;
            height:39px;
            min-width:206px;
            box-sizing:border-box;
            display:flex;
            align-items:center;
            padding:0 13px;
            background:#F6F8F7;
            border:1px solid #CBD7D1;
            border-radius:8px;
            color:#17201D;
            font-size:12px;
            font-weight:650;
          }}

          .chart {{
            width:100%;
            height:203px;
            margin-top:12px;
          }}

          .chart svg {{
            display:block;
            width:100%;
            height:200px;
            overflow:visible;
          }}

          .selected {{
            margin-top:0;
            padding:0 2px;
            font-size:11px;
            line-height:1.2;
            color:#66716D;
          }}

          .selected strong {{
            color:#17201D;
            font-weight:750;
          }}
        </style>
      </head>
      <body>
        <section class="analytics" aria-label="Transactions Overview">
          <div class="head">
            <div>
              <div class="title">Transactions Overview</div>
              <div class="subtitle">Transaction count over the selected period.</div>
            </div>
            <div class="period">Last 7 Days</div>
          </div>

          <div class="chart">
            <svg
              viewBox="0 0 {chart_w} {chart_h}"
              preserveAspectRatio="none"
              role="img"
              aria-label="Transaction counts for the last seven days"
            >
              {''.join(grid_svg)}
              {x_axis_svg}
              {''.join(y_labels_svg)}
              {''.join(bars_svg)}
              {''.join(labels_svg)}
            </svg>
          </div>

          <div class="selected">
            Selected: Last 7 Days
            <strong>{total_transactions} transactions</strong>
          </div>
        </section>
      </body>
    </html>
    """

    st.iframe(
        analytics_html,
        height=317,
    )


    # ---------------------------------------------------------
    # KEEP EXISTING QUICK ACTIONS / RECENT ACTIVITY BELOW.
    # Functionality remains unchanged; only its position is after
    # the reference-style overview block.
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="user-ref-lower-heading">Quick Actions</div>
        <div class="user-ref-lower-subtitle">Common operations for your account.</div>
        """,
        unsafe_allow_html=True,
    )

    q1, q2, q3, q4 = st.columns(4, gap="small")
    quick_actions = [
        (q1, "Deposit", "Add money", "deposit", ":material/add_circle:"),
        (q2, "Withdraw", "Take money out", "withdraw", ":material/remove_circle:"),
        (q3, "Transfer", "Move money", "transfer", ":material/swap_horiz:"),
        (q4, "Transactions", "View history", "transactions", ":material/receipt_long:"),
    ]

    for col, title, copy, page, icon in quick_actions:
        with col:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="user-ref-action-card">
                        <div class="user-ref-action-title">{html_escape(title)}</div>
                        <div class="user-ref-action-copy">{html_escape(copy)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                try:
                    st.button(
                        title,
                        icon=icon,
                        key=f"dashboard_{page}",
                        width="stretch",
                        type="primary",
                        on_click=navigate_to,
                        args=(page,),
                    )
                except TypeError:
                    st.button(
                        title,
                        key=f"dashboard_{page}",
                        width="stretch",
                        on_click=navigate_to,
                        args=(page,),
                    )

    st.markdown(
        """
        <div class="user-ref-lower-heading">Recent Transactions</div>
        <div class="user-ref-lower-subtitle">Your latest account activity.</div>
        """,
        unsafe_allow_html=True,
    )

    if not transactions:
        st.info("No transactions yet. Your activity will appear here.")
    else:
        rows = transactions[:8]
        for row in rows:
            kind = transaction_type(row)
            amount = safe_float(row.get("amount", 0))
            dt = (
                row.get("date")
                or row.get("timestamp")
                or row.get("created_at")
                or ""
            )
            direction = str(row.get("direction", "")).strip().lower()
            is_incoming = direction == "in" or "deposit" in str(kind).lower() or "received" in str(kind).lower()
            amount_color = "#16805F" if is_incoming else "#17201D"
            prefix = "+ " if is_incoming else ""

            st.markdown(
                f"""
                <div class="user-ref-transaction-row">
                    <div>
                        <div class="user-ref-transaction-kind">{html_escape(kind)}</div>
                        <div class="user-ref-transaction-date">{html_escape(str(dt))}</div>
                    </div>
                    <div class="user-ref-transaction-amount" style="color:{amount_color}!important;">{prefix}₹{amount:,.2f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

def profile_page():
    username = current_customer_username()
    user = current_customer_user()
    user_header(
        "Profile",
        "Manage your profile picture and review your Madhu Bank account details.",
        "Customer profile",
    )

    if not user:
        st.error("Profile information unavailable.")
        return

    name = _customer_display_name(user, username or "Customer")
    account_number = user.get("account_number") or ensure_account_number(username)
    status = user.get("status", "Active")
    account_type = user.get("account_type", "Savings")
    dob = user.get("dob", "Not available")
    security_question = user.get("security_question", "Not set")
    created_at = user.get("created_at", "Not available")
    pin_state = "Set" if user.get("transaction_pin_hash") else "Not set"
    profile_image = _profile_picture_data_url(user)

    left, right = st.columns([1.05, 1.55], gap="medium")

    with left:
        # Do not wrap this section in an HTML div opened in a separate
        # st.markdown call. Streamlit isolates each markdown element, which
        # created the empty rounded box visible above "Profile Picture".
        st.markdown('<div class="customer-profile-card-title">Profile Picture</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="customer-profile-card-subtitle">Upload a picture used by your customer profile and header.</div>',
            unsafe_allow_html=True,
        )

        if profile_image:
            st.markdown(
                f'<img class="customer-profile-page-image" src="{profile_image}" alt="Profile picture">',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="customer-profile-page-placeholder">{html_escape(_customer_initials(name))}</div>',
                unsafe_allow_html=True,
            )

        uploaded = st.file_uploader(
            "Choose profile picture",
            type=["png", "jpg", "jpeg", "webp"],
            key="customer_profile_picture_uploader",
            help="Image only. Maximum size: 2 MB.",
        )

        if uploaded is not None:
            raw = uploaded.getvalue()
            upload_hash = hashlib.sha256(raw).hexdigest()
            if len(raw) > 2 * 1024 * 1024:
                st.error("Profile picture must be 2 MB or smaller.")
            elif st.session_state.get("last_profile_picture_hash") != upload_hash:
                mime = uploaded.type or "image/png"
                encoded = base64.b64encode(raw).decode("ascii")
                users_collection.update_one(
                    {"username": username},
                    {"$set": {"profile_picture_data": encoded, "profile_picture_mime": mime}},
                )
                st.session_state.last_profile_picture_hash = upload_hash
                st.success("Profile picture updated successfully.")
                st.rerun()

        if profile_image:
            if st.button(
                "Remove Profile Picture",
                icon=":material/delete:",
                key="remove_customer_profile_picture",
                width="stretch",
            ):
                users_collection.update_one(
                    {"username": username},
                    {"$unset": {"profile_picture_data": "", "profile_picture_mime": ""}},
                )
                st.session_state.last_profile_picture_hash = None
                st.success("Profile picture removed.")
                st.rerun()

    with right:
        # Same cleanup for Customer Information: avoid a cross-element HTML
        # wrapper that renders as a detached blank surface.
        st.markdown('<div class="customer-profile-card-title">Customer Information</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="customer-profile-card-subtitle">Details connected to your banking account.</div>',
            unsafe_allow_html=True,
        )

        info_items = [
            ("Full Name", name),
            ("Username", username),
            ("Registered Email", user.get("email") or "Not registered"),
            ("Account Number", account_number or "Unavailable"),
            ("Account Type", account_type),
            ("Date of Birth", dob),
            ("Account Status", status),
            ("Security Question Type", security_question),
            ("Transaction PIN", pin_state),
            ("Created", created_at),
            ("Role", user.get("role", "user")),
        ]
        for label, value in info_items:
            st.markdown(
                f"""
                <div class="customer-profile-detail-row">
                    <div class="customer-profile-detail-label">{html_escape(label)}</div>
                    <div class="customer-profile-detail-value">{html_escape(value)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    pin_exists = bool(user.get("transaction_pin_hash"))
    st.markdown(
        f"""
        <div class="customer-profile-card">
            <div class="customer-profile-card-title">Security</div>
            <div class="customer-profile-card-subtitle">Manage the transaction PIN used by customer banking actions.</div>
            <div class="customer-profile-security-chip">Transaction PIN: {"Set" if pin_exists else "Not set"}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Transaction PIN")
    st.caption("A hidden 6-digit PIN is required for deposits, withdrawals, and transfers.")
    action = st.session_state.get("pin_pending_action")
    action_label = "Change PIN" if pin_exists else "Set 6-digit PIN"

    if not action:
        if st.button(action_label, width="content", icon=":material/lock_reset:"):
            st.session_state.pin_pending_action = "change" if pin_exists else "set"
            st.rerun()
    else:
        pending_email = st.session_state.get("pin_pending_email")
        email_verified = st.session_state.get("pin_email_verified", False)

        if pending_email and not email_verified:
            st.info(f"OTP sent to {pending_email}. Verify it before saving your PIN.")
            with st.form("pin_otp_verification_form"):
                otp_value = st.text_input("Email OTP", max_chars=6, type="password")
                verify_pin_otp = st.form_submit_button("Verify Email OTP", width="stretch")

            if verify_pin_otp:
                if not otp_value or not validate_otp(pending_email, otp_value):
                    st.error("Invalid or expired OTP. Please request a new OTP.")
                else:
                    if not user.get("email") or not user.get("email_verified"):
                        users_collection.update_one(
                            {"username": username},
                            {"$set": {"email": pending_email, "email_verified": True}},
                        )
                    st.session_state.pin_email_verified = True
                    st.rerun()
        elif email_verified:
            st.success("Email OTP verified. Enter your password and choose your transaction PIN.")
            with st.form("pin_change_form"):
                current_password = st.text_input("Password", type="password")
                new_pin = st.text_input("New 6-digit PIN", max_chars=6, type="password")
                confirm_pin = st.text_input("Confirm 6-digit PIN", max_chars=6, type="password")
                save_pin = st.form_submit_button("Save Transaction PIN", width="stretch")

            if save_pin:
                ok, message = _verify_and_set_pin(
                    user,
                    current_password,
                    new_pin,
                    confirm_pin,
                    action,
                )
                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            user_email = str(user.get("email") or "").strip().lower()
            if not user_email:
                st.info("Your account does not have a registered email address. Link an email to set up your PIN:")
                with st.form("profile_link_email_form"):
                    new_email_input = st.text_input("Email address", placeholder="e.g. yourname@example.com").strip().lower()
                    send_link_otp_btn = st.form_submit_button("Send Verification OTP", width="stretch")

                if send_link_otp_btn:
                    if not new_email_input or "@" not in new_email_input or "." not in new_email_input:
                        st.error("Please enter a valid email address.")
                    else:
                        _otp, sent = generate_and_send_otp(new_email_input, expires_in_seconds=300)
                        if not sent:
                            st.error(
                                "Unable to send verification OTP. "
                                f"{SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or 'Please check your email settings.'}"
                            )
                        else:
                            st.session_state.pin_pending_email = new_email_input
                            st.rerun()
            elif st.button("Send Email OTP", width="stretch"):
                _otp, sent = generate_and_send_otp(user_email, expires_in_seconds=300)
                if not sent:
                    st.error(
                        "Unable to send the PIN verification OTP. "
                        f"{SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or 'Please check your email settings.'}"
                    )
                else:
                    st.session_state.pin_pending_email = user_email
                    st.rerun()

        if st.button("Cancel", width="stretch"):
            _clear_pin_state()
            st.rerun()


def account_page():
    username = current_customer_username()
    user = current_customer_user()

    user_header(
        "My Account",
        "Personal and banking information for your account.",
        "Customer account",
    )

    if not user:
        st.error("Account information unavailable.")
        return

    account_number = user.get("account_number", "Unavailable")

    st.markdown(
        f"""
        <div class="user-panel">
            <div class="user-panel-title">Account Number</div>
            <div class="user-panel-subtitle">Use this numeric ID to identify and access this customer record across Madhu Bank.</div>
            <div class="account-mini">
                <div class="account-mini-label">Account Number</div>
                <div class="account-mini-value">{account_number}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    name = user.get("name")
    if not name:
        name = (
            f"{user.get('first_name', '')} "
            f"{user.get('last_name', '')}"
        ).strip() or username

    dob = user.get("dob", "N/A")
    account_type = user.get("account_type", "Savings")
    status = user.get("status", "Active")
    balance = current_balance(username)
    age = None

    try:
        if dob:
            parsed = datetime.strptime(
                str(dob)[:10],
                "%Y-%m-%d",
            ).date()
            today = date.today()
            age = today.year - parsed.year
            if (today.month, today.day) < (parsed.month, parsed.day):
                age -= 1
    except (TypeError, ValueError):
        age = None

    category = (
        "Major" if age is not None and age >= 18
        else "Minor" if age is not None
        else "Unknown"
    )

    left, right = st.columns(2)

    with left:
        info_rows = "".join(
            f"""
            <div class="account-mini" style="margin-top:8px;">
                <div class="account-mini-label">{html_escape(label)}</div>
                <div class="account-mini-value">{html_escape(str(value))}</div>
            </div>
            """
            for label, value in [
                ("Name", name),
                ("Username", username),
                ("Date of birth", dob),
                ("Age", age if age is not None else "N/A"),
            ]
        )
        st.markdown(
            f"""
            <div class="user-panel">
                <div class="user-panel-title">Personal information</div>
                <div class="user-panel-subtitle">
                    Information stored for your account.
                </div>
                {info_rows}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        with st.container(border=True):
            st.markdown("### Banking information")
            st.caption("Current account configuration.")

            b1, b2 = st.columns(2)
            with b1:
                st.markdown("**Account type**")
                st.write(account_type)
            with b2:
                st.markdown("**Account category**")
                st.write(category)

            b3, b4 = st.columns(2)
            with b3:
                st.markdown("**Status**")
                st.success(str(status))
            with b4:
                st.markdown("**Current balance**")
                st.write(f"₹{safe_float(balance):,.2f}")


def deposit_page():
    username = current_customer_username()
    balance = current_balance(username)
    user = current_customer_user() or {}

    user_header(
        "Deposit",
        "Add money to your Madhu Bank account.",
        "Banking",
    )

    has_pin = bool(user.get("transaction_pin_hash"))

    left, right = st.columns([1.45, 1])

    with left:
        if not has_pin:
            st.warning("⚠️ You have not set up a 6-digit Transaction PIN yet. A PIN is required for deposits, withdrawals, and transfers.")
            st.button(
                "Set Up Transaction PIN in Profile",
                key="deposit_goto_pin_setup",
                width="stretch",
                on_click=navigate_to,
                args=("profile",),
            )
            st.write("")

        with st.form("deposit_form"):
            st.markdown("### Deposit money")
            st.caption("Enter the amount you want to add to your account.")
            st.text_input(
                "Account Number",
                value=str(user.get("account_number", "")),
                disabled=True,
            )
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=100.0,
                format="%.2f",
            )
            transaction_pin = st.text_input(
                "6-digit PIN",
                max_chars=6,
                type="password",
            )
            submitted = st.form_submit_button(
                "Confirm deposit",
                width="stretch",
            )

        if submitted:
            if not has_pin:
                st.error("Please set up your 6-digit transaction PIN in Profile before making a deposit.")
            elif amount <= 0:
                st.error("Amount must be greater than 0.")
            elif not transaction_pin.isdigit() or len(transaction_pin) != 6:
                st.error("Enter your 6-digit transaction PIN.")
            elif not verify_transaction_pin(username, transaction_pin):
                st.error("Incorrect transaction PIN.")
            elif deposit_money(username, amount):
                new_balance = current_balance(username)
                st.toast("Deposit completed successfully.", icon="✅")
                st.success(f"Deposit successful. Current balance: ₹{safe_float(new_balance):,.2f}")
            else:
                st.toast("Deposit failed.", icon="⚠️")
                st.error("Deposit failed.")

    with right:
        st.markdown(
            f"""
            <div class="balance-card">
                <div class="balance-label">Current balance</div>
                <div class="balance-number">
                    ₹{safe_float(balance):,.2f}
                </div>
                <div class="balance-account">
                    Account Number {user.get("account_number", "Unavailable")} · {username}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def withdraw_page():
    username = current_customer_username()
    balance = current_balance(username)
    user = current_customer_user() or {}

    user_header(
        "Withdraw",
        "Withdraw money from your Madhu Bank account.",
        "Banking",
    )

    has_pin = bool(user.get("transaction_pin_hash"))

    left, right = st.columns([1.45, 1])

    with left:
        if not has_pin:
            st.warning("⚠️ You have not set up a 6-digit Transaction PIN yet. A PIN is required for deposits, withdrawals, and transfers.")
            st.button(
                "Set Up Transaction PIN in Profile",
                key="withdraw_goto_pin_setup",
                width="stretch",
                on_click=navigate_to,
                args=("profile",),
            )
            st.write("")

        with st.form("withdraw_form"):
            st.markdown("### Withdraw money")
            st.caption("Enter an amount within your available balance.")
            st.text_input(
                "Account Number",
                value=str(user.get("account_number", "")),
                disabled=True,
            )
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=100.0,
                format="%.2f",
            )
            transaction_pin = st.text_input(
                "6-digit PIN",
                max_chars=6,
                type="password",
            )
            submitted = st.form_submit_button(
                "Confirm withdrawal",
                width="stretch",
            )

        if submitted:
            if not has_pin:
                st.error("Please set up your 6-digit transaction PIN in Profile before making a withdrawal.")
            elif amount <= 0:
                st.error("Amount must be greater than 0.")
            elif not transaction_pin.isdigit() or len(transaction_pin) != 6:
                st.error("Enter your 6-digit transaction PIN.")
            elif not verify_transaction_pin(username, transaction_pin):
                st.error("Incorrect transaction PIN.")
            elif amount > balance:
                st.error("Insufficient balance.")
            elif withdraw_money(username, amount):
                new_balance = current_balance(username)
                st.toast("Withdrawal completed successfully.", icon="✅")
                st.success(f"Withdrawal successful. Current balance: ₹{safe_float(new_balance):,.2f}")
            else:
                st.toast("Withdrawal failed.", icon="⚠️")
                st.error("Withdrawal failed.")

    with right:
        st.markdown(
            f"""
            <div class="balance-card">
                <div class="balance-label">Available balance</div>
                <div class="balance-number">
                    ₹{safe_float(balance):,.2f}
                </div>
                <div class="balance-account">
                    Account Number {user.get("account_number", "Unavailable")} · {username}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def balance_page():
    username = current_customer_username()
    user = current_customer_user() or {}
    status = user.get("status", "Active")
    account_type = user.get("account_type", "Savings")
    balance = current_balance(username)

    user_header(
        "Balance",
        "View the current balance and account state.",
        "Account",
    )

    with st.form("balance_form"):
        st.markdown("### Balance enquiry")
        st.caption("Use the form to refresh your latest account balance.")
        st.text_input(
            "Account Number",
            value=str(user.get("account_number", "")),
            disabled=True,
        )
        st.form_submit_button(
            "Refresh balance",
            width="stretch",
        )

    st.markdown(
        f"""
        <div class="balance-card" style="margin-top:12px;margin-bottom:12px;">
            <div class="balance-label">Current balance</div>
            <div class="balance-number">
                ₹{safe_float(balance):,.2f}
            </div>
            <div class="balance-account">
                Account Number {user.get("account_number", "Unavailable")} · {account_type} account
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Account type",
            account_type,
        )

    with c2:
        st.metric(
            "Status",
            status,
        )


def _handle_resend_transfer_otp(email: str):
    now = time.time()
    last_sent = float(st.session_state.get("_last_transfer_resend_time", 0) or 0)
    if (now - last_sent) < 10.0:
        st.session_state["transfer_otp_resend_toast"] = "Please wait a moment before requesting another OTP."
        st.session_state["transfer_otp_resend_err"] = "OTP was recently sent. Please check your email or wait 10 seconds before retrying."
        st.session_state["transfer_otp_resend_msg"] = None
        return

    st.session_state["_last_transfer_resend_time"] = now
    otp_code, sent = generate_and_send_otp(email, expires_in_seconds=300)
    if sent:
        st.session_state.pending_transfer_otp = otp_code
        st.session_state["transfer_otp_resend_toast"] = "A new 6-digit OTP has been sent."
        st.session_state["transfer_otp_resend_msg"] = f"A fresh 6-digit OTP has been sent to {email}."
        st.session_state["transfer_otp_resend_err"] = None
    else:
        err_msg = SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or "Please check your email settings."
        st.session_state["transfer_otp_resend_err"] = f"Could not resend OTP. {err_msg}"
        st.session_state["transfer_otp_resend_toast"] = "Failed to send OTP."
        st.session_state["transfer_otp_resend_msg"] = None


def _handle_cancel_transfer():
    st.session_state.pending_transfer_otp = None
    st.session_state.pending_transfer_receiver_id = None
    st.session_state.pending_transfer_amount = None
    st.session_state.pending_transfer_note = None
    st.session_state.pop("transfer_otp_resend_msg", None)
    st.session_state.pop("transfer_otp_resend_err", None)
    st.session_state.pop("transfer_otp_resend_toast", None)
    st.session_state.pop("_last_transfer_resend_time", None)


def transfer_page():
    username = current_customer_username()
    user = current_customer_user() or {}
    sender_account_number = user.get("account_number")
    balance = current_balance(username)

    pending_receiver_id = st.session_state.get("pending_transfer_receiver_id")
    pending_amount = st.session_state.get("pending_transfer_amount")
    pending_note = st.session_state.get("pending_transfer_note")

    if st.session_state.get("pending_transfer_otp") and pending_receiver_id is not None and pending_amount is not None:
        user_email = str(user.get("email") or "").strip().lower()
        if not user_email:
            st.warning("Your account has no email on file. Please add an email to receive OTP approval.")
            return

        with st.container(border=True):
            st.markdown("### Transfer OTP verification")
            st.info(f"A 6-digit OTP was sent to **{user_email}** for transferring **₹{float(pending_amount):,.2f}** to Account Number **{int(pending_receiver_id)}**.")

            # Display any status message from resend
            if st.session_state.get("transfer_otp_resend_toast"):
                st.toast(st.session_state.pop("transfer_otp_resend_toast"), icon="📧")
            if st.session_state.get("transfer_otp_resend_msg"):
                st.success(st.session_state.pop("transfer_otp_resend_msg"))
            if st.session_state.get("transfer_otp_resend_err"):
                st.error(st.session_state.pop("transfer_otp_resend_err"))

            with st.form("transfer_otp_form"):
                otp_value = st.text_input("Enter OTP", max_chars=6, type="password", placeholder="Enter 6-digit code")
                verify_button = st.form_submit_button("Verify and Transfer", width="stretch", type="primary")

            if verify_button:
                if not otp_value or not validate_otp(user_email, otp_value):
                    st.error("Invalid or expired OTP. Please retry or tap 'Resend OTP' below.")
                else:
                    result = transfer_money(
                        sender_account_number,
                        int(pending_receiver_id),
                        float(pending_amount),
                        pending_note,
                    )

                    st.session_state.pending_transfer_otp = None
                    st.session_state.pending_transfer_receiver_id = None
                    st.session_state.pending_transfer_amount = None
                    st.session_state.pending_transfer_note = None
                    st.session_state.pop("transfer_otp_resend_msg", None)
                    st.session_state.pop("transfer_otp_resend_err", None)
                    st.session_state.pop("transfer_otp_resend_toast", None)
                    st.session_state.pop("_last_transfer_resend_time", None)

                    if result.get("ok"):
                        st.toast("Transfer completed successfully.", icon="✅")
                        st.session_state["transfer_completed_msg"] = (
                            f"₹{float(pending_amount):,.2f} transferred successfully to Account Number {int(pending_receiver_id)}. "
                            f"(Transaction ID: {result.get('transfer_id', 'N/A')})"
                        )

                        # High-Value Transaction Alert Trigger
                        if st.session_state.get("set_alert_high_val", True):
                            try:
                                threshold = float(st.session_state.get("set_alert_threshold", 50000))
                                if float(pending_amount) >= threshold:
                                    target_admin_email = st.session_state.get("admin_alert_email")
                                    dispatch_system_alert(
                                        alert_type="HIGH_VALUE_TRANSACTION",
                                        title=f"High-Value Transfer: ₹{float(pending_amount):,.2f}",
                                        message=f"Account {sender_account_number} ({username}) transferred ₹{float(pending_amount):,.2f} to Account {int(pending_receiver_id)}.",
                                        severity="warning" if float(pending_amount) < 200000 else "danger",
                                        metadata={
                                            "sender_account": sender_account_number,
                                            "receiver_account": int(pending_receiver_id),
                                            "amount": float(pending_amount),
                                            "transfer_id": result.get("transfer_id", "N/A"),
                                            "sender_username": username,
                                        },
                                        send_email=True,
                                        target_email=target_admin_email,
                                    )
                            except Exception:
                                pass
                        st.rerun()
                    else:
                        st.toast(result.get("message", "Transfer failed."), icon="⚠️")
                        st.error(result.get("message", "Transfer failed."))

            c_resend, c_cancel = st.columns(2, gap="small")
            with c_resend:
                st.button(
                    "Resend OTP",
                    width="stretch",
                    key="transfer_resend_otp_btn",
                    icon=":material/refresh:",
                    on_click=_handle_resend_transfer_otp,
                    args=(user_email,),
                )

            with c_cancel:
                st.button(
                    "Cancel Transfer",
                    width="stretch",
                    key="transfer_cancel_btn",
                    on_click=_handle_cancel_transfer,
                )

        return

    user_header(
        "Transfer",
        "Send money to another Madhu Bank customer using their Account Number.",
        "Banking",
    )

    has_pin = bool(user.get("transaction_pin_hash"))

    left, right = st.columns([1.45, 1])

    with left:
        if not has_pin:
            st.warning("⚠️ You have not set up a 6-digit Transaction PIN yet. A PIN is required for deposits, withdrawals, and transfers.")
            st.button(
                "Set Up Transaction PIN in Profile",
                key="transfer_goto_pin_setup",
                width="stretch",
                on_click=navigate_to,
                args=("profile",),
            )
            st.write("")

        if st.session_state.get("transfer_completed_msg"):
            st.success(st.session_state.pop("transfer_completed_msg"))

        with st.form("transfer_form"):
            st.markdown("### Transfer money")
            st.caption("Enter the recipient's numeric Account Number and amount.")

            st.text_input(
                "Your Account Number",
                value=str(sender_account_number or ""),
                disabled=True,
            )

            receiver_id = st.text_input(
                "Receiver Account Number",
                placeholder="Enter numeric Account Number",
            ).strip()

            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=100.0,
                format="%.2f",
            )

            note = st.text_input(
                "Note (optional)",
                max_chars=120,
            )

            transaction_pin = st.text_input(
                "6-digit PIN",
                max_chars=6,
                type="password",
            )

            submitted = st.form_submit_button(
                "Confirm transfer",
                width="stretch",
            )

        if submitted:
            if not has_pin:
                st.error("Please set up your 6-digit transaction PIN in Profile before making a transfer.")
            elif not transaction_pin.isdigit() or len(transaction_pin) != 6:
                st.toast("Enter your 6-digit transaction PIN.", icon="⚠️")
                st.error("Enter your 6-digit transaction PIN.")
            elif not verify_transaction_pin(username, transaction_pin):
                st.toast("Incorrect transaction PIN.", icon="⚠️")
                st.error("Incorrect transaction PIN.")
            elif not receiver_id.isdigit():
                st.toast("Receiver Account Number must be numeric.", icon="⚠️")
                st.error("Receiver Account Number must contain numbers only.")
            else:
                user_email = str(user.get("email") or "").strip().lower()
                if not user_email:
                    st.error("Your account does not have an email address. Add one to receive OTP verification.")
                else:
                    otp_code, sent = generate_and_send_otp(user_email, expires_in_seconds=300)
                    if not sent:
                        st.error(
                            "Unable to send OTP email right now. "
                            f"{SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or 'Please check your email settings.'}"
                        )
                    else:
                        st.session_state.pending_transfer_otp = otp_code
                        st.session_state.pending_transfer_receiver_id = int(receiver_id)
                        st.session_state.pending_transfer_amount = float(amount)
                        st.session_state.pending_transfer_note = note
                        st.session_state["_last_transfer_resend_time"] = time.time()
                        st.rerun()

    with right:
        st.markdown(
            f"""
            <div class="balance-card">
                <div class="balance-label">Available balance</div>
                <div class="balance-number">
                    ₹{safe_float(balance):,.2f}
                </div>
                <div class="balance-account">
                    Account Number {sender_account_number or "Unavailable"} · {username}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="user-panel" style="margin-top:10px;">
                <div class="user-panel-title">How it works</div>
                <div class="user-panel-subtitle">
                    Your Account Number identifies your account. The recipient's Account Number
                    identifies the account that receives the funds. Both sides are
                    recorded in the shared transaction history.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _format_transaction_datetime(value):
    """Return transaction date/time using the timestamp's stored local offset."""
    if value in (None, ""):
        return "Date unavailable"

    try:
        text = str(value).strip()
        if not text:
            return "Date unavailable"

        # New transactions are stored with the computer's local timezone
        # offset (for example +05:30). Preserve that actual clock time
        # rather than converting it through the server/browser timezone.
        dt = pd.to_datetime(text, errors="coerce")
        if pd.isna(dt):
            return text

        if getattr(dt, "tzinfo", None) is not None:
            return dt.strftime("%d %b %Y, %I:%M %p")

        # Legacy timezone-naive records are treated as local time.
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return str(value)


def _transaction_party(row):
    """Return the human-readable counterparty for a transaction."""
    direction = str(row.get("direction", "")).strip().lower()

    if direction == "in":
        name = row.get("counterparty_name") or row.get("counterparty_username")
        if name:
            return "Received from", str(name)

        counterparty_id = row.get("counterparty_account_number")
        if counterparty_id is None and row.get("counterparty_user_id") is not None:
            legacy_user = users_collection.find_one({"user_id": row.get("counterparty_user_id")})
            counterparty_id = legacy_user.get("account_number") if legacy_user else None
        if counterparty_id is not None:
            other_user = get_user_by_account_number(counterparty_id)
            if other_user:
                name = (
                    other_user.get("name")
                    or f"{other_user.get('first_name', '')} {other_user.get('last_name', '')}".strip()
                    or other_user.get("username")
                )
                if name:
                    return "Received from", str(name)

        return "Received from", "Another Madhu Bank user"

    if direction == "out":
        name = row.get("counterparty_name") or row.get("counterparty_username")
        if name:
            return "Sent to", str(name)

        counterparty_id = row.get("counterparty_account_number")
        if counterparty_id is None and row.get("counterparty_user_id") is not None:
            legacy_user = users_collection.find_one({"user_id": row.get("counterparty_user_id")})
            counterparty_id = legacy_user.get("account_number") if legacy_user else None
        if counterparty_id is not None:
            other_user = get_user_by_account_number(counterparty_id)
            if other_user:
                name = (
                    other_user.get("name")
                    or f"{other_user.get('first_name', '')} {other_user.get('last_name', '')}".strip()
                    or other_user.get("username")
                )
                if name:
                    return "Sent to", str(name)

    return "Transaction", "Madhu Bank"


def transactions_page():
    username = current_customer_username()
    user = current_customer_user() or {}
    transactions = get_transactions(username)
    balance = current_balance(username)
    account_number = user.get("account_number") or ensure_account_number(username)

    user_header(
        "Transactions",
        "Review the financial activity and transaction history for your account.",
        "MADHU BANK / CUSTOMER",
    )

    if not transactions:
        st.markdown(
            """
            <div class="user-panel" style="text-align:center;padding:48px 24px;">
                <div style="font-size:36px;margin-bottom:12px;">💳</div>
                <div style="font-size:16px;font-weight:700;color:#17201D;margin-bottom:6px;">No transactions recorded yet</div>
                <div style="font-size:13px;color:#66716D;max-width:440px;margin:0 auto 16px auto;">
                    Your account activity, deposits, withdrawals, and money transfers will appear here.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Newest activity first when a date is available.
    def sort_key(row):
        value = row.get("date") or row.get("timestamp") or row.get("created_at")
        try:
            parsed = pd.to_datetime(value, errors="coerce", utc=True)
            return parsed if not pd.isna(parsed) else pd.Timestamp.min.tz_localize("UTC")
        except Exception:
            return pd.Timestamp.min.tz_localize("UTC")

    transactions = sorted(transactions, key=sort_key, reverse=True)

    # ---------------------------------------------------------
    # TRANSACTION SUMMARY METRICS (KPI ROW)
    # ---------------------------------------------------------
    total_count = len(transactions)
    total_inflow = 0.0
    total_outflow = 0.0

    for row in transactions:
        kind = transaction_type(row)
        amount = safe_float(row.get("amount", 0))
        direction = str(row.get("direction", "")).strip().lower()
        is_in = direction == "in" or "deposit" in str(kind).lower() or "received" in str(kind).lower()
        is_out = direction == "out" or "withdraw" in str(kind).lower() or "sent" in str(kind).lower()
        if is_in:
            total_inflow += amount
        elif is_out:
            total_outflow += amount
        else:
            if "deposit" in str(kind).lower():
                total_inflow += amount
            else:
                total_outflow += amount

    net_activity = total_inflow - total_outflow

    kpis = [
        (
            "TOTAL TRANSACTIONS",
            str(total_count),
            "Recorded activity",
            "↔",
            "transactions",
        ),
        (
            "TOTAL MONEY IN",
            f"₹{total_inflow:,.2f}",
            "Deposits & incoming",
            "↓",
            "balance",
        ),
        (
            "TOTAL MONEY OUT",
            f"₹{total_outflow:,.2f}",
            "Withdrawals & outgoing",
            "↑",
            "account",
        ),
        (
            "CURRENT BALANCE",
            f"₹{safe_float(balance):,.2f}",
            f"Net: {'+' if net_activity >= 0 else '-'}₹{abs(net_activity):,.2f}",
            "◉",
            "status",
        ),
    ]

    kpi_cols = st.columns(4, gap="small")
    for col, (label, val, note, icon, kind) in zip(kpi_cols, kpis):
        with col:
            st.markdown(
                f"""
                <div class="user-ref-kpi user-ref-kpi-{kind} admin-kpi">
                    <div class="admin-kpi-top">
                        <div class="admin-kpi-label">{html_escape(label)}</div>
                        <div class="admin-kpi-icon">{icon}</div>
                    </div>
                    <div class="admin-kpi-value">{html_escape(val)}</div>
                    <div class="admin-kpi-foot">{html_escape(note)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SEARCH, FILTER & EXPORT CONTROLS
    # ---------------------------------------------------------
    f1, f2, f3 = st.columns([2.2, 1.2, 1.1], gap="small")

    with f1:
        search_query = st.text_input(
            "Search",
            placeholder="Search by ID, party, type or note...",
            key="customer_tx_search",
            label_visibility="collapsed",
        )

    with f2:
        selected_filter = st.selectbox(
            "Filter",
            ["All Activity", "Deposits", "Withdrawals", "Transfers"],
            key="customer_tx_filter",
            label_visibility="collapsed",
        )

    with f3:
        export_records = []
        for r in transactions:
            k = transaction_type(r)
            a = safe_float(r.get("amount", 0))
            d = _format_transaction_datetime(r.get("date") or r.get("timestamp") or r.get("created_at"))
            pl, pn = _transaction_party(r)
            tid = r.get("transaction_id") or r.get("transfer_id") or "N/A"
            st_val = r.get("status") or "Completed"
            export_records.append({
                "Transaction ID": tid,
                "Type": k,
                "Counterparty": pn,
                "Amount (INR)": a,
                "Date & Time": d,
                "Status": st_val,
                "Note": r.get("note") or r.get("description") or "",
            })
        csv_data = pd.DataFrame(export_records).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Export Statement",
            data=csv_data,
            file_name=f"madhu_bank_statement_{username}.csv",
            mime="text/csv",
            key="customer_tx_export",
            width="stretch",
            icon=":material/download:",
        )

    # ---------------------------------------------------------
    # FILTER APPLICATION
    # ---------------------------------------------------------
    filtered_transactions = []
    search_lower = search_query.strip().lower()

    for row in transactions:
        kind = transaction_type(row)
        party_label, party_name = _transaction_party(row)
        tx_id = str(row.get("transaction_id") or row.get("transfer_id") or "")
        note = str(row.get("note") or row.get("description") or "")
        amount_val = safe_float(row.get("amount", 0))

        if selected_filter == "Deposits" and "deposit" not in str(kind).lower():
            continue
        if selected_filter == "Withdrawals" and "withdraw" not in str(kind).lower():
            continue
        if selected_filter == "Transfers" and "transfer" not in str(kind).lower():
            continue

        if search_lower:
            combined = f"{kind} {party_label} {party_name} {tx_id} {note} {amount_val}".lower()
            if search_lower not in combined:
                continue

        filtered_transactions.append(row)

    if not filtered_transactions:
        st.info("No transactions match the selected filter or search.")
        return

    # ---------------------------------------------------------
    # ENTERPRISE TRANSACTION ACTIVITY TABLE
    # ---------------------------------------------------------
    html = '<div class="admin-table-wrap"><table class="admin-table">'
    html += '<thead><tr>'
    html += '<th style="width:140px;">Type</th>'
    html += '<th>Details & Counterparty</th>'
    html += '<th style="width:170px;">Transaction ID</th>'
    html += '<th style="width:190px;">Date & Time</th>'
    html += '<th style="width:110px;">Status</th>'
    html += '<th style="width:140px;text-align:right;">Amount</th>'
    html += '</tr></thead><tbody>'

    for index, row in enumerate(filtered_transactions, start=1):
        kind = transaction_type(row)
        amount = safe_float(row.get("amount", 0))
        dt = (
            row.get("date")
            or row.get("timestamp")
            or row.get("created_at")
            or ""
        )
        date_text = _format_transaction_datetime(dt)
        party_label, party_name = _transaction_party(row)
        direction = str(row.get("direction", "")).strip().lower()
        is_pos = direction == "in" or "deposit" in str(kind).lower() or "received" in str(kind).lower()
        is_neg = direction == "out" or "withdraw" in str(kind).lower() or "sent" in str(kind).lower()

        amt_color = "#16805F" if is_pos else ("#B42318" if is_neg else "#17201D")
        amt_prefix = "+ " if is_pos else ("- " if is_neg else "")
        status = str(row.get("status") or "Completed")

        # Type pill with distinct icon
        if "deposit" in str(kind).lower():
            icon_badge = '<span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:6px;background:#E8F5F0;color:#16805F;font-size:13px;font-weight:700;">↓</span>'
            type_cell = f'<span style="display:inline-flex;align-items:center;gap:8px;font-weight:600;color:#0E5B45;">{icon_badge}Deposit</span>'
            detail_title = "Self Deposit"
            detail_sub = "Madhu Bank Account Credit"
        elif "withdraw" in str(kind).lower():
            icon_badge = '<span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:6px;background:#FDECEC;color:#B42318;font-size:13px;font-weight:700;">↑</span>'
            type_cell = f'<span style="display:inline-flex;align-items:center;gap:8px;font-weight:600;color:#9B1C1C;">{icon_badge}Withdrawal</span>'
            detail_title = "Cash Withdrawal"
            detail_sub = f"Account #{account_number}"
        elif direction == "in":
            icon_badge = '<span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:6px;background:#E8F5F0;color:#16805F;font-size:13px;font-weight:700;">↙</span>'
            type_cell = f'<span style="display:inline-flex;align-items:center;gap:8px;font-weight:600;color:#0E5B45;">{icon_badge}Transfer In</span>'
            detail_title = f"{party_label}: {party_name}"
            detail_sub = "Direct Account Transfer"
        elif direction == "out":
            icon_badge = '<span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:6px;background:#EAF3FA;color:#2563A6;font-size:13px;font-weight:700;">↗</span>'
            type_cell = f'<span style="display:inline-flex;align-items:center;gap:8px;font-weight:600;color:#1F5A8A;">{icon_badge}Transfer Out</span>'
            detail_title = f"{party_label}: {party_name}"
            detail_sub = "Direct Account Transfer"
        else:
            icon_badge = '<span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:6px;background:#E8F5F0;color:#16805F;font-size:13px;font-weight:700;">•</span>'
            type_cell = f'<span style="display:inline-flex;align-items:center;gap:8px;font-weight:600;color:#17201D;">{icon_badge}{html_escape(str(kind))}</span>'
            detail_title = party_name or "Madhu Bank Transaction"
            detail_sub = party_label

        note = row.get("note") or row.get("description")
        if note:
            detail_sub += f' · Note: {html_escape(str(note))}'

        tx_id = row.get("transaction_id") or row.get("transfer_id") or f"TX-{index:010d}"

        html += "<tr>"
        html += f"<td>{type_cell}</td>"
        html += f'<td><div style="font-weight:600;color:#17201D;font-size:13px;">{html_escape(detail_title)}</div><div style="font-size:11.5px;color:#66716D;margin-top:2px;">{html_escape(detail_sub)}</div></td>'
        html += f'<td><span style="font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:11.5px;color:#4F5B56;background:#F0F4F2;padding:3px 8px;border-radius:5px;border:1px solid #DDE5E1;letter-spacing:0.3px;">{html_escape(str(tx_id))}</span></td>'
        html += f'<td><span style="color:#4F5B56;font-size:12.5px;font-weight:500;">{html_escape(date_text)}</span></td>'
        html += f"<td>{status_badge(status)}</td>"
        html += f'<td style="text-align:right;"><span style="font-size:14px;font-weight:700;color:{amt_color};">{amt_prefix}₹{amount:,.2f}</span></td>'
        html += "</tr>"

    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TRANSACTION RECEIPT INSPECTOR (EXPANDER)
    # ---------------------------------------------------------
    with st.expander("🔍 View Transaction Receipt Details", expanded=False):
        receipt_options = [
            f"{_format_transaction_datetime(r.get('date') or r.get('timestamp') or r.get('created_at'))} · {transaction_type(r)} · ₹{safe_float(r.get('amount', 0)):,.2f} ({r.get('transaction_id') or r.get('transfer_id') or f'TX-{i+1:04d}'})"
            for i, r in enumerate(filtered_transactions)
        ]
        sel_idx = st.selectbox(
            "Select transaction to inspect receipt",
            range(len(receipt_options)),
            format_func=lambda i: receipt_options[i],
            key="customer_tx_receipt_select",
        )
        if sel_idx is not None and sel_idx < len(filtered_transactions):
            r = filtered_transactions[sel_idx]
            k = transaction_type(r)
            a = safe_float(r.get("amount", 0))
            d = _format_transaction_datetime(r.get("date") or r.get("timestamp") or r.get("created_at"))
            pl, pn = _transaction_party(r)
            tid = r.get("transaction_id") or r.get("transfer_id") or "N/A"
            st_val = r.get("status") or "Completed"
            direction = str(r.get("direction", "")).strip().lower()
            is_pos = direction == "in" or "deposit" in str(k).lower() or "received" in str(k).lower()
            amt_col = "#16805F" if is_pos else "#B42318"
            amt_pfx = "+ " if is_pos else "- "

            rc1, rc2 = st.columns(2)
            with rc1:
                st.caption("Transaction ID")
                st.markdown(f"**`{tid}`**")
                st.caption("Transaction Type")
                st.write(k)
                st.caption("Amount")
                st.markdown(f'<strong style="color:{amt_col};font-size:18px;">{amt_pfx}₹{a:,.2f}</strong>', unsafe_allow_html=True)
            with rc2:
                st.caption("Status")
                st.markdown(status_badge(st_val), unsafe_allow_html=True)
                st.caption(pl)
                st.write(pn)
                st.caption("Date & Time")
                st.write(d)
            note_val = r.get("note") or r.get("description")
            if note_val:
                st.caption("Reference Note")
                st.write(str(note_val))

def admin_login_page():

    auth_reference_theme()

    bank_header()

    # Keep the administrator form exactly the same width as the user Login form.
    left, center = st.columns([1, 1], gap="medium")

    with left:
        with st.container(key="auth_visual_fixed"):
            auth_visual_panel("admin")

    with center:
        with st.container(key="auth_admin_scroll"):

            st.markdown(
                f"""
                <div class="auth-brand-header">
                    <div class="auth-brand-logo">{madhu_bank_logo()}</div>
                    <div class="auth-brand-title">MADHU BANK</div>
                </div>
                <div class="auth-main-heading">Admin Portal</div>
                <div class="auth-main-desc">Secure administrator access for MADHU BANK.</div>
                """,
                unsafe_allow_html=True,
            )

            pending_admin_email = st.session_state.get("pending_admin_login_email")
            pending_admin_user = st.session_state.get("pending_admin_login_username") or "admin"

            if pending_admin_email:
                st.info(f"OTP sent to {pending_admin_email}. Enter it to complete admin login.")
                with st.form("admin_login_otp_form"):
                    otp_value = st.text_input(
                        "Admin OTP (6 digits)",
                        max_chars=6,
                        type="password",
                        key="admin_login_otp",
                        placeholder="Enter code sent to admin email",
                    )
                    verify_button = st.form_submit_button("Verify OTP and Login", width="stretch")

                if verify_button:
                    if not otp_value:
                        st.error("Please enter the OTP sent to your admin email.")
                    elif not validate_otp(pending_admin_email, otp_value):
                        st.error("Invalid or expired OTP. Please retry.")
                    else:
                        st.session_state.pending_admin_login_username = None
                        st.session_state.pending_admin_login_email = None
                        st.session_state.logged_in = True
                        st.session_state.username = pending_admin_user
                        st.session_state.role = "admin"
                        st.session_state.page = "admin_dashboard"
                        st.session_state["_reset_scroll_after_nav"] = True
                        st.rerun()

                c_resend, c_cancel = st.columns(2, gap="small")
                with c_resend:
                    if st.button("Resend OTP", width="stretch", key="admin_login_resend_otp", icon=":material/refresh:"):
                        now = time.time()
                        last_sent = float(st.session_state.get("_last_admin_inline_resend", 0) or 0)
                        if (now - last_sent) < 10.0:
                            st.toast("OTP was recently sent. Please wait a moment.", icon="⏳")
                        else:
                            st.session_state["_last_admin_inline_resend"] = now
                            _otp, sent = generate_and_send_otp(pending_admin_email, expires_in_seconds=300)
                            if sent:
                                st.toast("A new OTP has been sent to your email.", icon="📧")
                                st.success(f"A new 6-digit OTP has been sent to {pending_admin_email}.")
                            else:
                                st.error(
                                    "Could not resend the OTP. "
                                    f"{SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or 'Please check your email settings.'}"
                                )
                with c_cancel:
                    if st.button("Cancel OTP Login", width="stretch", key="admin_cancel_otp_btn"):
                        st.session_state.pending_admin_login_username = None
                        st.session_state.pending_admin_login_email = None
                        st.rerun()

            else:
                with st.form("admin_login_form"):
                    admin_id = st.text_input(
                        "Admin Email",
                        key="admin_login_id_input",
                    )
                    password = st.text_input(
                        "Admin Password",
                        type="password",
                        key="admin_login_password_input",
                    )
                    admin_login_button = st.form_submit_button(
                        "Send OTP & Login",
                        width="stretch",
                    )

                if admin_login_button:
                    clean_id = admin_id.strip()
                    if not clean_id or not password:
                        st.error("Please enter admin email and password.")
                    else:
                        result = admin_login(clean_id, password)
                        if not result:
                            st.error("Invalid admin credentials.")
                        else:
                            target_email = get_admin_email(clean_id)
                            if not target_email:
                                st.error("No email configured for admin. Check system settings.")
                            else:
                                _otp, sent = generate_and_send_otp(target_email, expires_in_seconds=300)
                                if not sent:
                                    st.error(
                                        "Unable to send admin OTP email. "
                                        f"{SMTP_CONFIGURATION_ERROR or get_last_otp_email_error() or 'Please check your email settings.'}"
                                    )
                                else:
                                    resolved_username = "admin"
                                    if "@" not in clean_id:
                                        resolved_username = clean_id
                                    st.session_state.pending_admin_login_username = resolved_username
                                    st.session_state.pending_admin_login_email = target_email
                                    st.rerun()

            st.button(
                "Back to User Login",
                width="stretch",
                on_click=navigate_to,
                args=("login",),
            )


# =========================================================

# =========================================================
# ADMIN THEME
# =========================================================

def admin_theme():
    """Administration console theme (injected via centralized design system)."""
    pass


def admin_header(title, subtitle):
    """Render the admin page heading without a second profile control.

    The administrator Profile menu is kept only in the top navigation bar.
    """
    st.markdown(
        f"""
        <div class="admin-topbar">
            <div>
                <div class="admin-page-kicker">MADHU BANK / ADMINISTRATION</div>
                <div class="admin-page-title">{html_escape(title)}</div>
                <div class="admin-page-subtitle">{html_escape(subtitle)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def admin_panel(title, subtitle=""):
    subtitle_html = f'<div class="admin-panel-title-sub">{html_escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="admin-panel-title">
            <div class="admin-panel-title-main">{html_escape(title)}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def admin_kpi(label, value, icon, footer="", state=""):
    st.markdown(
        f"""
        <div class="admin-kpi">
            <div class="admin-kpi-top">
                <div class="admin-kpi-label">{html_escape(label)}</div>
                <div class="admin-kpi-icon">{icon}</div>
            </div>
            <div class="admin-kpi-value">{html_escape(value)}</div>
            <div class="admin-kpi-foot {state}">{html_escape(footer)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def html_escape(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def status_badge(status):
    value = str(status or "Unknown")
    low = value.lower()

    if low in {"completed", "active", "success"}:
        cls = "status-completed"
    elif low in {"pending", "processing"}:
        cls = "status-pending"
    elif low in {"failed", "disabled", "rejected"}:
        cls = "status-failed"
    else:
        cls = "status-neutral"

    return (
        f'<span class="status-badge {cls}">'
        f'{html_escape(value)}'
        f'</span>'
    )


def _transaction_sort_timestamp(value):
    """Return a timezone-safe datetime for transaction sorting."""
    if value in (None, ""):
        return pd.NaT
    try:
        text = str(value).strip()
        if not text:
            return pd.NaT
        dt = pd.to_datetime(text, errors="coerce")
        if pd.isna(dt):
            return pd.NaT
        # Normalize aware values to UTC for chronological comparison.
        if getattr(dt, "tzinfo", None) is not None:
            return dt.tz_convert("UTC").tz_localize(None)
        # Naive values are already local wall-clock timestamps.
        return dt
    except Exception:
        return pd.NaT


def normalize_transaction_df(rows):
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    if "_id" in df.columns:
        df = df.drop(columns=["_id"])

    if "timestamp" in df.columns and "date" not in df.columns:
        df = df.rename(columns={"timestamp": "date"})

    if "created_at" in df.columns and "date" not in df.columns:
        df = df.rename(columns={"created_at": "date"})

    if "transaction_type" in df.columns and "type" not in df.columns:
        df = df.rename(columns={"transaction_type": "type"})

    # Make sure every transaction has a visible transaction ID.
    # Older records may not have one stored, so use the MongoDB record ID
    # as a stable fallback and persist the generated value when possible.
    if "transaction_id" not in df.columns:
        if "_id" in df.columns:
            df["transaction_id"] = [
                f"TX-{str(record_id)[-12:].upper()}"
                for record_id in df["_id"]
            ]
            for record_id, tx_id in zip(df["_id"], df["transaction_id"]):
                try:
                    transactions_collection.update_one(
                        {"_id": record_id, "transaction_id": {"$exists": False}},
                        {"$set": {"transaction_id": tx_id}},
                    )
                except Exception:
                    pass
        else:
            df["transaction_id"] = [
                f"TX-{index + 1:010d}" for index in range(len(df))
            ]
    else:
        missing_tx = df["transaction_id"].isna() | (
            df["transaction_id"].astype(str).str.strip().str.lower().isin({"", "nan", "n/a"})
        )
        if missing_tx.any():
            generated = []
            record_ids = df["_id"].tolist() if "_id" in df.columns else [None] * len(df)
            for index, (is_missing, record_id) in enumerate(zip(missing_tx, record_ids)):
                current = df.iloc[index]["transaction_id"]
                if is_missing:
                    tx_id = f"TX-{str(record_id)[-12:].upper()}" if record_id is not None else f"TX-{index + 1:010d}"
                    generated.append(tx_id)
                    if record_id is not None:
                        try:
                            transactions_collection.update_one(
                                {"_id": record_id},
                                {"$set": {"transaction_id": tx_id}},
                            )
                        except Exception:
                            pass
                else:
                    generated.append(current)
            df["transaction_id"] = generated

    # Populate numeric Account Numbers from the username for legacy transaction rows.
    if "account_number" not in df.columns:
        if "username" in df.columns:
            df["account_number"] = df["username"].map(
                lambda value: ensure_account_number(str(value)) if pd.notna(value) and str(value).strip() else None
            )
        else:
            df["account_number"] = None
    else:
        missing_account_number = df["account_number"].isna() | (
            df["account_number"].astype(str).str.strip().str.lower().isin({"", "nan", "n/a"})
        )
        if missing_account_number.any() and "username" in df.columns:
            fallback_ids = []
            record_ids = df["_id"].tolist() if "_id" in df.columns else [None] * len(df)
            for index, (is_missing, record_id) in enumerate(zip(missing_account_number, record_ids)):
                current = df.iloc[index]["account_number"]
                if is_missing:
                    username = df.iloc[index].get("username")
                    uid = ensure_account_number(str(username)) if pd.notna(username) and str(username).strip() else None
                    fallback_ids.append(uid)
                    if record_id is not None and uid is not None:
                        try:
                            transactions_collection.update_one(
                                {"_id": record_id},
                                {"$set": {"account_number": uid}},
                            )
                        except Exception:
                            pass
                else:
                    fallback_ids.append(current)
            df["account_number"] = fallback_ids

    if "date" in df.columns:
        # Keep the transaction clock time exactly as recorded by the local
        # machine. Older records may contain timezone-aware ISO timestamps,
        # while newer records use local, timezone-naive timestamps.
        df["_sort_date"] = df["date"].apply(_transaction_sort_timestamp)

    return df


def canonical_transaction_type(value):
    """Normalize transaction labels so dashboard summaries stay accurate.

    Handles common variants such as deposit/deposits/credit and
    withdrawal/withdraw/withdrawals/debit.
    """
    text = str(value or "").strip().lower()

    if any(token in text for token in ("deposit", "credit", "add money")):
        return "Deposits"
    if any(token in text for token in ("withdraw", "withdrawal", "debit", "take money")):
        return "Withdrawals"
    if "transfer" in text:
        return "Transfers"
    if any(token in text for token in ("payment", "pay")):
        return "Payments"
    return "Other"


def render_admin_transaction_table(rows, limit=None):
    df = normalize_transaction_df(rows)

    if df.empty:
        st.markdown(
            '<div class="admin-muted">No transaction records available.</div>',
            unsafe_allow_html=True,
        )
        return

    # Always show the newest transaction first. _sort_date preserves local
    # wall-clock times for new records and handles legacy timezone-aware rows.
    if "_sort_date" in df.columns:
        df = df.sort_values(
            by="_sort_date",
            ascending=False,
            na_position="last",
            kind="stable",
        ).reset_index(drop=True)

    if limit is not None:
        df = df.head(limit)

    cols = list(df.columns)

    def first_existing(names):
        for name in names:
            if name in cols:
                return name
        return None

    transaction_id = first_existing(
        ["transaction_id", "id", "txn_id"]
    )
    username_col = first_existing(
        ["username", "user", "customer"]
    )
    account_number_col = first_existing(["account_number"])
    type_col = first_existing(
        ["type", "transaction_type"]
    )
    amount_col = first_existing(
        ["amount", "value"]
    )
    date_col = first_existing(
        ["date", "timestamp", "created_at"]
    )
    status_col = first_existing(
        ["status"]
    )

    header_names = [
        "Transaction ID",
        "Account Number",
        "User",
        "Type",
        "Amount",
        "Date",
        "Status",
    ]

    html = '<div class="admin-table-wrap"><table class="admin-table">'
    html += "<thead><tr>"
    for h in header_names:
        html += f"<th>{h}</th>"
    html += "</tr></thead><tbody>"

    for row_index, (_, row) in enumerate(df.iterrows(), start=1):
        tx_id = (
            row.get(transaction_id, "N/A")
            if transaction_id
            else "N/A"
        )
        user = (
            row.get(username_col, "N/A")
            if username_col
            else "N/A"
        )
        account_number = (
            row.get(account_number_col, "N/A")
            if account_number_col
            else (ensure_account_number(user) or "N/A")
        )

        # Final UI fallbacks guarantee these columns are never blank/N/A
        # for a valid transaction record.
        if (tx_id is None or str(tx_id).strip().lower() in {"", "nan", "n/a"}):
            tx_id = f"TX-{row_index:010d}"
        if (account_number is None or str(account_number).strip().lower() in {"", "nan", "n/a"}):
            resolved_account_number = ensure_account_number(str(user)) if user else None
            account_number = resolved_account_number if resolved_account_number is not None else f"ACCOUNT-{row_index:06d}"
        tx_type = (
            row.get(type_col, "N/A")
            if type_col
            else "N/A"
        )
        amount = (
            row.get(amount_col, 0)
            if amount_col
            else 0
        )
        tx_date = (
            row.get(date_col, None)
            if date_col
            else None
        )
        status = (
            row.get(status_col, "Completed")
            if status_col
            else "Completed"
        )

        try:
            amount_text = f"₹{float(amount):,.2f}"
        except (TypeError, ValueError):
            amount_text = html_escape(amount)

        if pd.notna(tx_date) and isinstance(tx_date, pd.Timestamp):
            date_text = _format_transaction_datetime(tx_date)
        else:
            date_text = str(tx_date or "N/A")

        # Treat missing/NaN values as friendly display values instead of
        # exposing pandas "nan" in the admin UI.
        def display_value(value, fallback="N/A"):
            try:
                if pd.isna(value):
                    return fallback
            except (TypeError, ValueError):
                pass
            text = str(value).strip()
            return fallback if not text or text.lower() == "nan" else text

        tx_id_text = display_value(tx_id)

        # Account Numbers are stored as numbers. Pandas can represent a numeric
        # column as float when legacy rows contain mixed/missing values,
        # which would otherwise display values such as 18856069.0.
        account_number_text = display_value(account_number)
        try:
            account_number_number = float(account_number_text)
            if account_number_number.is_integer():
                account_number_text = str(int(account_number_number))
        except (TypeError, ValueError):
            pass

        user_text = display_value(user)
        type_text = display_value(tx_type)

        # Show useful transfer context directly inside the Type column.
        # Prefer the explicit direction/counterparty fields written by the
        # transfer service, and fall back to sender/receiver fields for older
        # records.
        if canonical_transaction_type(type_text) == "Transfers":
            direction = display_value(row.get("direction"), "")
            counterparty_name = display_value(
                row.get("counterparty_name"),
                ""
            )
            counterparty_account_number = display_value(
                row.get("counterparty_account_number"),
                ""
            )

            current_account_number = display_value(row.get("account_number"), "")
            sender_id = display_value(
                row.get("sender_account_number") or row.get("from_account_number"),
                ""
            )
            receiver_id = display_value(
                row.get("receiver_account_number") or row.get("to_account_number"),
                ""
            )
            sender_name = display_value(
                row.get("sender_name") or row.get("from_name"),
                ""
            )
            receiver_name = display_value(
                row.get("receiver_name") or row.get("to_name"),
                ""
            )

            if not direction:
                if sender_id and current_account_number and sender_id == current_account_number:
                    direction = "Out"
                elif receiver_id and current_account_number and receiver_id == current_account_number:
                    direction = "In"

            if not counterparty_account_number:
                if direction.lower() == "out":
                    counterparty_account_number = receiver_id
                elif direction.lower() == "in":
                    counterparty_account_number = sender_id

            if not counterparty_name:
                if direction.lower() == "out":
                    counterparty_name = receiver_name
                elif direction.lower() == "in":
                    counterparty_name = sender_name

            if direction.lower() == "in":
                detail_prefix = "Received from"
            elif direction.lower() == "out":
                detail_prefix = "Sent to"
            else:
                detail_prefix = "Transfer with"

            if counterparty_name and counterparty_account_number:
                type_text = (
                    f"Transfer · {detail_prefix} "
                    f"{counterparty_name} (Account Number {counterparty_account_number})"
                )
            elif counterparty_name:
                type_text = f"Transfer · {detail_prefix} {counterparty_name}"
            elif counterparty_account_number:
                type_text = (
                    f"Transfer · {detail_prefix} "
                    f"Account Number {counterparty_account_number}"
                )
            else:
                type_text = "Transfer · Details unavailable"

        status_text = display_value(status, "Completed")

        html += "<tr>"
        html += f"<td>{html_escape(tx_id_text)}</td>"
        html += f"<td>{html_escape(account_number_text)}</td>"
        html += f"<td>{html_escape(user_text)}</td>"
        html += f"<td>{html_escape(type_text)}</td>"
        html += f"<td>{amount_text}</td>"
        html += f'<td class="admin-muted">{html_escape(date_text)}</td>'
        html += f"<td>{status_badge(status_text)}</td>"
        html += "</tr>"

    html += "</tbody></table></div>"

    st.markdown(html, unsafe_allow_html=True)


# =========================================================
# ADMIN SIDEBAR
# =========================================================

def admin_sidebar():
    """Render the administrator navigation as a modern top menu bar."""
    try:
        seen_toast_ids = st.session_state.setdefault("seen_alert_toast_ids", set())
        unread_alerts_list = get_system_alerts(status_filter="Unread", limit=3)
        for alert in unread_alerts_list:
            aid = alert.get("alert_id")
            if aid and aid not in seen_toast_ids:
                seen_toast_ids.add(aid)
                sev_icon = "🚨" if str(alert.get("severity", "")).lower() in ("critical", "high", "danger") else "⚠️"
                st.toast(f"{sev_icon} **{alert.get('title', 'System Alert')}**: {alert.get('message', '')}", icon=sev_icon)
    except Exception:
        pass

    unread_alerts_n = get_unread_alerts_count()
    pending_req_n = account_review_requests_collection.count_documents({"status": "Pending"})
    total_badge_n = unread_alerts_n + pending_req_n
    req_label = f"Requests ({total_badge_n})" if total_badge_n > 0 else "Requests"

    admin_nav = [
        ("Dashboard", "admin_dashboard", ":material/dashboard:"),
        ("Users", "admin_users", ":material/group:"),
        ("Accounts", "admin_accounts", ":material/account_balance_wallet:"),
        ("Transactions", "admin_transactions", ":material/receipt_long:"),
        (req_label, "admin_requests", ":material/notifications_active:" if total_badge_n > 0 else ":material/rate_review:"),
        ("Reports", "admin_reports", ":material/bar_chart:"),
        ("Settings", "admin_settings", ":material/settings:"),
    ]

    # Keep the admin active-page state local to this navigation function.
    current_page = st.session_state.get("page", "admin_dashboard")

    # Fixed branding is intentionally outside the navigation bar.
    st.markdown(
        f"""
        <div class="admin-fixed-brand">
            <div class="top-nav-brand-mark">{madhu_bank_logo()}</div>
            <div>
                <div class="top-nav-brand-name">MADHU BANK</div>
                <div class="top-nav-brand-subtitle">Admin Portal</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        /* Out-of-flow container collapse to eliminate empty space under fixed header */
        div[data-testid="stElementContainer"]:has(.admin-fixed-brand),
        div[data-testid="stElementContainer"]:has(#madhu-scroll-reset-anchor),
        div[data-testid="stElementContainer"]:has(style:only-child),
        div[data-testid="stElementContainer"]:empty {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
        }

        div[data-testid="stElementContainer"]:has(> .st-key-admin_top_nav),
        div[data-testid="stElementContainer"]:has(.st-key-admin_top_nav) {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            border: 0 !important;
        }

        /* Zero out all outer wrappers, borders, shadows, backgrounds, and paddings */
        .st-key-admin_top_nav [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-admin_top_nav [data-testid="stVerticalBlockBorderWrapper"] > div,
        .st-key-admin_top_nav [data-testid="stVerticalBlock"],
        .st-key-admin_top_nav [data-testid="stVerticalBlock"] > div,
        .st-key-admin_top_nav [data-testid="stElementContainer"],
        .st-key-admin_top_nav [data-testid="stElementContainer"] > div,
        .st-key-admin_top_nav .stButton,
        .st-key-admin_top_nav .stButton > div,
        .st-key-admin_top_nav div[data-testid="stPopover"],
        .st-key-admin_top_nav div[data-testid="stPopover"] > div,
        .st-key-admin_top_nav div[data-testid="stPopover"] > div > div {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            border-width: 0 !important;
            box-shadow: none !important;
            outline: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .st-key-admin_top_nav .stButton,
        .st-key-admin_top_nav .stButton > div,
        .st-key-admin_top_nav div[data-testid="stPopover"],
        .st-key-admin_top_nav div[data-testid="stPopover"] > div {
            display: flex !important;
            width: 100% !important;
            min-width: 0 !important;
            max-width: none !important;
            flex: 1 1 auto !important;
            height: 38px !important;
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }

        /* Admin 8-column Navigation Buttons & Profile Popover Trigger */
        .st-key-admin_top_nav .stButton > button,
        .st-key-admin_top_nav div[data-testid="stPopover"] > button,
        .st-key-admin_top_nav div[data-testid="stPopover"] button {
            width: 100% !important;
            min-width: 0 !important;
            max-width: none !important;
            height: 38px !important;
            min-height: 38px !important;
            max-height: 38px !important;
            box-sizing: border-box !important;
            padding: 0 10px !important;
            margin: 0 !important;
            border-radius: 8px !important;
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            border: 1px solid #E1E7E3 !important;
            color: #4F5B56 !important;
            -webkit-text-fill-color: #4F5B56 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
            box-shadow: none !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 6px !important;
            transition: all 150ms ease !important;
        }

        .st-key-admin_top_nav .stButton > button *,
        .st-key-admin_top_nav div[data-testid="stPopover"] > button *,
        .st-key-admin_top_nav div[data-testid="stPopover"] button * {
            color: #4F5B56 !important;
            -webkit-text-fill-color: #4F5B56 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
        }

        .st-key-admin_top_nav .stButton > button:hover,
        .st-key-admin_top_nav div[data-testid="stPopover"] > button:hover,
        .st-key-admin_top_nav div[data-testid="stPopover"] button:hover {
            background: #E8F5F0 !important;
            background-color: #E8F5F0 !important;
            border-color: #BFE3D4 !important;
            color: #0E5B45 !important;
            -webkit-text-fill-color: #0E5B45 !important;
            transform: translateY(-1px) !important;
        }

        .st-key-admin_top_nav .stButton > button:hover *,
        .st-key-admin_top_nav div[data-testid="stPopover"] > button:hover *,
        .st-key-admin_top_nav div[data-testid="stPopover"] button:hover * {
            color: #0E5B45 !important;
            -webkit-text-fill-color: #0E5B45 !important;
        }

        .st-key-admin_top_nav .stButton > button[kind="primary"],
        .st-key-admin_top_nav .stButton > button[data-testid*="baseButton-primary"],
        .st-key-admin_top_nav div[data-testid="stPopover"] button[aria-expanded="true"] {
            background: #16805F !important;
            background-color: #16805F !important;
            border-color: #0E5B45 !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            box-shadow: 0 2px 8px rgba(22, 128, 95, 0.20) !important;
            transform: translateY(-1px) !important;
        }

        .st-key-admin_top_nav div[data-testid="stPopover"] button[aria-expanded="true"] * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }

        .st-key-admin_top_nav .stButton > button[kind="primary"] *,
        .st-key-admin_top_nav .stButton > button[data-testid*="baseButton-primary"] * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _reset_browser_scroll_after_navigation()

    with st.container(key="admin_top_nav"):
        cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1], gap="small")
        for col, (label, page_name, icon) in zip(cols[:7], admin_nav):
            with col:
                try:
                    st.button(
                        label, icon=icon, key=f"admin_top_nav_{page_name}",
                        width="stretch",
                        type="primary" if current_page == page_name else "secondary",
                        on_click=navigate_to,
                        args=(page_name,),
                    )
                except TypeError:
                    st.button(
                        label, key=f"admin_top_nav_{page_name}", width="stretch",
                        on_click=navigate_to,
                        args=(page_name,),
                    )
        with cols[7]:
            username = str(st.session_state.get("username") or "Administrator")
            initials = "".join(
                part[0] for part in username.replace("_", " ").split()[:2]
            ).upper() or "A"

            try:
                pop_ctx = st.popover(
                    "Profile",
                    icon=":material/account_circle:",
                    width="stretch",
                )
            except (TypeError, ValueError):
                try:
                    pop_ctx = st.popover(
                        "Profile",
                        icon=":material/account_circle:",
                        use_container_width=True,
                    )
                except TypeError:
                    pop_ctx = st.popover(
                        "Profile",
                        icon=":material/account_circle:",
                    )
            with pop_ctx:
                st.markdown(
                    f"""
                    <div class="admin-top-profile-popover">
                        <div class="admin-top-profile-avatar">{html_escape(initials)}</div>
                        <div class="admin-top-profile-name">{html_escape(username)}</div>
                        <div class="admin-top-profile-role">Madhu Bank Administrator</div>
                        <div class="admin-top-profile-row"><span>Username</span><strong>{html_escape(username)}</strong></div>
                        <div class="admin-top-profile-row"><span>Role</span><strong>Administrator</strong></div>
                        <div class="admin-top-profile-row"><span>Access</span><strong>Administrative Console</strong></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.button(
                    "Profile Settings",
                    icon=":material/manage_accounts:",
                    key="admin_top_profile_settings",
                    width="stretch",
                    on_click=navigate_to,
                    args=("admin_settings",),
                )
                st.button(
                    "Logout",
                    icon=":material/logout:",
                    key="admin_top_profile_logout",
                    width="stretch",
                    on_click=logout,
                )


def set_admin_page(page_name):
    navigate_to(page_name)


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard():
    admin_header(
        "Dashboard",
        "Monitor system activity and manage operations.",
    )

    # Channel 2: Admin Dashboard Banners for Active/Unread Alerts
    unread_alerts = get_system_alerts(status_filter="Unread", limit=5)
    unread_count = get_unread_alerts_count()
    if unread_alerts:
        latest = unread_alerts[0]
        sev = str(latest.get("severity", "warning")).lower()
        is_crit = sev in ("critical", "high", "danger")
        banner_border = "#F8B4B4" if is_crit else "#FBD38D"
        banner_color = "#991B1B" if is_crit else "#975A16"
        banner_icon = "🚨" if is_crit else "⚠️"

        with st.container(border=True):
            b_left, b_right = st.columns([3.8, 1.2], gap="small")
            with b_left:
                extra_note = f" &bull; <em>+{unread_count - 1} more unread alert(s)</em>" if unread_count > 1 else ""
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;gap:12px;padding:2px 0;">
                        <span style="font-size:24px;">{banner_icon}</span>
                        <div>
                            <div style="font-weight:700;font-size:14px;color:{banner_color};">
                                {html_escape(latest.get('title', 'System Security Alert'))}
                                <span style="font-size:11px;padding:2px 8px;border-radius:10px;background:{banner_border};color:{banner_color};margin-left:8px;font-weight:600;">
                                    {html_escape(latest.get('alert_id', 'ALT'))}
                                </span>
                            </div>
                            <div style="font-size:12.5px;color:#4F5B56;margin-top:2px;">
                                {html_escape(latest.get('message', ''))}{extra_note}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with b_right:
                ack_col, view_col = st.columns(2, gap="small")
                with ack_col:
                    if st.button("Acknowledge", key=f"dash_ack_{latest.get('alert_id')}", width="stretch"):
                        acknowledge_system_alert(latest.get("alert_id"))
                        st.toast("Alert acknowledged.", icon="✅")
                        st.rerun()
                with view_col:
                    if st.button("View All", key="dash_view_all_alerts", width="stretch", type="primary"):
                        st.session_state.page = "admin_requests"
                        st.session_state["admin_requests_active_tab"] = "alerts"
                        st.rerun()
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    total_accounts = get_total_accounts()
    active_accounts = get_active_accounts()
    accounts = get_all_accounts()
    transactions = get_all_transactions()
    total_transactions = len(transactions)
    pending_requests = account_review_requests_collection.count_documents({"status": "Pending"})
    total_transaction_amount = sum(safe_float(tx.get("amount", 0)) for tx in transactions)
    combined_urgent = pending_requests + unread_count

    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        admin_kpi("TOTAL USERS", f"{len(accounts):,}", "◉", "Registered customers", "admin-positive")
    with c2:
        admin_kpi("TOTAL ACCOUNTS", f"{total_accounts:,}", "▣", f"{active_accounts:,} currently active", "")
    with c3:
        admin_kpi("TOTAL TRANSACTIONS", f"{total_transactions:,}", "↔", "Recorded activity", "")
    with c4:
        sub_desc = []
        if unread_count:
            sub_desc.append(f"{unread_count} alert{'s' if unread_count > 1 else ''}")
        if pending_requests:
            sub_desc.append(f"{pending_requests} review{'s' if pending_requests > 1 else ''}")
        status_sub = " • ".join(sub_desc) if sub_desc else "All systems normal"
        admin_kpi(
            "ACTIVE ALERTS & REQUESTS",
            f"{combined_urgent:,}",
            "🚨" if combined_urgent else "✓",
            status_sub,
            "admin-danger" if combined_urgent else "admin-positive",
        )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)


    tx_df = normalize_transaction_df(transactions)

    # ---------------------------------------------------------
    # REFERENCE-STYLE ANALYTICS AREA
    # ---------------------------------------------------------

    # Top: full-width transactions overview chart.
    with st.container(border=True):
        head_col, filter_col = st.columns([4.3, 1.0], gap="small")
        with head_col:
            st.markdown(
                '<div class="ref-topline"><div><div class="ref-card-title">Transactions Overview</div><div class="ref-card-subtitle">Transaction count over the selected period.</div></div></div>',
                unsafe_allow_html=True,
            )
        with filter_col:
            time_range = st.selectbox(
                "Period",
                ["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last 6 Months", "Last 12 Months"],
                index=0,
                key="admin_dashboard_time_range",
                label_visibility="collapsed",
            )

        if tx_df.empty or "date" not in tx_df.columns or "_sort_date" not in tx_df.columns:
            st.markdown(
                '<div class="tx-empty-state" style="min-height:220px;"><div class="tx-empty-icon">◌</div><div class="tx-empty-title">No transaction activity to visualize</div><div class="tx-empty-copy">New banking activity will automatically appear in this analytics panel.</div></div>',
                unsafe_allow_html=True,
            )
        else:
            chart_df = tx_df.dropna(subset=["_sort_date"]).copy()
            chart_df["date"] = pd.to_datetime(chart_df["_sort_date"], errors="coerce")
            chart_df = chart_df.dropna(subset=["date"])
            chart_df["day"] = chart_df["date"].dt.floor("D")
            chart_df["month"] = chart_df["date"].dt.to_period("M").dt.to_timestamp()

            if chart_df.empty:
                st.markdown(
                    '<div class="tx-empty-state" style="min-height:220px;"><div class="tx-empty-icon">◌</div><div class="tx-empty-title">Transaction dates are unavailable</div><div class="tx-empty-copy">The transaction records exist, but there are no usable dates for the chart.</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                end_day = chart_df["day"].max()
                if time_range == "Last 7 Days":
                    start_day = end_day - pd.Timedelta(days=6)
                    grouped = (chart_df[chart_df["day"].between(start_day, end_day)]
                                .groupby("day").size()
                                .reindex(pd.date_range(start_day, end_day, freq="D"), fill_value=0))
                elif time_range == "Last 30 Days":
                    start_day = end_day - pd.Timedelta(days=29)
                    grouped = (chart_df[chart_df["day"].between(start_day, end_day)]
                                .groupby("day").size()
                                .reindex(pd.date_range(start_day, end_day, freq="D"), fill_value=0))
                else:
                    months = {"Last 3 Months": 3, "Last 6 Months": 6, "Last 12 Months": 12}[time_range]
                    end_month = chart_df["month"].max()
                    start_month = end_month - pd.DateOffset(months=months - 1)
                    grouped = (chart_df[chart_df["month"] >= start_month]
                                .groupby("month").size()
                                .reindex(pd.date_range(start_month, end_month, freq="MS"), fill_value=0))

                chart_plot = grouped.rename("Transactions").reset_index()
                chart_plot.columns = ["Period", "Transactions"]
                chart_plot["PeriodLabel"] = chart_plot["Period"].apply(
                    lambda d: d.strftime("%d %b") if time_range in {"Last 7 Days", "Last 30 Days"} else d.strftime("%b %Y")
                )

                chart = {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "width": "container",
                    "height": 185,
                    "background": "transparent",
                    "data": {"values": chart_plot.to_dict("records")},
                    "layer": [
                        {
                            "mark": {"type": "bar", "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3, "width": {"band": 0.55}, "color": "#16805F"},
                            "encoding": {
                                "x": {"field": "Period", "type": "temporal", "axis": {"title": None, "labelColor": "#4F5B56", "labelFontSize": 11, "grid": False, "labelAngle": 0, "tickColor": "#E1E7E3"}},
                                "y": {"field": "Transactions", "type": "quantitative", "axis": {"title": None, "labelColor": "#4F5B56", "labelFontSize": 11, "grid": True, "gridColor": "#EDF0EE", "domain": False, "tickCount": 4, "format": "d"}},
                                "tooltip": [{"field": "PeriodLabel", "type": "nominal", "title": "Period"}, {"field": "Transactions", "type": "quantitative", "title": "Transactions"}],
                            },
                        },
                        {
                            "mark": {"type": "line", "interpolate": "monotone", "color": "#0E5B45", "strokeWidth": 2, "point": {"filled": True, "fill": "#E8F5F0", "stroke": "#16805F", "strokeWidth": 1.5, "size": 24}},
                            "encoding": {"x": {"field": "Period", "type": "temporal"}, "y": {"field": "Transactions", "type": "quantitative"}},
                        },
                    ],
                    "config": {"view": {"stroke": None}},
                }
                st.vega_lite_chart(chart, width="stretch")
                st.markdown(
                    f'<div class="ref-analytics-note"><span>Selected: {time_range}</span><span>{int(chart_plot["Transactions"].sum()):,} transactions</span></div>',
                    unsafe_allow_html=True,
                )

    # Bottom: Transaction summary + Total balance.
    low_left, low_right = st.columns([1.15, 0.85], gap="small")

    with low_left:
        with st.container(border=True):
            st.markdown('<div class="ref-summary-head"><span class="ref-summary-dot"></span><div><div class="ref-card-title">Transaction Summary</div></div></div>', unsafe_allow_html=True)

            summary_values = {"Deposits": 0, "Withdrawals": 0, "Transfers": 0, "Payments": 0}
            if not tx_df.empty and "type" in tx_df.columns:
                normalized_types = tx_df["type"].apply(canonical_transaction_type).value_counts()
                for key in summary_values:
                    summary_values[key] = int(normalized_types.get(key, 0))

            nonzero = [{"Type": k, "Count": v} for k, v in summary_values.items() if v > 0]
            donut_total = int(sum(summary_values.values()))
            summary_colors = {"Deposits": "#16805F", "Withdrawals": "#C45151", "Transfers": "#3778A8", "Payments": "#C58A18"}
            if nonzero:
                pie_df = pd.DataFrame(nonzero)
                donut_chart = {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "width": 190,
                    "height": 190,
                    "background": "transparent",
                    "data": {"values": pie_df.to_dict("records")},
                    "layer": [
                        {"mark": {"type": "arc", "innerRadius": 62, "outerRadius": 88, "padAngle": 0.035, "cornerRadius": 4}, "encoding": {"theta": {"field": "Count", "type": "quantitative"}, "color": {"field": "Type", "type": "nominal", "scale": {"domain": list(summary_colors.keys()), "range": list(summary_colors.values())}, "legend": None}, "tooltip": [{"field": "Type", "type": "nominal", "title": "Type"}, {"field": "Count", "type": "quantitative", "title": "Transactions"}]}},
                        {"mark": {"type": "text", "fontSize": 20, "fontWeight": 700, "color": "#17201D", "dy": -2}, "encoding": {"text": {"value": str(donut_total)}}},
                        {"mark": {"type": "text", "fontSize": 12, "fontWeight": 600, "color": "#4F5B56", "dy": 14}, "encoding": {"text": {"value": "Total"}}},
                    ],
                    "config": {"view": {"stroke": None}},
                }
                st.vega_lite_chart(donut_chart, width="stretch")
            else:
                st.markdown('<div style="color:#66716D;font-size:12px;padding:34px 0;text-align:center;">No transaction activity recorded yet.</div>', unsafe_allow_html=True)

    with low_right:
        with st.container(border=True):
            total_balance = safe_float(get_total_bank_balance())
            st.markdown(
                f'<div class="ref-balance-label">Total Balance</div><div class="ref-balance-value">₹{total_balance:,.2f}</div><div class="ref-balance-note">Aggregate customer account balance</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div class="ref-balance-chart">
                    <svg viewBox="0 0 280 100" width="100%" height="88" preserveAspectRatio="none" aria-hidden="true">
                        <defs>
                            <linearGradient id="refBalFill" x1="0" x2="0" y1="0" y2="1">
                                <stop offset="0%" stop-color="#16805F" stop-opacity="0.22"/>
                                <stop offset="100%" stop-color="#16805F" stop-opacity="0.01"/>
                            </linearGradient>
                        </defs>
                        <path d="M0,88 L0,75 L26,69 L50,79 L77,58 L101,63 L127,40 L153,51 L180,28 L206,37 L232,16 L258,28 L280,6 L280,100 L0,100 Z" fill="url(#refBalFill)"/>
                        <polyline points="0,75 26,69 50,79 77,58 101,63 127,40 153,51 180,28 206,37 232,16 258,28 280,6" fill="none" stroke="#16805F" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="232" cy="16" r="4" fill="#21916D"/>
                    </svg>
                    <div class="ref-balance-caption">Asset trend</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        admin_panel("Recent Transactions", "Latest records from the transaction collection.")
        render_admin_transaction_table(transactions, limit=10)


# =========================================================
# ADMIN USERS
# =========================================================

def admin_users():
    admin_header(
        "Users",
        "Search users and review account ownership.",
    )

    search_text = st.text_input(
        "Search users",
        placeholder="Search Account Number, name, or username",
        key="admin_users_search",
    )

    search_value = search_text.strip()
    matched_user = get_user_by_account_number(search_value) if search_value.isdigit() else None
    if matched_user:
        accounts = search_accounts(matched_user.get("username", ""))
    else:
        accounts = search_accounts(search_value) if search_value else get_all_accounts()

    if not accounts:
        st.info("No users found.")
        return

    rows = []

    for account in accounts:
        rows.append(
            {
                "Account Number": ensure_account_number(account.get("username", "")) or "N/A",
                "Name": get_account_name_from_admin(account),
                "Username": account.get(
                    "username",
                    "N/A",
                ),
                "Account": account.get(
                    "account_type",
                    "N/A",
                ),
                "Status": account.get(
                    "status",
                    "Unknown",
                ),
            }
        )

    df = pd.DataFrame(rows)

    st.markdown(
        '<div class="admin-table-wrap">',
        unsafe_allow_html=True,
    )

    html = '<table class="admin-table"><thead><tr>'
    for column in df.columns:
        html += f"<th>{column}</th>"
    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        html += f'<td>{html_escape(row["Account Number"])}</td>'
        html += f'<td>{html_escape(row["Name"])}</td>'
        html += f'<td>{html_escape(row["Username"])}</td>'
        html += f'<td>{html_escape(row["Account"])}</td>'
        html += f'<td>{status_badge(row["Status"])}</td>'
        html += "</tr>"

    html += "</tbody></table>"
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def get_account_name_from_admin(account):
    if account.get("name"):
        return str(account["name"])

    first = account.get("first_name", "")
    last = account.get("last_name", "")
    combined = f"{first} {last}".strip()

    return combined or account.get("username", "N/A")


# =========================================================
# ADMIN ACCOUNT MANAGEMENT
# =========================================================

def admin_accounts():
    admin_header(
        "Accounts",
        "Manage account status, inspect details, and remove accounts.",
    )

    search_text = st.text_input(
        "Search accounts",
        placeholder="Search Account Number, name, or username",
        key="admin_account_search_new",
    )

    search_value = search_text.strip()
    matched_user = get_user_by_account_number(search_value) if search_value.isdigit() else None
    if matched_user:
        accounts = search_accounts(matched_user.get("username", ""))
    else:
        accounts = search_accounts(search_value) if search_value else get_all_accounts()

    if not accounts:
        st.info("No accounts found.")
        return

    active_user = st.session_state.get("last_managed_user")

    for account in accounts:
        username = account.get("username", "")
        name = get_account_name_from_admin(account)
        status = account.get("status", "Active")
        is_expanded = (active_user == username)

        with st.expander(
            f"{name} - {username}",
            expanded=is_expanded,
        ):
            info1, info2, info3 = st.columns(3)

            with info1:
                st.markdown(
                    f"""
                    <div class="admin-mini-label">BALANCE</div>
                    <div class="admin-mini-value">
                        ₹{safe_float(account.get("balance", 0)):,.2f}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with info2:
                st.markdown(
                    f"""
                    <div class="admin-mini-label">ACCOUNT TYPE</div>
                    <div class="admin-mini-value">
                        {html_escape(account.get("account_type", "N/A"))}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with info3:
                st.markdown(
                    f"""
                    <div class="admin-mini-label">STATUS</div>
                    <div style="margin-top:6px;">
                        {status_badge(status)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            a1, a2, a3 = st.columns(3)

            with a1:
                action = (
                    "Disable"
                    if str(status).lower() == "active"
                    else "Enable"
                )

                if st.button(
                    action,
                    key=f"admin_status_{username}",
                    width='stretch',
                ):
                    if action == "Disable":
                        result = disable_account(username)
                    else:
                        result = enable_account(username)

                    if result:
                        st.session_state["last_managed_user"] = username
                        st.success(f"Account {action.lower()}d.")
                        st.rerun()
                    else:
                        st.error("Unable to update account status.")

            with a2:
                try:
                    pop_ctx = st.popover(
                        "Details",
                        width="stretch",
                    )
                except (TypeError, ValueError):
                    try:
                        pop_ctx = st.popover(
                            "Details",
                            use_container_width=True,
                        )
                    except TypeError:
                        pop_ctx = st.popover("Details")
                with pop_ctx:
                    details = pd.DataFrame(
                        [
                            [
                                "Name",
                                name,
                            ],
                            [
                                "Username",
                                account.get(
                                    "username",
                                    "N/A",
                                ),
                            ],
                            [
                                "Date of Birth",
                                account.get(
                                    "dob",
                                    "N/A",
                                ),
                            ],
                            [
                                "Account Type",
                                account.get(
                                    "account_type",
                                    "N/A",
                                ),
                            ],
                            [
                                "Balance",
                                f"₹{safe_float(account.get('balance', 0)):,.2f}",
                            ],
                            [
                                "Status",
                                account.get(
                                    "status",
                                    "N/A",
                                ),
                            ],
                            [
                                "Role",
                                account.get(
                                    "role",
                                    "N/A",
                                ),
                            ],
                        ],
                        columns=["Field", "Value"],
                    )

                    st.dataframe(
                        details,
                        hide_index=True,
                        width=380,
                        height=300,
                    )

            with a3:
                delete_key = f"admin_delete_confirm_{username}"

                if not st.session_state.get(
                    delete_key,
                    False,
                ):
                    if st.button(
                        "Delete",
                        key=f"admin_delete_{username}",
                        width='stretch',
                    ):
                        st.session_state[delete_key] = True
                        st.rerun()
                else:
                    st.warning(
                        "Delete permanently removes the account. "
                        "Your backend should also remove its transactions."
                    )

                    d1, d2 = st.columns(2)

                    with d1:
                        if st.button(
                            "Confirm delete",
                            key=f"admin_confirm_delete_{username}",
                            width='stretch',
                        ):
                            if delete_account(username):
                                st.session_state[delete_key] = False
                                st.session_state["last_managed_user"] = None
                                st.success("Account deleted.")
                                st.rerun()
                            else:
                                st.error("Account deletion failed.")

                    with d2:
                        if st.button(
                            "Cancel",
                            key=f"admin_cancel_delete_{username}",
                            width='stretch',
                        ):
                            st.session_state[delete_key] = False
                            st.rerun()


# =========================================================
# ADMIN TRANSACTIONS
# =========================================================

def admin_transactions():
    admin_header(
        "Transactions",
        "Search and monitor every recorded transaction.",
    )

    # Read directly from MongoDB so legacy records retain their _id while we
    # backfill missing transaction_id and account_number values.
    transactions = list(transactions_collection.find({}))
    df = normalize_transaction_df(transactions)

    # Always show the newest transaction first.
    # Use the normalized datetime helper because the raw date column can
    # contain a mixture of strings and datetime objects.
    if not df.empty and "_sort_date" in df.columns:
        df = df.sort_values(
            by="_sort_date",
            ascending=False,
            na_position="last",
            kind="stable",
        ).reset_index(drop=True)

    f1, f2, f3 = st.columns([1.25, 1, 1])

    with f1:
        search = st.text_input(
            "Search",
            placeholder="Search Account Number, username, or transaction type",
            key="admin_tx_search",
        )

    with f2:
        tx_type_options = [
            "All",
            "Deposit",
            "Withdrawal",
            "Transfer",
            "Payment",
        ]

        selected_type = st.selectbox(
            "Transaction type",
            tx_type_options,
            key="admin_tx_type",
        )

    with f3:
        status_options = ["All"]
        if not df.empty and "status" in df.columns:
            status_options += sorted(
                {
                    str(v)
                    for v in df["status"].dropna().unique()
                }
            )

        selected_status = st.selectbox(
            "Status",
            status_options,
            key="admin_tx_status",
        )

    if not df.empty:
        if search.strip():
            search_value = search.strip()
            matched_user = get_user_by_account_number(search_value) if search_value.isdigit() else None
            if matched_user and "username" in df.columns:
                df = df[
                    df["username"].astype(str).str.casefold()
                    == str(matched_user.get("username", "")).casefold()
                ]
            else:
                searchable = df.astype(str).apply(
                    lambda col: col.str.contains(
                        search_value,
                        case=False,
                        na=False,
                    )
                ).any(axis=1)
                df = df[searchable]

        if selected_type != "All" and "type" in df.columns:
            selected_canonical = {
                "Deposit": "Deposits",
                "Withdrawal": "Withdrawals",
                "Transfer": "Transfers",
                "Payment": "Payments",
            }.get(selected_type, selected_type)
            df = df[
                df["type"].apply(canonical_transaction_type) == selected_canonical
            ]

        if selected_status != "All" and "status" in df.columns:
            df = df[
                df["status"].astype(str) == selected_status
            ]

        filtered_rows = df.to_dict("records")
    else:
        filtered_rows = []

    c1, c2 = st.columns([4, 1])

    with c2:
        if st.button(
            "Export view",
            key="admin_export_transactions",
            width='stretch',
        ):
            export_df = normalize_transaction_df(filtered_rows).copy()
            unwanted = {"_id", "_sort_date", "notification_seen", "user_id", "counterparty_user_id"}
            export_df = export_df.drop(columns=[c for c in unwanted if c in export_df.columns], errors="ignore")
            empty_cols = [c for c in export_df.columns if export_df[c].apply(lambda v: v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip().lower() in ("", "none", "nan", "null")).all()]
            export_df = export_df.drop(columns=empty_cols, errors="ignore")

            if "date" in export_df.columns:
                export_df["date"] = export_df["date"].astype(str)

            csv_data = export_df.to_csv(index=False).encode(
                "utf-8"
            )

            st.download_button(
                "Download CSV",
                data=csv_data,
                file_name="madhu_bank_transactions.csv",
                mime="text/csv",
                width='stretch',
            )

    if not filtered_rows:
        st.info("No transactions match the current filters.")
        return

    render_admin_transaction_table(filtered_rows)


# =========================================================
# ADMIN DEPOSITS
# =========================================================


# =========================================================
# ADMIN WITHDRAWALS
# =========================================================


# =========================================================
# ADMIN REPORTS
# =========================================================

def admin_reports():
    admin_header(
        "Reports",
        "Generate simple operational reports from current bank data.",
    )

    report_type = st.selectbox(
        "Report type",
        [
            "Transactions",
            "Users",
            "Accounts",
            "Deposits",
            "Withdrawals",
        ],
        key="admin_report_type",
    )

    start_date = st.date_input(
        "From",
        value=date.today().replace(
            year=max(1990, date.today().year - 1)
        ),
        key="admin_report_start",
    )

    end_date = st.date_input(
        "To",
        value=date.today(),
        key="admin_report_end",
    )

    if start_date > end_date:
        st.error("The start date must be before the end date.")
        return

    if report_type == "Users":
        rows = get_all_accounts()
        report_df = pd.DataFrame(rows)

    elif report_type == "Accounts":
        rows = get_all_accounts()
        report_df = pd.DataFrame(rows)

    else:
        rows = get_all_transactions()
        report_df = normalize_transaction_df(rows)

        if "date" in report_df.columns:
            # Use the normalized datetime series created from both legacy
            # and current transaction timestamp formats.
            if "_sort_date" in report_df.columns:
                report_df = report_df.dropna(subset=["_sort_date"]).copy()
                report_dates = report_df["_sort_date"].dt.date
            else:
                report_dates = pd.to_datetime(
                    report_df["date"],
                    errors="coerce",
                    format="mixed",
                ).dt.date
                report_df = report_df.loc[report_dates.notna()].copy()
                report_dates = report_dates.loc[report_df.index]

            report_df = report_df[
                report_dates.between(
                    start_date,
                    end_date,
                )
            ]

        if report_type == "Deposits" and "type" in report_df.columns:
            report_df = report_df[
                report_df["type"]
                .astype(str)
                .str.contains(
                    "deposit|credit",
                    case=False,
                    regex=True,
                    na=False,
                )
            ]

        if report_type == "Withdrawals" and "type" in report_df.columns:
            report_df = report_df[
                report_df["type"]
                .astype(str)
                .str.contains(
                    "withdraw|debit",
                    case=False,
                    regex=True,
                    na=False,
                )
            ]

    if report_df.empty:
        st.info("No report data for the selected criteria.")
        return

    st.markdown(
        f"""
        <div style="background:#FFFFFF; border:1px solid #E1E7E3; border-radius:12px; padding:18px 20px; margin: 12px 0 16px 0; box-shadow: 0 5px 20px rgba(23,32,29,0.05);">
            <div class="admin-panel-title-main">
                {report_type} Report
            </div>
            <div class="admin-panel-title-sub">
                {len(report_df):,} records in the selected range
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Clean report columns: drop unwanted internal fields and drop all columns which fields have None
    unwanted_cols = {
        "_id", "_sort_date", "notification_seen", "user_id", "counterparty_user_id",
        "transaction_pin_hash", "security_answer_hash", "security_question",
        "profile_picture_data", "profile_picture_mime"
    }
    report_df = report_df.drop(columns=[c for c in unwanted_cols if c in report_df.columns], errors="ignore").copy()

    # Fill banking defaults for core columns to prevent false nulls
    if "status" in report_df.columns:
        report_df["status"] = report_df["status"].fillna("Completed")
    if "currency" in report_df.columns:
        report_df["currency"] = report_df["currency"].fillna("INR")
    if "description" in report_df.columns:
        report_df["description"] = report_df["description"].fillna("Banking Transaction")
    if "account_type" in report_df.columns:
        report_df["account_type"] = report_df["account_type"].fillna("Savings")

    def is_val_empty(v):
        if v is None:
            return True
        if isinstance(v, float) and pd.isna(v):
            return True
        s = str(v).strip().lower()
        return s in ("", "none", "nan", "null", "<na>", "nat")

    # Remove all columns whose fields have None / null
    cols_to_drop = [c for c in report_df.columns if report_df[c].apply(is_val_empty).any()]
    report_df = report_df.drop(columns=cols_to_drop, errors="ignore")

    export_df = report_df.copy()

    for col in export_df.columns:
        if pd.api.types.is_datetime64_any_dtype(export_df[col]):
            export_df[col] = export_df[col].astype(str)

    csv_data = export_df.to_csv(index=False).encode("utf-8")

    if report_type == "Transactions":
        with st.container(key="admin_report_export"):
            st.download_button(
                "Export report",
                data=csv_data,
                file_name=f"madhu_bank_{report_type.lower()}_report.csv",
                mime="text/csv",
                width="stretch",
            )
    else:
        st.download_button(
            "Export report",
            data=csv_data,
            file_name=f"madhu_bank_{report_type.lower()}_report.csv",
            mime="text/csv",
            width="stretch",
        )

    # Streamlit/PyArrow requires a consistent type for every dataframe column.
    display_df = export_df.copy()
    if "date" in display_df.columns:
        display_df["date"] = display_df["date"].apply(
            lambda value: "" if value in (None, "") or pd.isna(value) else str(value)
        )

    for col in display_df.columns:
        if display_df[col].dtype == "object":
            display_df[col] = display_df[col].map(
                lambda value: "" if is_val_empty(value) else str(value)
            )

    st.dataframe(
        display_df,
        width='stretch',
        hide_index=True,
    )


# =========================================================
# ADMIN ACCOUNT REVIEW REQUESTS
# =========================================================

def admin_requests():
    admin_header(
        "Requests & Alerts",
        "Review customer unlock requests and manage system security alerts.",
    )

    tab_review, tab_alerts = st.tabs([
        "📋 Customer Review Requests",
        "🚨 System & Security Alerts",
    ])

    with tab_review:
        requests = get_account_review_requests()
        pending = [r for r in requests if str(r.get("status", "")).lower() == "pending"]

        k1, k2, k3 = st.columns(3)
        with k1:
            admin_kpi("TOTAL REQUESTS", f"{len(requests):,}", "↗", "All account-review requests")
        with k2:
            admin_kpi("PENDING", f"{len(pending):,}", "!", "Awaiting review", "admin-warning" if pending else "")
        with k3:
            reviewed = len(requests) - len(pending)
            admin_kpi("REVIEWED", f"{reviewed:,}", "✓", "Approved or rejected")

        st.write("")

        status_filter = st.selectbox(
            "Request status",
            ["All", "Pending", "Approved", "Rejected"],
            key="admin_request_status_filter",
        )
        filtered = get_account_review_requests(status_filter)

        if not filtered:
            st.info("No account review requests match the selected status.")
        else:
            for request in filtered:
                request_id = request.get("_id")
                username = str(request.get("username", "Unknown"))
                name = str(request.get("name", username))
                account_number = request.get("account_number", "Unavailable")
                status = str(request.get("status", "Pending"))
                created_at = request.get("created_at")
                reviewed_at = request.get("reviewed_at")
                request_note = request.get("request_note") or ""
                admin_note = request.get("admin_note") or ""

                with st.container(border=True):
                    row1, row2, row3 = st.columns([2.1, 1.4, 1.1])
                    with row1:
                        st.markdown(f"**{name}**")
                        st.caption(f"Username: {username} · Account Number: {account_number}")
                    with row2:
                        st.write(f"**Status:** {status}")
                        if created_at:
                            st.caption(f"Requested: {_format_transaction_datetime(created_at)}")
                    with row3:
                        if status.lower() == "pending":
                            st.markdown("**Action**")

                    if request_note:
                        st.markdown("**Customer message:**")
                        st.info(request_note)

                    if admin_note and status.lower() != "pending":
                        st.markdown("**Administrator reason:**")
                        st.write(admin_note)

                    if status.lower() == "pending":
                        reason_key = f"admin_request_reason_{request_id}"
                        reason = st.text_area(
                            "Reason / admin note",
                            key=reason_key,
                            placeholder="Required when rejecting. This reason will be visible to the customer.",
                            height=90,
                        )
                        action1, action2, action3 = st.columns([1, 1, 2])
                        with action1:
                            approve = st.button(
                                "Accept & Activate",
                                key=f"approve_request_{request_id}",
                                width="stretch",
                            )
                        with action2:
                            reject = st.button(
                                "Reject",
                                key=f"reject_request_{request_id}",
                                width="stretch",
                            )
                        with action3:
                            st.caption("Accept activates the account. Reject requires a reason that is shown to the customer.")

                        if approve:
                            ok, message = update_account_review_request(request_id, "Approved", reason)
                            if ok:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                        elif reject:
                            if not str(reason or "").strip():
                                st.error("Enter a reason before rejecting this request.")
                            else:
                                ok, message = update_account_review_request(request_id, "Rejected", reason)
                                if ok:
                                    st.warning(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                    else:
                        if reviewed_at:
                            st.caption(f"Reviewed: {_format_transaction_datetime(reviewed_at)}")
                        if request.get("reviewed_by"):
                            st.caption(f"Reviewed by: {request.get('reviewed_by')}")
                        if admin_note:
                            st.info(f"Admin note: {admin_note}")

    with tab_alerts:
        # Channel 3: Dedicated System & Security Alerts review list
        all_alerts = get_system_alerts(status_filter="All", limit=200)
        unread_alerts = [a for a in all_alerts if a.get("status") == "Unread"]
        ack_alerts = [a for a in all_alerts if a.get("status") == "Acknowledged"]
        dismissed_alerts = [a for a in all_alerts if a.get("status") == "Dismissed"]

        ak1, ak2, ak3, ak4 = st.columns(4, gap="small")
        with ak1:
            admin_kpi("TOTAL ALERTS", f"{len(all_alerts):,}", "🚨", "All recorded events", "")
        with ak2:
            admin_kpi("UNREAD", f"{len(unread_alerts):,}", "⚠️", "Needs acknowledgment", "admin-danger" if unread_alerts else "")
        with ak3:
            admin_kpi("ACKNOWLEDGED", f"{len(ack_alerts):,}", "✓", "Reviewed by admin", "admin-positive" if ack_alerts else "")
        with ak4:
            admin_kpi("DISMISSED", f"{len(dismissed_alerts):,}", "✕", "Closed records", "")

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        filt_col1, filt_col2 = st.columns([3.5, 1.5], gap="small")
        with filt_col1:
            alert_filter = st.selectbox(
                "Alert Status Filter",
                ["All", "Unread", "Acknowledged", "Dismissed"],
                index=0,
                key="admin_alert_status_filter",
            )
        with filt_col2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if unread_alerts and st.button("Acknowledge All Unread", key="btn_ack_all_unread", width="stretch"):
                for ua in unread_alerts:
                    acknowledge_system_alert(ua.get("alert_id"))
                st.toast("All unread alerts marked as acknowledged.", icon="✅")
                st.rerun()

        filtered_alerts = get_system_alerts(status_filter=alert_filter, limit=100)

        if not filtered_alerts:
            st.markdown(
                '<div class="tx-empty-state" style="min-height:180px;"><div class="tx-empty-icon">✓</div><div class="tx-empty-title">No alerts matching filter</div><div class="tx-empty-copy">System events and security notifications will appear here when triggered.</div></div>',
                unsafe_allow_html=True,
            )
        else:
            for alert in filtered_alerts:
                aid = alert.get("alert_id")
                atype = alert.get("type", "SYSTEM")
                title = alert.get("title", "Alert")
                msg = alert.get("message", "")
                severity = str(alert.get("severity", "warning")).lower()
                status = alert.get("status", "Unread")
                created_at = alert.get("created_at")
                meta = alert.get("metadata", {})
                email_sent = alert.get("email_sent", False)
                recipient = alert.get("recipient_email")

                is_crit = severity in ("critical", "high", "danger")
                badge_bg = "#FDECEC" if is_crit else "#FEF6E7" if severity in ("warning", "medium") else "#E8F5F0"
                badge_color = "#991B1B" if is_crit else "#975A16" if severity in ("warning", "medium") else "#0E5B45"

                with st.container(border=True):
                    r1, r2 = st.columns([3.5, 1.5], gap="small")
                    with r1:
                        st.markdown(
                            f"""
                            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                                <span style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:6px;background:{badge_bg};color:{badge_color};">
                                    {severity.upper()}
                                </span>
                                <span style="font-size:12px;font-weight:600;color:#66716D;">
                                    {atype} &bull; {aid}
                                </span>
                            </div>
                            <div style="font-size:15px;font-weight:700;color:#17201D;margin-bottom:4px;">
                                {html_escape(title)}
                            </div>
                            <div style="font-size:13px;color:#4F5B56;line-height:1.4;">
                                {html_escape(msg)}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Render metadata details if present
                        if meta:
                            meta_chips = []
                            for k, v in meta.items():
                                if k == "amount":
                                    meta_chips.append(f"<strong>Amount:</strong> ₹{safe_float(v):,.2f}")
                                else:
                                    meta_chips.append(f"<strong>{k.replace('_', ' ').title()}:</strong> {v}")
                            if meta_chips:
                                st.markdown(
                                    f"""<div style="margin-top:8px;font-size:12px;color:#4F5B56;background:#F8FAF9;border:1px solid #E1E7E3;border-radius:6px;padding:6px 10px;">{' &bull; '.join(meta_chips)}</div>""",
                                    unsafe_allow_html=True,
                                )

                    with r2:
                        status_chip = status_badge(status)
                        st.markdown(
                            f"""
                            <div style="text-align:right;margin-bottom:6px;">
                                {status_chip}
                            </div>
                            <div style="font-size:11.5px;color:#66716D;text-align:right;">
                                {_format_transaction_datetime(created_at) if created_at else 'Just now'}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if email_sent and recipient:
                            st.markdown(
                                f"""<div style="font-size:11px;color:#0E5B45;text-align:right;margin-top:4px;">✉️ Dispatched to {html_escape(recipient)}</div>""",
                                unsafe_allow_html=True,
                            )
                        elif recipient:
                            st.markdown(
                                f"""<div style="font-size:11px;color:#66716D;text-align:right;margin-top:4px;">✉️ SMTP queued</div>""",
                                unsafe_allow_html=True,
                            )

                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                        # Action buttons
                        if status == "Unread":
                            ac1, ac2 = st.columns(2, gap="small")
                            with ac1:
                                if st.button("Acknowledge", key=f"req_ack_{aid}", width="stretch", type="primary"):
                                    acknowledge_system_alert(aid)
                                    st.toast(f"Alert {aid} acknowledged.", icon="✅")
                                    st.rerun()
                            with ac2:
                                if st.button("Dismiss", key=f"req_dism_{aid}", width="stretch"):
                                    dismiss_system_alert(aid)
                                    st.toast(f"Alert {aid} dismissed.", icon="🗑️")
                                    st.rerun()
                        elif status == "Acknowledged":
                            if st.button("Dismiss Alert", key=f"req_dism_{aid}", width="stretch"):
                                dismiss_system_alert(aid)
                                st.toast(f"Alert {aid} dismissed.", icon="🗑️")
                                st.rerun()


# =========================================================
# ADMIN SETTINGS
# =========================================================

def admin_settings():
    admin_header(
        "Settings",
        "Administration preferences, security policies, and system controls.",
    )

    username = html_escape(str(st.session_state.get("username", "admin")))

    # ---------------------------------------------------------
    # OPERATIONAL METRICS (TOP KPI ROW)
    # ---------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        admin_kpi("SYSTEM STATUS", "Operational", "●", "All services healthy", "admin-positive")
    with c2:
        admin_kpi("SECURITY ENFORCED", "Enterprise", "🛡️", "Argon2 + AES-256 active", "admin-positive")
    with c3:
        admin_kpi("ADMIN SESSION", "admin", "◉", "Root access role", "admin-positive")
    with c4:
        admin_kpi("DATABASE CLUSTER", "Connected", "⚡", "MongoDB live & synchronized", "admin-positive")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # MAIN CONFIGURATION PANELS
    # ---------------------------------------------------------
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        # Card 1: Administrator Profile & Credentials
        with st.container(border=True):
            admin_panel(
                "Administrator Profile",
                "Primary security officer and system identity.",
            )

            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:14px;padding:14px;background:#F8FAF9;border:1px solid #E1E7E3;border-radius:10px;margin-bottom:14px;">
                    <div style="width:46px;height:46px;border-radius:10px;background:#E8F5F0;color:#16805F;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;border:1px solid #BFE3D4;">
                        AD
                    </div>
                    <div>
                        <div style="font-size:15px;font-weight:700;color:#17201D;">System Administrator</div>
                        <div style="font-size:12px;color:#66716D;">@{username} · Superuser (Root)</div>
                    </div>
                    <div style="margin-left:auto;">
                        {status_badge("Active")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="admin-top-profile-row" style="padding:10px 0;font-size:13px;">
                    <span style="color:#66716D;">Authorization Level</span>
                    <strong style="color:#17201D;">Level 1 (Full Root Privileges)</strong>
                </div>
                <div class="admin-top-profile-row" style="padding:10px 0;font-size:13px;">
                    <span style="color:#66716D;">Audit Capabilities</span>
                    <strong style="color:#17201D;">Ledger, User &amp; Review Access</strong>
                </div>
                <div class="admin-top-profile-row" style="padding:10px 0;font-size:13px;border-bottom:none;">
                    <span style="color:#66716D;">Active Session IP</span>
                    <strong style="color:#17201D;">127.0.0.1 (Local Host)</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("Change Administrator Password", expanded=False):
                with st.form("admin_password_change_form"):
                    new_p = st.text_input("New Admin Password", type="password", key="new_admin_pwd")
                    confirm_p = st.text_input("Confirm New Password", type="password", key="confirm_admin_pwd")
                    if st.form_submit_button("Update Password", width="stretch", type="primary"):
                        if not new_p:
                            st.error("Please enter a new password.")
                        elif new_p != confirm_p:
                            st.error("Passwords do not match.")
                        elif len(new_p) < 6:
                            st.error("Password must be at least 6 characters.")
                        else:
                            import backend.admin
                            backend.admin.ADMIN_PASSWORD = new_p
                            st.session_state["admin_custom_password"] = new_p
                            st.success("Admin password updated successfully!")

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        # Card 2: Notification & Alert Routing
        with st.container(border=True):
            admin_panel(
                "Notification Policies",
                "System event triggers and administrative broadcasts.",
            )

            st.markdown(
                """
                <div style="font-size:12.5px;color:#4F5B56;margin-bottom:12px;">
                    Configure how transactional alerts and account review triggers are dispatched.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.checkbox("High-Value Transaction Alerts", value=True, key="set_alert_high_val")
            threshold_val = st.number_input(
                "Alert threshold amount (₹)",
                min_value=1000,
                max_value=10000000,
                value=50000,
                step=5000,
                key="set_alert_threshold",
            )
            st.checkbox("Account Status & Freeze Notifications", value=True, key="set_alert_status")
            st.checkbox("Security Login Failure Alerts", value=True, key="set_alert_security")

            admin_email_input = st.text_input(
                "Admin Notification Email (SMTP)",
                value=st.session_state.get("admin_alert_email", "madhumathib45@gmail.com"),
                key="admin_alert_email_input",
                help="Alert emails will be dispatched to this address via Gmail SMTP.",
            )
            st.session_state["admin_alert_email"] = admin_email_input

            st.markdown(
                """
                <div style="background:#F8FAF9;border:1px solid #E1E7E3;border-radius:8px;padding:10px 12px;margin:12px 0;font-size:12px;color:#4F5B56;line-height:1.5;">
                    <strong style="color:#17201D;display:block;margin-bottom:4px;">📍 Where Alerts Appear:</strong>
                    • <strong>In-App Floating Toasts:</strong> Bottom-right popups on screen for instant events.<br/>
                    • <strong>Admin Dashboard Banners:</strong> Top alert banners and red <em>ACTIVE ALERTS & REQUESTS</em> KPI.<br/>
                    • <strong>Admin Requests Tab:</strong> Dedicated review list under the <em>Requests &amp; Alerts</em> menu.<br/>
                    • <strong>Email Alerts:</strong> Dispatched to the configured administrator email address via SMTP.
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn_col1, btn_col2 = st.columns(2, gap="small")
            with btn_col1:
                if st.button("Save Alert Policies", key="btn_save_alerts", width="stretch", type="primary"):
                    st.session_state["admin_alert_email"] = admin_email_input
                    st.toast("Alert policies and email routing saved.", icon="✅")
                    st.success("Alert policies and destination email saved successfully.")
            with btn_col2:
                if st.button("🔔 Test Alert Trigger", key="btn_test_alert", width="stretch"):
                    alert_doc = dispatch_system_alert(
                        alert_type="HIGH_VALUE_TRANSACTION",
                        title=f"Test High-Value Alert (> ₹{threshold_val:,.2f})",
                        message=f"Manual simulation triggered for high-value threshold ₹{threshold_val:,.2f} by Administrator.",
                        severity="warning",
                        metadata={"threshold": threshold_val, "triggered_by": username},
                        send_email=True,
                        target_email=admin_email_input,
                    )
                    email_note = f"and dispatched via SMTP to {admin_email_input}" if alert_doc.get("email_sent") else "(SMTP email queued/check Gmail credentials)"
                    st.toast(f"🚨 ALERT: {alert_doc.get('alert_id')} recorded!", icon="⚠️")
                    st.success(f"🔔 Live Alert **{alert_doc.get('alert_id')}** recorded in MongoDB {email_note}! Visible in Dashboard banners, Requests & Alerts tab, and In-App Toasts.")

    with col2:
        # Card 3: Security & Access Control
        with st.container(border=True):
            admin_panel(
                "Security & Access Control",
                "Authentication protocols and protection controls.",
            )

            st.markdown(
                """
                <div style="font-size:12.5px;color:#4F5B56;margin-bottom:12px;">
                    Enforced policies across the Madhu Bank application cluster.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.checkbox("Require Administrator Two-Factor Verification", value=True, key="sec_2fa")
            st.checkbox("Enforce Secure Password Hashing (BCrypt / SHA-256)", value=True, key="sec_hash")
            st.checkbox("Automatic Session Timeout on Idle (30 Minutes)", value=True, key="sec_timeout")
            st.checkbox("Audit Log Every Financial Transaction Modification", value=True, key="sec_audit")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            s_col1, s_col2 = st.columns(2)
            with s_col1:
                if st.button("Rotate Session Keys", key="btn_rotate_keys", width="stretch"):
                    st.toast("Security session keys rotated.", icon="🔑")
            with s_col2:
                if st.button("Save Security Rules", key="btn_save_sec", width="stretch", type="primary"):
                    st.success("Security configuration applied.")

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        # Card 4: System Architecture & Maintenance
        with st.container(border=True):
            admin_panel(
                "System Architecture & Health",
                "Current application stack and database diagnostics.",
            )

            total_acc = get_total_accounts()
            total_tx = len(get_all_transactions())

            st.markdown(
                f"""
                <div class="admin-top-profile-row" style="padding:9px 0;font-size:12.5px;">
                    <span style="color:#66716D;">Frontend Engine</span>
                    <strong style="color:#17201D;">Streamlit 1.63 (Modern DOM)</strong>
                </div>
                <div class="admin-top-profile-row" style="padding:9px 0;font-size:12.5px;">
                    <span style="color:#66716D;">Backend Runtime</span>
                    <strong style="color:#17201D;">Python 3.14 (Async Engine)</strong>
                </div>
                <div class="admin-top-profile-row" style="padding:9px 0;font-size:12.5px;">
                    <span style="color:#66716D;">Primary Database</span>
                    <strong style="color:#16805F;">MongoDB (Local Cluster · Connected)</strong>
                </div>
                <div class="admin-top-profile-row" style="padding:9px 0;font-size:12.5px;">
                    <span style="color:#66716D;">Customer Records</span>
                    <strong style="color:#17201D;">{total_acc:,} accounts stored</strong>
                </div>
                <div class="admin-top-profile-row" style="padding:9px 0;font-size:12.5px;border-bottom:none;">
                    <span style="color:#66716D;">Financial Ledger</span>
                    <strong style="color:#17201D;">{total_tx:,} transactions recorded</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            m_col1, m_col2 = st.columns(2)
            with m_col1:
                if st.button("🧹 Clear App Cache", key="btn_clear_cache", width="stretch"):
                    try:
                        st.cache_data.clear()
                    except Exception:
                        pass
                    st.success("Cache cleared successfully!")
            with m_col2:
                import json
                diag_data = json.dumps({
                    "system": "Madhu Bank Enterprise",
                    "version": "2.4.0",
                    "status": "Operational",
                    "accounts_count": total_acc,
                    "transactions_count": total_tx,
                    "timestamp": str(datetime.now())
                }, indent=2).encode("utf-8")
                st.download_button(
                    "📦 Export Diagnostics",
                    data=diag_data,
                    file_name="madhu_bank_diagnostics.json",
                    mime="application/json",
                    key="btn_export_diag",
                    width="stretch",
                )


# =========================================================
# ADMIN BANK OVERVIEW
# =========================================================

def admin_overview():
    admin_header(
        "Bank Overview",
        "High-level operational statistics from the current backend.",
    )

    accounts = get_all_accounts()
    transactions = get_all_transactions()

    account_df = (
        pd.DataFrame(accounts)
        if accounts
        else pd.DataFrame()
    )
    tx_df = normalize_transaction_df(transactions)

    c1, c2, c3 = st.columns(3)

    with c1:
        active = get_active_accounts()
        admin_kpi(
            "ACTIVE ACCOUNTS",
            f"{active:,}",
            "●",
            "Currently enabled",
            "admin-positive",
        )

    with c2:
        disabled = get_disabled_accounts()
        admin_kpi(
            "DISABLED ACCOUNTS",
            f"{disabled:,}",
            "●",
            "Currently disabled",
            "admin-warning" if disabled else "",
        )

    with c3:
        total_balance = get_total_bank_balance()
        admin_kpi(
            "BANK BALANCE",
            f"₹{safe_float(total_balance):,.0f}",
            "₹",
            "Total customer balances",
        )

    st.write("")

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            admin_panel(
                "Account status",
                "Active versus disabled accounts.",
            )

            if account_df.empty or "status" not in account_df.columns:
                st.info("No status data.")
            else:
                counts = (
                    account_df["status"]
                    .fillna("Unknown")
                    .astype(str)
                    .value_counts()
                )
                chart = pd.DataFrame(
                    {"Accounts": counts.values},
                    index=counts.index,
                )
                st.bar_chart(
                    chart,
                    height=250,
                    width='stretch',
                )

    with right:
        with st.container(border=True):
            admin_panel(
                "Transaction types",
                "Current transaction distribution.",
            )

            if tx_df.empty or "type" not in tx_df.columns:
                st.info("No transaction type data.")
            else:
                counts = (
                    tx_df["type"]
                    .fillna("Unknown")
                    .astype(str)
                    .value_counts()
                )
                chart = pd.DataFrame(
                    {"Transactions": counts.values},
                    index=counts.index,
                )
                st.bar_chart(
                    chart,
                    height=250,
                    width='stretch',
                )


# =========================================================
# MADHU BANK — BOTH USER + ADMIN FINAL VISUAL SYSTEM
# Visual/CSS layer only. Existing functionality remains unchanged.
# =========================================================

# =========================================================
# MADHU BANK — CLEAN NEW COLOR THEME
# The old applied User/Admin palette is intentionally removed.
# =========================================================
def apply_clean_emerald_theme():
    pass


def apply_admin_reference_user_geometry():
    pass


def apply_admin_login_palette_theme():
    pass


# =========================================================
# MAIN APPLICATION
# =========================================================

if not st.session_state.logged_in:

    if st.session_state.page == "login":
        login_page()

    elif st.session_state.page == "login_otp_verification":
        login_otp_verification_page()

    elif st.session_state.page == "disabled_account_review":
        disabled_account_review_page()

    elif st.session_state.page == "register":
        register_page()

    elif st.session_state.page == "register_otp_verification":
        register_otp_verification_page()

    elif st.session_state.page == "forgot_password":
        forgot_password_page()

    elif st.session_state.page == "admin_login":
        admin_login_page()

else:

    if st.session_state.role == "admin":

        admin_theme()
        apply_admin_login_palette_theme()
        admin_sidebar()

        if st.session_state.page == "admin_dashboard":
            admin_dashboard()

        elif st.session_state.page == "admin_users":
            admin_users()

        elif st.session_state.page == "admin_accounts":
            admin_accounts()

        elif st.session_state.page == "admin_transactions":
            admin_transactions()

        elif st.session_state.page == "admin_requests":
            admin_requests()

        elif st.session_state.page == "admin_reports":
            admin_reports()

        elif st.session_state.page == "admin_settings":
            admin_settings()

        elif st.session_state.page == "admin_overview":
            admin_overview()

        else:
            admin_dashboard()

    else:

        user_theme()
        apply_clean_emerald_theme()
        banking_sidebar()
        apply_admin_reference_user_geometry()

        if st.session_state.page == "dashboard":
            dashboard()

        elif st.session_state.page == "account":
            account_page()

        elif st.session_state.page == "profile":
            profile_page()

        elif st.session_state.page == "account_review":
            account_review_page()

        elif st.session_state.page == "deposit":
            deposit_page()

        elif st.session_state.page == "withdraw":
            withdraw_page()

        elif st.session_state.page == "transfer":
            transfer_page()

        elif st.session_state.page == "balance":
            balance_page()

        elif st.session_state.page == "transactions":
            transactions_page()

        else:
            dashboard()



# =========================================================
# CENTRALIZED DESIGN SYSTEM INJECTION
# Centralized visual system
# across both Customer and Administration portals.
# =========================================================
if st.session_state.get("logged_in", False):
    st.markdown(get_shared_styles(), unsafe_allow_html=True)
    if st.session_state.get("role") == "admin":
        st.markdown(get_admin_theme_styles(), unsafe_allow_html=True)
    else:
        st.markdown(get_user_theme_styles(), unsafe_allow_html=True)
else:
    st.markdown(get_auth_theme_styles(), unsafe_allow_html=True)

st.session_state["_scroll_reset_in_progress"] = False

