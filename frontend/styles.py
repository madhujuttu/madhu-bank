"""
Madhu Bank Design System & Theme Styles
"""

import base64
from functools import lru_cache
import os


@lru_cache(maxsize=1)
def get_shared_styles() -> str:
    return """
    <style>
    /* =========================================================
       1. GLOBAL FINTECH DESIGN TOKENS & ELEMENT RESETS
       ========================================================= */
    :root {
        --font-sans: 'Inter', ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;

        --canvas-bg: #F0F0EC;
        --surface-white: #FFFFFF;
        --surface-subtle: #FAF8FB;
        --surface-muted: #F1F5F9;

        --text-headline: #0F172A;
        --text-body: #1E293B;
        --text-secondary: #475569;
        --text-muted: #64748B;

        --border-subtle: #ECE5EE;
        --border-default: #E2E8F0;
        --border-strong: #CBD5E1;
        --border-focus: #10B981;

        --color-emerald: #10B981;
        --color-emerald-dark: #059669;
        --color-emerald-light: #ECFDF5;
        --color-indigo: #6366F1;
        --color-indigo-dark: #4F46E5;
        --color-indigo-light: #EEF2FF;
        --color-rose: #F43F5E;
        --color-rose-dark: #E11D48;
        --color-rose-light: #FFF1F2;
        --color-amber: #F59E0B;
        --color-amber-dark: #D97706;
        --color-amber-light: #FEF3C7;

        --radius-sm: 6px;
        --radius-md: 9px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        --radius-full: 9999px;

        --shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.04);
        --shadow-sm: 0 2px 6px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02);
        --shadow-md: 0 6px 18px rgba(82, 67, 107, 0.07);
        --shadow-lg: 0 12px 32px rgba(15, 23, 42, 0.08), 0 3px 10px rgba(15, 23, 42, 0.03);
    }

    /* Hide standard Streamlit header, decorative bar, and sidebar */
    header[data-testid="stHeader"],
    div[data-testid="stDecoration"],
    section[data-testid="stSidebar"],
    div[data-testid="stSidebarCollapsedControl"],
    footer {
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
    }

    /* Hide browser native password reveal / clear buttons (prevents duplicate eye icon in Edge/Windows) */
    input[type="password"]::-ms-reveal,
    input[type="password"]::-ms-clear,
    input::-ms-reveal,
    input::-ms-clear {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        pointer-events: none !important;
        visibility: hidden !important;
    }

    /* Base typography & canvas */
    html:not(:has(.auth-visual-panel)),
    body:not(:has(.auth-visual-panel)),
    .stApp:not(:has(.auth-visual-panel)) {
        font-family: var(--font-sans) !important;
        background: var(--canvas-bg) !important;
        background-color: var(--canvas-bg) !important;
        background-image: none !important;
        color: var(--text-headline) !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
        text-rendering: optimizeLegibility !important;
    }

    /* Modern sleek custom scrollbar */
    ::-webkit-scrollbar {
        width: 7px;
        height: 7px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: var(--radius-full);
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #94A3B8;
    }

    /* Zero-pixel anchor for JavaScript scroll reset */
    [data-testid="stElementContainer"]:has(#madhu-scroll-reset-anchor) {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        max-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        border: 0 !important;
    }

    /* Brand Mark & Header Fallback Styles */
    .madhu-brand-mark {
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;
    }

    .bank-header {
        position: sticky;
        top: 0;
        z-index: 999;
        width: 100%;
        background: #FFFFFF;
        padding: 14px 20px 12px 20px;
        margin-bottom: 24px;
        border-bottom: 1px solid #E2E8F0;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .bank-name {
        font-size: 28px;
        font-weight: 700;
        color: #172554;
        letter-spacing: 1px;
        margin: 0;
    }

    .bank-tagline {
        font-size: 13px;
        color: #64748B;
        margin-top: 4px;
        letter-spacing: 0.3px;
    }

    /* =========================================================
       2. UNIVERSAL TEXT VISIBILITY GUARANTEE
       Guarantees high contrast, dark readable text across all elements
       ========================================================= */
    p:not(.auth-visual-panel *), span:not(.auth-visual-panel *), label:not(.auth-visual-panel *),
    h1:not(.auth-visual-panel *), h2:not(.auth-visual-panel *), h3:not(.auth-visual-panel *),
    h4:not(.auth-visual-panel *), h5:not(.auth-visual-panel *), h6:not(.auth-visual-panel *),
    strong:not(.auth-visual-panel *), em:not(.auth-visual-panel *), li:not(.auth-visual-panel *), dt, dd,
    .stMarkdown:not(.auth-visual-panel *), .stMarkdown:not(.auth-visual-panel) p,
    [data-testid="stMarkdownContainer"]:not(:has(.auth-visual-panel)) p,
    [data-testid="stMarkdownContainer"]:not(:has(.auth-visual-panel)) span,
    [data-testid="stMarkdownContainer"]:not(:has(.auth-visual-panel)) div,
    [data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] span, [data-testid="stWidgetLabel"] p,
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input,
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] *,
    .ref-card-title, .admin-page-title, .user-page-title,
    .admin-kpi-value, .ref-balance-value, .tx-hero-title, .tx-summary-title,
    .customer-profile-card-title, .customer-profile-name, .customer-profile-detail-value,
    .user-profile-name, .admin-top-profile-name, .admin-panel-title-main {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    /* Preserve brilliant white text in dark authentication visual panels */
    .auth-visual-panel,
    .auth-visual-panel *,
    .auth-visual-panel p,
    .auth-visual-panel span,
    .auth-visual-panel div,
    .auth-visual-panel h1,
    .visual-top-label,
    .visual-top-label *,
    .visual-hero-heading,
    .visual-hero-heading *,
    .visual-hero-desc,
    .visual-hero-desc *,
    .visual-footer-pill,
    .visual-footer-pill *,
    .banking-security-cue,
    .banking-security-cue * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        text-shadow: 0 2px 14px rgba(0, 0, 0, 0.95) !important;
    }

    /* Secondary / Muted readable text */
    .stCaption, [data-testid="stCaptionContainer"],
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *,
    .admin-page-subtitle, .user-page-subtitle,
    .admin-page-kicker, .user-kicker,
    .ref-card-subtitle, .ref-summary-name, .ref-balance-label, .ref-balance-note,
    .admin-kpi-label, .admin-kpi-foot, .account-mini-label, .balance-label,
    .customer-profile-card-subtitle, .customer-profile-detail-label,
    .user-profile-role, .admin-top-profile-role, .admin-panel-title-sub,
    .tx-empty-copy, .ref-analytics-note, .admin-muted {
        color: #475569 !important;
        -webkit-text-fill-color: #475569 !important;
    }

    /* Input placeholders */
    ::placeholder, input::placeholder, textarea::placeholder {
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
        opacity: 1 !important;
    }

    /* =========================================================
       3. UNIVERSAL BORDER COLOR HARMONIZATION
       Eliminates harsh black/dark borders, replacing with modern subtle fintech borders
       ========================================================= */
    *, *:before, *:after {
        border-color: #E2E8F0;
    }

    /* Explicit overrides for components with legacy or browser black borders */
    [style*="border-color: black"], [style*="border-color: #000"], [style*="border-color: #17151B"],
    [style*="border: 1px solid black"], [style*="border: 1px solid #000"],
    div[data-testid="stVerticalBlockBorderWrapper"] > div,
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stForm"],
    div[data-testid="stExpander"],
    div[data-testid="stDataFrame"],
    .ref-card, .ref-analytics-shell, .user-ref-kpi, .admin-kpi,
    table, th, td, hr {
        border-color: #ECE5EE !important;
    }

    /* =========================================================
    /* =========================================================
       4. STANDARDIZED FORM INPUTS & ENTRY FIELDS
       Crisp, high-contrast, clearly visible borders across all
       text inputs, search boxes, number inputs, selectboxes, text areas,
       date/time pickers.
       ========================================================= */

    /* Outer widget containers must stay transparent so the canvas flows naturally */
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stTextInput"],
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stTextInput"] > div,
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stNumberInput"],
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stNumberInput"] > div,
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stSelectbox"],
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stSelectbox"] > div,
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stMultiSelect"],
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stMultiSelect"] > div,
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stTextArea"],
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stTextArea"] > div,
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stDateInput"],
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stDateInput"] > div,
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stTimeInput"],
    .stApp:not(:has(.auth-visual-panel)) div[data-testid="stTimeInput"] > div {
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }

    /* Universal visible border & white surface on ALL input control boxes */
    [data-testid="stTextInputRootElement"],
    [data-testid="stNumberInputContainer"],
    [data-testid="stTextAreaRootElement"],
    [data-testid="stSelectbox"] > div,
    [data-testid="stMultiSelect"] > div,
    [data-testid="stDateInput"] > div,
    [data-testid="stTimeInput"] > div,
    div[data-baseweb="input"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"],
    .stTextInput [data-testid="stTextInputRootElement"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        background-image: none !important;
        border: 1.5px solid #8FA299 !important;
        border-radius: 8px !important;
        min-height: 42px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05) !important;
        transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out !important;
        box-sizing: border-box !important;
    }

    /* Inner base-input wrapper clean reset */
    div[data-baseweb="base-input"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }

    /* Inner input text styling */
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    div[data-testid="stDateInput"] input,
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTimeInput"] input,
    div[data-baseweb="textarea"] textarea,
    [data-testid="stTextInputField"],
    [data-testid="stNumberInputField"] {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        min-height: 38px !important;
        padding: 0 12px !important;
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        outline: none !important;
    }

    /* Hover states across all input controls */
    [data-testid="stTextInputRootElement"]:hover,
    [data-testid="stNumberInputContainer"]:hover,
    [data-testid="stTextAreaRootElement"]:hover,
    [data-testid="stSelectbox"] > div:hover,
    div[data-baseweb="input"]:hover,
    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="textarea"]:hover {
        border-color: #16805F !important;
    }

    /* Focus states */
    [data-testid="stTextInputRootElement"]:focus-within,
    [data-testid="stNumberInputContainer"]:focus-within,
    [data-testid="stTextAreaRootElement"]:focus-within,
    [data-testid="stSelectbox"] > div:focus-within,
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within > div,
    div[data-baseweb="textarea"]:focus-within {
        border-color: #16805F !important;
        box-shadow: 0 0 0 3px rgba(22, 128, 95, 0.18) !important;
        outline: none !important;
    }

    /* Field labels */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stDateInput label,
    .stTimeInput label,
    .stMultiSelect label,
    .stTextArea label,
    [data-testid="stWidgetLabel"] label {
        color: #1E293B !important;
        -webkit-text-fill-color: #1E293B !important;
        font-size: 13px !important;
        font-weight: 650 !important;
        margin-bottom: 5px !important;
    }

    /* Remove 'Press Enter to submit form' / 'Press Enter to apply' helper instructions from all fields */
    [data-testid="InputInstructions"],
    [data-testid="InputInstructions"] *,
    .stTextInput [data-testid="InputInstructions"],
    .stTextArea [data-testid="InputInstructions"],
    .stNumberInput [data-testid="InputInstructions"],
    .stDateInput [data-testid="InputInstructions"],
    .stTimeInput [data-testid="InputInstructions"],
    div:has(> [data-testid="InputInstructions"]),
    div[data-testid="stTextInput"] div:has(> [data-testid="InputInstructions"]),
    div[data-testid="stNumberInput"] div:has(> [data-testid="InputInstructions"]),
    div[data-testid="stTextArea"] div:has(> [data-testid="InputInstructions"]) {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: none !important;
    }

    /* Dropdown selected value container inside selectbox */
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div[aria-selected],
    div[data-baseweb="select"] [role="combobox"] {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        font-size: 13.5px !important;
        font-weight: 550 !important;
    }

    /* Dropdown chevron and input icons */
    div[data-baseweb="select"] svg,
    div[data-testid="stDateInput"] svg,
    div[data-testid="stNumberInput"] button svg {
        fill: #475569 !important;
        color: #475569 !important;
    }

    /* Streamlit BaseWeb Dropdown Overlays (Selectbox popovers) */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08) !important;
        padding: 6px !important;
        z-index: 999999 !important;
    }

    li[role="option"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        font-size: 13px !important;
        font-weight: 550 !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        transition: background 0.12s ease !important;
    }

    li[role="option"] * {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background: #F1F5F9 !important;
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    /* BaseWeb Calendar Popover for Date Input */
    div[data-baseweb="calendar"],
    div[data-baseweb="datepicker"],
    div[data-baseweb="calendar"] * {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    div[data-baseweb="calendar"] [role="gridcell"] {
        color: #0F172A !important;
    }

    div[data-baseweb="calendar"] [role="gridcell"]:hover,
    div[data-baseweb="calendar"] [aria-selected="true"] {
        background: #EEF2FF !important;
        color: #4338CA !important;
        -webkit-text-fill-color: #4338CA !important;
    }

    /* MultiSelect Tags */
    div[data-baseweb="tag"] {
        background: #F1F5F9 !important;
        color: #0F172A !important;
        border: 1px solid #E2E8F0 !important;
    }
    div[data-baseweb="tag"] * {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    /* =========================================================
       5. STREAMLIT CONTAINERS, FORMS & EXPANDERS
       ========================================================= */
    .stApp:not(:has(.auth-visual-panel)) .block-container div[data-testid="stVerticalBlockBorderWrapper"]:not(.st-key-admin_top_nav *):not(.st-key-user_top_nav *):not(.st-key-auth_visual_fixed *):not(.st-key-auth_visual_fixed) > div {
        background: #FFFFFF !important;
        border: 1px solid #ECE5EE !important;
        border-radius: 12px !important;
        box-shadow: var(--shadow-sm) !important;
        padding: 16px 20px !important;
    }

    div[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #ECE5EE !important;
        border-radius: 10px !important;
        box-shadow: var(--shadow-xs) !important;
        margin-bottom: 12px !important;
    }

    div[data-testid="stExpander"] summary {
        font-weight: 650 !important;
        color: #0F172A !important;
    }

    /* Streamlit Alert Callouts */
    div[data-testid="stAlert"] {
        border-radius: 10px !important;
        border: 1px solid #E2E8F0 !important;
    }
    div[data-testid="stAlert"] * {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    /* =========================================================
       6. BUTTONS & CONTROLS
       ========================================================= */
    /* Neutral / Secondary Buttons */
    .stApp:not(:has(.auth-visual-panel)) .stButton > button {
        border-radius: var(--radius-md) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        min-height: 38px !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #D8DDE3 !important;
        color: #1E293B !important;
        -webkit-text-fill-color: #1E293B !important;
        box-shadow: var(--shadow-xs) !important;
        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stApp:not(:has(.auth-visual-panel)) .stButton > button * {
        color: #1E293B !important;
        -webkit-text-fill-color: #1E293B !important;
    }

    .stApp:not(:has(.auth-visual-panel)) .stButton > button:hover {
        background: #F8FAFC !important;
        background-color: #F8FAFC !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stApp:not(:has(.auth-visual-panel)) .stButton > button:hover * {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    .stApp:not(:has(.auth-visual-panel)) .stButton > button:active {
        transform: scale(0.99) !important;
    }

    /* Primary Action Buttons (vibrant emerald on dashboard, strictly overridden in auth) */
    .stApp:not(:has(.auth-visual-panel)) .stButton > button[kind="primary"],
    .stApp:not(:has(.auth-visual-panel)) .stButton > button[data-testid*="baseButton-primary"],
    .stApp:not(:has(.auth-visual-panel)) [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        border: 1px solid #059669 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(5, 150, 105, 0.22) !important;
    }

    .stApp:not(:has(.auth-visual-panel)) .stButton > button[kind="primary"] *,
    .stApp:not(:has(.auth-visual-panel)) .stButton > button[data-testid*="baseButton-primary"] *,
    .stApp:not(:has(.auth-visual-panel)) [data-testid="stFormSubmitButton"] button * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    .stApp:not(:has(.auth-visual-panel)) .stButton > button[kind="primary"]:hover,
    .stApp:not(:has(.auth-visual-panel)) .stButton > button[data-testid*="baseButton-primary"]:hover,
    .stApp:not(:has(.auth-visual-panel)) [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        box-shadow: 0 6px 18px rgba(5, 150, 105, 0.30) !important;
        transform: translateY(-1px) !important;
    }

    /* Universal Popover Container — clean and transparent (no outer ghost box) */
    div[data-testid="stPopover"],
    div[data-testid="stPopover"] > div,
    div[data-testid="stPopover"] > div > div {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        border-width: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Universal Popover Trigger Buttons (Profile & others — NO BLACK BUTTONS) */
    div[data-testid="stPopover"] > button,
    div[data-testid="stPopover"] button,
    div[data-testid="stPopover"] [data-testid="stBaseButton-secondary"] {
        background: #F8FAFC !important;
        background-color: #F8FAFC !important;
        background-image: none !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 9px !important;
        color: #334155 !important;
        -webkit-text-fill-color: #334155 !important;
        font-size: 11.5px !important;
        font-weight: 650 !important;
        height: 38px !important;
        min-height: 38px !important;
        padding: 0 10px !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }

    div[data-testid="stPopover"] button *,
    div[data-testid="stPopover"] > button * {
        color: #334155 !important;
        -webkit-text-fill-color: #334155 !important;
    }

    div[data-testid="stPopover"] button:hover,
    div[data-testid="stPopover"] > button:hover {
        background: #EEF2FF !important;
        background-color: #EEF2FF !important;
        border-color: #C7D2FE !important;
        color: #1E1B4B !important;
        -webkit-text-fill-color: #1E1B4B !important;
        transform: translateY(-1px) !important;
    }

    div[data-testid="stPopover"] button:hover *,
    div[data-testid="stPopover"] > button:hover * {
        color: #1E1B4B !important;
        -webkit-text-fill-color: #1E1B4B !important;
    }

    /* =========================================================
       7. EMPTY STATES & UTILITY CARDS
       ========================================================= */
    .tx-empty-state {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 180px !important;
        padding: 30px 20px !important;
        background: #FAF8FB !important;
        border: 1px solid #ECE5EE !important;
        border-radius: 12px !important;
        text-align: center !important;
        box-sizing: border-box !important;
    }

    .tx-empty-icon {
        font-size: 32px !important;
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
        margin-bottom: 8px !important;
    }

    .tx-empty-title {
        font-size: 14px !important;
        font-weight: 750 !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        margin-bottom: 4px !important;
    }

    .tx-empty-copy {
        font-size: 12px !important;
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
        max-width: 380px !important;
    }

    /* Glass Panels */
    .admin-glass {
        background: #FFFFFF !important;
        border: 1px solid #ECE5EE !important;
        border-radius: 12px !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .admin-report-radiant-blue {
        background: linear-gradient(135deg, #FFFFFF 0%, #EEF2FF 100%) !important;
        border-color: #C7D2FE !important;
    }

    /* Keyframe Animations */
    @keyframes panelEntrance {
        from {
            opacity: 0;
            transform: translateY(-6px) scale(0.985);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    @keyframes cardFadeIn {
        from {
            opacity: 0;
            transform: translateY(4px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """


