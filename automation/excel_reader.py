import pandas as pd
import unidecode
from typing import List, Dict

from .logger import log

def _normalize_text(text: str) -> str:
    """Normalizes a string for comparison."""
    if not isinstance(text, str):
        return ""
    return " ".join(unidecode.unidecode(text).lower().split())

def _map_columns_from_config(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Renames DataFrame columns based on the user-defined mapping in config.json.
    """
    # Create a reverse mapping from the user's column name to our standard name
    # e.g., {"código da conta a debitar": "cod_debito"}
    reverse_mapping = {v: k for k, v in column_mapping.items()}

    # Normalize the keys of the reverse mapping for robust matching
    normalized_reverse_mapping = {_normalize_text(k): v for k, v in reverse_mapping.items()}

    rename_dict = {}
    for col in df.columns:
        normalized_col = _normalize_text(str(col))
        if normalized_col in normalized_reverse_mapping:
            rename_dict[col] = normalized_reverse_mapping[normalized_col]

    df_renamed = df.rename(columns=rename_dict)
    log.info(f"Columns renamed to: {list(df_renamed.columns)}")
    return df_renamed

def load_and_process_excel_files(file_paths: List[str], header_row: int, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Loads data from Excel, using user-defined header row and column mapping.
    """
    all_data = []
    log.info(f"Loading data from {len(file_paths)} Excel file(s), using header on row {header_row}.")

    for file_path in file_paths:
        try:
            log.info(f"Reading file: {file_path}")
            df = pd.read_excel(file_path, engine='openpyxl', dtype=str, header=header_row)

            df = df.dropna(how='all').fillna("")
            df_processed = _map_columns_from_config(df, column_mapping)

            all_data.append(df_processed)

        except FileNotFoundError:
            log.error(f"Excel file not found at path: {file_path}")
        except Exception as e:
            log.error(f"An error occurred while reading '{file_path}': {e}", exc_info=True)

    if not all_data:
        log.warning("No data was loaded from Excel files.")
        return pd.DataFrame()

    combined_df = pd.concat(all_data, ignore_index=True)
    log.info(f"Successfully loaded and combined {len(combined_df)} rows.")

    # Check if all required standard columns are present after renaming
    required_cols = list(column_mapping.keys())
    for col in required_cols:
        if col not in combined_df.columns:
            log.error(f"Critical Column Missing: Standard column '{col}' was not found after mapping.")
            raise ValueError(f"A coluna padrão '{col}' não foi encontrada. Verifique seu 'column_mapping' no config.json.")

    return combined_df
