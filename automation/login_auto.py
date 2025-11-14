import os
import subprocess
import time
import pyautogui
from typing import Dict, Any

from .logger import log
from .utils import (
    click_on_image,
    wait_for_window,
    safe_type,
    handle_errors_and_screenshot,
    wait_for_screen_to_vanish
)

# --- Image Constants ---
IMG_LOGIN_KBL_FORM = "login_kbl_web.png"
IMG_LOGIN_KBL_ENTRAR_BTN = "login_kbl_entrar_btn.png"
IMG_REMOTEAPP_LAUNCH_ICON = "remoteapp_launch_icon.png"
IMG_REMOTEAPP_POPUP = "login_remoteapp_popup.png"
IMG_REMOTEAPP_PASS_FIELD = "remoteapp_pass_field.png"
IMG_REMOTEAPP_OK_BTN = "remoteapp_ok_btn.png"
IMG_DOMINIO_ICON = "icon_dominio_desktop.png"

# --- State Handlers ---

@handle_errors_and_screenshot
def handle_start_state(config: Dict[str, Any]):
    """Action for when no known state is found. Tries to open the browser."""
    log.info("Unknown state detected. Attempting to start the process by opening the browser.")
    browser_path = config.get("browser_path")
    url = config.get("login_url")

    # This check is important to prevent re-opening the browser if it's just slow to load
    if not wait_for_window(IMG_LOGIN_KBL_FORM, config, timeout=3):
        log.info(f"Opening browser at: {browser_path}")
        subprocess.Popen([browser_path, '--start-maximized', url])
    else:
        log.info("Browser already open and on the login page.")

    wait_for_window(IMG_LOGIN_KBL_FORM, config, timeout=20)

@handle_errors_and_screenshot
def handle_web_login_state(config: Dict[str, Any]):
    """Handler for the KBL web login screen."""
    log.info("Handling web login state...")
    user = os.getenv("DOMINIO_USER")
    password = os.getenv("DOMINIO_PASS")
    if not user or not password:
        raise ValueError("Environment variables DOMINIO_USER and DOMINIO_PASS must be set.")

    click_on_image(IMG_LOGIN_KBL_FORM, config)
    time.sleep(0.5)

    safe_type(user)
    pyautogui.press('tab')
    safe_type(password)

    click_on_image(IMG_LOGIN_KBL_ENTRAR_BTN, config)

    # Confirmation Step: Wait for the login form to disappear
    if not wait_for_screen_to_vanish(IMG_LOGIN_KBL_FORM, config, timeout=15):
        raise Exception("Clicked 'Entrar' button, but login screen did not disappear.")
    log.info("Web login successful, screen has changed.")

@handle_errors_and_screenshot
def handle_launch_remoteapp_state(config: Dict[str, Any]):
    """Handler for the screen where the RemoteApp launch icon is visible."""
    log.info("Handling RemoteApp launch state...")
    click_on_image(IMG_REMOTEAPP_LAUNCH_ICON, config)

    # Confirmation Step: Wait for the launch icon to disappear
    if not wait_for_screen_to_vanish(IMG_REMOTEAPP_LAUNCH_ICON, config, timeout=15):
        raise Exception("Clicked RemoteApp launch icon, but the screen did not change.")
    log.info("RemoteApp launch successful.")

@handle_errors_and_screenshot
def handle_remoteapp_login_state(config: Dict[str, Any]):
    """Handler for the RemoteApp credentials popup."""
    log.info("Handling RemoteApp login popup state...")
    rdp_pass = os.getenv("RDP_PASS")
    if not rdp_pass:
        raise ValueError("Environment variable RDP_PASS must be set.")

    click_on_image(IMG_REMOTEAPP_PASS_FIELD, config)
    safe_type(rdp_pass)
    click_on_image(IMG_REMOTEAPP_OK_BTN, config)

    # Confirmation Step: Wait for the popup to disappear
    if not wait_for_screen_to_vanish(IMG_REMOTEAPP_POPUP, config, timeout=20):
        raise Exception("Submitted RDP password, but the popup did not disappear.")
    log.info("RemoteApp login successful.")

@handle_errors_and_screenshot
def handle_remote_desktop_state(config: Dict[str, Any]):
    """Handler for when the remote desktop is visible."""
    log.info("Handling remote desktop state...")
    time.sleep(2) # Allow desktop to stabilize
    click_on_image(IMG_DOMINIO_ICON, config, clicks=2, confidence=0.9)

    # Confirmation Step: Wait for the icon to "disappear" (or for the main menu to appear)
    # A better confirmation is to wait for the next state's image.
    log.info("Domínio application started.")