@lru_cache(maxsize=1)
def get_user_theme_styles() -> str:
    return """
    <style>
    /* =========================================================
       CUSTOMER PORTAL (USER UI) — PREMIUM FINTECH EXPERIENCE
       Clean Light Theme, Low Background, Emerald Accents
       ========================================================= */

    /* Universal Token Variables for User UI */
    :root {
        --user-primary: #16805F;
        --user-dark-primary: #0E5B45;
        --user-secondary-green: #21916D;
        --user-light-green: #BFE3D4;
        --user-soft-green: #E8F5F0;
        --user-bg: #F6F8F7;
        --user-card: #FFFFFF;
        --user-text-primary: #17201D;
        --user-text-secondary: #66716D;
        --user-text-muted: #929B97;
        --user-border: #E4E9E6;
        --user-divider: #EDF0EE;
        --user-success: #16805F;
        --user-warning: #C58A18;
        --user-danger: #C45151;
        --user-info: #3778A8;
    }

    /* Page Canvas Background — Low color, clean light fintech backdrop */
    .stApp:has(.st-key-user_top_nav),
    .stApp:has(.user-fixed-brand) {
        background: #F6F8F7 !important;
        background-color: #F6F8F7 !important;
        background-image: radial-gradient(circle at 90% 4%, rgba(22, 128, 95, 0.025) 0%, transparent 40%),
                          radial-gradient(circle at 10% 25%, rgba(33, 145, 109, 0.02) 0%, transparent 35%) !important;
        color: #17201D !important;
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Fixed Customer Brand Header */
    .stApp:has(.st-key-user_top_nav) .user-fixed-brand {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 52px !important;
        min-height: 52px !important;
        max-height: 52px !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        margin: 0 !important;
        padding: 6px 24px !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        background-image: none !important;
        border: 0 !important;
        border-bottom: 1px solid #E4E9E6 !important;
        border-radius: 0 !important;
        box-shadow: 0 1px 3px rgba(23, 32, 29, 0.03) !important;
        z-index: 20002 !important;
        overflow: visible !important;
    }

    .stApp:has(.st-key-user_top_nav) .user-fixed-brand .top-nav-brand-mark svg {
        width: 32px !important;
        height: 32px !important;
        display: block !important;
    }

    .stApp:has(.st-key-user_top_nav) .user-fixed-brand .top-nav-brand-name {
        margin: 0 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-size: 13px !important;
        line-height: 1.1 !important;
        font-weight: 750 !important;
        letter-spacing: .04em !important;
    }

    .stApp:has(.st-key-user_top_nav) .user-fixed-brand .top-nav-brand-subtitle {
        margin-top: 1px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 10px !important;
        line-height: 1.1 !important;
        font-weight: 500 !important;
    }

    /* Fixed Customer Top Navigation Bar */
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav {
        position: fixed !important;
        top: 52px !important;
        left: 0 !important;
        right: 0 !important;
        width: auto !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        box-sizing: border-box !important;
        display: block !important;
        padding: 5px 24px !important;
        margin: 0 !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        background-image: none !important;
        border: 0 !important;
        border-bottom: 1px solid #E4E9E6 !important;
        border-radius: 0 !important;
        box-shadow: 0 2px 6px rgba(23, 32, 29, 0.02) !important;
        z-index: 20001 !important;
        overflow: visible !important;
    }

    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav > div,
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav [data-testid="stVerticalBlockBorderWrapper"],
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav [data-testid="stVerticalBlockBorderWrapper"] > div,
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav [data-testid="stVerticalBlock"],
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav [data-testid="stVerticalBlock"] > div,
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav [data-testid="stElementContainer"],
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav [data-testid="stElementContainer"] > div,
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav .stButton,
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav .stButton > div,
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav div[data-testid="stPopover"],
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav div[data-testid="stPopover"] > div,
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav div[data-testid="stPopover"] > div > div {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        border-width: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav [data-testid="stHorizontalBlock"] {
        position: relative !important;
        z-index: 2 !important;
        width: 100% !important;
        height: 38px !important;
        min-height: 38px !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: stretch !important;
        gap: 8px !important;
    }

    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 0 !important;
        width: 0 !important;
        min-width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative !important;
        overflow: visible !important;
        z-index: 10020 !important;
    }

    .st-key-user_top_nav .stButton,
    .st-key-user_top_nav .stButton > div,
    .st-key-user_top_nav div[data-testid="stPopover"],
    .st-key-user_top_nav div[data-testid="stPopover"] > div {
        width: 100% !important;
        min-width: 0 !important;
        max-width: none !important;
        height: 38px !important;
        display: flex !important;
        align-items: stretch !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Five equal-width customer top nav buttons — uniform 38px height, baseline, and styling */
    .st-key-user_top_nav .stButton > button,
    .st-key-user_top_nav div[data-testid="stPopover"] button {
        width: 100% !important;
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        border-radius: 8px !important;
        padding: 0 14px !important;
        box-sizing: border-box !important;
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        border: 1px solid transparent !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        box-shadow: none !important;
        transform: none !important;
        transition: background 160ms ease, color 160ms ease, border-color 160ms ease !important;
    }

    .st-key-user_top_nav .stButton > button *,
    .st-key-user_top_nav div[data-testid="stPopover"] button * {
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
    }

    .st-key-user_top_nav .stButton > button:hover,
    .st-key-user_top_nav div[data-testid="stPopover"] button:hover {
        background: #F0F7F4 !important;
        background-color: #F0F7F4 !important;
        border-color: #BFE3D4 !important;
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
        transform: none !important;
    }

    .st-key-user_top_nav .stButton > button:hover *,
    .st-key-user_top_nav div[data-testid="stPopover"] button:hover * {
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
    }

    /* Active navigation item: soft green background with dark primary text */
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav .stButton > button[kind="primary"],
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav .stButton > button[data-testid*="baseButton-primary"],
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav div[data-testid="stPopover"] button[aria-expanded="true"],
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav .nav-selected > button {
        background: #E8F5F0 !important;
        background-color: #E8F5F0 !important;
        background-image: none !important;
        border: 1px solid #BFE3D4 !important;
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        transform: none !important;
    }

    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav .stButton > button[kind="primary"] *,
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav .stButton > button[data-testid*="baseButton-primary"] *,
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav div[data-testid="stPopover"] button[aria-expanded="true"] *,
    .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav .nav-selected > button * {
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
    }

    /* Navigation Icons */
    .st-key-user_top_nav .stButton > button [data-testid="stIconMaterial"],
    .st-key-user_top_nav .stButton > button svg {
        color: #66716D !important;
        font-size: 18px !important;
        transition: color 160ms ease !important;
    }

    .st-key-user_top_nav .stButton > button:hover [data-testid="stIconMaterial"],
    .st-key-user_top_nav .stButton > button:hover svg {
        color: #16805F !important;
    }

    .st-key-user_top_nav .stButton > button[kind="primary"] [data-testid="stIconMaterial"],
    .st-key-user_top_nav .stButton > button[kind="primary"] svg,
    .st-key-user_top_nav .nav-selected > button [data-testid="stIconMaterial"],
    .st-key-user_top_nav .nav-selected > button svg {
        color: #16805F !important;
    }

    /* Out-of-flow container collapse to eliminate empty space under fixed header */
    .stApp:has(.st-key-user_top_nav) div[data-testid="stElementContainer"]:has(.user-fixed-brand),
    .stApp:has(.st-key-user_top_nav) div[data-testid="stElementContainer"]:has(#madhu-scroll-reset-anchor),
    .stApp:has(.st-key-user_top_nav) div[data-testid="stElementContainer"]:has(style:only-child),
    .stApp:has(.st-key-user_top_nav) div[data-testid="stElementContainer"]:empty {
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

    .stApp:has(.st-key-user_top_nav) div[data-testid="stElementContainer"]:has(> .st-key-user_top_nav),
    .stApp:has(.st-key-user_top_nav) div[data-testid="stElementContainer"]:has(.st-key-user_top_nav) {
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

    /* Main Block Container — clean top offset and spacing */
    .stApp:has(.st-key-user_top_nav) .block-container,
    .stApp:has(.st-key-user_top_nav) [data-testid="stMainBlockContainer"] {
        position: relative !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        max-width: none !important;
        box-sizing: border-box !important;
        padding-top: 110px !important;
        padding-left: 32px !important;
        padding-right: 32px !important;
        padding-bottom: 48px !important;
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
    }

    /* Customer Page Header */
    .stApp:has(.st-key-user_top_nav) .user-topbar,
    .stApp:has(.st-key-user_top_nav) .admin-topbar {
        position: relative !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: flex-end !important;
        gap: 20px !important;
        margin: 4px 0 22px !important;
        padding: 0 !important;
    }

    .stApp:has(.st-key-user_top_nav) .user-kicker,
    .stApp:has(.st-key-user_top_nav) .admin-page-kicker {
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        margin-bottom: 6px !important;
    }

    .stApp:has(.st-key-user_top_nav) .user-page-title,
    .stApp:has(.st-key-user_top_nav) .admin-page-title {
        margin: 0 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-size: 28px !important;
        line-height: 1.15 !important;
        font-weight: 700 !important;
        letter-spacing: -0.4px !important;
    }

    .stApp:has(.st-key-user_top_nav) .user-page-subtitle,
    .stApp:has(.st-key-user_top_nav) .admin-page-subtitle {
        margin-top: 6px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 13px !important;
        line-height: 1.4 !important;
    }

    /* Floating Dropdowns: My Account, Banking, Profile */
    .st-key-user_account_dropdown,
    .st-key-user_banking_dropdown,
    .st-key-user_profile_dropdown {
        isolation: isolate !important;
        position: absolute !important;
        top: 44px !important;
        margin: 0 !important;
        z-index: 2000000 !important;
        box-sizing: border-box !important;
        overflow: visible !important;
        border: 1px solid #E4E9E6 !important;
        border-radius: 12px !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        background-image: none !important;
        box-shadow: 0 10px 28px rgba(23, 32, 29, 0.08), 0 3px 8px rgba(23, 32, 29, 0.04) !important;
        animation: panelEntrance 0.16s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
    }

    .st-key-user_account_dropdown::after,
    .st-key-user_banking_dropdown::after,
    .st-key-user_profile_dropdown::after {
        content: "" !important;
        position: absolute !important;
        inset: -1px !important;
        z-index: -1 !important;
        background: #FFFFFF !important;
        border: 1px solid #E4E9E6 !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 28px rgba(23, 32, 29, 0.06) !important;
        pointer-events: none !important;
    }

    .st-key-user_account_dropdown > div,
    .st-key-user_banking_dropdown > div,
    .st-key-user_profile_dropdown > div {
        position: relative !important;
        z-index: 1 !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
    }

    .st-key-user_account_dropdown,
    .st-key-user_banking_dropdown {
        left: 0 !important;
        right: auto !important;
        width: min(230px, calc(100vw - 20px)) !important;
        min-width: 200px !important;
        max-width: 240px !important;
        padding: 8px !important;
    }

    /* Option buttons directly inside My Account & Banking dropdowns */
    .st-key-user_account_dropdown .stButton,
    .st-key-user_banking_dropdown .stButton {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }

    .st-key-user_account_dropdown .stButton > button,
    .st-key-user_banking_dropdown .stButton > button {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        width: 100% !important;
        height: 38px !important;
        min-height: 38px !important;
        margin: 0 0 4px 0 !important;
        padding: 0 12px !important;
        border: 1px solid #EDF0EE !important;
        border-radius: 8px !important;
        background: #FAFBFB !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-size: 13px !important;
        font-weight: 550 !important;
        text-align: left !important;
        box-shadow: none !important;
        transform: none !important;
        transition: all 0.15s ease-in-out !important;
    }

    .st-key-user_account_dropdown .stButton > button *,
    .st-key-user_banking_dropdown .stButton > button * {
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
    }

    .st-key-user_account_dropdown .stButton:last-child > button,
    .st-key-user_banking_dropdown .stButton:last-child > button {
        margin-bottom: 0 !important;
    }

    .st-key-user_account_dropdown .stButton > button:hover,
    .st-key-user_banking_dropdown .stButton > button:hover {
        background: #E8F5F0 !important;
        border-color: #BFE3D4 !important;
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
        transform: translateX(2px) !important;
    }

    .st-key-user_account_dropdown .stButton > button:hover *,
    .st-key-user_banking_dropdown .stButton > button:hover * {
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
    }

    .st-key-user_account_dropdown .stButton > button [data-testid="stIconMaterial"],
    .st-key-user_banking_dropdown .stButton > button [data-testid="stIconMaterial"] {
        font-size: 18px !important;
        margin-right: 8px !important;
        color: #66716D !important;
        transition: color 0.15s ease !important;
    }

    .st-key-user_account_dropdown .stButton > button:hover [data-testid="stIconMaterial"],
    .st-key-user_banking_dropdown .stButton > button:hover [data-testid="stIconMaterial"] {
        color: #16805F !important;
    }

    /* Customer Profile Dropdown Card */
    .st-key-user_profile_dropdown {
        left: auto !important;
        right: 0 !important;
        width: min(310px, calc(100vw - 20px)) !important;
        min-width: 280px !important;
        max-width: 310px !important;
        padding: 16px 14px 14px 14px !important;
    }

    .st-key-user_profile_dropdown .user-profile-header {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        text-align: center !important;
        padding: 2px 0 10px 0 !important;
        border-bottom: 1px solid #EDF0EE !important;
        margin-bottom: 10px !important;
    }

    .st-key-user_profile_dropdown .user-profile-avatar {
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        min-height: 48px !important;
        border-radius: 50% !important;
        background: #E8F5F0 !important;
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        font-size: 18px !important;
        font-weight: 750 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto 8px auto !important;
        border: 2px solid #BFE3D4 !important;
        box-shadow: 0 2px 6px rgba(22, 128, 95, 0.10) !important;
    }

    .st-key-user_profile_dropdown .user-profile-name {
        font-size: 14px !important;
        font-weight: 750 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        line-height: 1.25 !important;
        margin: 0 !important;
        text-align: center !important;
    }

    .st-key-user_profile_dropdown .user-profile-role {
        font-size: 10px !important;
        font-weight: 600 !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin: 4px 0 0 0 !important;
        text-align: center !important;
    }

    .st-key-user_profile_dropdown .user-profile-table {
        background: #F6F8F7 !important;
        border: 1px solid #E4E9E6 !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        margin-bottom: 10px !important;
        box-sizing: border-box !important;
    }

    .st-key-user_profile_dropdown .user-profile-row {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 12px !important;
        min-height: 28px !important;
        padding: 5px 0 !important;
        border-bottom: 1px solid #EDF0EE !important;
        box-sizing: border-box !important;
    }

    .st-key-user_profile_dropdown .user-profile-row:last-child {
        border-bottom: none !important;
    }

    .st-key-user_profile_dropdown .user-profile-row span {
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 11px !important;
        font-weight: 550 !important;
    }

    .st-key-user_profile_dropdown .user-profile-row strong {
        text-align: right !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        overflow-wrap: anywhere !important;
    }

    .st-key-user_profile_dropdown .st-key-user_top_profile_settings button {
        width: 100% !important;
        height: 36px !important;
        min-height: 36px !important;
        margin: 0 0 6px 0 !important;
        border-radius: 8px !important;
        background: #FFFFFF !important;
        border: 1px solid #BFE3D4 !important;
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        transition: background 160ms ease !important;
    }

    .st-key-user_profile_dropdown .st-key-user_top_profile_settings button:hover {
        background: #E8F5F0 !important;
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
    }

    /* Subtle danger styling for Logout */
    .st-key-user_profile_dropdown .st-key-user_top_profile_logout button {
        width: 100% !important;
        height: 36px !important;
        min-height: 36px !important;
        margin: 0 !important;
        border-radius: 8px !important;
        background: #FFFFFF !important;
        border: 1px solid #E4E9E6 !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        transition: all 160ms ease !important;
    }

    .st-key-user_profile_dropdown .st-key-user_top_profile_logout button:hover {
        background: #FFF1F2 !important;
        border-color: #FFE4E6 !important;
        color: #C45151 !important;
        -webkit-text-fill-color: #C45151 !important;
    }

    /* Customer KPI & Analytics Cards */
    .stApp:has(.st-key-user_top_nav) .user-ref-kpi,
    .stApp:has(.st-key-user_top_nav) .admin-kpi {
        width: 100% !important;
        min-height: 112px !important;
        padding: 16px 18px !important;
        background: #FFFFFF !important;
        border: 1px solid #E4E9E6 !important;
        border-radius: 13px !important;
        box-shadow: 0 5px 20px rgba(23, 32, 29, 0.05) !important;
        transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease !important;
    }

    .stApp:has(.st-key-user_top_nav) .user-ref-kpi:hover,
    .stApp:has(.st-key-user_top_nav) .admin-kpi:hover {
        border-color: #BFE3D4 !important;
        box-shadow: 0 8px 25px rgba(23, 32, 29, 0.08) !important;
        transform: translateY(-2px) !important;
    }

    .stApp:has(.st-key-user_top_nav) .admin-kpi-top {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        margin-bottom: 8px !important;
    }

    .stApp:has(.st-key-user_top_nav) .admin-kpi-label {
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
    }

    .stApp:has(.st-key-user_top_nav) .admin-kpi-icon {
        width: 28px !important;
        height: 28px !important;
        border-radius: 50% !important;
        background: #E8F5F0 !important;
        color: #16805F !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 14px !important;
    }

    .stApp:has(.st-key-user_top_nav) .admin-kpi-value {
        margin-top: 4px !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-size: 24px !important;
        line-height: 1.1 !important;
        font-weight: 750 !important;
    }

    .stApp:has(.st-key-user_top_nav) .admin-kpi-foot {
        margin-top: 6px !important;
        color: #929B97 !important;
        -webkit-text-fill-color: #929B97 !important;
        font-size: 11px !important;
        font-weight: 500 !important;
    }

    /* Customer Balance Card (prominent 14px radius, #17201D numbers) */
    .balance-card {
        position: relative !important;
        overflow: hidden !important;
        padding: 24px 26px !important;
        border-radius: 14px !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E4E9E6 !important;
        color: #17201D !important;
        box-shadow: 0 8px 25px rgba(23, 32, 29, 0.06) !important;
        margin-bottom: 20px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
    }

    .balance-card:hover {
        transform: translateY(-2px) !important;
        border-color: #BFE3D4 !important;
        box-shadow: 0 12px 30px rgba(23, 32, 29, 0.08) !important;
    }

    .balance-card::before {
        content: "" !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 4px !important;
        height: 100% !important;
        background: #16805F !important;
    }

    .balance-card .balance-label {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-bottom: 6px !important;
    }

    .balance-card .balance-number {
        font-size: 32px !important;
        font-weight: 750 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        letter-spacing: -0.5px !important;
        margin-bottom: 8px !important;
        line-height: 1.15 !important;
    }

    .balance-card .balance-account {
        font-size: 12px !important;
        color: #929B97 !important;
        -webkit-text-fill-color: #929B97 !important;
        font-weight: 500 !important;
    }

    /* Universal Cards, Panels, and Containers */
    .user-panel,
    .customer-profile-card,
    .stApp:has(.st-key-user_top_nav) div[data-testid="stForm"],
    .stApp:has(.st-key-user_top_nav) div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stForm"]),
    .stApp:has(.st-key-user_top_nav) [data-testid="stExpander"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E4E9E6 !important;
        border-radius: 13px !important;
        box-shadow: 0 5px 20px rgba(23, 32, 29, 0.05) !important;
        padding: 22px 24px !important;
        box-sizing: border-box !important;
        margin-bottom: 16px !important;
    }

    .user-panel-title,
    .customer-profile-card-title {
        font-size: 16px !important;
        font-weight: 750 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        margin-bottom: 4px !important;
    }

    .user-panel-subtitle,
    .customer-profile-card-subtitle {
        font-size: 12px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        margin-bottom: 16px !important;
    }

    .account-mini {
        background: #F6F8F7 !important;
        border: 1px solid #EDF0EE !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        margin-top: 8px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
    }

    .account-mini-label {
        font-size: 12px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-weight: 500 !important;
    }

    .account-mini-value {
        font-size: 13px !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-weight: 700 !important;
    }

    .customer-profile-detail-row {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding: 10px 0 !important;
        border-bottom: 1px solid #EDF0EE !important;
    }

    .customer-profile-detail-row:last-child {
        border-bottom: none !important;
    }

    .customer-profile-detail-label {
        font-size: 13px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-weight: 550 !important;
    }

    .customer-profile-detail-value {
        font-size: 13px !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-weight: 650 !important;
    }

    .customer-profile-security-chip {
        display: inline-block !important;
        background: #E8F5F0 !important;
        color: #16805F !important;
        padding: 4px 10px !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        margin-top: 6px !important;
    }

    /* Universal Button System — scoped to main page content (NOT top navbar) */
    .stApp:has(.st-key-user_top_nav) .block-container .stButton > button[kind="primary"],
    .stApp:has(.st-key-user_top_nav) .block-container .stButton > button[data-testid*="baseButton-primary"],
    .stApp:has(.st-key-user_top_nav) button[kind="primaryFormSubmit"],
    .stApp:has(.st-key-user_top_nav) [data-testid="stFormSubmitButton"] > button {
        background: #16805F !important;
        background-color: #16805F !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        height: 42px !important;
        min-height: 42px !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(22, 128, 95, 0.12) !important;
        transition: transform 160ms ease, background 160ms ease, box-shadow 160ms ease !important;
    }

    .stApp:has(.st-key-user_top_nav) .block-container .stButton > button[kind="primary"] *,
    .stApp:has(.st-key-user_top_nav) .block-container .stButton > button[data-testid*="baseButton-primary"] *,
    .stApp:has(.st-key-user_top_nav) button[kind="primaryFormSubmit"] *,
    .stApp:has(.st-key-user_top_nav) [data-testid="stFormSubmitButton"] > button * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    .stApp:has(.st-key-user_top_nav) .block-container .stButton > button[kind="primary"]:hover,
    .stApp:has(.st-key-user_top_nav) .block-container .stButton > button[data-testid*="baseButton-primary"]:hover,
    .stApp:has(.st-key-user_top_nav) button[kind="primaryFormSubmit"]:hover,
    .stApp:has(.st-key-user_top_nav) [data-testid="stFormSubmitButton"] > button:hover {
        background: #0E5B45 !important;
        background-color: #0E5B45 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 7px 18px rgba(14, 91, 69, 0.16) !important;
    }

    /* Secondary buttons in content */
    .stApp:has(.st-key-user_top_nav) .block-container .stButton > button:not([kind="primary"]):not([data-testid*="baseButton-primary"]) {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        border: 1px solid #BFE3D4 !important;
        border-radius: 8px !important;
        height: 40px !important;
        min-height: 40px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        transition: all 160ms ease !important;
    }

    .stApp:has(.st-key-user_top_nav) .block-container .stButton > button:not([kind="primary"]):not([data-testid*="baseButton-primary"]):hover {
        background: #E8F5F0 !important;
        background-color: #E8F5F0 !important;
        border-color: #16805F !important;
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
        transform: translateY(-1px) !important;
    }

    /* Form Inputs & Fields: User Theme */
    .stApp:has(.st-key-user_top_nav) div[data-testid="stTextInput"],
    .stApp:has(.st-key-user_top_nav) div[data-testid="stTextInput"] > div,
    .stApp:has(.st-key-user_top_nav) div[data-testid="stNumberInput"],
    .stApp:has(.st-key-user_top_nav) div[data-testid="stNumberInput"] > div,
    .stApp:has(.st-key-user_top_nav) div[data-testid="stSelectbox"],
    .stApp:has(.st-key-user_top_nav) div[data-testid="stSelectbox"] > div,
    .stApp:has(.st-key-user_top_nav) div[data-testid="stMultiSelect"],
    .stApp:has(.st-key-user_top_nav) div[data-testid="stMultiSelect"] > div,
    .stApp:has(.st-key-user_top_nav) div[data-testid="stTextArea"],
    .stApp:has(.st-key-user_top_nav) div[data-testid="stTextArea"] > div,
    .stApp:has(.st-key-user_top_nav) div[data-testid="stDateInput"],
    .stApp:has(.st-key-user_top_nav) div[data-testid="stDateInput"] > div,
    .stApp:has(.st-key-user_top_nav) div[data-testid="stTimeInput"],
    .stApp:has(.st-key-user_top_nav) div[data-testid="stTimeInput"] > div {
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }

    .stApp:has(.st-key-user_top_nav) [data-testid="stTextInputRootElement"],
    .stApp:has(.st-key-user_top_nav) [data-testid="stNumberInputContainer"],
    .stApp:has(.st-key-user_top_nav) [data-testid="stTextAreaRootElement"],
    .stApp:has(.st-key-user_top_nav) [data-testid="stSelectbox"] > div,
    .stApp:has(.st-key-user_top_nav) [data-testid="stMultiSelect"] > div,
    .stApp:has(.st-key-user_top_nav) [data-testid="stDateInput"] > div,
    .stApp:has(.st-key-user_top_nav) [data-testid="stTimeInput"] > div,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="input"],
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="select"] > div,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="textarea"],
    .stApp:has(.st-key-user_top_nav) .stTextInput [data-testid="stTextInputRootElement"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1.5px solid #8FA299 !important;
        border-radius: 8px !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-size: 13.5px !important;
        min-height: 42px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
        box-sizing: border-box !important;
    }

    .stApp:has(.st-key-user_top_nav) div[data-baseweb="base-input"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }

    .stApp:has(.st-key-user_top_nav) div[data-baseweb="input"] input,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="base-input"] input,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="textarea"] textarea,
    .stApp:has(.st-key-user_top_nav) [data-testid="stTextInputField"],
    .stApp:has(.st-key-user_top_nav) [data-testid="stNumberInputField"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        outline: none !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
    }

    .stApp:has(.st-key-user_top_nav) [data-testid="stTextInputRootElement"]:hover,
    .stApp:has(.st-key-user_top_nav) [data-testid="stNumberInputContainer"]:hover,
    .stApp:has(.st-key-user_top_nav) [data-testid="stTextAreaRootElement"]:hover,
    .stApp:has(.st-key-user_top_nav) [data-testid="stSelectbox"] > div:hover,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="input"]:hover,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="select"] > div:hover,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="textarea"]:hover {
        border-color: #16805F !important;
    }

    .stApp:has(.st-key-user_top_nav) [data-testid="stTextInputRootElement"]:focus-within,
    .stApp:has(.st-key-user_top_nav) [data-testid="stNumberInputContainer"]:focus-within,
    .stApp:has(.st-key-user_top_nav) [data-testid="stTextAreaRootElement"]:focus-within,
    .stApp:has(.st-key-user_top_nav) [data-testid="stSelectbox"] > div:focus-within,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="input"]:focus-within,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="select"] > div:focus-within,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="textarea"]:focus-within {
        border-color: #16805F !important;
        box-shadow: 0 0 0 3px rgba(22, 128, 95, 0.18) !important;
        outline: none !important;
    }

    .stApp:has(.st-key-user_top_nav) input:disabled,
    .stApp:has(.st-key-user_top_nav) div[data-baseweb="input"]:has(input:disabled) {
        background: #F6F8F7 !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        border-color: #CBD5E1 !important;
    }

    .stApp:has(.st-key-user_top_nav) label p {
        color: #17201D !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    /* Quick Actions (Dashboard) */
    .user-ref-lower-heading {
        color: #17201D !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        margin: 24px 0 4px !important;
    }

    .user-ref-lower-subtitle {
        color: #66716D !important;
        font-size: 12px !important;
        margin-bottom: 14px !important;
    }

    .user-ref-action-card {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 2px 2px 8px 2px !important;
        box-shadow: none !important;
    }

    .user-ref-action-title {
        font-size: 14.5px !important;
        font-weight: 700 !important;
        color: #17201D !important;
        margin-bottom: 2px !important;
    }

    .user-ref-action-copy {
        font-size: 12px !important;
        color: #66716D !important;
        line-height: 1.35 !important;
    }

    /* Customer Dashboard Quick Action Cards */
    .stApp:has(.st-key-user_top_nav) div[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        border: 1px solid #E4E9E6 !important;
        border-radius: 12px !important;
        box-shadow: 0 3px 12px rgba(23, 32, 29, 0.04) !important;
        transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease !important;
    }

    .stApp:has(.st-key-user_top_nav) div[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #BFE3D4 !important;
        box-shadow: 0 8px 22px rgba(22, 128, 95, 0.09) !important;
        transform: translateY(-2px) !important;
    }

    /* All 4 quick action buttons - unified, high contrast primary emerald */
    .st-key-dashboard_deposit button,
    .st-key-dashboard_withdraw button,
    .st-key-dashboard_transfer button,
    .st-key-dashboard_transactions button {
        background: #16805F !important;
        background-color: #16805F !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        height: 38px !important;
        min-height: 38px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        box-shadow: 0 2px 6px rgba(22, 128, 95, 0.14) !important;
        transition: all 160ms ease !important;
    }

    .st-key-dashboard_deposit button:hover,
    .st-key-dashboard_withdraw button:hover,
    .st-key-dashboard_transfer button:hover,
    .st-key-dashboard_transactions button:hover {
        background: #0E5B45 !important;
        background-color: #0E5B45 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(14, 91, 69, 0.18) !important;
    }

    .st-key-dashboard_deposit button svg,
    .st-key-dashboard_withdraw button svg,
    .st-key-dashboard_transfer button svg,
    .st-key-dashboard_transactions button svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    /* Recent Transactions & Row System */
    .user-ref-transaction-row {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 12px 16px !important;
        background: #FFFFFF !important;
        border: 1px solid #E4E9E6 !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 2px 6px rgba(23, 32, 29, 0.02) !important;
        transition: background 150ms ease, border-color 150ms ease !important;
    }

    .user-ref-transaction-row:hover {
        background: #F9FBFA !important;
        border-color: #BFE3D4 !important;
    }

    .user-ref-transaction-kind {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #17201D !important;
    }

    .user-ref-transaction-date {
        font-size: 11px !important;
        color: #929B97 !important;
        margin-top: 2px !important;
    }

    .user-ref-transaction-amount {
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #16805F !important;
    }

    /* Expanders in Transactions page */
    .stApp:has(.st-key-user_top_nav) [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #E4E9E6 !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        padding: 0 !important;
        box-shadow: 0 2px 6px rgba(23, 32, 29, 0.02) !important;
    }

    .stApp:has(.st-key-user_top_nav) [data-testid="stExpander"] summary {
        padding: 12px 16px !important;
        font-weight: 600 !important;
        color: #17201D !important;
        font-size: 13.5px !important;
        border-radius: 10px !important;
    }

    .stApp:has(.st-key-user_top_nav) [data-testid="stExpander"] summary:hover {
        background: #F9FBFA !important;
    }

    .stApp:has(.st-key-user_top_nav) [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 14px 18px !important;
        border-top: 1px solid #EDF0EE !important;
        background: #FAFBFB !important;
        border-radius: 0 0 10px 10px !important;
    }

    /* Profile Page Placeholders & Avatars */
    .customer-profile-page-placeholder {
        width: 80px !important;
        height: 80px !important;
        border-radius: 50% !important;
        background: #E8F5F0 !important;
        color: #16805F !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 2px solid #BFE3D4 !important;
        margin-bottom: 12px !important;
    }

    .customer-profile-page-image {
        width: 80px !important;
        height: 80px !important;
        border-radius: 50% !important;
        object-fit: cover !important;
        border: 2px solid #BFE3D4 !important;
        margin-bottom: 12px !important;
    }

    /* Scoped container border and metrics styling */
    .stApp:has(.st-key-user_top_nav) .block-container [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        border: 1px solid #E4E9E6 !important;
        border-radius: 13px !important;
        box-shadow: 0 5px 20px rgba(23, 32, 29, 0.05) !important;
    }

    .stApp:has(.st-key-user_top_nav) [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #E4E9E6 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 14px rgba(23, 32, 29, 0.04) !important;
    }

    .stApp:has(.st-key-user_top_nav) [data-testid="stMetricLabel"] * {
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
    }

    .stApp:has(.st-key-user_top_nav) [data-testid="stMetricValue"] * {
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-size: 22px !important;
        font-weight: 750 !important;
    }

    /* Mobile Responsive Adaptation */
    @media (max-width: 780px) {
        .stApp:has(.st-key-user_top_nav) .block-container,
        .stApp:has(.st-key-user_top_nav) [data-testid="stMainBlockContainer"] {
            padding-left: 14px !important;
            padding-right: 14px !important;
            padding-top: 104px !important;
        }

        .stApp:has(.st-key-user_top_nav) .user-fixed-brand {
            height: 48px !important;
            padding: 4px 14px !important;
        }

        .stApp:has(.st-key-user_top_nav) .st-key-user_top_nav {
            top: 48px !important;
            height: 48px !important;
            min-height: 48px !important;
            padding: 4px 10px !important;
        }
    }
    </style>
    """


