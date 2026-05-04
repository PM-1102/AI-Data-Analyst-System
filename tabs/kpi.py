import streamlit as st
import plotly.express as px
import pandas as pd


def render():
    """KPI Dashboard - Simple and user-friendly"""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; margin: 0;">📊 Key Metrics</h1>
        <p style="color: #8b97b3; margin: 0.5rem 0; font-size: 1.1rem;">Quick overview of your data insights</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Check data availability
    if st.session_state.clean_df is None:
        st.error("❌ No data found!")
        st.info("👉 **Step 1**: Go to 'Upload' tab and select your file")
        st.info("👉 **Step 2**: Click 'Clean & Prepare Data' button")
        st.info("👉 **Step 3**: Come back here to see your KPIs")
        return

    df = st.session_state.clean_df

    # Get numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    # ========== BASIC INFO ==========
    st.markdown("### 📋 Dataset Overview")

    info_cols = st.columns(4)
    with info_cols[0]:
        st.metric("Total Records", f"{len(df):,}")
    with info_cols[1]:
        st.metric("Total Fields", df.shape[1])
    with info_cols[2]:
        st.metric("Numeric Fields", len(numeric_cols))
    with info_cols[3]:
        st.metric("Text Fields", len(categorical_cols))

    st.divider()

    # ========== NUMERIC METRICS ==========
    if numeric_cols:
        st.markdown("### 🔢 Number Metrics")

        # Create simple summary table
        summary_data = []
        for col in numeric_cols:
            summary_data.append({
                "Column": col.replace('_', ' ').title(),
                "Average": f"{df[col].mean():.2f}",
                "Min": f"{df[col].min():.2f}",
                "Max": f"{df[col].max():.2f}",
                "Count": f"{df[col].notna().sum()}"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.divider()

        # Charts for numeric columns
        st.markdown("### 📈 Quick Charts")

        chart_tabs = st.tabs(["Averages", "Distribution", "Trends"])

        with chart_tabs[0]:
            # Average values chart
            avg_data = []
            for col in numeric_cols:
                avg_data.append({"Metric": col.replace('_', ' ').title(), "Value": df[col].mean()})
            
            if avg_data:
                avg_df = pd.DataFrame(avg_data)
                fig = px.bar(avg_df, x="Metric", y="Value", 
                            title="Average Values by Metric",
                            color="Value",
                            color_continuous_scale="Blues")
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[1]:
            # Pick one column to show distribution
            if numeric_cols:
                col_to_show = st.selectbox("Select a metric to see its distribution", 
                                          numeric_cols,
                                          format_func=lambda x: x.replace('_', ' ').title())
                
                fig = px.histogram(df, x=col_to_show, nbins=20,
                                 title=f"Distribution of {col_to_show.replace('_', ' ').title()}",
                                 color_discrete_sequence=["#00d4ff"])
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[2]:
            st.info("💡 This shows trends over time if your data has date/time information")
            
            # Check if there's a time-based column
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            if date_cols and len(numeric_cols) > 0:
                date_col = date_cols[0]
                numeric_col = st.selectbox("Select metric", numeric_cols, key="trend")
                
                try:
                    trend_df = df[[date_col, numeric_col]].sort_values(date_col)
                    fig = px.line(trend_df, x=date_col, y=numeric_col,
                                title=f"{numeric_col.replace('_', ' ').title()} Over Time",
                                markers=True)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning("Could not create trend chart")
            else:
                st.text("No date/time column found in your data")

    else:
        st.info("📊 No numeric columns found in your data")

    st.divider()

    # ========== CATEGORY METRICS ==========
    if categorical_cols:
        st.markdown("### 🏷️ Category Breakdown")

        selected_cat = st.selectbox("Select a category to analyze", 
                                   categorical_cols,
                                   format_func=lambda x: x.replace('_', ' ').title())

        if selected_cat:
            # Count values
            value_counts = df[selected_cat].value_counts().reset_index()
            value_counts.columns = [selected_cat, "Count"]

            col1, col2 = st.columns([2, 1])

            with col1:
                fig = px.pie(value_counts, names=selected_cat, values="Count",
                           title=f"Breakdown of {selected_cat.replace('_', ' ').title()}")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("**Top Categories:**")
                for idx, row in value_counts.head(5).iterrows():
                    st.metric(str(row[selected_cat])[:20], row["Count"])

    else:
        st.info("🏷️ No text/category columns in your data")

    st.divider()

    # ========== HELP SECTION ==========
    with st.expander("💡 How to use this page", expanded=False):
        st.markdown("""
        **📊 Dataset Overview**: Shows basic information about your data
        
        **🔢 Number Metrics**: Statistics (average, min, max) for all numeric columns
        
        **📈 Quick Charts**:
        - *Averages*: Bar chart comparing average values
        - *Distribution*: Histogram showing how values spread
        - *Trends*: Line chart if your data has dates
        
        **🏷️ Category Breakdown**: Pie chart showing distribution of text/category values
        
        **👉 Next**: Try the Dashboard tab for more visualizations!
        """)
