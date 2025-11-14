import pandas as pd
import unidecode
from typing import List, Dict, Optional

from .logger import log

COLUMN_ALIASES = {
    "cod_debito": ["debito", "debitar", "conta debito", "classificacao debito", "classificacao"],
    "desc_debito": ["descricao debito", "desc debito", "hist debito"],
    "cod_credito": ["credito", "creditar", "conta credito", "classificacao credito"],
    "desc_credito": ["descricao credito", "desc credito", "hist credito"],
    "valor": ["valor", "vlr", "total"],
    "historico": ["historico", "descricao", "descr"],
    "data": ["data", "dt"],
}
# Create a flat list of all possible alias names for detection
KNOWN_ALIASES = [alias for sublist in COLUMN_ALIASES.values() for alias in sublist]

def _normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = unidecode.unidecode(text).lower()
    return " ".join(text.split())

def _find_header_row(df_preview: pd.DataFrame, known_aliases: List[str]) -> Optional[int]:
    """Analyzes the first ~20 rows of a DataFrame to find the best candidate for a header row."""
    best_match_count = 0
    header_row_index = None

    for i, row in df_preview.head(20).iterrows():
        match_count = 0
        for cell in row:
            normalized_cell = _normalize_text(str(cell))
            if normalized_cell in known_aliases:
                match_count += 1

        # A good header should have at least a few matches
        if match_count > best_match_count and match_count > 2:
            best_match_count = match_count
            header_row_index = i

    if header_row_index is not None:
        log.info(f"Automatically detected header row at index {header_row_index} with {best_match_count} column matches.")
    else:
        log.warning("Could not automatically detect a suitable header row. Defaulting to the first row.")

    return header_row_index

def _map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renames DataFrame columns based on the alias map."""
    rename_map = {}
    normalized_columns = {col: _normalize_text(str(col)) for col in df.columns}

    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            for original_col, normalized_col in normalized_columns.items():
                if alias == normalized_col:
                    if standard_name not in rename_map.values():
                        rename_map[original_col] = standard_name
                        break
            if standard_name in rename_map.values():
                break

    df_renamed = df.rename(columns=rename_map)
    log.info(f"Columns renamed to: {list(df_renamed.columns)}")
    return df_renamed

def load_and_process_excel_files(file_paths: List[str]) -> pd.DataFrame:
    """
    Loads data from Excel files, automatically detects the header row,
    and processes the data.
    """
    all_data = []
    for file_path in file_paths:
        try:
            log.info(f"Processing file: {file_path}")

            # 1. Read the first 20 rows without a header to find the real header
            df_preview = pd.read_excel(file_path, engine='openpyxl', header=None, nrows=20)
            header_row = _find_header_row(df_preview, KNOWN_ALIASES)

            # 2. Read the full file using the detected header row (or default to 0)
            df = pd.read_excel(file_path, engine='openpyxl', dtype=str, header=header_row or 0)

            df = df.dropna(how='all').fillna("")
            df_processed = _map_columns(df)

            all_data.append(df_processed)

        except FileNotFoundError:
            log.error(f"Excel file not found at path: {file_path}")
        except Exception as e:
            log.error(f"An error occurred while reading '{file_path}': {e}", exc_info=True)

    if not all_data:
        log.warning("No data was loaded from the Excel files.")
        return pd.DataFrame()

    combined_df = pd.concat(all_data, ignore_index=True)
    log.info(f"Successfully loaded and combined {len(combined_df)} rows.")

    required_cols = ["cod_debito", "cod_credito", "valor"]
    for col in required_cols:
        if col not in combined_df.columns:
            log.error(f"Critical Column Missing: The final DataFrame does not have a '{col}' column.")
            raise ValueError(f"A coluna padrão '{col}' não foi encontrada após a detecção automática.")

    return combined_df
