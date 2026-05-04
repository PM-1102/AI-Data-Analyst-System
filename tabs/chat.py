import streamlit as st
import pandas as pd
from utils.session import SessionManager, get_clean_df
from utils.context_builder import build_data_context
from services.llm_engine import generate_ai_response
from services.query_engine import QueryEngine


def render():
    # Initialize chat history in session state (global, not tab-specific)
    if "global_chat_history" not in st.session_state:
        st.session_state.global_chat_history = []

    # ========== SIDEBAR: CHAT HISTORY ==========
    with st.sidebar:
        st.markdown("### 📝 Conversation")
        
        if st.session_state.global_chat_history:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.global_chat_history = []
                st.rerun()
            
            st.divider()
            
            # Display history in a scrollable, clean format
            for idx, chat_item in enumerate(st.session_state.global_chat_history):
                if chat_item["type"] == "user":
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <p style="font-size: 0.85rem; color: #00c6ff; margin-bottom: 0.3rem;">👤 You</p>
                        <p style="font-size: 0.9rem; color: #e0e6ed; margin: 0; padding: 0.5rem; background: rgba(0, 198, 255, 0.1); border-radius: 0.5rem; border-left: 2px solid #00c6ff;">{chat_item['message'][:100]}{'...' if len(chat_item['message']) > 100 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <p style="font-size: 0.85rem; color: #10b981; margin-bottom: 0.3rem;">🤖 AI</p>
                        <p style="font-size: 0.9rem; color: #8b97b3; margin: 0; padding: 0.5rem; background: rgba(16, 185, 129, 0.05); border-radius: 0.5rem; border-left: 2px solid #10b981;">{chat_item['message'][:100]}{'...' if len(chat_item['message']) > 100 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <p style="color: #8b97b3; font-size: 0.9rem; text-align: center; padding: 2rem 0;">
                📭 No conversation yet<br>Ask a question to start!
            </p>
            """, unsafe_allow_html=True)

    # ========== MAIN AREA: CLEAN AND FOCUSED ==========
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; margin: 0;">🤖 Ask AI Analyst</h1>
        <p style="color: #8b97b3; margin: 0.5rem 0; font-size: 1.1rem;">Ask natural language questions about your data</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    df = get_clean_df()

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

    # ========== QUERY INPUT SECTION ==========
    st.markdown("### ❓ Your Question")
    
    user_query = st.text_input(
        "Ask a question about your data",
        placeholder="e.g. What's the average tip by day?",
        label_visibility="collapsed"
    )

    # Example queries
    with st.expander("💡 Example Queries"):
        examples = [
            "total bill for female on saturday",
            "average tip by day",
            "highest bill amount",
            "how many records on friday",
            "average total_bill by sex",
            "sum of tips by time"
        ]
        cols = st.columns(3)
        for col_idx, example in enumerate(examples):
            with cols[col_idx % 3]:
                if st.button(f"📌 {example}", use_container_width=True, key=f"example_{col_idx}_{example}"):
                    user_query = example

    # Submit button
    submit_button = st.button("🚀 Analyze", use_container_width=True, type="primary", key="analyze_btn")

    st.divider()

    # ========== ANALYSIS SECTION ==========
    if submit_button:
        if not user_query.strip():
            st.warning("⚠️ Please enter a question first")
            return

        # Add to chat history
        st.session_state.global_chat_history.append({
            "type": "user",
            "message": user_query
        })

        try:
            # Processing indicator
            with st.spinner("🧠 Analyzing your data..."):
                # 🔍 Create engine and parse query
                engine = QueryEngine(df)
                result = engine.run_query(user_query)

                # ⚠️ Check for errors in result
                if "error" in result:
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
                        debug_cols = st.columns(4)
                        
                        with debug_cols[0]:
                            col = engine.detect_column(user_query)
                            st.metric("Column", col or "N/A")
                        
                        with debug_cols[1]:
                            agg = engine.detect_aggregation(user_query)
                            st.metric("Aggregation", agg or "N/A")
                        
                        with debug_cols[2]:
                            groupby_col = engine.detect_groupby_column(user_query)
                            st.metric("Group By", groupby_col or "None")
                        
                        with debug_cols[3]:
                            filters = engine.detect_filters(user_query)
                            st.metric("Filters", len(filters) if filters else 0)
                    
                    # Add error to chat history
                    st.session_state.global_chat_history.append({
                        "type": "ai",
                        "message": f"❌ {result['error']}"
                    })
                    
                    st.rerun()
                    return

                # Show chart if available
                if result.get("chart"):
                    st.plotly_chart(result["chart"], use_container_width=True)

                # Get result text
                result_text = result.get("result_text", str(result.get("result", "Query completed")))

                # If result is DataFrame, display it nicely
                if isinstance(result.get("result"), pd.DataFrame):
                    st.markdown("### 📊 Results Table")
                    st.dataframe(result["result"], use_container_width=True)
                    display_result = result_text
                else:
                    display_result = result_text

                # Build context for AI response
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

            # ========== RESULTS DISPLAY ==========
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
                # Answer Card
                st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.05)); border: 1px solid rgba(16,185,129,0.3);">
                    <h3 style="color: #10b981; margin-top: 0;">✅ Answer</h3>
                </div>
                """, unsafe_allow_html=True)
                st.success(answer_part)

                st.markdown("")  # Spacing

                # Insight Card
                if insight_part:
                    st.markdown("""
                    <div class="metric-card" style="background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(245,158,11,0.05)); border: 1px solid rgba(245,158,11,0.3);">
                        <h3 style="color: #f59e0b; margin-top: 0;">💡 Key Insight</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.info(insight_part)

                st.markdown("")  # Spacing

                # Recommendation Card
                if recommendation_part:
                    st.markdown("""
                    <div class="metric-card" style="background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(59,130,246,0.05)); border: 1px solid rgba(59,130,246,0.3);">
                        <h3 style="color: #3b82f6; margin-top: 0;">💼 Recommendation</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.info(recommendation_part)
            else:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #00c6ff; margin-top: 0;">✅ Analysis Complete</h3>
                </div>
                """, unsafe_allow_html=True)
                st.info(response)

            # Add AI response to chat history
            st.session_state.global_chat_history.append({
                "type": "ai",
                "message": response[:200] + "..." if len(response) > 200 else response
            })

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.error(error_msg)
            st.session_state.global_chat_history.append({
                "type": "ai",
                "message": error_msg
            })
