import os
import subprocess
import time
import pyautogui
from typing import Dict, Any

from .logger import log
from .utils import click_on_image, wait_for_window, safe_type, handle_errors_and_screenshot

# --- Constants for Image Templates ---
# The user MUST capture these specific images for the login flow to work.

# KBL Web Login Screen
IMG_LOGIN_KBL_FORM = "login_kbl_web.png"           # The overall form area
IMG_LOGIN_KBL_ENTRAR_BTN = "login_kbl_entrar_btn.png"   # The 'Entrar' button - STILL NEEDED

# Post-Login / RemoteApp Launch Screen
IMG_REMOTEAPP_LAUNCH_ICON = "remoteapp_launch_icon.png" # The icon/button to launch the RDP session

# RemoteApp Credentials Popup
IMG_REMOTEAPP_POPUP = "login_remoteapp_popup.png"          # The popup window itself
IMG_REMOTEAPP_PASS_FIELD = "remoteapp_pass_field.png"     # The password field in the popup
IMG_REMOTEAPP_OK_BTN = "remoteapp_ok_btn.png"             # The 'OK' button in the popup

# Remote Desktop
IMG_DOMINIO_ICON = "icon_dominio_desktop.png" # The Domínio Contábil icon on the remote desktop

@handle_errors_and_screenshot
def open_browser_and_navigate(config: Dict[str, Any]):
    """Opens the browser and navigates to the specified login URL."""
    browser_path = config.get("browser_path")
    url = config.get("login_url")

    log.info(f"Opening browser at: {browser_path}")
    subprocess.Popen([browser_path, '--start-maximized', url])
    log.info(f"Navigating to: {url}")

    if not wait_for_window(IMG_LOGIN_KBL_FORM, config, timeout=20):
        raise Exception("Browser opened, but KBL login page did not load or was not recognized.")
    log.info("Browser is open and login page is ready.")

@handle_errors_and_screenshot
def perform_web_login(config: Dict[str, Any]):
    """Fills the KBL web login form using keyboard navigation and submits."""
    user = os.getenv("DOMINIO_USER")
    password = os.getenv("DOMINIO_PASS")
    if not user or not password:
        raise ValueError("Environment variables DOMINIO_USER and DOMINIO_PASS must be set.")

    log.info("Performing web login using keyboard navigation.")
    # Click the main form to ensure it has focus
    click_on_image(IMG_LOGIN_KBL_FORM, config)
    time.sleep(0.5)

    # Assuming the first action after click is typing in the username field
    log.info("Typing username...")
    safe_type(user)

    pyautogui.press('tab')
    time.sleep(0.3)

    log.info("Typing password...")
    safe_type(password)

    # Click the 'Entrar' button by image
    click_on_image(IMG_LOGIN_KBL_ENTRAR_BTN, config)
    log.info("Web login submitted.")

@handle_errors_and_screenshot
def launch_remoteapp_session(config: Dict[str, Any]):
    """Waits for and clicks the icon to launch the RemoteApp session."""
    log.info("Waiting for RemoteApp launch icon to appear...")
    if not wait_for_window(IMG_REMOTEAPP_LAUNCH_ICON, config, timeout=20):
        raise Exception("RemoteApp launch icon not found after web login.")

    click_on_image(IMG_REMOTEAPP_LAUNCH_ICON, config)
    log.info("RemoteApp session launched.")

@handle_errors_and_screenshot
def perform_remoteapp_login(config: Dict[str, Any]):
    """Waits for the RemoteApp popup and enters the password."""
    rdp_pass = os.getenv("RDP_PASS")
    if not rdp_pass:
        raise ValueError("Environment variable RDP_PASS must be set.")

    log.info("Waiting for RemoteApp credentials popup...")
    if not wait_for_window(IMG_REMOTEAPP_POPUP, config, timeout=30):
        raise Exception("RemoteApp credentials popup did not appear.")

    log.info("Entering RemoteApp password.")
    # This part can also be refactored to use keyboard nav if needed,
    # but an image for the password field is generally more reliable in popups.
    click_on_image(IMG_REMOTEAPP_PASS_FIELD, config)
    safe_type(rdp_pass)

    click_on_image(IMG_REMOTEAPP_OK_BTN, config)
    log.info("RemoteApp login submitted.")

@handle_errors_and_screenshot
def start_dominio_application(config: Dict[str, Any]):
    """Waits for the remote desktop and double-clicks the Domínio icon."""
    log.info("Waiting for remote desktop to load...")
    if not wait_for_window(IMG_DOMINIO_ICON, config, timeout=60):
        raise Exception("Remote desktop did not load or Domínio icon was not found.")

    log.info("Remote desktop is ready. Starting Domínio Contábil...")
    time.sleep(2) # Allow desktop to stabilize
    click_on_image(IMG_DOMINIO_ICON, config, clicks=2, confidence=0.9)
    log.info("Domínio application started.")
