from typing import Dict, Any

from .logger import log
from .utils import click_on_image, wait_for_window, handle_errors_and_screenshot

# Image names are now just the filenames, not full paths.
MENU_CONTABILIDADE = "menu_contabilidade.png"
MENU_MOVIMENTOS = "menu_movimentos.png"
MENU_CONSULTA_MOVIMENTOS = "menu_consulta_movimentos.png"
JANELA_GERAL = "janela_geral.png"

@handle_errors_and_screenshot
def navigate_to_lancamentos_screen(config: Dict[str, Any]) -> bool:
    """
    Navigates through the Domínio Contábil main menu to the accounting entries screen.

    Args:
        config: The application's configuration dictionary.

    Returns:
        True if navigation is successful, False otherwise.
    """
    log.info("Starting navigation to the accounting entries screen.")
    timeout = config.get("timeout", 20)

    try:
        # The 'config' object is now passed to each UI function.
        log.info("Looking for 'Contabilidade' menu.")
        click_on_image(MENU_CONTABILIDADE, config, timeout=timeout)

        log.info("Looking for 'Movimentos' submenu.")
        click_on_image(MENU_MOVIMENTOS, config, timeout=timeout)

        log.info("Looking for 'Consulta / Movimentos' submenu.")
        click_on_image(MENU_CONSULTA_MOVIMENTOS, config, timeout=timeout)

        log.info("Waiting for the 'Geral' (main entries) window.")
        if not wait_for_window(JANELA_GERAL, config, timeout=timeout):
            log.error("The 'Geral' window did not appear as expected.")
            return False

        log.info("Successfully navigated to the accounting entries screen.")
        return True

    except Exception as e:
        log.error(f"Failed to navigate to the accounting entries screen. Error: {e}")
        # The decorator will have already taken a screenshot.
        return False
