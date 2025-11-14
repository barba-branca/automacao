import pandas as pd
import unidecode
from typing import List, Dict

from .logger import log

# Mapping of possible column names (and their variations) to a standard internal name.
COLUMN_ALIASES = {
    "cod_debito": ["debito", "debitar", "conta debito", "classificacao debito", "classificacao"],
    "desc_debito": ["descricao debito", "desc debito", "hist debito"],
    "cod_credito": ["credito", "creditar", "conta credito", "classificacao credito"],
    "desc_credito": ["descricao credito", "desc credito", "hist credito"],
    "valor": ["valor", "vlr", "total"],
    "historico": ["historico", "descricao", "descr"],
    "data": ["data", "dt"],
}

def _normalize_text(text: str) -> str:
    """
    Normalizes a string by converting to lowercase, removing accents and extra spaces.
    """
    if not isinstance(text, str):
        return ""
    text = unidecode.unidecode(text)  # Remove accents
    text = text.lower()              # Convert to lowercase
    text = " ".join(text.split())    # Remove multiple spaces
    return text

def _map_columns(df: pd.DataFrame, alias_map: Dict[str, List[str]]) -> pd.DataFrame:
    """
    Renames DataFrame columns based on the provided alias map.
    """
    rename_map = {}
    normalized_columns = {col: _normalize_text(col) for col in df.columns}

    for standard_name, aliases in alias_map.items():
        for alias in aliases:
            # Check if the normalized alias is present in the normalized column names
            for original_col, normalized_col in normalized_columns.items():
                if alias == normalized_col:
                    if standard_name not in rename_map.values():
                        rename_map[original_col] = standard_name
                        break # Found a match for this standard_name, move to the next one
            if standard_name in rename_map.values():
                break

    df_renamed = df.rename(columns=rename_map)
    log.info(f"Columns renamed to: {list(df_renamed.columns)}")
    return df_renamed

def load_and_process_excel_files(file_paths: List[str], header_row: int = 0) -> pd.DataFrame:
    """
    Loads data from a list of Excel files, processes and normalizes it.

    Args:
        file_paths: A list of paths to the Excel files.
        header_row: The row number (0-indexed) to use as the column headers.

    Returns:
        A single pandas DataFrame containing the combined and processed data.
    """
    all_data = []
    log.info(f"Loading data from {len(file_paths)} Excel file(s), using header row {header_row}.")

    for file_path in file_paths:
        try:
            log.info(f"Reading file: {file_path}")
            # Read all columns as string type and specify the header row
            df = pd.read_excel(file_path, engine='openpyxl', dtype=str, header=header_row)

            # Clean up the dataframe
            df = df.dropna(how='all') # Remove rows that are completely empty
            df = df.fillna("") # Replace remaining NaN with empty strings

            # Normalize and map columns
            df_processed = _map_columns(df, COLUMN_ALIASES)

            all_data.append(df_processed)

        except FileNotFoundError:
            log.error(f"Excel file not found at path: {file_path}")
        except Exception as e:
            log.error(f"An error occurred while reading '{file_path}': {e}")

    if not all_data:
        log.warning("No data was loaded from the Excel files.")
        return pd.DataFrame()

    # Combine all dataframes into one
    combined_df = pd.concat(all_data, ignore_index=True)
    log.info(f"Successfully loaded and combined {len(combined_df)} rows from all files.")

    # Final check for required columns
    required_cols = ["cod_debito", "cod_credito", "valor", "historico", "data"]
    for col in required_cols:
        if col not in combined_df.columns:
            log.error(f"Critical Column Missing: The final DataFrame does not have a '{col}' column.")
            # Depending on requirements, we could raise an error or return an empty df
            raise ValueError(f"A coluna padrão '{col}' não foi encontrada após o processamento.")

    return combined_df

if __name__ == '__main__':
    # Create dummy excel files for testing
    data1 = {
        "Data": ["01/11/2025"],
        "DEBITAR": ["1.1.1.02.0002"],
        "Descrição Débito": ["CAIXA ECONOMICA FEDERAL"],
        "Creditar": ["2.2.1.07.00001"],
        "Descrição Crédito": ["BANCO FINASA S/A"],
        "Valor": ["1500.75"],
        "Histórico": ["Pagamento de fornecedor A"]
    }
    data2 = {
        "data": ["02/11/2025"],
        "conta_debito": ["01.1.5.01"], # Leading zero for test
        "desc debito": ["Mercadorias para Revenda"],
        "conta_credito": ["1.1.3.08.00014"],
        "desc credito": ["COFINS a Recuperar"],
        "vlr": ["99.90"],
        "descr": ["Compra de mercadorias B"]
    }

    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)

    dummy_file1 = "test1.xlsx"
    dummy_file2 = "test2.xlsx"

    df1.to_excel(dummy_file1, index=False)
    df2.to_excel(dummy_file2, index=False)

    log.info("--- Running excel_reader.py example ---")
    processed_data = load_and_process_excel_files([dummy_file1, dummy_file2])

    print("\nProcessed DataFrame Head:")
    print(processed_data.head())
    print("\nProcessed DataFrame Info:")
    processed_data.info()
