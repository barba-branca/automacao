from typing import Dict, Any
import pyautogui
import time

from .logger import log
from .utils import click_on_image, safe_type, handle_errors_and_screenshot, wait_for_window
from . import plano_contas_selector as pcs

# --- Image Constants ---
# Using the main screen image as an anchor to start filling the form.
TELA_GERAL_LANCAMENTOS = "tela_geral_lancamentos.png"

# These still ideally need specific images, but we will rely on keyboard navigation.
# You should capture images for BOTAO_LANCAR and BOTAO_NOVO for robustness.
BOTAO_LANCAR = "botao_lancar.png" # User needs to provide this
BOTAO_NOVO = "botao_novo.png"   # User needs to provide this

def _selecionar_conta(cod_conta: str, desc_conta: str, config: Dict[str, Any]) -> bool:
    """Handles the full process of selecting an account (debit or credit)."""
    if not pcs.abrir_selector(config):
        return False

    log.info(f"Attempt 1: Searching for account by code '{cod_conta}'.")
    pcs.buscar_conta(cod_conta, "código", config)
    if pcs.selecionar_primeiro_resultado(config):
        log.info("Account selected successfully by code.")
        return True

    log.warning(f"Could not select account by code '{cod_conta}'. Trying by description.")

    search_desc = (desc_conta[:25] if len(desc_conta) > 25 else desc_conta)
    log.info(f"Attempt 2: Searching by description '{search_desc}'.")
    pcs.buscar_conta(search_desc, "descrição", config)
    if pcs.selecionar_primeiro_resultado(config):
        log.info("Account selected successfully by description.")
        return True

    log.error(f"Failed to select account for Code: {cod_conta}, Desc: {desc_conta}.")
    pyautogui.press('esc') # Try to close the selector to not block the screen
    return False

@handle_errors_and_screenshot
def preencher_lancamento(lancamento_data: Dict[str, Any], config: Dict[str, Any]):
    """
    Fills out a single accounting entry using keyboard navigation primarily.
    This function assumes the entry screen is fresh and the cursor is at the first field.
    """
    timeout = config.get("timeout", 20)

    # Ensure the main entry screen is visible before we begin
    if not wait_for_window(TELA_GERAL_LANCAMENTOS, config, timeout=5):
        raise Exception("Main entry screen not visible. Cannot fill form.")

    # The flow relies on a consistent TAB order from the first field.
    # We assume the cursor is already in the first field (Débito).

    # 1. Select Debit Account
    log.info(f"Selecting Debit account: {lancamento_data['cod_debito']}")
    if not _selecionar_conta(
        lancamento_data['cod_debito'], lancamento_data.get('desc_debito', ''), config
    ):
        raise Exception("Could not select the Debit account.")
    pyautogui.press('enter') # Confirm selection
    time.sleep(0.5)

    # 2. Select Credit Account
    log.info(f"Selecting Credit account: {lancamento_data['cod_credito']}")
    if not _selecionar_conta(
        lancamento_data['cod_credito'], lancamento_data.get('desc_credito', ''), config
    ):
        raise Exception("Could not select the Credit account.")
    pyautogui.press('enter')
    time.sleep(0.5)

    # 3. Fill Value
    log.info(f"Filling value: {lancamento_data['valor']}")
    safe_type(str(lancamento_data['valor']))
    pyautogui.press('tab')

    # 4. Fill Date
    log.info(f"Filling date: {lancamento_data['data']}")
    safe_type(str(lancamento_data['data']))
    pyautogui.press('tab')

    # 5. Fill History
    log.info(f"Filling history: {lancamento_data['historico']}")
    safe_type(str(lancamento_data['historico']))

    # 6. Click "Lançar" (Save)
    log.info("Clicking the 'Lançar' (Save) button.")
    click_on_image(BOTAO_LANCAR, config, timeout=timeout)
    time.sleep(1) # Wait for processing

    # 7. Click "Novo" to prepare for the next entry
    log.info("Clicking the 'Novo' (New) button to clear the form.")
    click_on_image(BOTAO_NOVO, config, timeout=timeout)
    time.sleep(0.5)

    log.info("Entry completed successfully.")
