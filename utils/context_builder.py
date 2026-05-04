def build_data_context(df):
    """
    Build rich context for LLM with comprehensive data insights
    """
    
    # 1. Dataset Overview
    overview = f"""
DATASET OVERVIEW
═══════════════════════════════════════════════════════════════
Rows: {df.shape[0]} | Columns: {df.shape[1]}
Missing Values: {int(df.isnull().sum().sum())} cells
"""
    
    # 2. Column Information
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    columns_info = f"""
COLUMNS
═══════════════════════════════════════════════════════════════
Numeric: {', '.join(numeric_cols) if numeric_cols else 'None'}
Categorical: {', '.join(categorical_cols) if categorical_cols else 'None'}

Data Types:
"""
    for col, dtype in df.dtypes.items():
        columns_info += f"  {col}: {dtype}\n"
    
    # 3. Numeric Statistics
    numeric_stats = ""
    if numeric_cols:
        numeric_stats = f"""
NUMERIC COLUMNS STATISTICS
═══════════════════════════════════════════════════════════════
"""
        numeric_stats += df[numeric_cols].describe().to_string()
    
    # 4. Categorical Statistics
    categorical_stats = ""
    if categorical_cols:
        categorical_stats = f"""

CATEGORICAL COLUMNS (Unique Values)
═══════════════════════════════════════════════════════════════
"""
        for col in categorical_cols:
            unique_vals = df[col].unique()
            categorical_stats += f"{col}: {', '.join([str(v) for v in unique_vals[:10]])}"
            if len(unique_vals) > 10:
                categorical_stats += f" ... and {len(unique_vals) - 10} more\n"
            else:
                categorical_stats += "\n"
    
    # 5. Combined Summary
    summary = overview + columns_info + numeric_stats + categorical_stats
    
    # 6. Data Preview
    preview = df.head(10).to_string()
    
    return summary, preview