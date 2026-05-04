import re
from services.query_engine import QueryEngine

# 🔹 FILTER MAPPING - Maps natural language terms to data values
FILTER_MAPPING = {
    # Gender
    "female": ("sex", "Female"),
    "male": ("sex", "Male"),
    "woman": ("sex", "Female"),
    "man": ("sex", "Male"),
    "women": ("sex", "Female"),
    "men": ("sex", "Male"),
    
    # Days
    "sunday": ("day", "Sun"),
    "sun": ("day", "Sun"),
    "sunday's": ("day", "Sun"),
    
    "monday": ("day", "Mon"),
    "mon": ("day", "Mon"),
    
    "tuesday": ("day", "Tue"),
    "tue": ("day", "Tue"),
    
    "wednesday": ("day", "Wed"),
    "wed": ("day", "Wed"),
    
    "thursday": ("day", "Thur"),
    "thur": ("day", "Thur"),
    "thurs": ("day", "Thur"),
    
    "friday": ("day", "Fri"),
    "fri": ("day", "Fri"),
    
    "saturday": ("day", "Sat"),
    "sat": ("day", "Sat"),
    "saturday's": ("day", "Sat"),
    
    # Meal times
    "lunch": ("time", "Lunch"),
    "lunch time": ("time", "Lunch"),
    "dinner": ("time", "Dinner"),
    "dinner time": ("time", "Dinner"),
    "breakfast": ("time", "Breakfast"),
    "brunch": ("time", "Brunch"),
}


def extract_filters(query, df_columns, df=None):
    """
    Extract structured filters from user query with multiple strategies
    """
    filters = {}
    query_lower = query.lower()

    # Strategy 1: Apply filter mapping (most reliable)
    for keyword, (col, val) in FILTER_MAPPING.items():
        if keyword in query_lower:
            filters[col] = val

    # Strategy 2: Direct dataset value detection
    if df is not None:
        for col in df_columns:
            if df[col].dtype == "object":
                unique_vals = df[col].astype(str).unique()
                for val in unique_vals:
                    # Case-insensitive match
                    if str(val).lower() in query_lower:
                        filters[col] = val

    # Strategy 3: Numeric conditions
    if "high" in query_lower or "greater" in query_lower or "more than average" in query_lower:
        filters["total_bill"] = ">mean"

    if "low" in query_lower or "less" in query_lower or "less than average" in query_lower:
        filters["total_bill"] = "<mean"

    return filters


def run_query_analysis(df, user_query):
    """
    Run query analysis using QueryEngine for detailed results
    """
    engine = QueryEngine(df)
    result = engine.run_query(user_query)
    return result