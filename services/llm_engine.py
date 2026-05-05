from groq import Groq
import streamlit as st
import os
from utils.logger import setup_logger
from utils.config import Config

logger = setup_logger(__name__)

# Initialize Groq client with API key from Streamlit secrets
client = None

try:
    api_key = st.secrets.get("GROQ_API_KEY")
    
    # DEBUG: Show if API key is found
    st.write("DEBUG: API KEY FOUND:", bool(api_key))
    
    if api_key:
        client = Groq(api_key=api_key)
        logger.info("✅ Groq client initialized with Streamlit secrets API key")
    else:
        logger.warning("⚠️ GROQ_API_KEY not found in Streamlit secrets")
        
except Exception as e:
    logger.error(f"❌ Error initializing Groq client: {type(e).__name__}: {str(e)}")
    client = None


def generate_ai_response(user_query, df_summary, filtered_data_preview):
    """
    Generate AI response using Groq with comprehensive error handling
    """

    if not client:
        return """Answer:
AI service is currently unavailable.

Insight:
The system could not connect to the AI engine.

Recommendation:
Check API key configuration or try again later."""

    prompt = f"""You are a strict Data Analyst. Your ONLY job is to analyze provided data.

CRITICAL RULES:
1. Use ONLY data provided below - NEVER invent numbers
2. If asked about missing data, say "This data is not available in the dataset"
3. Show your reasoning: "Based on X data points..."
4. Quote actual values from the data
5. Be concise and specific
6. Maximum 3 sentences per section

USER QUESTION:
"{user_query}"

═══════════════════════════════════════════════════════════════════════════════════════════════

DATA AVAILABLE FOR ANALYSIS:

{df_summary}

═══════════════════════════════════════════════════════════════════════════════════════════════

SAMPLE DATA ROWS:
{filtered_data_preview}

═══════════════════════════════════════════════════════════════════════════════════════════════

RESPONSE FORMAT:

Answer:
[Direct answer]

Insight:
[Key finding]

Recommendation:
[Actionable suggestion]
"""

    try:
        logger.info(f"🚀 Sending query to Groq: {user_query[:50]}...")
        response = client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_TOKENS
        )

        logger.info(f"✅ AI response generated successfully for query: {user_query[:50]}...")
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"❌ Error generating AI response: {type(e).__name__}: {str(e)}", exc_info=True)

        return f"""Answer:
Failed to generate AI response.

Insight:
An error occurred: {type(e).__name__}

Recommendation:
Please try again. If problem persists, check API key and Groq service status."""
