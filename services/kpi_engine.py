import pandas as pd
import numpy as np


class KPIEngine:

    @staticmethod
    def generate_kpis(df: pd.DataFrame):
        """Generate KPIs for any dataset type"""
        kpis = []
        
        if df is None or df.empty:
            return [{"label": "Status", "value": "No data"}]

        try:
            # Basic KPIs
            kpis.append({"label": "Total Rows", "value": df.shape[0]})
            kpis.append({"label": "Total Columns", "value": df.shape[1]})

            # Numeric KPIs
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

            for col in numeric_cols[:3]:
                try:
                    col_data = pd.to_numeric(df[col], errors='coerce')
                    mean_val = col_data.mean()
                    max_val = col_data.max()
                    
                    if not np.isnan(mean_val):
                        kpis.append({
                            "label": f"Avg {col}",
                            "value": round(float(mean_val), 2)
                        })
                    if not np.isnan(max_val):
                        kpis.append({
                            "label": f"Max {col}",
                            "value": round(float(max_val), 2)
                        })
                except Exception as e:
                    continue

            # Categorical KPIs
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()

            for col in cat_cols[:2]:
                try:
                    value_counts = df[col].value_counts()
                    if len(value_counts) > 0:
                        top = value_counts.index[0]
                        pct = round((value_counts.iloc[0] / len(df)) * 100, 1)
                        kpis.append({
                            "label": f"Top {col}",
                            "value": f"{str(top)[:30]} ({pct}%)"
                        })
                except Exception as e:
                    continue

            return kpis if kpis else [{"label": "Status", "value": "Data loaded"}]
            
        except Exception as e:
            return [{"label": "Error", "value": "Unable to generate KPIs"}]

    @staticmethod
    def get_primary_kpis(df):
        """Get primary KPIs for dashboard - works with any dataset"""
        kpis = []
        
        if df is None or df.empty:
            return [{"label": "Status", "value": "No data"}]

        try:
            # Total rows
            kpis.append({
                "label": "Total Records",
                "value": len(df)
            })

            # Numeric summary - get first 2 numeric columns
            num_cols = df.select_dtypes(include=['number']).columns.tolist()

            for col in num_cols[:2]:
                try:
                    col_data = pd.to_numeric(df[col], errors='coerce')
                    mean_val = col_data.mean()
                    max_val = col_data.max()
                    
                    if not np.isnan(mean_val):
                        kpis.append({
                            "label": f"Avg {col}",
                            "value": round(float(mean_val), 2)
                        })

                    if not np.isnan(max_val):
                        kpis.append({
                            "label": f"Max {col}",
                            "value": round(float(max_val), 2)
                        })
                except:
                    pass

            return kpis if kpis else [{"label": "Status", "value": "Data loaded"}]
            
        except Exception as e:
            return [{"label": "Status", "value": "Data loaded"}]