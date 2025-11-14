import time
from typing import Dict, Any, Iterator, Callable

from .logger import setup_logger
from .state_detector import detectar_estado_atual
from . import login_auto
from . import excel_reader
from . import dominio
from . import lancamento
from pathlib import Path

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
log = setup_logger(log_dir=(BASE_DIR / "logs"))

def load_config(filepath: Path) -> Dict[str, Any]:
    """Loads and returns the JSON configuration."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return Path(f.read()).read_text()


def get_lancamento_iterator(config: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
    """Loads data from Excel and returns an iterator over the rows."""
    planilhas = [config.get("planilha1"), config.get("planilha2")]
    paths = [BASE_DIR / p for p in planilhas if p]
    if not paths:
        return iter([])
    df = excel_reader.load_and_process_excel_files(paths)
    return (row.to_dict() for _, row in df.iterrows())

def main():
    """
    Main function to orchestrate the automation using a robust state-handler model.
    """
    log.info("=============================================")
    log.info("=== INICIANDO AUTOMAÇÃO DE LANÇAMENTOS (STATE-HANDLER MODEL) ===")
    log.info("=============================================")

    try:
        config = load_config(CONFIG_FILE)
        config["base_dir"] = BASE_DIR

        lancamentos_iterator = get_lancamento_iterator(config)
        current_lancamento = next(lancamentos_iterator, None)

        # Map states to their handler functions
        STATE_HANDLERS: Dict[str, Callable[[Dict[str, Any]], None]] = {
            "STATE_LOGIN_WEB": login_auto.handle_web_login_state,
            "STATE_LAUNCH_REMOTEAPP": login_auto.handle_launch_remoteapp_state,
            "STATE_LOGIN_REMOTEAPP": login_auto.handle_remoteapp_login_state,
            "STATE_DESKTOP_REMOTE": login_auto.handle_remote_desktop_state,
            "STATE_DOMINIO_MAIN_MENU": dominio.navigate_to_lancamentos_screen,
        }

        while current_lancamento:
            time.sleep(1) # Prevent high CPU usage
            current_state = detectar_estado_atual(config)

            if current_state is None:
                # If we are in an unknown state, try to recover by starting from the beginning.
                login_auto.handle_start_state(config)
                continue

            if current_state in STATE_HANDLERS:
                handler = STATE_HANDLERS[current_state]
                log.info(f"Executing handler for state: {current_state}")
                handler(config)

            elif current_state == "STATE_LANCAMENTOS_SCREEN":
                log.info(f"--- Processing Entry: {current_lancamento.get('historico', 'N/A')} ---")
                try:
                    lancamento.preencher_lancamento(current_lancamento, config)
                    log.info("Entry processed successfully.")
                    current_lancamento = next(lancamentos_iterator, None) # Get next item
                except Exception as e:
                    log.error(f"Failed to process entry. Skipping. Error: {e}", exc_info=True)
                    current_lancamento = next(lancamentos_iterator, None) # Skip to next

            else:
                log.warning(f"No handler defined for state: {current_state}. Waiting...")
                time.sleep(3)

    except Exception as e:
        log.critical(f"A fatal error occurred in the main controller: {e}", exc_info=True)

    finally:
        log.info("============================================")
        log.info("========= AUTOMATION FINISHED =========")
        log.info("============================================")
