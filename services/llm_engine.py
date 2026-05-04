import os
import streamlit as st
from groq import Groq
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize Groq client with secure API key handling
try:
    # Use st.secrets first (production), then environment variable (development)
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not configured in secrets or environment")
    client = Groq(api_key=api_key)
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {str(e)}")
    client = None


def generate_ai_response(user_query, df_summary, filtered_data_preview):
    """
    Generate AI response using Groq with controlled context and fact-checking
    
    Args:
        user_query: User's natural language question
        df_summary: Statistical summary of data
        filtered_data_preview: Sample rows of data
    
    Returns:
        AI-generated response with Answer, Insight, Recommendation
    
    Raises:
        Exception: If API call fails or client not initialized
    """
    
    if not client:
        raise RuntimeError("Groq client not initialized. Check API key configuration.")

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
Please structure your response with these exact sections:

Answer:
[Direct answer to the question based ONLY on provided data]

Insight:
[One key finding from the data that supports the answer]

Recommendation:
[Actionable suggestion based on the data]

IMPORTANT: If the answer requires data not shown above, state clearly that this information is not available."""

    try:
        response = client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_TOKENS,
            timeout=Config.LLM_TIMEOUT_SECONDS
        )
        
        logger.info(f"AI response generated successfully for query: {user_query[:50]}...")
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to generate AI response: {str(e)}")