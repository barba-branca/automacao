from typing import Dict, Any

from .logger import log
from .utils import (
    press_hotkey,
    wait_for_window,
    safe_type,
    click_on_image,
    handle_errors_and_screenshot
)

# Image names are now just the filenames.
JANELA_PLANO_CONTAS = "janela_plano_contas.png"
CAMPO_PESQUISA = "campo_pesquisa_plano_contas.png"
BOTAO_PESQUISAR = "botao_pesquisar_plano_contas.png"
PRIMEIRO_RESULTADO = "primeiro_resultado_plano_contas.png"
BOTAO_SELECIONAR = "botao_selecionar_plano_contas.png"

@handle_errors_and_screenshot
def abrir_selector(config: Dict[str, Any]) -> bool:
    """
    Opens the account plan selector window using the hotkey from the config.
    """
    timeout = config.get("timeout", 15)
    atalhos = config.get("atalhos", {}).get("plano_contas", ["fn", "f2"])

    log.info(f"Attempting to open the account plan selector with hotkey: {atalhos}.")
    press_hotkey(atalhos)
    if wait_for_window(JANELA_PLANO_CONTAS, config, timeout=timeout):
        log.info("Account plan selector window is open.")
        return True
    else:
        log.error("Failed to open the account plan selector window.")
        return False

@handle_errors_and_screenshot
def buscar_conta(texto_busca: str, tipo_busca: str, config: Dict[str, Any]) -> bool:
    """
    Searches for an account within the selector window by code or description.
    """
    timeout = config.get("timeout", 10)
    log.info(f"Searching for account by {tipo_busca}: '{texto_busca}'")

    click_on_image(CAMPO_PESQUISA, config, timeout=timeout)
    safe_type(texto_busca)
    click_on_image(BOTAO_PESQUISAR, config, timeout=timeout)

    log.info("Search command executed.")
    return True

@handle_errors_and_screenshot
def selecionar_primeiro_resultado(config: Dict[str, Any]) -> bool:
    """
    Selects the first result in the search list and confirms the selection.
    """
    timeout = config.get("timeout", 10)
    log.info("Attempting to select the first search result.")

    try:
        click_on_image(PRIMEIRO_RESULTADO, config, timeout=timeout, clicks=2)
        log.info("Successfully selected the first result by double-clicking.")
        return True
    except Exception:
        log.warning("Double-click failed. Trying fallback: single-click + 'Selecionar' button.")
        try:
            click_on_image(PRIMEIRO_RESULTADO, config, timeout=5)
            click_on_image(BOTAO_SELECIONAR, config, timeout=5)
            log.info("Fallback selection method successful.")
            return True
        except Exception as fallback_e:
            log.error(f"Fallback selection method also failed: {fallback_e}")
            return False