@lru_cache(maxsize=1)
def get_admin_theme_styles() -> str:
    return """
    <style>
    /* =========================================================
       MADHU BANK — PREMIUM ENTERPRISE ADMIN BANKING DASHBOARD
       Color System:
       PRIMARY: #16805F | DARK: #0E5B45 | SECONDARY: #21916D
       LIGHT: #BFE3D4 | SOFT: #E8F5F0 | PAGE BG: #F5F7F6 | SURFACE: #FFFFFF
       PRIMARY TEXT: #17201D | SECONDARY TEXT: #66716D | MUTED: #929B97
       BORDER: #E1E7E3 | DIVIDER: #EDF0EE
       SUCCESS: #16805F | WARNING: #C58A18 | DANGER: #C45151 | INFO: #3778A8
       ========================================================= */

    /* Base Canvas & Viewport Reset for Admin */
    html:has(.st-key-admin_top_nav),
    body:has(.st-key-admin_top_nav),
    .stApp:has(.st-key-admin_top_nav) {
        font-family: 'Inter', ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background: #F5F7F6 !important;
        background-color: #F5F7F6 !important;
        background-image: none !important;
        color: #17201D !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }

    /* Fixed Admin Brand Header */
    .stApp:has(.st-key-admin_top_nav) .admin-fixed-brand {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 52px !important;
        min-height: 52px !important;
        max-height: 52px !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        margin: 0 !important;
        padding: 6px 24px !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border-bottom: 1px solid #E1E7E3 !important;
        box-shadow: 0 1px 3px rgba(23, 32, 29, 0.02) !important;
        z-index: 20002 !important;
        overflow: visible !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-fixed-brand .top-nav-brand-mark svg {
        width: 32px !important;
        height: 32px !important;
        display: block !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-fixed-brand .top-nav-brand-name {
        margin: 0 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-size: 13px !important;
        line-height: 1.1 !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-fixed-brand .top-nav-brand-subtitle {
        margin-top: 1px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 10px !important;
        line-height: 1.1 !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
    }

    /* Fixed Admin Top Navigation Bar */
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav {
        position: fixed !important;
        top: 52px !important;
        left: 0 !important;
        right: 0 !important;
        width: auto !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        box-sizing: border-box !important;
        display: block !important;
        padding: 5px 24px !important;
        margin: 0 !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border-bottom: 1px solid #E1E7E3 !important;
        box-shadow: 0 3px 15px rgba(23, 32, 29, 0.04) !important;
        z-index: 20001 !important;
        overflow: visible !important;
    }

    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav > div,
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stVerticalBlockBorderWrapper"],
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stVerticalBlockBorderWrapper"] > div,
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stVerticalBlock"],
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stVerticalBlock"] > div,
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stElementContainer"],
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stElementContainer"] > div,
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav .stButton,
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav .stButton > div,
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav div[data-testid="stPopover"],
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav div[data-testid="stPopover"] > div,
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav div[data-testid="stPopover"] > div > div {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        border-width: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stHorizontalBlock"] {
        position: relative !important;
        z-index: 2 !important;
        width: 100% !important;
        height: 38px !important;
        min-height: 38px !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: stretch !important;
        gap: 6px !important;
    }

    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 0 !important;
        width: 0 !important;
        min-width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative !important;
    }

    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div,
    .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav [data-testid="stHorizontalBlock"] > div[data-testid="column"] > div,
    .st-key-admin_top_nav .stButton,
    .st-key-admin_top_nav .stButton > div,
    .st-key-admin_top_nav div[data-testid="stPopover"],
    .st-key-admin_top_nav div[data-testid="stPopover"] > div,
    .st-key-admin_top_nav div[data-testid="stPopover"] > div > div {
        display: flex !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: none !important;
        flex: 1 1 auto !important;
        height: 38px !important;
        margin: 0 !important;
        padding: 0 !important;
        box-sizing: border-box !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
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
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
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
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }

    /* Standardize material icon sizing across all 8 controls (18px) */
    .st-key-admin_top_nav .stButton > button svg,
    .st-key-admin_top_nav div[data-testid="stPopover"] button svg,
    .st-key-admin_top_nav .stButton > button [data-testid="stIconMaterial"],
    .st-key-admin_top_nav div[data-testid="stPopover"] button [data-testid="stIconMaterial"] {
        font-size: 18px !important;
        width: 18px !important;
        height: 18px !important;
        color: currentColor !important;
        fill: currentColor !important;
        margin: 0 !important;
    }

    .st-key-admin_top_nav div[data-testid="stPopover"] button svg:last-of-type:not(:first-child) {
        display: none !important;
    }

    /* Navigation Hover */
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

    /* Active Admin page button: Brand Green #16805F */
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

    /* Out-of-flow container collapse */
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stElementContainer"]:has(.admin-fixed-brand),
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stElementContainer"]:has(#madhu-scroll-reset-anchor),
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stElementContainer"]:has(style:only-child),
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stElementContainer"]:empty {
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

    .stApp:has(.st-key-admin_top_nav) div[data-testid="stElementContainer"]:has(> .st-key-admin_top_nav),
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stElementContainer"]:has(.st-key-admin_top_nav) {
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

    /* Admin Main Block Container */
    .stApp:has(.st-key-admin_top_nav) .block-container,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stMainBlockContainer"] {
        position: relative !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        max-width: none !important;
        box-sizing: border-box !important;
        padding-top: 114px !important;
        padding-left: 32px !important;
        padding-right: 32px !important;
        padding-bottom: 48px !important;
        background: #F5F7F6 !important;
        background-color: #F5F7F6 !important;
        background-image: none !important;
    }

    /* Admin Page Header */
    .stApp:has(.st-key-admin_top_nav) .admin-topbar {
        position: relative !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: flex-end !important;
        gap: 20px !important;
        margin: 4px 0 24px !important;
        padding: 0 !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-page-kicker {
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        margin-bottom: 6px !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-page-title {
        margin: 0 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-size: 28px !important;
        line-height: 1.15 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-page-subtitle {
        margin-top: 6px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 13px !important;
        line-height: 1.45 !important;
        font-weight: 400 !important;
    }

    /* Section Panels */
    .admin-panel-title {
        margin-bottom: 14px !important;
    }

    .admin-panel-title-main {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        letter-spacing: -0.2px !important;
    }

    .admin-panel-title-sub {
        font-size: 12px !important;
        font-weight: 400 !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        margin-top: 3px !important;
    }

    /* Universal Enterprise Cards (Section 18) */
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E1E7E3 !important;
        border-radius: 12px !important;
        box-shadow: 0 5px 20px rgba(23, 32, 29, 0.05) !important;
        padding: 20px !important;
        box-sizing: border-box !important;
        transition: box-shadow 150ms ease, border-color 150ms ease !important;
    }

    .stApp:has(.st-key-admin_top_nav) div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
        border-color: #BFE3D4 !important;
        box-shadow: 0 8px 24px rgba(23, 32, 29, 0.08) !important;
    }

    /* KPI / Summary Cards (Section 8, 9) */
    .stApp:has(.st-key-admin_top_nav) .admin-kpi {
        width: 100% !important;
        min-height: 116px !important;
        padding: 18px 20px !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E1E7E3 !important;
        border-radius: 14px !important;
        box-shadow: 0 5px 20px rgba(23, 32, 29, 0.05) !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-kpi:hover {
        border-color: #BFE3D4 !important;
        box-shadow: 0 8px 24px rgba(23, 32, 29, 0.08) !important;
        transform: translateY(-2px) !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-kpi-top {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        margin-bottom: 10px !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-kpi-label {
        font-family: 'Inter', sans-serif !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
    }

    /* Small soft-green icon container (Section 9) */
    .stApp:has(.st-key-admin_top_nav) .admin-kpi-icon {
        width: 32px !important;
        height: 32px !important;
        border-radius: 8px !important;
        background: #E8F5F0 !important;
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 16px !important;
        line-height: 1 !important;
        flex-shrink: 0 !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-kpi-value {
        font-family: 'Inter', sans-serif !important;
        font-size: 28px !important;
        line-height: 1.1 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        margin: 4px 0 8px 0 !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-kpi-foot {
        font-size: 11.5px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-weight: 500 !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-kpi-foot.admin-positive {
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-kpi-foot.admin-danger {
        color: #C45151 !important;
        -webkit-text-fill-color: #C45151 !important;
        font-weight: 600 !important;
    }

    .stApp:has(.st-key-admin_top_nav) .admin-kpi-foot.admin-warning {
        color: #C58A18 !important;
        -webkit-text-fill-color: #C58A18 !important;
        font-weight: 600 !important;
    }

    /* Mini Labels in Account Expander */
    .admin-mini-label {
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.8px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }

    .admin-mini-value {
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
    }

    /* Admin Data Tables (Section 10) */
    .admin-table-wrap {
        overflow-x: auto !important;
        border: 1px solid #E1E7E3 !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(23, 32, 29, 0.03) !important;
        margin: 8px 0 !important;
    }

    .admin-table {
        width: 100% !important;
        border-collapse: collapse !important;
        table-layout: auto !important;
        min-width: 900px !important;
        font-size: 12.5px !important;
        font-family: 'Inter', sans-serif !important;
    }

    .admin-table th {
        padding: 12px 16px !important;
        text-align: left !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-size: 11.5px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
        font-weight: 600 !important;
        background: #F7F9F8 !important;
        border-bottom: 1px solid #E1E7E3 !important;
        white-space: nowrap !important;
    }

    .admin-table td {
        padding: 13px 16px !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        border-bottom: 1px solid #EDF0EE !important;
        vertical-align: middle !important;
        white-space: nowrap !important;
        font-weight: 500 !important;
        font-size: 12.5px !important;
    }

    .admin-table tr:last-child td {
        border-bottom: none !important;
    }

    .admin-table tr:hover td {
        background: #F8FBFA !important;
    }

    .admin-muted {
        color: #929B97 !important;
        -webkit-text-fill-color: #929B97 !important;
        font-size: 12px !important;
    }

    /* Action button in table that forwards to arrow symbol below */
    .admin-manage-btn {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        padding: 0 !important;
        margin: 0 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12.5px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 3px !important;
        transition: color 120ms ease, transform 120ms ease !important;
    }

    .admin-manage-btn:hover {
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        text-decoration: underline !important;
    }

    .admin-manage-btn:active {
        transform: translateY(1px) !important;
    }

    /* Expander styling in admin accounts */
    .stApp:has(.st-key-admin_top_nav) div[class*="st-key-expander_wrap_"] {
        margin-bottom: 8px !important;
    }

    .stApp:has(.st-key-admin_top_nav) div[class*="st-key-expander_wrap_"] details[data-testid="stExpander"] {
        border: 1px solid #E1E7E3 !important;
        border-radius: 8px !important;
        background: #FFFFFF !important;
        transition: border-color 200ms ease, box-shadow 200ms ease !important;
    }

    .stApp:has(.st-key-admin_top_nav) div[class*="st-key-expander_wrap_"] details[data-testid="stExpander"]:hover {
        border-color: #BFE3D4 !important;
    }

    .stApp:has(.st-key-admin_top_nav) div[class*="st-key-expander_wrap_"] details[data-testid="stExpander"][open] {
        border-color: #16805F !important;
        box-shadow: 0 4px 14px rgba(22, 128, 95, 0.08) !important;
    }

    /* Status Badges (Section 11) */
    .status-badge {
        display: inline-flex !important;
        align-items: center !important;
        padding: 4px 8px !important;
        border-radius: 6px !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        letter-spacing: 0.2px !important;
    }

    .status-completed, .status-active, .status-approved {
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        background: #E8F5F0 !important;
        border: 1px solid #BFE3D4 !important;
    }

    .status-pending, .status-processing, .status-review {
        color: #C58A18 !important;
        -webkit-text-fill-color: #C58A18 !important;
        background: #FFF6E5 !important;
        border: 1px solid #FDE68A !important;
    }

    .status-failed, .status-rejected, .status-disabled, .status-cancelled {
        color: #C45151 !important;
        -webkit-text-fill-color: #C45151 !important;
        background: #FFF0F1 !important;
        border: 1px solid #FECDD3 !important;
    }

    .status-neutral {
        color: #3778A8 !important;
        -webkit-text-fill-color: #3778A8 !important;
        background: #EEF5FA !important;
        border: 1px solid #BAE6FD !important;
    }

    /* Action Buttons in Content (Section 15) */
    .stApp:has(.st-key-admin_top_nav) .stButton:not(.st-key-admin_top_nav *) > button {
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
        height: 38px !important;
        min-height: 38px !important;
        padding: 0 16px !important;
        transition: all 150ms ease !important;
    }

    .stApp:has(.st-key-admin_top_nav) .stButton:not(.st-key-admin_top_nav *) > button:hover {
        transform: translateY(-1px) !important;
    }

    /* Primary buttons */
    .stApp:has(.st-key-admin_top_nav) .stButton:not(.st-key-admin_top_nav *) > button[kind="primary"],
    .stApp:has(.st-key-admin_top_nav) .stButton:not(.st-key-admin_top_nav *) > button[data-testid*="baseButton-primary"] {
        background: #16805F !important;
        background-color: #16805F !important;
        border: 1px solid #0E5B45 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(22, 128, 95, 0.20) !important;
    }

    .stApp:has(.st-key-admin_top_nav) .stButton:not(.st-key-admin_top_nav *) > button[kind="primary"]:hover,
    .stApp:has(.st-key-admin_top_nav) .stButton:not(.st-key-admin_top_nav *) > button[data-testid*="baseButton-primary"]:hover {
        background: #0E5B45 !important;
        background-color: #0E5B45 !important;
        border-color: #0E5B45 !important;
    }

    /* Secondary / Default buttons */
    .stApp:has(.st-key-admin_top_nav) .stButton:not(.st-key-admin_top_nav *) > button[kind="secondary"],
    .stApp:has(.st-key-admin_top_nav) .stButton:not(.st-key-admin_top_nav *) > button[data-testid*="baseButton-secondary"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #BFE3D4 !important;
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
    }

    .stApp:has(.st-key-admin_top_nav) .stButton:not(.st-key-admin_top_nav *) > button[kind="secondary"]:hover,
    .stApp:has(.st-key-admin_top_nav) .stButton:not(.st-key-admin_top_nav *) > button[data-testid*="baseButton-secondary"]:hover {
        background: #E8F5F0 !important;
        background-color: #E8F5F0 !important;
        border-color: #16805F !important;
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
    }

    /* Download button */
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stDownloadButton"] > button {
        background: #FFFFFF !important;
        border: 1px solid #BFE3D4 !important;
        border-radius: 8px !important;
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
        height: 38px !important;
        transition: all 150ms ease !important;
    }

    .stApp:has(.st-key-admin_top_nav) div[data-testid="stDownloadButton"] > button:hover {
        background: #E8F5F0 !important;
        border-color: #16805F !important;
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
        transform: translateY(-1px) !important;
    }

    /* Content Popover Trigger Buttons (e.g. Details in Accounts) */
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stPopover"]:not(.st-key-admin_top_nav *),
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stPopover"]:not(.st-key-admin_top_nav *) > div {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        border-width: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }

    .stApp:has(.st-key-admin_top_nav) div[data-testid="stPopover"]:not(.st-key-admin_top_nav *) > button {
        width: 100% !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #BFE3D4 !important;
        border-radius: 8px !important;
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
        height: 38px !important;
        min-height: 38px !important;
        transition: all 150ms ease !important;
    }

    .stApp:has(.st-key-admin_top_nav) div[data-testid="stPopover"]:not(.st-key-admin_top_nav *) > button:hover {
        background: #E8F5F0 !important;
        background-color: #E8F5F0 !important;
        border-color: #16805F !important;
        color: #0E5B45 !important;
        -webkit-text-fill-color: #0E5B45 !important;
        transform: translateY(-1px) !important;
    }

    /* Search & Inputs: Admin Theme - Crisp, visible borders across all entry fields */
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stTextInput"],
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stTextInput"] > div,
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stNumberInput"],
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stNumberInput"] > div,
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stSelectbox"],
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stSelectbox"] > div,
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stMultiSelect"],
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stMultiSelect"] > div,
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stTextArea"],
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stTextArea"] > div,
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stDateInput"],
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stDateInput"] > div,
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stTimeInput"],
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stTimeInput"] > div {
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }

    .stApp:has(.st-key-admin_top_nav) [data-testid="stTextInputRootElement"],
    .stApp:has(.st-key-admin_top_nav) [data-testid="stNumberInputContainer"],
    .stApp:has(.st-key-admin_top_nav) [data-testid="stTextAreaRootElement"],
    .stApp:has(.st-key-admin_top_nav) [data-testid="stSelectbox"] > div,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stMultiSelect"] > div,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stDateInput"] > div,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stTimeInput"] > div,
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="input"],
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="select"] > div,
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="textarea"],
    .stApp:has(.st-key-admin_top_nav) .stTextInput [data-testid="stTextInputRootElement"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1.5px solid #8FA299 !important;
        border-radius: 8px !important;
        min-height: 42px !important;
        box-shadow: 0 1px 2px rgba(23, 32, 29, 0.04) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
        box-sizing: border-box !important;
    }

    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="base-input"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }

    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="input"] input,
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="base-input"] input,
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="textarea"] textarea,
    .stApp:has(.st-key-admin_top_nav) .stTextInput input,
    .stApp:has(.st-key-admin_top_nav) .stDateInput input,
    .stApp:has(.st-key-admin_top_nav) .stTextArea textarea,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stTextInputField"],
    .stApp:has(.st-key-admin_top_nav) [data-testid="stNumberInputField"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        outline: none !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    .stApp:has(.st-key-admin_top_nav) [data-testid="stTextInputRootElement"]:hover,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stNumberInputContainer"]:hover,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stTextAreaRootElement"]:hover,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stSelectbox"] > div:hover,
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="input"]:hover,
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="select"] > div:hover,
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="textarea"]:hover {
        border-color: #16805F !important;
    }

    .stApp:has(.st-key-admin_top_nav) [data-testid="stTextInputRootElement"]:focus-within,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stNumberInputContainer"]:focus-within,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stTextAreaRootElement"]:focus-within,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stSelectbox"] > div:focus-within,
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="input"]:focus-within,
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="select"] > div:focus-within,
    .stApp:has(.st-key-admin_top_nav) div[data-baseweb="textarea"]:focus-within,
    .stApp:has(.st-key-admin_top_nav) .stTextInput input:focus,
    .stApp:has(.st-key-admin_top_nav) .stDateInput input:focus,
    .stApp:has(.st-key-admin_top_nav) .stTextArea textarea:focus {
        border-color: #16805F !important;
        box-shadow: 0 0 0 3px rgba(22, 128, 95, 0.18) !important;
        outline: none !important;
    }

    .stApp:has(.st-key-admin_top_nav) input::placeholder,
    .stApp:has(.st-key-admin_top_nav) textarea::placeholder {
        color: #8A9A92 !important;
        -webkit-text-fill-color: #8A9A92 !important;
    }

    /* Form Labels */
    .stApp:has(.st-key-admin_top_nav) [data-testid="stWidgetLabel"] label,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stWidgetLabel"] span,
    .stApp:has(.st-key-admin_top_nav) [data-testid="stWidgetLabel"] p {
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
    }

    /* Expanders */
    .stApp:has(.st-key-admin_top_nav) div[data-testid="stExpander"] {
        border: 1px solid #E1E7E3 !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(23, 32, 29, 0.02) !important;
        margin-bottom: 8px !important;
    }

    .stApp:has(.st-key-admin_top_nav) div[data-testid="stExpander"] summary {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-size: 13px !important;
        padding: 12px 16px !important;
    }

    /* Admin Profile Popover (Section 19, 20) */
    div[data-testid="stPopoverBody"]:has(.admin-top-profile-popover) {
        border-radius: 12px !important;
        border: 1px solid #E1E7E3 !important;
        background: #FFFFFF !important;
        box-shadow: 0 14px 34px rgba(23, 32, 29, 0.12) !important;
        padding: 18px 16px 16px 16px !important;
        min-width: 290px !important;
    }

    .admin-top-profile-avatar {
        width: 46px !important;
        height: 46px !important;
        border-radius: 50% !important;
        background: #E8F5F0 !important;
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        font-weight: 700 !important;
        font-size: 17px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto 10px auto !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(22, 128, 95, 0.12) !important;
    }

    .admin-top-profile-name {
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        text-align: center !important;
    }

    .admin-top-profile-role {
        font-size: 10.5px !important;
        font-weight: 600 !important;
        color: #16805F !important;
        -webkit-text-fill-color: #16805F !important;
        text-transform: uppercase !important;
        text-align: center !important;
        margin-top: 3px !important;
        letter-spacing: 0.5px !important;
    }

    .admin-top-profile-row {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 8px 0 !important;
        font-size: 12px !important;
        border-bottom: 1px solid #EDF0EE !important;
    }

    .admin-top-profile-row:last-child {
        border-bottom: none !important;
    }

    .admin-top-profile-row span {
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        font-weight: 500 !important;
    }

    .admin-top-profile-row strong {
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        font-weight: 600 !important;
    }

    /* Admin Logout in Popover (Section 20) */
    div[data-testid="stPopoverBody"]:has(.admin-top-profile-popover) button:has([data-testid*="logout"]) {
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        border: 1px solid #E1E7E3 !important;
        background: #FFFFFF !important;
        transition: all 150ms ease !important;
    }

    div[data-testid="stPopoverBody"]:has(.admin-top-profile-popover) button:has([data-testid*="logout"]):hover {
        background: #FFF0F1 !important;
        background-color: #FFF0F1 !important;
        border-color: #E9B9BE !important;
        color: #C45151 !important;
        -webkit-text-fill-color: #C45151 !important;
    }

    div[data-testid="stPopoverBody"]:has(.admin-top-profile-popover) button:has([data-testid*="logout"]):hover * {
        color: #C45151 !important;
        -webkit-text-fill-color: #C45151 !important;
    }

    /* Analytics Card Labels */
    .ref-topline {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }

    .ref-card-title {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
    }

    .ref-card-subtitle {
        font-size: 12px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        margin-top: 2px !important;
    }

    .ref-balance-label {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        text-transform: uppercase !important;
        letter-spacing: 0.7px !important;
    }

    .ref-balance-value {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #17201D !important;
        -webkit-text-fill-color: #17201D !important;
        margin-top: 4px !important;
        letter-spacing: -0.3px !important;
    }

    .ref-balance-note {
        font-size: 11.5px !important;
        color: #929B97 !important;
        -webkit-text-fill-color: #929B97 !important;
        margin-top: 2px !important;
    }

    .ref-analytics-note {
        display: flex !important;
        justify-content: space-between !important;
        font-size: 11.5px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        margin-top: 8px !important;
        padding-top: 8px !important;
        border-top: 1px solid #EDF0EE !important;
    }

    .ref-summary-head {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        margin-bottom: 12px !important;
    }

    .ref-summary-dot {
        width: 8px !important;
        height: 8px !important;
        border-radius: 50% !important;
        background: #16805F !important;
    }

    .ref-balance-caption {
        font-size: 11px !important;
        color: #66716D !important;
        -webkit-text-fill-color: #66716D !important;
        margin-top: 4px !important;
        text-align: right !important;
    }

    /* Responsive adjustments (Section 25) */
    @media (max-width: 900px) {
        .stApp:has(.st-key-admin_top_nav) .block-container,
        .stApp:has(.st-key-admin_top_nav) [data-testid="stMainBlockContainer"] {
            padding-left: 16px !important;
            padding-right: 16px !important;
            padding-top: 110px !important;
        }

        .stApp:has(.st-key-admin_top_nav) .admin-fixed-brand {
            padding: 4px 16px !important;
        }

        .stApp:has(.st-key-admin_top_nav) .st-key-admin_top_nav {
            padding: 4px 16px !important;
        }

        .st-key-admin_top_nav .stButton > button,
        .st-key-admin_top_nav div[data-testid="stPopover"] > button {
            font-size: 10.5px !important;
            padding: 0 4px !important;
        }
    }
    </style>
    """


