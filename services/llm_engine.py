import os
import streamlit as st
from groq import Groq
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

client = None  # ✅ always define globally

# Initialize Groq client safely with detailed logging
def initialize_groq_client():
    """Initialize Groq client with comprehensive error handling"""
    global client
    
    try:
        # Try multiple ways to get API key
        api_key = None
        
        # Method 1: Try st.secrets (works in Streamlit Cloud)
        try:
            if hasattr(st, 'secrets') and st.secrets:
                api_key = st.secrets.get("GROQ_API_KEY")
                if api_key:
                    logger.info("✅ API key loaded from Streamlit secrets")
        except Exception as e:
            logger.debug(f"Could not access st.secrets: {e}")
        
        # Method 2: Try environment variable (works in local/Docker)
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                logger.info("✅ API key loaded from environment variable")
        
        # If we found an API key, initialize Groq
        if api_key:
            logger.info("🔑 Initializing Groq client with API key...")
            client = Groq(api_key=api_key)
            logger.info("✅ Groq client initialized successfully")
            return client
        else:
            logger.warning("⚠️ GROQ_API_KEY not found in secrets or environment")
            return None
        
    except TypeError as te:
        logger.error(f"❌ Groq initialization TypeError (likely invalid parameter): {str(te)}")
        return None
    except ValueError as ve:
        logger.error(f"❌ Groq initialization ValueError (likely API key issue): {str(ve)}")
        return None
    except Exception as e:
        logger.error(f"❌ Groq initialization failed: {type(e).__name__}: {str(e)}")
        return None

# Initialize on module load
client = initialize_groq_client()


def ensure_groq_client():
    """Ensure Groq client is initialized, retry if needed"""
    global client
    
    # If client is already initialized, return it
    if client:
        return client
    
    # Try to initialize again (st.secrets might be available now)
    logger.info("🔄 Retrying Groq client initialization...")
    client = initialize_groq_client()
    return client


def generate_ai_response(user_query, df_summary, filtered_data_preview):
    """
    Generate AI response using Groq with comprehensive error handling
    """

    # ✅ Ensure client is initialized (retry if first attempt failed)
    groq_client = ensure_groq_client()
    
    if not groq_client:
        logger.warning("❌ Groq client not available - returning fallback response")
        return """Answer:
🔐 AI service requires API key configuration.

Insight:
The system couldn't initialize the AI engine. This usually means:
1. GROQ_API_KEY is not set in Streamlit secrets
2. Or there was an initialization error

Recommendation:
For Streamlit Cloud: Add GROQ_API_KEY to your Streamlit secrets.
For local development: Set GROQ_API_KEY in your .env file."""

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
        response = groq_client.chat.completions.create(
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
