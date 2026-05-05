import streamlit as st
import pandas as pd


def render():
    """Clean tab - shows already-cleaned data statistics"""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; margin: 0;">🧹 Data Cleaned</h1>
        <p style="color: #8b97b3; margin: 0.5rem 0; font-size: 1.1rem;">Your dataset has been automatically prepared</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Check if data is loaded and cleaned
    from utils.session import get_safe_df
    df = get_safe_df()
    
    if df is None:
        st.error("❌ No data available - Please upload data first")
        st.stop()

    # ========== CLEANING SUMMARY ==========
    st.markdown("### ✅ Cleaning Summary")
    
    if hasattr(st.session_state, 'clean_report') and st.session_state.clean_report:
        report = st.session_state.clean_report
        
        summary_cols = st.columns(4)
        with summary_cols[0]:
            if 'original_shape' in report:
                st.metric("Original Rows", f"{report['original_shape'][0]:,}")
            
        with summary_cols[1]:
            if 'rows_removed' in report:
                st.metric("Rows Removed", report['rows_removed'])
        
        with summary_cols[2]:
            if 'columns_removed' in report:
                st.metric("Columns Removed", report['columns_removed'])
        
        with summary_cols[3]:
            st.metric("Status", report.get('status', 'Unknown'))
    
    st.divider()

    # ========== CLEANED DATA STATISTICS ==========
    st.markdown("### 📊 Cleaned Data Profile")

    profile_cols = st.columns(4)
    with profile_cols[0]:
        st.metric("Total Rows", f"{df.shape[0]:,}")
    with profile_cols[1]:
        st.metric("Total Columns", df.shape[1])
    with profile_cols[2]:
        missing_cells = int(df.isnull().sum().sum())
        st.metric("Missing Values", missing_cells)
    with profile_cols[3]:
        duplicate_rows = df.duplicated().sum()
        st.metric("Duplicates", duplicate_rows)

    st.divider()

    # ========== COLUMN ANALYSIS ==========
    st.markdown("### 🔬 Column Analysis")

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    col_analysis = st.columns(3)
    with col_analysis[0]:
        st.metric("Numeric Columns", len(numeric_cols))
    with col_analysis[1]:
        st.metric("Categorical Columns", len(categorical_cols))
    with col_analysis[2]:
        st.metric("Total Columns", len(numeric_cols) + len(categorical_cols))

    st.divider()

    # ========== COLUMN TYPES ==========
    st.markdown("### 🔍 Column Types & Statistics")

    col_info = pd.DataFrame({
        "Column": df.columns,
        "Type": [str(dtype) for dtype in df.dtypes],
        "Non-Null": [df[col].notna().sum() for col in df.columns],
        "Missing": [df[col].isna().sum() for col in df.columns],
        "Unique": [df[col].nunique() for col in df.columns]
    })
    
    st.dataframe(col_info, use_container_width=True)

    st.divider()

    # ========== DATA PREVIEW ==========
    st.markdown("### 👁️ Data Preview")

    preview_tabs = st.tabs(["First 20 Rows", "Last 20 Rows", "Sample"])

    with preview_tabs[0]:
        st.dataframe(df.head(20), use_container_width=True)

    with preview_tabs[1]:
        st.dataframe(df.tail(20), use_container_width=True)

    with preview_tabs[2]:
        sample_size = min(20, len(df))
        st.dataframe(df.sample(n=sample_size), use_container_width=True)

    st.divider()

    # ========== NUMERIC COLUMNS SUMMARY ==========
    if numeric_cols:
        st.markdown("### 📊 Numeric Columns Summary")
        numeric_stats = df[numeric_cols].describe().T
        st.dataframe(numeric_stats, use_container_width=True)
        st.divider()

    # ========== NEXT STEPS ==========
    st.markdown("### 🎯 Ready for Analysis!")

    next_cols = st.columns(3)

    with next_cols[0]:
        if st.button("📊 KPI Dashboard", use_container_width=True, type="primary"):
            st.session_state.page = "KPI"
            st.rerun()

    with next_cols[1]:
        if st.button("📈 Visualizations", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()

    with next_cols[2]:
        if st.button("🤖 AI Analysis", use_container_width=True):
            st.session_state.page = "Ask AI"
            st.rerun()
