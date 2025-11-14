import json
from typing import Dict, Any
from pathlib import Path

# Importar todos os módulos da automação com imports relativos
from .logger import setup_logger
from . import login # Import the new login module
from . import excel_reader
from . import dominio
from . import lancamento

# Define o diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.json"

# Configura o logger
log = setup_logger(log_dir=(BASE_DIR / "logs"))

def load_config(filepath: Path) -> Dict[str, Any]:
    """Loads the JSON configuration file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            log.info(f"Loading configuration from {filepath}")
            return json.load(f)
    except FileNotFoundError:
        log.error(f"Configuration file not found: {filepath}")
        raise
    except json.JSONDecodeError:
        log.error(f"Error decoding JSON from the configuration file: {filepath}")
        raise

def main():
    """
    Main function to orchestrate the entire accounting automation process.
    """
    log.info("=============================================")
    log.info("=== INICIANDO AUTOMAÇÃO DE LANÇAMENTOS CONTÁBEIS ===")
    log.info("=============================================")

    dados_lancamentos = None # Initialize to ensure it's available in 'finally'
    sucessos, falhas = 0, 0

    try:
        # 1. Carregar Configuração
        config = load_config(CONFIG_FILE)
        config["base_dir"] = BASE_DIR

        # 2. Executar Fluxo de Login
        log.info("STEP 1: EXECUTING LOGIN FLOW...")
        login.execute_full_login_flow(config)
        log.info("Login flow completed. Proceeding to data processing.")

        # 3. Ler e Processar Planilhas Excel
        log.info("STEP 2: READING AND PROCESSING EXCEL FILES...")
        planilhas = [config.get("planilha1"), config.get("planilha2")]
        planilhas_paths = [BASE_DIR / p for p in planilhas if p]

        if not planilhas_paths:
            log.critical("No Excel files specified in config.json. Aborting.")
            return

        dados_lancamentos = excel_reader.load_and_process_excel_files(planilhas_paths)

        if dados_lancamentos.empty:
            log.warning("No data found in Excel files. Finishing process.")
            return

        # 4. Navegar até a Tela de Lançamentos no Sistema Domínio
        log.info("STEP 3: NAVIGATING TO ACCOUNTING ENTRIES SCREEN...")
        if not dominio.navigate_to_lancamentos_screen(config):
            log.critical("Failed to navigate to the entries screen. Aborting.")
            return

        # 5. Iterar e Realizar Lançamentos
        log.info("STEP 4: STARTING DATA ENTRY PROCESS...")
        total = len(dados_lancamentos)
        log.info(f"Found {total} entries to process.")

        for index, row in dados_lancamentos.iterrows():
            log.info(f"--- Processing Entry {index + 1} of {total} ---")
            try:
                lancamento.preencher_lancamento(row.to_dict(), config)
                log.info(f"Entry {index + 1} (Ref: {row.get('historico', 'N/A')}) completed successfully.")
                sucessos += 1
            except Exception as e:
                log.error(f"Failed to process entry {index + 1}. Error: {e}", exc_info=True)
                log.error(f"Data for failed entry: {row.to_dict()}")
                falhas += 1

    except Exception as e:
        log.critical(f"A fatal and unexpected error occurred in the main orchestration: {e}", exc_info=True)

    finally:
        log.info("============================================")
        log.info("========= AUTOMATION FINISHED =========")
        if dados_lancamentos is not None:
            log.info(f"Total Entries Planned: {len(dados_lancamentos)}")
            log.info(f"  -> Successes: {sucessos}")
            log.info(f"  -> Failures:  {falhas}")
        else:
            log.info("No data was loaded to process.")
        log.info("============================================")