@lru_cache(maxsize=4)
def get_auth_waves_svg(view_width=1000, view_height=1000, is_panel=False) -> str:
    """Vector SVG abstract flowing wave artwork with magenta, purple, deep violet, cyan & navy."""
    raw_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_width} {view_height}" preserveAspectRatio="xMidYMid slice" width="100%" height="100%">
  <defs>
    <linearGradient id="mbDarkCanvas" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#050610" />
      <stop offset="35%" stop-color="#0E0820" />
      <stop offset="70%" stop-color="#080C22" />
      <stop offset="100%" stop-color="#020308" />
    </linearGradient>
    <linearGradient id="mbWavePinkPurple" x1="0%" y1="15%" x2="100%" y2="85%">
      <stop offset="0%" stop-color="#FF2E93" stop-opacity="0.95" />
      <stop offset="30%" stop-color="#D84FB4" stop-opacity="0.92" />
      <stop offset="65%" stop-color="#9672F4" stop-opacity="0.88" />
      <stop offset="100%" stop-color="#61D8E7" stop-opacity="0.85" />
    </linearGradient>
    <linearGradient id="mbWaveDeepViolet" x1="15%" y1="95%" x2="85%" y2="5%">
      <stop offset="0%" stop-color="#5E4AA8" stop-opacity="0.92" />
      <stop offset="45%" stop-color="#9672F4" stop-opacity="0.85" />
      <stop offset="80%" stop-color="#FF65D1" stop-opacity="0.80" />
      <stop offset="100%" stop-color="#FF2E93" stop-opacity="0.90" />
    </linearGradient>
    <linearGradient id="mbWaveCyanMagenta" x1="0%" y1="35%" x2="100%" y2="65%">
      <stop offset="0%" stop-color="#61D8E7" stop-opacity="0.85" />
      <stop offset="45%" stop-color="#9672F4" stop-opacity="0.75" />
      <stop offset="100%" stop-color="#FF2E93" stop-opacity="0.80" />
    </linearGradient>
    <linearGradient id="mbLuminousRibbon" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.75" />
      <stop offset="25%" stop-color="#FF65D1" stop-opacity="0.85" />
      <stop offset="65%" stop-color="#9672F4" stop-opacity="0.75" />
      <stop offset="100%" stop-color="#61D8E7" stop-opacity="0.50" />
    </linearGradient>
    <radialGradient id="mbGlowPink" cx="28%" cy="38%" r="48%">
      <stop offset="0%" stop-color="#FF2E93" stop-opacity="0.50" />
      <stop offset="50%" stop-color="#D84FB4" stop-opacity="0.22" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="mbGlowPurple" cx="72%" cy="62%" r="52%">
      <stop offset="0%" stop-color="#9672F4" stop-opacity="0.45" />
      <stop offset="60%" stop-color="#5E4AA8" stop-opacity="0.18" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="mbGlowCyan" cx="82%" cy="22%" r="42%">
      <stop offset="0%" stop-color="#61D8E7" stop-opacity="0.40" />
      <stop offset="60%" stop-color="#61D8E7" stop-opacity="0.12" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0" />
    </radialGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#mbDarkCanvas)" />
  <circle cx="{view_width * 0.28}" cy="{view_height * 0.38}" r="{view_width * 0.40}" fill="url(#mbGlowPink)" />
  <circle cx="{view_width * 0.72}" cy="{view_height * 0.62}" r="{view_width * 0.44}" fill="url(#mbGlowPurple)" />
  <circle cx="{view_width * 0.82}" cy="{view_height * 0.22}" r="{view_width * 0.35}" fill="url(#mbGlowCyan)" />
  <path d="M -120,{view_height * 0.82} C {view_width * 0.22},{view_height * 0.94} {view_width * 0.42},{view_height * 0.58} {view_width * 0.66},{view_height * 0.68} C {view_width * 0.86},{view_height * 0.76} {view_width * 1.06},{view_height * 0.48} {view_width + 120},{view_height * 0.42} L {view_width + 120},{view_height + 120} L -120,{view_height + 120} Z" fill="url(#mbWaveDeepViolet)" opacity="0.70" />
  <path d="M -120,{view_height * 0.58} C {view_width * 0.16},{view_height * 0.32} {view_width * 0.38},{view_height * 0.78} {view_width * 0.64},{view_height * 0.50} C {view_width * 0.84},{view_height * 0.26} {view_width * 0.96},{view_height * 0.42} {view_width + 120},{view_height * 0.32} C {view_width * 0.92},{view_height * 0.64} {view_width * 0.72},{view_height * 0.84} {view_width * 0.48},{view_height * 0.74} C {view_width * 0.26},{view_height * 0.64} {view_width * 0.06},{view_height * 0.84} -120,{view_height * 0.74} Z" fill="url(#mbWavePinkPurple)" opacity="0.84" />
  <path d="M -120,{view_height * 0.40} C {view_width * 0.14},{view_height * 0.66} {view_width * 0.34},{view_height * 0.18} {view_width * 0.60},{view_height * 0.40} C {view_width * 0.82},{view_height * 0.58} {view_width * 0.94},{view_height * 0.22} {view_width + 120},{view_height * 0.16} L {view_width + 120},{view_height * 0.52} C {view_width * 0.90},{view_height * 0.66} {view_width * 0.74},{view_height * 0.88} {view_width * 0.46},{view_height * 0.76} C {view_width * 0.24},{view_height * 0.66} {view_width * 0.08},{view_height * 0.70} -120,{view_height * 0.56} Z" fill="url(#mbWaveCyanMagenta)" opacity="0.78" />
  <path d="M -100,{view_height * 0.42} C {view_width * 0.15},{view_height * 0.64} {view_width * 0.35},{view_height * 0.20} {view_width * 0.60},{view_height * 0.41} C {view_width * 0.80},{view_height * 0.57} {view_width * 0.92},{view_height * 0.25} {view_width + 100},{view_height * 0.18}" fill="none" stroke="url(#mbLuminousRibbon)" stroke-width="4.5" stroke-linecap="round" opacity="0.75" />
  <path d="M -80,{view_height * 0.60} C {view_width * 0.18},{view_height * 0.36} {view_width * 0.40},{view_height * 0.80} {view_width * 0.66},{view_height * 0.52} C {view_width * 0.82},{view_height * 0.30} {view_width * 0.96},{view_height * 0.46} {view_width + 100},{view_height * 0.36}" fill="none" stroke="url(#mbWavePinkPurple)" stroke-width="2.5" stroke-linecap="round" opacity="0.60" />
