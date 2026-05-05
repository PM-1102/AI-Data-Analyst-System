import os
import streamlit as st
from groq import Groq
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

client = None  # ✅ always define globally

# Initialize Groq client safely
try:
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not configured")

    # ✅ Simple initialization without proxy or http_client overrides
    client = Groq(api_key=api_key)

    logger.info("Groq client initialized successfully")

except Exception as e:
    logger.error(f"Failed to initialize Groq client: {str(e)}")
    client = None


def generate_ai_response(user_query, df_summary, filtered_data_preview):
    """
    Generate AI response using Groq
    """

    # ✅ FIXED indentation + safe fallback
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
        response = client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_TOKENS,
            timeout=Config.LLM_TIMEOUT_SECONDS
        )

        logger.info(f"AI response generated for query: {user_query[:50]}...")
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}", exc_info=True)

        return f"""Answer:
Failed to generate AI response.

Insight:
An error occurred while processing your request.

Recommendation:
Please try again or check logs. Error: {str(e)}"""
