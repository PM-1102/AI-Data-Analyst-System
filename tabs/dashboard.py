import streamlit as st
import pandas as pd
import plotly.express as px
from utils.session import SessionManager


def render():
    """Dashboard - Simple visualization interface"""
    
    df = SessionManager.get_clean_df()

    if df is None:
        st.error("❌ No data found!")
        st.info("👉 **Step 1**: Go to 'Upload' tab and select your file")
        st.info("👉 **Step 2**: Click 'Clean & Prepare Data' button")
        st.info("👉 **Step 3**: Come back here to visualize")
        return

    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; margin: 0;">📈 Dashboard</h1>
        <p style="color: #8b97b3; margin: 0.5rem 0; font-size: 1.1rem;">Interactive charts and visual insights</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Get column types
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    # Overview
    st.markdown("### 📊 Quick Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Records", f"{len(df):,}")
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Numeric", len(numeric_cols))
    with col4:
        st.metric("Categories", len(categorical_cols))

    st.divider()

    # Main visualization tabs
    st.markdown("### 🎨 Visualizations")

    chart_tabs = st.tabs(["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"])

    # TAB 1: BAR CHART
    with chart_tabs[0]:
        st.markdown("**Bar Chart** - Compare values across categories")
        
        if categorical_cols and numeric_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("Category (X-axis)", categorical_cols, key="bar_x",
                                     format_func=lambda x: x.replace('_', ' ').title())
            
            with col2:
                y_col = st.selectbox("Values (Y-axis)", numeric_cols, key="bar_y",
                                     format_func=lambda x: x.replace('_', ' ').title())
            
            try:
                # Aggregate by category
                data_agg = df.groupby(x_col)[y_col].agg(['sum', 'mean', 'count']).reset_index()
                
                metric_choice = st.radio("Show", ["Total", "Average", "Count"], horizontal=True)
                
                if metric_choice == "Total":
                    y_data = "sum"
                    title_metric = "Total"
                elif metric_choice == "Average":
                    y_data = "mean"
                    title_metric = "Average"
                else:
                    y_data = "count"
                    title_metric = "Count"
                
                fig = px.bar(data_agg, x=x_col, y=y_data,
                           title=f"{title_metric} {y_col} by {x_col}",
                           labels={y_data: y_col.replace('_', ' ')})
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Could not create chart: {str(e)}")
        else:
            st.info("📊 Need at least one category column and one numeric column")

    # TAB 2: LINE CHART
    with chart_tabs[1]:
        st.markdown("**Line Chart** - Track values over time or sequence")
        
        if len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("X-axis", numeric_cols, key="line_x",
                                     format_func=lambda x: x.replace('_', ' ').title())
            
            with col2:
                y_col = st.selectbox("Y-axis", numeric_cols, key="line_y",
                                     format_func=lambda x: x.replace('_', ' ').title())
            
            try:
                df_sorted = df.sort_values(x_col).reset_index(drop=True)
                df_sorted['Index'] = range(len(df_sorted))
                
                fig = px.line(df_sorted, x=df_sorted['Index'], y=y_col,
                            title=f"{y_col} Trend",
                            markers=True)
                fig.update_xaxes(title="Record Number")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Could not create chart: {str(e)}")
        else:
            st.info("📊 Need at least 2 numeric columns for line chart")

    # TAB 3: SCATTER PLOT
    with chart_tabs[2]:
        st.markdown("**Scatter Plot** - Find relationships between values")
        
        if len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x", 
                                     format_func=lambda x: x.replace('_', ' ').title())
            
            with col2:
                y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y",
                                     format_func=lambda x: x.replace('_', ' ').title())
            
            try:
                fig = px.scatter(df, x=x_col, y=y_col,
                               title=f"{x_col} vs {y_col}")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Correlation info
                corr = df[x_col].corr(df[y_col])
                if abs(corr) > 0.7:
                    st.success(f"✅ **Strong relationship** (correlation: {corr:.2f})")
                elif abs(corr) > 0.4:
                    st.info(f"📊 **Moderate relationship** (correlation: {corr:.2f})")
                else:
                    st.warning(f"⚠️ **Weak relationship** (correlation: {corr:.2f})")
                    
            except Exception as e:
                st.error(f"Could not create chart: {str(e)}")
        else:
            st.info("📊 Need at least 2 numeric columns for scatter plot")

    # TAB 4: PIE CHART
    with chart_tabs[3]:
        st.markdown("**Pie Chart** - Show composition and proportions")
        
        if categorical_cols:
            cat_col = st.selectbox("Select category", categorical_cols, key="pie_cat",
                                   format_func=lambda x: x.replace('_', ' ').title())
            
            try:
                data_counts = df[cat_col].value_counts().reset_index()
                data_counts.columns = [cat_col, 'Count']
                
                fig = px.pie(data_counts, names=cat_col, values='Count',
                           title=f"Distribution of {cat_col}")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show percentages
                st.markdown("**Breakdown:**")
                total = data_counts['Count'].sum()
                for idx, row in data_counts.head(10).iterrows():
                    pct = (row['Count'] / total) * 100
                    st.text(f"• {row[cat_col]}: {row['Count']} ({pct:.1f}%)")
                    
            except Exception as e:
                st.error(f"Could not create chart: {str(e)}")
        else:
            st.info("📊 Need at least one category column for pie chart")

    st.divider()

    # Data table viewer
    st.markdown("### 📋 View Your Data")
    
    if st.checkbox("Show raw data table", value=False):
        st.dataframe(df, use_container_width=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv,
            file_name="data.csv",
            mime="text/csv"
        )

    st.divider()

    # Help section
    with st.expander("💡 Chart Guide", expanded=False):
        st.markdown("""
        **📊 Bar Chart**: Best for comparing values across categories
        - Example: Sales by region, Count by category
        
        **📈 Line Chart**: Best for trends over time or sequence
        - Example: Stock price over time, Performance trend
        
        **🔵 Scatter Plot**: Best for finding relationships
        - Example: Height vs Weight, Price vs Quality
        
        **🥧 Pie Chart**: Best for showing parts of a whole
        - Example: Market share, Budget allocation
        
        **💡 Tips**:
        - Use legends to understand what each color means
        - Hover over charts to see exact values
        - Hover on columns for more info
        """)
