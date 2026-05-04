import pandas as pd
import numpy as np
import difflib
import plotly.express as px


class QueryEngine:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.columns = df.columns.tolist()
        self.numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    # ========== GROUPBY DETECTION ==========
    def detect_groupby_column(self, query):
        """Detect if query asks for aggregation BY a column - works with ANY column"""
        query_lower = query.lower()
        
        # Keywords indicating groupby
        groupby_keywords = ["by ", "per ", "each ", "for each ", "grouped by"]
        
        groupby_col = None
        for keyword in groupby_keywords:
            if keyword in query_lower:
                # Extract what comes after the keyword
                idx = query_lower.find(keyword)
                after_keyword = query_lower[idx + len(keyword):].strip()
                
                # Check if any column name matches
                for col in self.columns:
                    if col.lower() in after_keyword.lower():
                        return col
                
                # Fuzzy match
                words = after_keyword.split()
                if words:
                    matches = difflib.get_close_matches(words[0], self.columns, n=1, cutoff=0.6)
                    if matches:
                        return matches[0]
        
        return None

    # ========== SMART COLUMN DETECTION ==========
    def detect_column(self, query):
        """Detect target column - works with ANY dataset"""
        query_lower = query.lower()

        # Priority: exact column name match
        for col in self.columns:
            if col.lower() in query_lower:
                return col

        # Priority: numeric columns for aggregations
        if any(agg in query_lower for agg in ["average", "mean", "sum", "total", "max", "min", "median"]):
            if self.numeric_cols:
                return self.numeric_cols[0]  # Return first numeric column

        # Fuzzy match against all columns
        words_in_query = query_lower.split()
        for word in words_in_query:
            if len(word) > 2:  # Ignore small words
                matches = difflib.get_close_matches(word, self.columns, n=1, cutoff=0.6)
                if matches:
                    return matches[0]

        # Fallback: return first numeric column if available
        return self.numeric_cols[0] if self.numeric_cols else (self.categorical_cols[0] if self.categorical_cols else None)

    # ========== AGGREGATION DETECTION ==========
    def detect_aggregation(self, query):
        """Detect aggregation function"""
        query_lower = query.lower()

        if "average" in query_lower or "mean" in query_lower or "avg" in query_lower:
            return "mean"
        if "sum" in query_lower or "total" in query_lower:
            return "sum"
        if "max" in query_lower or "highest" in query_lower or "maximum" in query_lower:
            return "max"
        if "min" in query_lower or "lowest" in query_lower or "minimum" in query_lower:
            return "min"
        if "count" in query_lower or "how many" in query_lower or "number of" in query_lower:
            return "count"
        if "median" in query_lower or "middle" in query_lower:
            return "median"
        if "std" in query_lower or "standard deviation" in query_lower or "variance" in query_lower:
            return "std"

        return "mean"  # Default

    # ========== FILTERS DETECTION ==========
    def detect_filters(self, query):
        """Detect filters - works with ANY categorical values"""
        query_lower = query.lower()
        filters = {}

        # Look for categorical columns and their potential values
        for col in self.categorical_cols:
            unique_values = self.df[col].unique()
            for val in unique_values:
                val_str = str(val).lower()
                if val_str and val_str in query_lower:
                    filters[col] = val
                    break  # One filter per column

        return filters

    # ========== APPLY FILTERS ==========
    def apply_filters(self, df, filters):
        """Apply filters to dataframe with case-insensitive matching"""
        for col, val in filters.items():
            if col in df.columns:
                df = df[df[col].astype(str).str.lower() == str(val).lower()]
        return df

    # ========== MAIN QUERY EXECUTION ==========
    def run_query(self, query):
        """Execute query on ANY dataset"""
        try:
            # Handle empty dataframe
            if self.df.empty:
                return {"error": "No data available. Please upload a file first."}

            agg = self.detect_aggregation(query)
            col = self.detect_column(query)
            groupby_col = self.detect_groupby_column(query)
            filters = self.detect_filters(query)

            if not col:
                return {
                    "error": "Could not identify which column to analyze.",
                    "suggestion": f"Available columns: {', '.join(self.columns[:5])}"
                }

            # Apply filters
            df_filtered = self.apply_filters(self.df.copy(), filters)

            if df_filtered.empty:
                return {
                    "error": "No data matches your filters",
                    "suggestion": "Try different filter values"
                }

            # ========== GROUPED AGGREGATION ==========
            if groupby_col and groupby_col in df_filtered.columns and groupby_col != col:
                try:
                    # Check if column to aggregate is numeric or categorical
                    if col in self.numeric_cols:
                        # Numeric aggregation with groupby
                        result_df = df_filtered.groupby(groupby_col, observed=True)[col].agg([agg, "count"]).reset_index()
                        result_df.columns = [groupby_col, agg, "count"]
                        
                        # Round numeric values
                        try:
                            result_df[agg] = result_df[agg].astype(float).round(2)
                        except:
                            pass
                        
                        # Create readable text
                        result_text = f"{agg.capitalize()} of {col} by {groupby_col}:\n\n"
                        for idx, row in result_df.iterrows():
                            result_text += f"• {row[groupby_col]}: {row[agg]} (count={int(row['count'])})\n"
                        
                        # Create chart
                        chart = px.bar(
                            result_df,
                            x=groupby_col,
                            y=agg,
                            title=f"{agg.capitalize()} of {col} by {groupby_col}",
                            labels={agg: f"{agg.capitalize()}"}
                        )
                        chart.update_layout(height=400)
                        
                        return {
                            "result": result_df,
                            "result_text": result_text.strip(),
                            "explanation": f"{agg} grouped by {groupby_col}",
                            "chart": chart
                        }
                    else:
                        # Categorical column - show counts by groupby column
                        result_df = df_filtered.groupby([groupby_col, col]).size().reset_index(name='count')
                        result_text = f"Count of {col} by {groupby_col}:\n\n"
                        for idx, row in result_df.iterrows():
                            result_text += f"• {row[groupby_col]} - {row[col]}: {row['count']}\n"
                        
                        chart = px.bar(
                            result_df,
                            x=groupby_col,
                            y='count',
                            color=col,
                            title=f"Distribution of {col} by {groupby_col}",
                            labels={'count': 'Count'}
                        )
                        chart.update_layout(height=400)
                        
                        return {
                            "result": result_df,
                            "result_text": result_text.strip(),
                            "explanation": f"Distribution by {groupby_col}",
                            "chart": chart
                        }
                except Exception as e:
                    return {"error": f"Error in grouped aggregation: {str(e)}"}

            # ========== SINGLE AGGREGATION ==========
            try:
                # Validate aggregation on numeric columns
                if col not in self.numeric_cols and agg in ["mean", "sum", "max", "min", "median", "std"]:
                    # Try to convert to numeric
                    try:
                        temp_col = pd.to_numeric(df_filtered[col], errors='coerce')
                        if temp_col.notna().sum() == 0:
                            return {
                                "error": f"Cannot calculate {agg} on non-numeric column '{col}'",
                                "suggestion": f"Try with a numeric column: {', '.join(self.numeric_cols[:3])}"
                            }
                        df_filtered[col] = temp_col
                    except:
                        return {
                            "error": f"Cannot calculate {agg} on column '{col}'",
                            "suggestion": f"Use a numeric column instead"
                        }

                # Calculate result
                if agg == "mean":
                    result = pd.to_numeric(df_filtered[col], errors='coerce').mean()
                elif agg == "sum":
                    result = pd.to_numeric(df_filtered[col], errors='coerce').sum()
                elif agg == "max":
                    result = pd.to_numeric(df_filtered[col], errors='coerce').max()
                elif agg == "min":
                    result = pd.to_numeric(df_filtered[col], errors='coerce').min()
                elif agg == "median":
                    result = pd.to_numeric(df_filtered[col], errors='coerce').median()
                elif agg == "std":
                    result = pd.to_numeric(df_filtered[col], errors='coerce').std()
                elif agg == "count":
                    result = len(df_filtered)
                else:
                    result = df_filtered[col].nunique()

                # Format result
                if isinstance(result, (float, np.floating)) and not np.isnan(result):
                    result = round(result, 2)
                elif pd.isna(result):
                    result = "No data"

                return {
                    "result": result,
                    "result_text": f"{agg.capitalize()} of {col}: {result}",
                    "explanation": f"{agg} of {col}",
                    "chart": None
                }
            except Exception as e:
                return {"error": f"Error calculating {agg}: {str(e)}"}

        except Exception as e:
            return {"error": f"Error processing query: {str(e)}"}
            if groupby_col and groupby_col in df_filtered.columns:
                # Handle case where we're grouping categorical column (can't aggregate)
                if df_filtered[col].dtype == "object":
                    # For categorical columns, just return counts
                    result_df = df_filtered.groupby(groupby_col).size().reset_index(name="count")
                    result_text = f"Count by {groupby_col}:\n\n"
                    for idx, row in result_df.iterrows():
                        result_text += f"• {row[groupby_col]}: {row['count']}\n"
                    
                    # Create chart
                    chart = px.bar(
                        result_df, 
                        x=groupby_col, 
                        y="count",
                        title=f"Count by {groupby_col}",
                        labels={"count": "Count"}
                    )
                    chart.update_layout(height=400)
                    
                    return {
                        "result": result_df,
                        "result_text": result_text.strip(),
                        "explanation": f"Count grouped by {groupby_col}",
                        "chart": chart
                    }
                else:
                    # Numeric column aggregation
                    result_df = df_filtered.groupby(groupby_col)[col].agg([agg, "count"]).reset_index()
                    result_df.columns = [groupby_col, agg, "count"]
                    result_df[agg] = result_df[agg].round(2)
                    
                    # Create readable text
                    result_text = f"{agg.capitalize()} of {col} by {groupby_col}:\n\n"
                    for idx, row in result_df.iterrows():
                        result_text += f"• {row[groupby_col]}: {row[agg]} (n={int(row['count'])})\n"
                    
                    # Create chart
                    chart = px.bar(
                        result_df,
                        x=groupby_col,
                        y=agg,
                        title=f"{agg.capitalize()} of {col} by {groupby_col}",
                        labels={agg: f"{agg.capitalize()} {col}"}
                    )
                    chart.update_layout(height=400)
                    
                    return {
                        "result": result_df,
                        "result_text": result_text.strip(),
                        "explanation": f"{agg} of {col} grouped by {groupby_col}",
                        "chart": chart
                    }

            # ========== SINGLE AGGREGATION ==========
            # Validate aggregation rules
            if agg in ["mean", "sum", "max", "min", "median", "std"] and df_filtered[col].dtype == "object":
                return {
                    "error": f"❌ Cannot calculate {agg} on categorical column '{col}'",
                    "suggestion": "Use a numeric column like total_bill, tip, or size"
                }

            if agg == "mean":
                result = df_filtered[col].mean()
            elif agg == "sum":
                result = df_filtered[col].sum()
            elif agg == "max":
                result = df_filtered[col].max()
            elif agg == "min":
                result = df_filtered[col].min()
            elif agg == "median":
                result = df_filtered[col].median()
            elif agg == "std":
                result = df_filtered[col].std()
            elif agg == "count":
                result = len(df_filtered)
            else:
                return {"result": df_filtered.head()}

            if isinstance(result, float):
                result = round(result, 2)

            return {
                "result": result,
                "result_text": f"{agg.capitalize()} of {col}: {result}",
                "explanation": f"{agg} of {col}",
                "chart": None
            }

        except Exception as e:
            return {"error": f"❌ Error processing query: {str(e)}"}