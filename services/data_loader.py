import pandas as pd
import os
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DataLoader:
    
    @staticmethod
    def load_file(file, sheet_name=0):
        """
        Load CSV, Excel, or JSON file with validation
        Works with ANY dataset format
        
        Args:
            file: Streamlit UploadedFile object
            sheet_name: For Excel files, which sheet to load (0-indexed or sheet name string)
        
        Returns:
            Tuple of (dataframe, file_extension)
        
        Raises:
            Exception: If file format unsupported, too large, or empty
        """
        try:
            file_name = file.name
            file_extension = os.path.splitext(file_name)[1].lower()
            file_size_bytes = file.size if hasattr(file, 'size') else 0
            
            # ========== VALIDATION ==========
            
            # Check file extension
            allowed_ext = [f'.{ext}' for ext in Config.ALLOWED_EXTENSIONS]
            if file_extension not in allowed_ext:
                raise ValueError(
                    f"Unsupported file format: {file_extension}. "
                    f"Allowed: {', '.join(allowed_ext)}"
                )
            
            # Check file size
            if not Config.validate_file_size(file_size_bytes):
                raise ValueError(
                    f"File too large: {file_size_bytes / 1024 / 1024:.2f}MB. "
                    f"Maximum allowed: {Config.MAX_FILE_SIZE_MB}MB"
                )
            
            logger.info(f"Loading file: {file_name} ({file_size_bytes / 1024:.2f}KB)")
            
            # ========== LOAD FILE WITH ENCODING FALLBACKS ==========
            
            df = None
            
            if file_extension == ".csv":
                # Try multiple encodings for CSV
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except Exception as e:
                        file.seek(0)  # Reset file pointer
                        continue
                
                if df is None:
                    df = pd.read_csv(file)  # Try default
            
            elif file_extension in [".xls", ".xlsx"]:
                # Handle Excel files - read first sheet by default
                try:
                    df = pd.read_excel(file, sheet_name=sheet_name)
                except Exception as e:
                    logger.warning(f"Error reading Excel sheet {sheet_name}: {e}")
                    raise ValueError(f"Error reading Excel sheet: {str(e)}")
            
            elif file_extension == ".json":
                # Handle JSON files - both object and array formats
                try:
                    df = pd.read_json(file)
                except Exception as e:
                    file.seek(0)
                    try:
                        df = pd.read_json(file, lines=True)  # Try newline-delimited JSON
                    except:
                        raise ValueError(f"Error reading JSON file: {str(e)}")
            
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # ========== POST-LOAD VALIDATION ==========
            
            # Check if dataframe is empty
            if df is None or df.empty:
                raise ValueError("Uploaded file is empty or contains no data")
            
            # Remove completely empty rows/columns
            df = df.dropna(how='all')
            df = df.dropna(axis=1, how='all')
            
            if df.empty:
                raise ValueError("File contains only empty rows/columns")
            
            # Check row count limits
            if len(df) > Config.MAX_ROWS_FOR_FULL_ANALYSIS:
                logger.warning(
                    f"Large dataset detected: {len(df)} rows. "
                    f"Performance may be affected. Consider using a subset."
                )
            
            logger.info(
                f"File loaded successfully: {len(df)} rows, {len(df.columns)} columns, "
                f"types: {dict(df.dtypes)}"
            )
            
            return df, file_extension.lstrip('.')
        
        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)