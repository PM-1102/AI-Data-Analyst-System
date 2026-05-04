import pandas as pd
import numpy as np
import streamlit as st
from utils.logger import setup_logger
import re

logger = setup_logger(__name__)


class DataCleaner:
    """
    Universal data cleaner that produces ALWAYS PyArrow-compatible dataframes.
    Key principles:
    1. Remove ALL problematic characters from column names
    2. Convert ALL data types to safe types (no mixed types)
    3. Handle ALL edge cases (merged cells, sparse data, weird formatting)
    """

    @staticmethod
    def is_pyarrow_safe(df: pd.DataFrame) -> bool:
        """Check if dataframe is safe for PyArrow conversion"""
        try:
            import pyarrow as pa
            pa.Table.from_pandas(df)
            return True
        except Exception as e:
            logger.warning(f"PyArrow check failed: {str(e)}")
            return False

    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggressively clean column names to be PyArrow-safe.
        Only keeps: a-z, A-Z, 0-9, underscore
        """
        df = df.copy()
        new_columns = []
        
        for i, col in enumerate(df.columns):
            col_str = str(col).strip()
            
            # Remove ALL special characters
            col_clean = re.sub(r'[^a-zA-Z0-9_]', '', col_str)
            col_clean = col_clean.lower()
            
            # Handle empty names
            if not col_clean:
                col_clean = f'column_{i}'
            
            new_columns.append(col_clean)
        
        # Fix duplicates
        seen = {}
        final_columns = []
        for col in new_columns:
            if col in seen:
                seen[col] += 1
                final_columns.append(f'{col}_{seen[col]}')
            else:
                seen[col] = 0
                final_columns.append(col)
        
        df.columns = final_columns
        return df

    @staticmethod
    def clean_data_types(df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert all columns to PyArrow-safe types.
        - Numeric columns -> float64
        - Everything else -> string
        """
        df = df.copy()
        
        for col in df.columns:
            try:
                # Try numeric conversion
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                # If >30% converted, keep as numeric
                if numeric_col.notna().sum() / len(df) > 0.3:
                    df[col] = numeric_col.fillna(0)  # Fill NaN with 0 for numeric
                    continue
            except:
                pass
            
            # Convert to string (safest type)
            try:
                df[col] = df[col].astype(str)
            except:
                df[col] = ''
        
        return df

    @staticmethod
    def remove_problematic_rows(df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows that are all empty or mostly empty"""
        df = df.copy()
        # Keep rows with at least 1 non-empty value
        df = df.dropna(how='all')
        return df

    @staticmethod
    def detect_header_row(df: pd.DataFrame) -> int:
        """Find the row most likely to be headers"""
        if len(df) == 0:
            return 0
        
        max_non_null = 0
        header_row = 0
        
        for i in range(min(10, len(df))):
            non_null_count = df.iloc[i].notnull().sum()
            if non_null_count > max_non_null:
                max_non_null = non_null_count
                header_row = i
        
        return header_row if max_non_null > 0 else 0

    @staticmethod
    def clean_data(df: pd.DataFrame) -> tuple:
        """
        Main cleaning function - produces ALWAYS PyArrow-safe dataframes.
        Returns: (cleaned_df, report_dict)
        """
        try:
            report = {}
            
            if df is None or df.empty:
                logger.warning("Empty dataframe provided")
                return pd.DataFrame(), {'error': 'Empty dataframe', 'original_shape': (0, 0)}
            
            report['original_shape'] = df.shape
            df = df.copy()

            # STEP 1: Remove completely empty columns
            df = df.dropna(axis=1, how='all')
            
            # STEP 2: Detect and use header row
            header_row = DataCleaner.detect_header_row(df)
            if header_row > 0 and header_row < len(df):
                df.columns = [str(x).strip() if pd.notna(x) else f'col_{i}' 
                              for i, x in enumerate(df.iloc[header_row])]
                df = df.iloc[header_row + 1:]
            
            # STEP 3: Remove completely empty rows
            df = DataCleaner.remove_problematic_rows(df)
            
            # STEP 4: Clean column names AGGRESSIVELY
            df = DataCleaner.clean_column_names(df)
            
            # STEP 5: Clean data types to PyArrow-safe types
            df = DataCleaner.clean_data_types(df)
            
            # STEP 6: Reset index
            df = df.reset_index(drop=True)
            
            # STEP 7: Verify PyArrow compatibility
            if not DataCleaner.is_pyarrow_safe(df):
                logger.warning("Final dataframe not PyArrow-safe, attempting final fix...")
                # Last resort: convert everything to string
                df = df.astype(str)
            
            # Report
            report['final_shape'] = df.shape
            report['rows_removed'] = report['original_shape'][0] - df.shape[0]
            report['columns_removed'] = report['original_shape'][1] - df.shape[1]
            report['status'] = 'SUCCESS'
            
            logger.info(f"Data cleaning complete: {report['original_shape']} -> {report['final_shape']}")
            
            return df, report

        except Exception as e:
            logger.error(f"Critical cleaning error: {str(e)}", exc_info=True)
            # Return empty but safe dataframe
            return pd.DataFrame(), {'error': str(e), 'status': 'FAILED'}