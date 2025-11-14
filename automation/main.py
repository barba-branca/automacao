import time
import json
from typing import Dict, Any, Iterator
from pathlib import Path

# Importar todos os módulos da automação
from .logger import setup_logger
from .state_detector import detectar_estado_atual
from . import login_auto
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
        log.error(f"Error decoding JSON: {filepath}")
        raise

def get_lancamento_iterator(config: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
    """Loads Excel data and returns an iterator over the rows."""
    planilhas = [config.get("planilha1"), config.get("planilha2")]
    paths = [BASE_DIR / p for p in planilhas if p]
    if not paths:
        log.warning("No Excel files configured.")
        return iter([]) # Return an empty iterator

    df = excel_reader.load_and_process_excel_files(paths)
    return (row.to_dict() for index, row in df.iterrows())

def main():
    """
    Main function to orchestrate the automation using a state machine approach.
    """
    log.info("=============================================")
    log.info("=== INICIANDO AUTOMAÇÃO DE LANÇAMENTOS (STATE-DRIVEN) ===")
    log.info("=============================================")

    try:
        config = load_config(CONFIG_FILE)
        log.info(f"DEBUG: Configuration dictionary loaded: {config}")
        config["base_dir"] = BASE_DIR

        # Open the browser as the very first action. The state machine will handle the rest.
        login_auto.open_browser_and_navigate(config)

        lancamentos_iterator = get_lancamento_iterator(config)
        current_lancamento = next(lancamentos_iterator, None)

        while current_lancamento:
            # Main state-driven loop
            time.sleep(1) # Small delay to prevent CPU spinning
            current_state = detectar_estado_atual(config)

            if current_state is None:
                log.error("Unknown state. Could not find any recognizable UI element. Retrying in 5 seconds...")
                time.sleep(5)
                continue

            # --- State Handling ---
            if current_state == "STATE_LOGIN_WEB":
                login_auto.perform_web_login(config)

            elif current_state == "STATE_LAUNCH_REMOTEAPP":
                login_auto.launch_remoteapp_session(config)

            elif current_state == "STATE_LOGIN_REMOTEAPP":
                login_auto.perform_remoteapp_login(config)

            elif current_state == "STATE_DESKTOP_REMOTE":
                login_auto.start_dominio_application(config)

            elif current_state == "STATE_DOMINIO_MAIN_MENU":
                dominio.navigate_to_lancamentos_screen(config)

            elif current_state == "STATE_LANCAMENTOS_SCREEN":
                log.info(f"--- Processing Entry: {current_lancamento.get('historico', 'N/A')} ---")
                try:
                    lancamento.preencher_lancamento(current_lancamento, config)
                    log.info("Entry processed successfully.")
                    current_lancamento = next(lancamentos_iterator, None) # Move to the next item
                except Exception as e:
                    log.error(f"Failed to process entry. Error: {e}", exc_info=True)
                    # Decide on error handling: skip, retry, or stop. For now, we'll skip.
                    current_lancamento = next(lancamentos_iterator, None)

            else:
                log.warning(f"Unhandled state: {current_state}. Waiting...")
                time.sleep(3)

    except Exception as e:
        log.critical(f"A fatal error occurred in the state machine controller: {e}", exc_info=True)

    finally:
        log.info("============================================")
        log.info("========= AUTOMATION FINISHED =========")
        log.info("============================================")
