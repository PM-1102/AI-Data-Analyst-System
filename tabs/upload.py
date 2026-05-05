import streamlit as st
import pandas as pd
from services.data_loader import DataLoader
from services.data_cleaner import DataCleaner


def render():
    """Upload tab - handles file upload and automatic data cleaning"""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; margin: 0;">📤 Upload Dataset</h1>
        <p style="color: #8b97b3; margin: 0.5rem 0; font-size: 1.1rem;">Upload your CSV or Excel file for analysis</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ========== FILE UPLOAD ==========
    st.markdown("### 📁 Select Your File")

    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Maximum size: 200MB"
    )

    if uploaded_file is not None:
        try:
            # Load the file
            with st.spinner("📂 Loading file..."):
                df, file_extension = DataLoader.load_file(uploaded_file)

            st.success(f"✅ File loaded successfully ({file_extension} format)")

            # Store raw df temporarily for display
            st.session_state.df = df
            st.session_state.clean_df = df  # 🔥 fallback so app never breaks
            st.divider()

            # ========== RAW DATA INFO ==========
            st.markdown("### 📊 Raw Data Information")

            info_cols = st.columns(4)
            with info_cols[0]:
                st.metric("Total Rows", f"{df.shape[0]:,}")
            with info_cols[1]:
                st.metric("Total Columns", df.shape[1])
            with info_cols[2]:
                missing_cells = int(df.isnull().sum().sum())
                st.metric("Missing Values", missing_cells)
            with info_cols[3]:
                duplicate_rows = df.duplicated().sum()
                st.metric("Duplicates", duplicate_rows)

            st.divider()

            # ========== AUTO CLEAN SECTION ==========
            st.markdown("### 🧹 Automatic Data Cleaning")

            if st.button("🚀 Clean & Prepare Data", use_container_width=True, type="primary"):
                with st.spinner("🔄 Cleaning your data..."):
                    # Clean the data
                    clean_df, clean_report = DataCleaner.clean_data(df)

                    # Verify PyArrow compatibility
                    if not DataCleaner.is_pyarrow_safe(clean_df):
                        st.error("⚠️ Data still has compatibility issues. Applying additional fixes...")
                        # Convert all to string as fallback
                        clean_df = clean_df.astype(str)

                    # Store in session state
                    st.session_state.clean_df = clean_df
                    st.session_state.df = df  # Also store raw for reference
                    st.session_state.clean_report = clean_report
                    st.session_state.file_uploaded = True

                st.rerun()
                return
                st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.05)); border: 1px solid rgba(16,185,129,0.3);">
                    <h3 style="color: #10b981; margin-top: 0;">✅ Data Cleaned Successfully!</h3>
                    <p style="margin: 0.5rem 0; color: #e8edf8;">Your dataset is ready for analysis. Go to the 'Clean' tab to review.</p>
                </div>
                """, unsafe_allow_html=True)

                st.divider()

                # Show cleaning summary
                st.markdown("### 📋 Cleaning Summary")

                summary_cols = st.columns(4)
                with summary_cols[0]:
                    st.metric("Rows After", f"{clean_df.shape[0]:,}")
                with summary_cols[1]:
                    st.metric("Columns After", clean_df.shape[1])
                with summary_cols[2]:
                    missing_after = int(clean_df.isnull().sum().sum())
                    st.metric("Missing After", missing_after)
                with summary_cols[3]:
                    dup_after = clean_df.duplicated().sum()
                    st.metric("Duplicates After", dup_after)

                st.divider()

                # Column analysis
                st.markdown("### 🔍 Column Analysis")

                numeric_cols = clean_df.select_dtypes(include=['number']).columns.tolist()
                categorical_cols = clean_df.select_dtypes(include=['object']).columns.tolist()

                col_analysis = st.columns(3)
                with col_analysis[0]:
                    st.metric("Numeric Columns", len(numeric_cols))
                with col_analysis[1]:
                    st.metric("Categorical Columns", len(categorical_cols))
                with col_analysis[2]:
                    st.metric("Total Columns", len(numeric_cols) + len(categorical_cols))

                st.divider()

                # Data preview
                st.markdown("### 👀 Preview Cleaned Data")
                st.dataframe(clean_df.head(10), use_container_width=True)

                st.divider()

                # Next steps
                st.markdown("### 🎯 Next Steps")
                next_cols = st.columns(3)

                with next_cols[0]:
                    if st.button("📊 View Data Stats", use_container_width=True):
                        st.session_state.page = "Clean"
                        st.rerun()

                with next_cols[1]:
                    if st.button("📈 Generate KPIs", use_container_width=True):
                        st.session_state.page = "KPI"
                        st.rerun()

                with next_cols[2]:
                    if st.button("🤖 Ask AI", use_container_width=True):
                        st.session_state.page = "Ask AI"
                        st.rerun()

        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            st.error("Please check that your file format is valid (CSV or Excel)")

    else:
        # Info box when no file is uploaded
        st.info("""
        ### 📝 How to Use

        1. **Upload** your CSV or Excel file using the uploader above
        2. **Review** the raw data information
        3. **Click "Clean & Prepare"** to automatically clean your dataset
        4. **Explore** your cleaned data in the Clean tab
        5. **Analyze** using KPIs, Dashboard, or AI Chat

        ### ✨ Supported Features
        - **CSV files** - All encodings supported
        - **Excel files** - Multiple sheets
        - **Automatic cleaning** - Column names, data types, empty rows
        - **Header detection** - Finds the correct header row
        - **Type conversion** - Optimizes data types
        """)

        st.divider()

        st.markdown("### 📚 File Requirements")
        st.markdown("""
        **Maximum Size**
        - Up to 200MB

        **🏷️ Best Practice**
        - Headers in first row
        - Consistent data types
        - Clean column names

        **✨ Auto Features**
        - Header detection
        - Type conversion
        - Name cleaning
        - Empty removal
        """)
