from typing import Dict, Any
import pyautogui
import time

from .logger import log
from .utils import click_on_image, wait_for_window, safe_type, handle_errors_and_screenshot

# --- Image Constants ---
# Using the broader images provided by the user.
# We will click on these and then use keyboard navigation (Tab) to reach the fields.
IMG_LOGIN_KBL_SCREEN = "login_kbl_web.png"
IMG_REMOTEAPP_POPUP = "login_remoteapp_popup.png"
IMG_DOMINIO_ICON = "icon_dominio_desktop.png"
IMG_DOMINIO_MAIN_MENU = "menu_dominio.png" # Identifier that Domínio is ready

@handle_errors_and_screenshot
def execute_full_login_flow(config: Dict[str, Any]):
    """
    Orchestrates the entire login process from the KBL web page to the Domínio main menu.
    """
    log.info("Starting the full login flow...")

    creds = config.get("credentials")
    if not creds:
        raise ValueError("Credentials not found in config.json. Cannot proceed with login.")

    # Step 1: KBL Web Login
    if not wait_for_window(IMG_LOGIN_KBL_SCREEN, config, timeout=15):
        raise Exception(f"KBL Web Login screen ('{IMG_LOGIN_KBL_SCREEN}') not found.")

    log.info("KBL Web Login screen detected.")
    _handle_kbl_web_login(config, creds.get("web_user"), creds.get("web_pass"))

    # Step 2: RemoteApp Popup Login
    if not wait_for_window(IMG_REMOTEAPP_POPUP, config, timeout=25):
        raise Exception(f"RemoteApp connection popup ('{IMG_REMOTEAPP_POPUP}') did not appear.")

    log.info("RemoteApp popup detected.")
    _handle_remoteapp_popup(config, creds.get("rdp_pass"))

    # Step 3: Start Domínio from the desktop icon
    if not wait_for_window(IMG_DOMINIO_ICON, config, timeout=40):
        raise Exception(f"Domínio desktop icon ('{IMG_DOMINIO_ICON}') did not appear after login.")

    log.info("Domínio desktop icon detected. Starting application...")
    # Add a small delay for the desktop to stabilize
    time.sleep(2)
    click_on_image(IMG_DOMINIO_ICON, config, clicks=2, confidence=0.9)

    # Step 4: Wait for Domínio to be ready
    if not wait_for_window(IMG_DOMINIO_MAIN_MENU, config, timeout=60):
        raise Exception(f"Domínio main menu ('{IMG_DOMINIO_MAIN_MENU}') did not appear after starting the application.")

    log.info("Login flow completed successfully. Domínio is ready.")


def _handle_kbl_web_login(config: Dict[str, Any], user: str, password: str):
    """
    Handles the fields on the KBL web login page using keyboard navigation.
    NOTE: This assumes a specific tab order on the web page.
    """
    timeout = config.get("timeout")

    log.info("Filling KBL web login form.")
    # Click on a stable part of the form to give it focus
    click_on_image(IMG_LOGIN_KBL_SCREEN, config, timeout=timeout)
    time.sleep(0.5)

    # Assuming the cursor starts in the "Nome de Usuário" field after the click.
    log.info("Typing web username...")
    safe_type(user)

    pyautogui.press('tab')
    time.sleep(0.2)

    log.info("Typing web password...")
    safe_type(password)

    # Tab to the radio buttons. Assuming RemoteApp is the second one.
    pyautogui.press('tab')
    pyautogui.press('right') # Move from HTML5 to RemoteApp
    time.sleep(0.2)

    pyautogui.press('tab') # Move to "Entrar" button
    pyautogui.press('enter')
    log.info("KBL web login submitted.")


def _handle_remoteapp_popup(config: Dict[str, Any], password: str):
    """
    Handles the RemoteApp credential popup using keyboard navigation.
    NOTE: Assumes the user field is pre-filled and correct.
    """
    timeout = config.get("timeout")

    log.info("Filling RemoteApp password.")
    # Click on the popup to give it focus.
    click_on_image(IMG_REMOTEAPP_POPUP, config, timeout=timeout)
    time.sleep(0.5)

    # Assuming the focus starts on the username field, tab to the password field.
    pyautogui.press('tab')
    time.sleep(0.2)

    safe_type(password)

    pyautogui.press('tab') # Tab to OK button
    pyautogui.press('enter')
    log.info("RemoteApp credentials submitted.")
