import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import time
from tabs import upload, clean, kpi, dashboard, chat
from utils.session import SessionManager
from utils.config import get_config
from utils.logger import setup_logger

# Initialize configuration
config = get_config()
logger = setup_logger(__name__)

# ========== VALIDATE DEPLOYMENT CONFIG ==========
try:
    api_key = config.get_groq_api_key()
except Exception:
    st.warning("⚠️ API key not configured. AI features disabled.")
    api_key = None

st.set_page_config(
    page_title=f"{config.APP_NAME} - {config.APP_DESCRIPTION}",
    layout=config.PAGE_LAYOUT,
    initial_sidebar_state=config.SIDEBAR_INITIAL_STATE,
    menu_items=None
)

# ========== CSS Loading ==========
def load_css():
    """Load CSS with fallback handling"""
    try:
        # Try multiple possible paths
        css_paths = [
            "main.css",
            "./main.css",
            "app/main.css"
        ]
        
        css_content = None
        for path in css_paths:
            try:
                with open(path, encoding="utf-8") as f:
                    css_content = f.read()
                    logger.info(f"CSS loaded from: {path}")
                    break
            except FileNotFoundError:
                continue
        
        if css_content:
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        else:
            logger.warning("CSS file not found in any expected location")
    except Exception as e:
        logger.error(f"Error loading CSS: {str(e)}")

load_css()

# ========== SESSION Initialization ==========
SessionManager.init()

if "page" not in st.session_state:
    st.session_state.page = "Upload"

# ========== SIDEBAR - Enhanced Navigation ==========
with st.sidebar:
    # Brand Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="margin: 0; font-size: 2.5rem;">📊</h1>
        <h2 style="margin: 0.5rem 0 0 0; background: linear-gradient(135deg, #00c6ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8rem;">DataSense AI</h2>
        <p style="color: #8b97b3; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Professional Analytics Engine</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Data Status
    raw_data_ready = st.session_state.get("df") is not None
    clean_data_ready = st.session_state.get("clean_df") is not None
    
    col1, col2 = st.columns(2)
    with col1:
        if raw_data_ready:
            st.markdown('<span class="status-badge status-success">📥 Data Loaded</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-warning">⚪ Pending</span>', unsafe_allow_html=True)
    
    with col2:
        if clean_data_ready:
            st.markdown('<span class="status-badge status-success">✨ Cleaned</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-info">⏳ Waiting</span>', unsafe_allow_html=True)

    st.divider()

    # Navigation Pages
    st.markdown("### 🗂️ Navigation")
    
    pages = [
        ("📤 Upload", "Upload"),
        ("🧹 Clean", "Clean"),
        ("📊 KPI", "KPI"),
        ("📈 Dashboard", "Dashboard"),
        ("🤖 Ask AI", "Ask AI")
    ]

    for icon_label, page_name in pages:
        is_active = st.session_state.page == page_name
        
        # Check if page is accessible
        if page_name == "Clean" and not raw_data_ready:
            st.button(icon_label, use_container_width=True, disabled=True, help="Upload data first")
        elif page_name in ["KPI", "Dashboard", "Ask AI"] and not clean_data_ready:
            st.button(icon_label, use_container_width=True, disabled=True, help="Clean data first")
        else:
            button_style = """
            <style>
            button {
                border: 2px solid transparent !important;
                transition: all 0.3s ease !important;
            }
            button:hover {
                border: 2px solid #00c6ff !important;
            }
            </style>
            """ if is_active else ""
            
            if st.button(
                f"{'✓' if is_active else '○'} {icon_label}",
                use_container_width=True,
                key=f"btn_{page_name}",
                help=f"Go to {page_name}"
            ):
                st.session_state.page = page_name
                st.rerun()

    st.divider()

    # Footer Info
    if clean_data_ready:
        file_info = st.session_state.get("file_info")
        if file_info:
            st.markdown("### 📋 Dataset Info")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", file_info.get("rows", "N/A"), delta=None)
            with col2:
                st.metric("Columns", file_info.get("cols", "N/A"), delta=None)
            with col3:
                st.metric("Status", "Ready", delta=None)

# ========== Main Content Area ==========
raw_data_ready = st.session_state.get("df") is not None
clean_data_ready = st.session_state.get("clean_df") is not None

# Data Flow Guards
if st.session_state.page == "Clean" and not raw_data_ready:
    st.error("❌ Upload data first to proceed to cleaning")
    st.stop()

if st.session_state.page in ["KPI", "Dashboard", "Ask AI"] and not clean_data_ready:
    st.warning("⚠️ Please clean your data first before proceeding to analysis")
    st.stop()

# ========== Page Routing ==========
page = st.session_state.page

if page == "Upload":
    upload.render()
elif page == "Clean":
    clean.render()
elif page == "KPI":
    kpi.render()
elif page == "Dashboard":
    dashboard.render()
elif page == "Ask AI":
    chat.render()