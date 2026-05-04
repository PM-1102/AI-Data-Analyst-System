import streamlit as st
import pandas as pd
from utils.session import get_clean_df
from utils.context_builder import build_data_context
from services.llm_engine import generate_ai_response
from services.query_engine import QueryEngine


def render():
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; margin: 0;">🤖 Ask AI Analyst</h1>
        <p style="color: #8b97b3; margin: 0.5rem 0; font-size: 1.1rem;">Ask natural language questions about your data</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    df = get_clean_df()  # ✅ Use cleaned data for consistency

    # 🚫 No data guard
    if df is None:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.error("❌ No data available - Please upload and clean data first")
        with col2:
            if st.button("📂 Go to Upload", use_container_width=True, type="primary"):
                st.session_state.page = "Upload"
                st.rerun()
        return

    # ========== Query Input Section ==========
    st.markdown("### ❓ Your Question")
    
    query_col1, query_col2 = st.columns([4, 1])
    
    with query_col1:
        user_query = st.text_input(
            "Ask a question about your data",
            placeholder="e.g. What's the total bill for female on Saturday?",
            label_visibility="collapsed"
        )
    
    with query_col2:
        submit_button = st.button("🚀 Analyze", use_container_width=True, type="primary")

    # Example queries
    with st.expander("💡 Example Queries"):
        examples = [
            "total bill for female on saturday",
            "average tip by day",
            "highest bill amount",
            "how many records on friday"
        ]
        cols = st.columns(len(examples))
        for col, example in zip(cols, examples):
            with col:
                if st.button(f"📌 {example[:20]}...", use_container_width=True, key=f"example_{example}"):
                    user_query = example
                    submit_button = True

    st.divider()

    # ========== Analysis Section ==========
    if submit_button:
        if not user_query.strip():
            st.warning("⚠️ Please enter a question first")
            return

        try:
            # Create three columns for layout
            query_info_col, debug_col = st.columns([3, 1])
            
            with query_info_col:
                st.markdown("### 🔄 Processing Your Query")
                progress_bar = st.progress(0)
            
            with st.spinner("🧠 Analyzing your data..."):
                # Progress simulation
                for i in range(0, 100, 20):
                    progress_bar.progress(i)

                # 🔍 Create engine and parse query
                engine = QueryEngine(df)
                result = engine.run_query(user_query)
                
                progress_bar.progress(50)

                # Show chart if available
                if result.get("chart"):
                    st.plotly_chart(result["chart"], use_container_width=True)

                # ⚠️ Check for errors in result
                if "error" in result:
                    progress_bar.progress(100)
                    
                    st.markdown("### ❌ Query Analysis Result")
                    
                    # Error display with suggestions
                    error_col, suggestion_col = st.columns([1.5, 1])
                    
                    with error_col:
                        st.error(f"**Error**: {result['error']}")
                    
                    if "suggestion" in result:
                        with suggestion_col:
                            st.info(f"**Try this**: {result['suggestion']}")
                    
                    # Debug Information
                    with st.expander("🔍 Debug Information"):
                        st.markdown("**Query Details:**")
                        debug_cols = st.columns(3)
                        
                        with debug_cols[0]:
                            col = engine.detect_column(user_query)
                            st.metric("Detected Column", col or "N/A")
                        
                        with debug_cols[1]:
                            agg = engine.detect_aggregation(user_query)
                            st.metric("Aggregation", agg or "N/A")
                        
                        with debug_cols[2]:
                            filters = engine.detect_filters(user_query)
                            st.metric("Filters Applied", len(filters) if filters else 0)
                        
                        st.divider()
                        st.markdown("**Full Debug Output:**")
                        st.json({
                            "query": user_query,
                            "column": col,
                            "aggregation": agg,
                            "filters": filters,
                            "error": result.get("error")
                        })
                    return

                progress_bar.progress(75)

                # 🔎 Build context on result data
                if isinstance(result.get("result"), pd.DataFrame):
                    filtered_df = result["result"]
                else:
                    filtered_df = df

                filtered_summary, filtered_preview = build_data_context(filtered_df)

                # 🤖 AI response
                response = generate_ai_response(
                    user_query,
                    filtered_summary,
                    filtered_preview
                )
                
                progress_bar.progress(100)

            # ========== Results Display ==========
            st.markdown("### 📊 AI Analysis Results")
            
            # Parse response sections
            if "Answer:" in response:
                parts = response.split("Insight:")
                answer_part = parts[0].replace("Answer:", "").strip()

                insight_part = ""
                recommendation_part = ""

                if len(parts) > 1:
                    sub_parts = parts[1].split("Recommendation:")
                    insight_part = sub_parts[0].strip()

                    if len(sub_parts) > 1:
                        recommendation_part = sub_parts[1].strip()

                # Display in cards
                result_cols = st.columns(1)
                
                with result_cols[0]:
                    # Answer Card
                    with st.container():
                        st.markdown("""
                        <div class="metric-card">
                            <h3 style="color: #10b981; margin-top: 0;">✅ Answer</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.success(answer_part)

                    st.markdown("")  # Spacing

                    # Insight Card
                    if insight_part:
                        with st.container():
                            st.markdown("""
                            <div class="metric-card">
                                <h3 style="color: #f59e0b; margin-top: 0;">💡 Key Insight</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            st.info(insight_part)

                    st.markdown("")  # Spacing

                    # Recommendation Card
                    if recommendation_part:
                        with st.container():
                            st.markdown("""
                            <div class="metric-card">
                                <h3 style="color: #3b82f6; margin-top: 0;">📌 Recommendation</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            st.warning(recommendation_part)

            else:
                # Fallback display
                st.success(response)

            # Metadata
            st.divider()
            st.markdown("### 📈 Query Metadata")
            
            meta_cols = st.columns(4)
            with meta_cols[0]:
                st.metric("Dataset Rows", len(df))
            with meta_cols[1]:
                st.metric("Dataset Columns", len(df.columns))
            with meta_cols[2]:
                st.metric("Query Type", engine.detect_aggregation(user_query) or "Select")
            with meta_cols[3]:
                st.metric("Filters Used", len(engine.detect_filters(user_query)))

        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            with st.expander("📋 Error Details"):
                st.code(str(e), language="python")
