from groq import Groq
import streamlit as st

client = None

try:
    api_key = st.secrets.get("GROQ_API_KEY")

    if api_key:
        client = Groq(api_key=api_key)

except Exception:
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
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"""Answer:
Failed to generate AI response.

Insight:
An error occurred while processing your request.

Recommendation:
Please try again later."""
