import pandas as pd
import numpy as np


class InsightGenerator:

    @staticmethod
    def generate_insights(df):
        insights = []

        if df is None or df.empty:
            return []

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        # ---------------- 1. DATA QUALITY ---------------- #
        total_cells = df.shape[0] * df.shape[1]
        missing = df.isnull().sum().sum()

        completeness = ((total_cells - missing) / total_cells) * 100

        if completeness < 90:
            insights.append({
                "priority": "HIGH",
                "title": "Low Data Completeness",
                "insight": f"Only {completeness:.1f}% data available",
                "impact": "Analysis reliability is reduced"
            })

        # ---------------- 2. OUTLIERS ---------------- #
        for col in numeric_cols:
            data = df[col].dropna()

            if len(data) < 5:
                continue

            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1

            if IQR == 0:
                continue

            outliers = ((data < Q1 - 1.5*IQR) | (data > Q3 + 1.5*IQR)).sum()
            pct = (outliers / len(data)) * 100

            if pct > 8:
                insights.append({
                    "priority": "HIGH",
                    "title": "High Outliers",
                    "insight": f"{col} has {pct:.1f}% extreme values",
                    "impact": "May skew analysis results"
                })
                break  # only strongest

        # ---------------- 3. IMBALANCE ---------------- #
        for col in categorical_cols:
            top_pct = (df[col].value_counts().iloc[0] / len(df)) * 100

            if top_pct > 75:
                insights.append({
                    "priority": "MEDIUM",
                    "title": "Category Imbalance",
                    "insight": f"{col} dominated by one value ({top_pct:.0f}%)",
                    "impact": "Limits diversity in analysis"
                })
                break

        # ---------------- 4. CORRELATION ---------------- #
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()

            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    val = corr.iloc[i, j]

                    if abs(val) > 0.7:
                        insights.append({
                            "priority": "MEDIUM",
                            "title": "Strong Relationship",
                            "insight": f"{corr.columns[i]} & {corr.columns[j]} correlated ({val:.2f})",
                            "impact": "Variables may influence each other"
                        })
                        break
                else:
                    continue
                break

        # ---------------- 5. DATA SIZE ---------------- #
        if df.shape[0] < 50:
            insights.append({
                "priority": "LOW",
                "title": "Small Dataset",
                "insight": f"Only {df.shape[0]} records",
                "impact": "Limited statistical confidence"
            })

        # ---------------- SORT BY PRIORITY ---------------- #
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        insights = sorted(insights, key=lambda x: priority_order[x["priority"]])

        return insights[:3]  # limit