</svg>"""
    return "".join(line + "\n" for line in raw_svg.splitlines() if line.strip())


_AUTH_ARTWORK_URI_CACHE = None


def get_auth_artwork_data_uri() -> str:
    """Return base64 Data URI of the premium digital banking artwork (cached)."""
    global _AUTH_ARTWORK_URI_CACHE
    if _AUTH_ARTWORK_URI_CACHE is not None:
        return _AUTH_ARTWORK_URI_CACHE
    artwork_path = os.path.join(os.path.dirname(__file__), "assets", "banking_visual_artwork.jpg")
    if os.path.exists(artwork_path):
        try:
            with open(artwork_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                _AUTH_ARTWORK_URI_CACHE = f"data:image/jpeg;base64,{b64}"
                return _AUTH_ARTWORK_URI_CACHE
        except Exception:
            pass
    return get_auth_waves_data_uri()


@lru_cache(maxsize=1)
def get_auth_waves_data_uri() -> str:
    """Return a base64 Data URI of the abstract flowing wave artwork SVG."""
    svg = get_auth_waves_svg(1200, 900)
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


@lru_cache(maxsize=1)
def get_auth_theme_styles() -> str:
    waves_uri = get_auth_waves_data_uri()
    artwork_uri = get_auth_artwork_data_uri()
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@300;400;500;600;700&display=swap');

    /* =========================================================
       MADHU BANK — PREMIUM AUTHENTICATION UI MASTER DESIGN
       Deep Black Canvas + Flowing Wave Art + Centered White Card
       ========================================================= */

    :root {{
        --auth-black: #000000;
        --auth-white: #FFFFFF;
        --auth-pink: #D84FB4;
        --auth-pink-hot: #FF2E93;
        --auth-pink-light: #FF65D1;
        --auth-purple: #9672F4;
        --auth-purple-dark: #5E4AA8;
        --auth-cyan: #61D8E7;
        --auth-blue: #B6CAFA;
        --auth-navy: #0A1128;
        --auth-text: #111111;
        --auth-secondary: #625D68;
        --auth-muted: #817A86;
        --auth-input: #F7F8FA;
        --auth-border: #EEEEF1;
        --auth-success: #16805F;
        --auth-warning: #C58A18;
        --auth-error: #C45151;

        /* Compatibility variables */
        --auth-canvas: var(--auth-black);
        --auth-text-dark: var(--auth-text);
        --auth-text-body: #17151B;
        --auth-text-subtle: var(--auth-secondary);
        --auth-input-bg: var(--auth-input);
        --auth-input-border: var(--auth-border);
        --auth-input-focus: var(--auth-purple);
    }}

    /* =========================================================
       1. FULL SCREEN BACKGROUND (Section 4)
       Deep black base #000000 + flowing vector wave artwork
       ========================================================= */
    html:has(.auth-visual-panel),
    body:has(.auth-visual-panel),
    .stApp:has(.auth-visual-panel) {{
        background: #000000 !important;
        background-color: #000000 !important;
        min-height: 100vh !important;
        overflow-x: hidden !important;
        color: #111111 !important;
    }}

    /* Background dynamic abstract flowing wave artwork */
    .stApp:has(.auth-visual-panel)::before {{
        content: "" !important;
        position: fixed !important;
        inset: 0 !important;
        z-index: 0 !important;
        background-image: url('{waves_uri}') !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        opacity: 0.90 !important;
        pointer-events: none !important;
    }}

    /* Soft ambient vignette */
    .stApp:has(.auth-visual-panel)::after {{
        content: "" !important;
        position: fixed !important;
        inset: 0 !important;
        z-index: 1 !important;
        background: radial-gradient(circle at 50% 50%, rgba(0, 0, 0, 0.20) 0%, rgba(0, 0, 0, 0.75) 100%) !important;
        pointer-events: none !important;
    }}

    /* Suppress default headers, footers and old auth-bank-header */
    header[data-testid="stHeader"],
    footer,
    [data-testid="stBottom"],
    .stApp:has(.auth-visual-panel) .auth-bank-header,
    .stApp:has(.auth-visual-panel) [data-testid="stElementContainer"]:has(.auth-bank-header),
    .stApp:has(.auth-visual-panel) [data-testid="stElementContainer"]:has(.auth-top-space) {{
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        visibility: hidden !important;
    }}

    /* Center the main container in the viewport */
    .stApp:has(.auth-visual-panel) [data-testid="stAppViewContainer"],
    .stApp:has(.auth-visual-panel) section.main,
    .stApp:has(.auth-visual-panel) [data-testid="stMain"],
    .stApp:has(.auth-visual-panel) [data-testid="stMainBlockContainer"],
    .stApp:has(.auth-visual-panel) .block-container {{
        width: 100% !important;
        max-width: 100% !important;
        min-height: 100vh !important;
        padding: 24px 20px !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
        position: relative !important;
        z-index: 2 !important;
        background: transparent !important;
    }}

    /* =========================================================
       2. AUTHENTICATION CONTAINER (Section 5)
       92vw, max 1240px, min-height 680px, #FFFFFF, 32px radius, subtle shadow
       ========================================================= */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel),
    .madhu-auth-container {{
        width: 92vw !important;
        max-width: 1240px !important;
        min-height: 680px !important;
        margin: auto !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border-radius: 32px !important;
        box-shadow: 0 24px 70px rgba(0, 0, 0, 0.20) !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: stretch !important;
        padding: 16px !important;
        box-sizing: border-box !important;
        position: relative !important;
        z-index: 10 !important;
        gap: 0 !important;
    }}

    /* Reset Streamlit column borders & margins */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) > div[data-testid="stColumn"] {{
        margin: 0 !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* =========================================================
       3. LEFT VISUAL PANEL (Section 7, 8, 9, 10)
       50% split, 28px radius, full-bleed artwork, serif typography
       ========================================================= */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) > div[data-testid="stColumn"]:has(.auth-visual-panel),
    div[data-testid="stColumn"]:has(.auth-visual-panel) {{
        width: 50% !important;
        flex: 1 1 50% !important;
        max-width: 50% !important;
        min-height: 648px !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
    }}

    div[data-testid="stColumn"]:has(.auth-visual-panel) > div,
    div[data-testid="stColumn"]:has(.auth-visual-panel) [data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stColumn"]:has(.auth-visual-panel) [data-testid="stVerticalBlockBorderWrapper"] > div,
    div[data-testid="stColumn"]:has(.auth-visual-panel) [data-testid="stVerticalBlock"] {{
        height: 100% !important;
        min-height: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    .auth-visual-panel,
    .madhu-auth-visual {{
        position: relative !important;
        width: 100% !important;
        height: 100% !important;
        min-height: 648px !important;
        border-radius: 28px !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        box-sizing: border-box !important;
        background-color: #060713 !important;
        background-image: url("{artwork_uri}") !important;
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
    }}

    .auth-visual-art {{
        display: none !important;
    }}

    .auth-visual-content-wrapper {{
        position: relative !important;
        z-index: 2 !important;
        width: 100% !important;
        height: 100% !important;
        min-height: 648px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        padding: 42px 38px !important;
        box-sizing: border-box !important;
        background: linear-gradient(180deg, rgba(4, 6, 16, 0.88) 0%, rgba(4, 6, 16, 0.72) 24%, rgba(4, 6, 16, 0.12) 42%, rgba(4, 6, 16, 0.12) 64%, rgba(4, 6, 16, 0.88) 100%) !important;
    }}

    .auth-visual-spacer {{
        flex-grow: 1 !important;
        min-height: 200px !important;
        pointer-events: none !important;
    }}

    /* Left panel top quote / brand label (Section 8) */
    .visual-top-label,
    .visual-top-label span {{
        display: flex !important;
        align-items: center !important;
        gap: 14px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        color: #FFFFFF !important;
        opacity: 0.95 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}

    .visual-line {{
        height: 1px !important;
        flex-grow: 1 !important;
        max-width: 120px !important;
        background: linear-gradient(90deg, rgba(255, 255, 255, 0.75), transparent) !important;
    }}

    /* Left panel hero title: elegant serif (Section 9) */
    [data-testid="stMarkdownContainer"] .auth-visual-panel .visual-hero-heading,
    .auth-visual-panel .visual-hero-heading,
    .visual-hero-heading,
    .visual-hero-heading *,
    .visual-hero-heading h1 {{
        font-family: 'DM Serif Display', Georgia, serif !important;
        font-size: 38px !important;
        font-weight: 500 !important;
        line-height: 1.08 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        margin: 0 0 10px 0 !important;
        letter-spacing: -0.4px !important;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.95) !important;
    }}

    /* Left panel description (Section 10) */
    [data-testid="stMarkdownContainer"] .auth-visual-panel .visual-hero-desc,
    .auth-visual-panel .visual-hero-desc,
    .visual-hero-desc,
    .visual-hero-desc *,
    .visual-hero-desc p {{
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        line-height: 1.55 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        margin: 0 !important;
        max-width: 360px !important;
        text-shadow: 0 2px 14px rgba(0, 0, 0, 0.95) !important;
    }}

    /* Ultra-high-specificity white text guarantee for all left panel elements */
    [data-testid="stMarkdownContainer"] .auth-visual-panel,
    [data-testid="stMarkdownContainer"] .auth-visual-panel *,
    .auth-visual-panel .visual-top-label,
    .auth-visual-panel .visual-top-label *,
    .auth-visual-panel .visual-hero-heading,
    .auth-visual-panel .visual-hero-heading *,
    .auth-visual-panel .visual-hero-desc,
    .auth-visual-panel .visual-hero-desc *,
    .auth-visual-panel .banking-security-cue,
    .auth-visual-panel .banking-security-cue *,
    .auth-visual-panel .visual-footer-pill,
    .auth-visual-panel .visual-footer-pill * {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}

    /* =========================================================
       BANKING IDENTITY: DECORATIVE CARD & FINANCIAL GRAPH MOTIF
       ========================================================= */
    .banking-stage-container {{
        position: relative !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 10px 0 14px 0 !important;
    }}

    .banking-graph-layer {{
        position: absolute !important;
        width: 100% !important;
        max-width: 330px !important;
        height: 110px !important;
        top: -18px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 1 !important;
        pointer-events: none !important;
        opacity: 0.50 !important;
    }}

    .banking-graph-layer svg {{
        width: 100% !important;
        height: 100% !important;
        display: block !important;
    }}

    .banking-card-visual {{
        position: relative !important;
        z-index: 2 !important;
        width: 310px !important;
        max-width: 100% !important;
        height: 180px !important;
        border-radius: 16px !important;
        background: linear-gradient(135deg, rgba(14, 17, 36, 0.94) 0%, rgba(28, 17, 50, 0.95) 50%, rgba(8, 10, 22, 0.97) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        box-shadow: 0 18px 40px -8px rgba(0, 0, 0, 0.70), 0 0 0 1px rgba(255, 255, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.22) !important;
        overflow: hidden !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        transform: perspective(900px) rotateX(2deg) rotateY(-2deg) !important;
        transition: all 260ms ease !important;
    }}

    .banking-card-visual:hover {{
        transform: perspective(900px) rotateX(0deg) rotateY(0deg) translateY(-2px) !important;
        box-shadow: 0 24px 48px -8px rgba(0, 0, 0, 0.80), 0 0 22px rgba(150, 114, 244, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
    }}

    .card-sheen {{
        position: absolute !important;
        inset: 0 !important;
        background: linear-gradient(130deg, rgba(255, 255, 255, 0.16) 0%, rgba(255, 255, 255, 0.03) 45%, transparent 60%) !important;
        pointer-events: none !important;
        z-index: 1 !important;
    }}

    .card-inner {{
        position: relative !important;
        z-index: 2 !important;
        height: 100% !important;
        padding: 16px 18px !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
    }}

    .card-top-row {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }}

    .card-brand-symbol {{
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }}

    .card-brand-name {{
        font-family: 'Inter', sans-serif !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.5) !important;
    }}

    .card-top-right {{
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }}

    .card-contactless-icon {{
        width: 16px !important;
        height: 16px !important;
        stroke: rgba(255, 255, 255, 0.75) !important;
    }}

    .card-mid-row {{
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        margin: 6px 0 !important;
    }}

    .card-emv-chip {{
        width: 32px !important;
        height: 24px !important;
        border-radius: 5px !important;
        background: linear-gradient(135deg, #F3D068 0%, #D89F34 50%, #A8711E 100%) !important;
        position: relative !important;
        overflow: hidden !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.4), 0 2px 4px rgba(0, 0, 0, 0.4) !important;
        flex-shrink: 0 !important;
    }}

    .chip-line.horizontal {{
        position: absolute !important;
        top: 50% !important;
        left: 0 !important;
        right: 0 !important;
        height: 1px !important;
        background: rgba(0, 0, 0, 0.35) !important;
    }}

    .chip-line.vertical {{
        position: absolute !important;
        left: 50% !important;
        top: 0 !important;
        bottom: 0 !important;
        width: 1px !important;
        background: rgba(0, 0, 0, 0.35) !important;
    }}

    .card-number-placeholders {{
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        font-family: 'Inter', monospace, sans-serif !important;
        color: rgba(255, 255, 255, 0.90) !important;
        -webkit-text-fill-color: rgba(255, 255, 255, 0.90) !important;
    }}

    .card-bar {{
        font-size: 13px !important;
        letter-spacing: 2px !important;
        opacity: 0.75 !important;
    }}

    .card-last-digits {{
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}

    .card-bottom-row {{
        display: flex !important;
        justify-content: space-between !important;
        align-items: flex-end !important;
    }}

    .card-banking-identity {{
        display: flex !important;
        flex-direction: column !important;
        gap: 2px !important;
    }}

    .card-bank-sub {{
        font-family: 'Inter', sans-serif !important;
        font-size: 9px !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}

    .card-bank-tier {{
        font-family: 'Inter', sans-serif !important;
        font-size: 7.5px !important;
        font-weight: 600 !important;
        letter-spacing: 1.2px !important;
        color: rgba(255, 255, 255, 0.65) !important;
        -webkit-text-fill-color: rgba(255, 255, 255, 0.65) !important;
    }}

    .card-tier-pill {{
        padding: 3px 8px !important;
        border-radius: 9999px !important;
        background: rgba(255, 255, 255, 0.10) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 7.5px !important;
        font-weight: 700 !important;
        letter-spacing: 1.2px !important;
        color: #F7D070 !important;
        -webkit-text-fill-color: #F7D070 !important;
    }}

    /* Subtle Transaction Visual Motifs */
    .banking-transaction-motifs {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 9px !important;
        margin-top: 14px !important;
        padding: 6px 14px !important;
        border-radius: 9999px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        pointer-events: none !important;
    }}

    .motif-item {{
        display: flex !important;
        align-items: center !important;
        gap: 4px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 10px !important;
        font-weight: 500 !important;
        color: rgba(255, 255, 255, 0.72) !important;
        -webkit-text-fill-color: rgba(255, 255, 255, 0.72) !important;
        letter-spacing: 0.3px !important;
    }}

    .motif-arrow {{
        font-size: 11px !important;
        color: #61D8E7 !important;
        -webkit-text-fill-color: #61D8E7 !important;
    }}

    .motif-shield-icon {{
        width: 11px !important;
        height: 11px !important;
        stroke: #FF65D1 !important;
    }}

    .motif-divider {{
        font-size: 8px !important;
        color: rgba(255, 255, 255, 0.30) !important;
        -webkit-text-fill-color: rgba(255, 255, 255, 0.30) !important;
    }}

    /* Banking Security Cue */
    .auth-visual-footer {{
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 8px !important;
    }}

    .banking-security-cue {{
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        font-family: 'Inter', sans-serif !important;
        margin-bottom: 4px !important;
    }}

    .security-shield-svg {{
        width: 18px !important;
        height: 18px !important;
        flex-shrink: 0 !important;
    }}

    .security-cue-text {{
        display: flex !important;
        flex-direction: column !important;
        gap: 1px !important;
    }}

    .sec-title {{
        font-size: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}

    .sec-sub {{
        font-size: 9.5px !important;
        font-weight: 400 !important;
        color: rgba(255, 255, 255, 0.70) !important;
        -webkit-text-fill-color: rgba(255, 255, 255, 0.70) !important;
    }}

    .visual-footer-pill,
    .visual-footer-pill * {{
        font-family: 'Inter', sans-serif !important;
        font-size: 11.5px !important;
        font-weight: 500 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        letter-spacing: 0.3px !important;
    }}

    .visual-footer-pill {{
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        padding: 7px 16px !important;
        border-radius: 9999px !important;
        background: rgba(255, 255, 255, 0.14) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }}

    .pill-dot {{
        width: 6px !important;
        height: 6px !important;
        border-radius: 50% !important;
        background: #61D8E7 !important;
        box-shadow: 0 0 8px #61D8E7 !important;
    }}

    .auth-visual-panel a.anchor-link,
    .auth-visual-panel [data-testid="stHeaderActionElements"],
    .visual-hero-heading a {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* =========================================================
       4. RIGHT AUTH PANEL (Section 11, 12, 13, 14)
       50% split, pure white #FFFFFF, elegant serif headings, clean Inter UI
       ========================================================= */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) > div[data-testid="stColumn"]:not(:has(.auth-visual-panel)),
    div[data-testid="stColumn"]:has(.st-key-auth_login_scroll),
    div[data-testid="stColumn"]:has(.st-key-auth_register_scroll),
    div[data-testid="stColumn"]:has(.st-key-auth_forgot_scroll),
    div[data-testid="stColumn"]:has(.st-key-auth_admin_scroll),
    div[data-testid="stColumn"]:has(.st-key-auth_register_otp_scroll),
    div[data-testid="stColumn"]:has(.st-key-auth_login_otp_scroll),
    div[data-testid="stColumn"]:has(.st-key-auth_account_review_scroll),
    .madhu-auth-form {{
        width: 50% !important;
        flex: 1 1 50% !important;
        max-width: 50% !important;
        min-height: 648px !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        padding: 24px 44px !important;
        box-sizing: border-box !important;
    }}

    /* Inner scroll container */
    .st-key-auth_login_scroll,
    .st-key-auth_register_scroll,
    .st-key-auth_forgot_scroll,
    .st-key-auth_admin_scroll,
    .st-key-auth_register_otp_scroll,
    .st-key-auth_login_otp_scroll,
    .st-key-auth_account_review_scroll {{
        width: 100% !important;
        max-height: 648px !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        padding: 12px 10px 18px 10px !important;
        box-sizing: border-box !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        scrollbar-width: thin !important;
        scrollbar-color: rgba(150, 114, 244, 0.35) transparent !important;
    }}

    .st-key-auth_login_scroll::-webkit-scrollbar,
    .st-key-auth_register_scroll::-webkit-scrollbar,
    .st-key-auth_forgot_scroll::-webkit-scrollbar,
    .st-key-auth_admin_scroll::-webkit-scrollbar,
    .st-key-auth_register_otp_scroll::-webkit-scrollbar,
    .st-key-auth_login_otp_scroll::-webkit-scrollbar,
    .st-key-auth_account_review_scroll::-webkit-scrollbar {{
        width: 5px !important;
    }}

    .st-key-auth_login_scroll::-webkit-scrollbar-thumb,
    .st-key-auth_register_scroll::-webkit-scrollbar-thumb,
    .st-key-auth_forgot_scroll::-webkit-scrollbar-thumb,
    .st-key-auth_admin_scroll::-webkit-scrollbar-thumb,
    .st-key-auth_register_otp_scroll::-webkit-scrollbar-thumb,
    .st-key-auth_login_otp_scroll::-webkit-scrollbar-thumb,
    .st-key-auth_account_review_scroll::-webkit-scrollbar-thumb {{
        background: rgba(150, 114, 244, 0.35) !important;
        border-radius: 9999px !important;
    }}

    .st-key-auth_login_scroll > div,
    .st-key-auth_register_scroll > div,
    .st-key-auth_forgot_scroll > div,
    .st-key-auth_admin_scroll > div,
    .st-key-auth_register_otp_scroll > div,
    .st-key-auth_login_otp_scroll > div,
    .st-key-auth_account_review_scroll > div,
    .st-key-auth_login_scroll [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-auth_register_scroll [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-auth_forgot_scroll [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-auth_admin_scroll [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-auth_register_otp_scroll [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-auth_login_otp_scroll [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-auth_account_review_scroll [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-auth_login_scroll [data-testid="stVerticalBlockBorderWrapper"] > div,
    .st-key-auth_register_scroll [data-testid="stVerticalBlockBorderWrapper"] > div,
    .st-key-auth_forgot_scroll [data-testid="stVerticalBlockBorderWrapper"] > div,
    .st-key-auth_admin_scroll [data-testid="stVerticalBlockBorderWrapper"] > div,
    .st-key-auth_register_otp_scroll [data-testid="stVerticalBlockBorderWrapper"] > div,
    .st-key-auth_login_otp_scroll [data-testid="stVerticalBlockBorderWrapper"] > div,
    .st-key-auth_account_review_scroll [data-testid="stVerticalBlockBorderWrapper"] > div {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }}

    /* Brand Header: [LOGO] MADHU BANK (Section 12) */
    .auth-brand-header,
    .madhu-auth-brand {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 9px !important;
        margin: 0 auto 16px auto !important;
    }}

    .auth-brand-logo {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    .auth-brand-logo svg {{
        width: 26px !important;
        height: 26px !important;
    }}

    .auth-brand-title {{
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 1.5px !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        text-transform: uppercase !important;
    }}

    /* Auth Headings: Elegant Serif (Section 13) */
    .auth-main-heading,
    .login-heading,
    .madhu-auth-heading {{
        font-family: 'DM Serif Display', Georgia, serif !important;
        font-size: 36px !important;
        font-weight: 500 !important;
        line-height: 1.05 !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        text-align: center !important;
        margin: 0 0 8px 0 !important;
        letter-spacing: -0.3px !important;
    }}

    /* Auth Descriptions (Section 14) */
    .auth-main-desc,
    .login-subtitle {{
        font-family: 'Inter', sans-serif !important;
        font-size: 12.5px !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
        color: #625D68 !important;
        -webkit-text-fill-color: #625D68 !important;
        text-align: center !important;
        margin: 0 auto 22px auto !important;
        max-width: 360px !important;
    }}

    /* =========================================================
       5. FORM, LABELS & INPUT DESIGN (Section 15, 16, 17)
       #F7F8FA background, 1px solid #EEEEF1, 8px radius, #9672F4 focus
       ========================================================= */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stForm"] {{
        width: 100% !important;
        max-width: 440px !important;
        margin: 0 auto 8px auto !important;
        padding: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stForm"] [data-testid="stVerticalBlock"] {{
        gap: 0.60rem !important;
    }}

    /* Form Labels (Section 15): 12px, weight 500, #17151B, mb 6px */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) label,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stWidgetLabel"] label,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stWidgetLabel"] span,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stWidgetLabel"] p,
    .st-key-auth_login_scroll label,
    .st-key-auth_register_scroll label,
    .st-key-auth_forgot_scroll label,
    .st-key-auth_admin_scroll label,
    .st-key-auth_register_otp_scroll label,
    .st-key-auth_login_otp_scroll label,
    .st-key-auth_account_review_scroll label {{
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        color: #17151B !important;
        -webkit-text-fill-color: #17151B !important;
        margin-bottom: 6px !important;
        display: inline-block !important;
    }}

    /* All Input Entry Field Control Boxes in Auth Portal */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stTextInputRootElement"],
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stNumberInputContainer"],
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stTextAreaRootElement"],
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stSelectbox"] > div,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) div[data-baseweb="input"],
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-baseweb="select"] > div,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) div[data-baseweb="textarea"],
    .st-key-auth_login_scroll [data-testid="stTextInputRootElement"],
    .st-key-auth_register_scroll [data-testid="stTextInputRootElement"],
    .st-key-auth_forgot_scroll [data-testid="stTextInputRootElement"],
    .st-key-auth_admin_scroll [data-testid="stTextInputRootElement"],
    .st-key-auth_register_otp_scroll [data-testid="stTextInputRootElement"],
    .st-key-auth_login_otp_scroll [data-testid="stTextInputRootElement"],
    .st-key-auth_account_review_scroll [data-testid="stTextInputRootElement"],
    .st-key-auth_login_scroll [data-testid="stNumberInputContainer"],
    .st-key-auth_login_scroll [data-testid="stTextAreaRootElement"],
    .st-key-auth_login_scroll div[data-baseweb="input"],
    .st-key-auth_register_scroll div[data-baseweb="input"],
    .st-key-auth_forgot_scroll div[data-baseweb="input"],
    .st-key-auth_admin_scroll div[data-baseweb="input"],
    .st-key-auth_login_scroll .stTextInput [data-testid="stTextInputRootElement"],
    .st-key-auth_register_scroll .stTextInput [data-testid="stTextInputRootElement"],
    .st-key-auth_forgot_scroll .stTextInput [data-testid="stTextInputRootElement"],
    .st-key-auth_admin_scroll .stTextInput [data-testid="stTextInputRootElement"],
    [data-testid="stForm"] [data-testid="stTextInputRootElement"],
    [data-testid="stForm"] [data-testid="stNumberInputContainer"],
    [data-testid="stForm"] [data-testid="stTextAreaRootElement"],
    .madhu-auth-input {{
        min-height: 44px !important;
        background: #F8FAFC !important;
        background-color: #F8FAFC !important;
        border: 1.5px solid #94A3B8 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05) !important;
        transition: border-color 160ms ease, box-shadow 160ms ease, background-color 160ms ease !important;
        box-sizing: border-box !important;
    }}

    /* Inner input text field */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) input,
    .st-key-auth_login_scroll input,
    .st-key-auth_register_scroll input,
    .st-key-auth_forgot_scroll input,
    .st-key-auth_admin_scroll input,
    .st-key-auth_register_otp_scroll input,
    .st-key-auth_login_otp_scroll input,
    .st-key-auth_account_review_scroll input,
    [data-testid="stTextInputField"] {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        padding: 0 12px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }}

    /* Password visibility toggle button inside input box */
    [data-testid="stTextInputRootElement"] button,
    [data-testid="stTextInputRootElement"] button svg {{
        background: transparent !important;
        border: none !important;
        color: #64748B !important;
        fill: #64748B !important;
    }}

    /* Hide browser native password reveal / clear buttons (prevents duplicate eye in Edge/Windows) */
    input[type="password"]::-ms-reveal,
    input[type="password"]::-ms-clear,
    input::-ms-reveal,
    input::-ms-clear {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        pointer-events: none !important;
        visibility: hidden !important;
    }}

    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) textarea,
    .st-key-auth_login_scroll textarea {{
        background: transparent !important;
        border: none !important;
        outline: none !important;
        height: auto !important;
        min-height: 90px !important;
        padding: 10px 12px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13.5px !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }}

    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) input::placeholder,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) textarea::placeholder,
    .st-key-auth_login_scroll input::placeholder,
    .st-key-auth_register_scroll input::placeholder,
    .st-key-auth_forgot_scroll input::placeholder,
    .st-key-auth_admin_scroll input::placeholder {{
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
        font-size: 13px !important;
    }}

    /* Input Hover: vibrant violet accent */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stTextInputRootElement"]:hover,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stNumberInputContainer"]:hover,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stTextAreaRootElement"]:hover,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stSelectbox"] > div:hover,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) div[data-baseweb="input"]:hover,
    .st-key-auth_login_scroll [data-testid="stTextInputRootElement"]:hover,
    .st-key-auth_register_scroll [data-testid="stTextInputRootElement"]:hover,
    .st-key-auth_forgot_scroll [data-testid="stTextInputRootElement"]:hover,
    .st-key-auth_admin_scroll [data-testid="stTextInputRootElement"]:hover,
    [data-testid="stForm"] [data-testid="stTextInputRootElement"]:hover {{
        border-color: #9672F4 !important;
    }}

    /* Input Focus: white background with strong violet focus halo */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stTextInputRootElement"]:focus-within,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stNumberInputContainer"]:focus-within,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stTextAreaRootElement"]:focus-within,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stSelectbox"] > div:focus-within,
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) div[data-baseweb="input"]:focus-within,
    .st-key-auth_login_scroll [data-testid="stTextInputRootElement"]:focus-within,
    .st-key-auth_register_scroll [data-testid="stTextInputRootElement"]:focus-within,
    .st-key-auth_forgot_scroll [data-testid="stTextInputRootElement"]:focus-within,
    .st-key-auth_admin_scroll [data-testid="stTextInputRootElement"]:focus-within,
    [data-testid="stForm"] [data-testid="stTextInputRootElement"]:focus-within {{
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border-color: #9672F4 !important;
        box-shadow: 0 0 0 3px rgba(150, 114, 244, 0.20) !important;
        outline: none !important;
    }}

    /* Checkbox / Remember me (Section 20) */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stCheckbox"] label {{
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        color: #625D68 !important;
        -webkit-text-fill-color: #625D68 !important;
        cursor: pointer !important;
    }}

    /* =========================================================
       6. PRIMARY ACTION BUTTONS (Section 22, 23, 27)
       Standard: #000000, 8px radius, height 44px, hover #17151B
       Admin: #5E4AA8 accent, hover #4E3C96
       ========================================================= */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stFormSubmitButton"] {{
        width: 100% !important;
        max-width: 440px !important;
        margin: 10px auto 0 auto !important;
    }}

    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stFormSubmitButton"] button,
    div[data-testid="stColumn"]:has(.auth-visual-panel) ~ div[data-testid="stColumn"] [data-testid="stFormSubmitButton"] button,
    .st-key-auth_login_scroll [data-testid="stFormSubmitButton"] button,
    .st-key-auth_register_scroll [data-testid="stFormSubmitButton"] button,
    .st-key-auth_forgot_scroll [data-testid="stFormSubmitButton"] button,
    .st-key-auth_register_otp_scroll [data-testid="stFormSubmitButton"] button,
    .st-key-auth_login_otp_scroll [data-testid="stFormSubmitButton"] button,
    .st-key-auth_account_review_scroll [data-testid="stFormSubmitButton"] button,
    .madhu-auth-button {{
        background: #000000 !important;
        background-color: #000000 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid #000000 !important;
        border-radius: 8px !important;
        height: 44px !important;
        min-height: 44px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 170ms ease !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.10) !important;
    }}

    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) [data-testid="stFormSubmitButton"] button:hover,
    div[data-testid="stColumn"]:has(.auth-visual-panel) ~ div[data-testid="stColumn"] [data-testid="stFormSubmitButton"] button:hover,
    .st-key-auth_login_scroll [data-testid="stFormSubmitButton"] button:hover,
    .st-key-auth_register_scroll [data-testid="stFormSubmitButton"] button:hover,
    .st-key-auth_forgot_scroll [data-testid="stFormSubmitButton"] button:hover {{
        background: #17151B !important;
        background-color: #17151B !important;
        border-color: #17151B !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.15) !important;
    }}

    /* Admin Primary Button (Section 27): #5E4AA8 Accent */
    .st-key-auth_admin_scroll [data-testid="stFormSubmitButton"] button {{
        background: #5E4AA8 !important;
        background-color: #5E4AA8 !important;
        border: 1px solid #5E4AA8 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border-radius: 8px !important;
        height: 44px !important;
        min-height: 44px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 170ms ease !important;
    }}

    .st-key-auth_admin_scroll [data-testid="stFormSubmitButton"] button:hover {{
        background: #4E3C96 !important;
        background-color: #4E3C96 !important;
        border-color: #4E3C96 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 18px rgba(94, 74, 168, 0.30) !important;
    }}

    /* =========================================================
       7. SECONDARY ACTION BUTTONS & LINKS (Section 21, 29)
       8px radius, white surface, subtle border, smooth hover
       ========================================================= */
    .st-key-auth_login_scroll [data-testid="stHorizontalBlock"],
    .st-key-auth_register_scroll [data-testid="stHorizontalBlock"],
    .st-key-auth_forgot_scroll [data-testid="stHorizontalBlock"],
    .st-key-auth_admin_scroll [data-testid="stHorizontalBlock"],
    .st-key-auth_register_otp_scroll [data-testid="stHorizontalBlock"],
    .st-key-auth_login_otp_scroll [data-testid="stHorizontalBlock"],
    .st-key-auth_account_review_scroll [data-testid="stHorizontalBlock"] {{
        width: 100% !important;
        max-width: 440px !important;
        margin: 0 auto 6px auto !important;
        padding: 0 !important;
        box-sizing: border-box !important;
        gap: 8px !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        min-height: auto !important;
    }}

    .st-key-auth_login_scroll .stButton,
    .st-key-auth_register_scroll .stButton,
    .st-key-auth_forgot_scroll .stButton,
    .st-key-auth_admin_scroll .stButton,
    .st-key-auth_register_otp_scroll .stButton,
    .st-key-auth_login_otp_scroll .stButton,
    .st-key-auth_account_review_scroll .stButton {{
        width: 100% !important;
        max-width: 440px !important;
        margin: 0 auto 6px auto !important;
    }}

    .st-key-auth_login_scroll .stButton > button,
    .st-key-auth_register_scroll .stButton > button,
    .st-key-auth_forgot_scroll .stButton > button,
    .st-key-auth_admin_scroll .stButton > button,
    .st-key-auth_register_otp_scroll .stButton > button,
    .st-key-auth_login_otp_scroll .stButton > button,
    .st-key-auth_account_review_scroll .stButton > button {{
        width: 100% !important;
        height: 40px !important;
        min-height: 40px !important;
        border-radius: 8px !important;
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #EEEEF1 !important;
        color: #17151B !important;
        -webkit-text-fill-color: #17151B !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12.5px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 160ms ease !important;
        box-shadow: none !important;
    }}

    .st-key-auth_login_scroll .stButton > button:hover,
    .st-key-auth_register_scroll .stButton > button:hover,
    .st-key-auth_forgot_scroll .stButton > button:hover,
    .st-key-auth_admin_scroll .stButton > button:hover {{
        background: #F7F8FA !important;
        background-color: #F7F8FA !important;
        border-color: #D8DDE3 !important;
        color: #9672F4 !important;
        -webkit-text-fill-color: #9672F4 !important;
        transform: translateY(-1px) !important;
    }}

    /* Suppress Streamlit 'Press Enter to submit form' helper */
    [data-testid="InputInstructions"],
    div[data-testid="InputInstructions"],
    span[data-testid="InputInstructions"] {{
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }}

    /* Alerts and Feedback Containers */
    [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) .stAlert,
    .st-key-auth_login_scroll .stAlert,
    .st-key-auth_register_scroll .stAlert,
    .st-key-auth_forgot_scroll .stAlert,
    .st-key-auth_admin_scroll .stAlert {{
        border-radius: 8px !important;
        border: 1px solid #EEEEF1 !important;
        font-size: 12.5px !important;
        margin-bottom: 10px !important;
        max-width: 440px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }}

    /* =========================================================
       8. RESPONSIVE DESIGN (Section 37)
       Desktop: 50-50 split. Tablet/Mobile: Form is primary, zero clipping.
       ========================================================= */
    @media (max-width: 900px) {{
        [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) {{
            flex-direction: column !important;
            min-height: auto !important;
            width: 95vw !important;
            padding: 12px !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) > div[data-testid="stColumn"]:has(.auth-visual-panel),
        div[data-testid="stColumn"]:has(.auth-visual-panel) {{
            width: 100% !important;
            max-width: 100% !important;
            min-height: 260px !important;
        }}

        .auth-visual-panel {{
            min-height: 260px !important;
            padding: 24px 20px !important;
        }}

        .visual-hero-heading,
        .visual-hero-heading * {{
            font-size: 32px !important;
        }}

        .banking-stage-container {{
            display: none !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.auth-visual-panel) > div[data-testid="stColumn"]:not(:has(.auth-visual-panel)),
        div[data-testid="stColumn"]:has(.st-key-auth_login_scroll),
        div[data-testid="stColumn"]:has(.st-key-auth_register_scroll),
        div[data-testid="stColumn"]:has(.st-key-auth_forgot_scroll),
        div[data-testid="stColumn"]:has(.st-key-auth_admin_scroll),
        div[data-testid="stColumn"]:has(.st-key-auth_register_otp_scroll),
        div[data-testid="stColumn"]:has(.st-key-auth_login_otp_scroll),
        div[data-testid="stColumn"]:has(.st-key-auth_account_review_scroll) {{
            width: 100% !important;
            max-width: 100% !important;
            min-height: auto !important;
            padding: 20px 12px !important;
        }}
    }}
    </style>
    """
