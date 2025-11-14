from typing import Dict, Any, Optional

from .utils import find_image_on_screen
from .logger import log

# --- State Identifier Images ---
# These images are the "key frames" that define each state of the automation.
# The order in which they are checked is important.
STATE_IMAGES = {
    # Login Flow States
"STATE_LOGIN_WEB": "login_kbl_web.png",
    "STATE_LAUNCH_REMOTEAPP": "remoteapp_launch_icon.png",
    "STATE_LOGIN_REMOTEAPP": "login_remoteapp_popup.png",
    "STATE_DESKTOP_REMOTE": "icon_dominio_desktop.png",

    # Domínio Application States
    "STATE_DOMINIO_MAIN_MENU": "menu_dominio.png",
    "STATE_LANCAMENTOS_SCREEN": "tela_geral_lancamentos.png",

    # An idle state can be useful, maybe an image of the empty remote desktop background
    # "STATE_IDLE": "remote_desktop_background.png"
}

def detectar_estado_atual(config: Dict[str, Any]) -> Optional[str]:
    """
    Detects the current state of the UI by searching for a series of key images.

    It checks for images in a predefined order and returns the key of the first
    image found on the screen. This creates a simple but effective state machine.

    Args:
        config: The application's configuration dictionary.

    Returns:
        A string representing the current state (e.g., "STATE_LOGIN_WEB"),
        or None if no known state is detected.
    """
    log.debug("Detecting current application state...")

    # We use a very short timeout here because this function is meant to check
    # the *current* state, not wait for a future state to appear.
    short_timeout = 1

    for state, image_name in STATE_IMAGES.items():
        # Using a slightly lower confidence to handle minor rendering variations.
        location = find_image_on_screen(
            image_name, config, timeout=short_timeout, confidence=0.8
        )
        if location:
            log.info(f"State detected: {state} (found image '{image_name}')")
            return state

    log.warning("Could not determine the current state. No known images found on screen.")
    return None
