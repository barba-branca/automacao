from typing import Dict, Any

from .logger import log
from .utils import click_on_image, wait_for_window, handle_errors_and_screenshot

# Updated image names based on the user's provided files
MENU_DOMINIO = "menu_dominio.png"
MENU_CONTABILIDADE = "menu_contabilidade.png"
MENU_MOVIMENTOS = "menu_movimentos.png"
MENU_CONSULTA_LANCAMENTOS = "menu_consulta_lancamentos.png"
TELA_GERAL_LANCAMENTOS = "tela_geral_lancamentos.png"

@handle_errors_and_screenshot
def navigate_to_lancamentos_screen(config: Dict[str, Any]) -> bool:
    """
    Navigates through the Domínio Contábil main menu to the accounting entries screen.
    This function assumes the main Domínio window is already open and active.
    """
    log.info("Navigating through Domínio menus to the accounting entries screen.")
    timeout = config.get("timeout", 20)

    try:
        # Step 1: Click on "Domínio" menu
        log.info("Looking for 'Domínio' main menu button.")
        click_on_image(MENU_DOMINIO, config, timeout=timeout)

        # Step 2: Click on "Contabilidade" submenu
        log.info("Looking for 'Contabilidade' submenu.")
        click_on_image(MENU_CONTABILIDADE, config, timeout=timeout)

        # Step 3: Click on "Movimentos" submenu
        log.info("Looking for 'Movimentos' submenu.")
        click_on_image(MENU_MOVIMENTOS, config, timeout=timeout)

        # Step 4: Click on "Consulta e Lançamentos"
        log.info("Looking for 'Consulta e Lançamentos' submenu.")
        click_on_image(MENU_CONSULTA_LANCAMENTOS, config, timeout=timeout)

        # Step 5: Wait for the main entries window to appear
        log.info("Waiting for the main entries window.")
        if not wait_for_window(TELA_GERAL_LANCAMENTOS, config, timeout=timeout):
            log.error(f"The entries window ('{TELA_GERAL_LANCAMENTOS}') did not appear as expected.")
            return False

        log.info("Successfully navigated to the accounting entries screen.")
        return True

    except Exception as e:
        log.error(f"Failed to navigate to the accounting entries screen. Error: {e}")
        return False
