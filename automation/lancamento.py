from typing import Dict, Any

from .logger import log
from .utils import click_on_image, safe_type, handle_errors_and_screenshot
from . import plano_contas_selector as pcs

# Image names are now just the filenames.
CAMPO_DEBITO = "campo_debito.png"
CAMPO_CREDITO = "campo_credito.png"
CAMPO_VALOR = "campo_valor.png"
CAMPO_DATA = "campo_data.png"
CAMPO_HISTORICO = "campo_historico.png"
BOTAO_LANCAR = "botao_lancar.png"
BOTAO_NOVO = "botao_novo.png"

def _selecionar_conta(cod_conta: str, desc_conta: str, config: Dict[str, Any]) -> bool:
    """
    Handles the full process of selecting an account (debit or credit).
    Tries by code first, then by description as a fallback.
    """
    if not pcs.abrir_selector(config):
        return False

    # Try searching by exact code first
    log.info(f"Attempt 1: Searching for account by code '{cod_conta}'.")
    pcs.buscar_conta(cod_conta, "código", config)
    if pcs.selecionar_primeiro_resultado(config):
        log.info("Account selected successfully by code.")
        return True

    log.warning(f"Could not select account by code '{cod_conta}'. Search may have yielded no results. Trying by description.")

    # Fallback: search by description
    search_desc = (desc_conta[:25] if len(desc_conta) > 25 else desc_conta)
    log.info(f"Attempt 2: Searching for account by description '{search_desc}'.")
    pcs.buscar_conta(search_desc, "descrição", config)
    if pcs.selecionar_primeiro_resultado(config):
        log.info("Account selected successfully by description.")
        return True

    log.error(f"Failed to select account for Code: {cod_conta}, Desc: {desc_conta}.")
    # A robust implementation would press 'ESC' here to close the selector and retry.
    # For now, we'll let the error propagate up.
    return False

@handle_errors_and_screenshot
def preencher_lancamento(lancamento_data: Dict[str, Any], config: Dict[str, Any]):
    """
    Fills out a single accounting entry on the Domínio screen.
    """
    timeout = config.get("timeout", 20)

    # 1. Select Debit Account
    log.info(f"Selecting Debit account: {lancamento_data['cod_debito']}")
    click_on_image(CAMPO_DEBITO, config, timeout=timeout)
    if not _selecionar_conta(
        lancamento_data['cod_debito'],
        lancamento_data.get('desc_debito', ''),
        config
    ):
        raise Exception("Could not select the Debit account.")

    # 2. Select Credit Account
    log.info(f"Selecting Credit account: {lancamento_data['cod_credito']}")
    click_on_image(CAMPO_CREDITO, config, timeout=timeout)
    if not _selecionar_conta(
        lancamento_data['cod_credito'],
        lancamento_data.get('desc_credito', ''),
        config
    ):
        raise Exception("Could not select the Credit account.")

    # 3. Fill Value
    log.info(f"Filling value: {lancamento_data['valor']}")
    click_on_image(CAMPO_VALOR, config, timeout=timeout)
    safe_type(str(lancamento_data['valor']))

    # 4. Fill Date
    log.info(f"Filling date: {lancamento_data['data']}")
    click_on_image(CAMPO_DATA, config, timeout=timeout)
    safe_type(str(lancamento_data['data']))

    # 5. Fill History
    log.info(f"Filling history: {lancamento_data['historico']}")
    click_on_image(CAMPO_HISTORICO, config, timeout=timeout)
    safe_type(str(lancamento_data['historico']))

    # 6. Click "Lançar" (Save)
    log.info("Clicking the 'Lançar' (Save) button.")
    click_on_image(BOTAO_LANCAR, config, timeout=timeout)

    # 7. Click "Novo" to prepare for the next entry
    log.info("Clicking the 'Novo' (New) button to clear the form.")
    click_on_image(BOTAO_NOVO, config, timeout=timeout)

    log.info("Entry completed successfully.")
