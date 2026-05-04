import plotly.express as px
import pandas as pd


class ChartBuilder:

    @staticmethod
    def create_histogram(df, column):
        try:
            fig = px.histogram(df, x=column, nbins=30)
            fig.update_layout(title=f"Distribution of {column}", xaxis_title=column)
            return fig
        except Exception as e:
            print(f"Histogram error: {e}")
            return None

    @staticmethod
    def create_bar_chart(df, x_col, y_col):
        try:
            fig = px.bar(df, x=x_col, y=y_col)
            fig.update_layout(title=f"{y_col} by {x_col}")
            return fig
        except Exception as e:
            print(f"Bar chart error: {e}")
            return None

    @staticmethod
    def create_scatter_plot(df, x_col, y_col):
        try:
            fig = px.scatter(df, x=x_col, y=y_col)
            fig.update_layout(title=f"{y_col} vs {x_col}")
            return fig
        except Exception as e:
            print(f"Scatter error: {e}")
            return None

    @staticmethod
    def create_heatmap(df):
        try:
            numeric_df = df.select_dtypes(include=['number'])
            corr = numeric_df.corr()
            fig = px.imshow(corr, labels=dict(color="Correlation"))
            fig.update_layout(title="Correlation Matrix")
            return fig
        except Exception as e:
            print(f"Heatmap error: {e}")
            return None