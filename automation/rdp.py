import subprocess
import time
from typing import Optional

from .logger import log
from .utils import find_image_on_screen, handle_errors_and_screenshot

@handle_errors_and_screenshot
def connect_rdp(rdp_filepath: str, rdp_window_identifier_image: Optional[str] = None) -> bool:
    """
    Connects to a Remote Desktop session using a .rdp file.

    Args:
        rdp_filepath: The full path to the .rdp configuration file.
        rdp_window_identifier_image: Optional path to an image that confirms the RDP window is open and active.

    Returns:
        True if the connection process was initiated successfully, False otherwise.
    """
    log.info(f"Attempting to open RDP connection using file: {rdp_filepath}")
    try:
        # Using mstsc.exe is the standard way to open RDP sessions on Windows.
        subprocess.Popen(["mstsc.exe", rdp_filepath])

        # If an identifier image is provided, wait for the window to appear.
        if rdp_window_identifier_image:
            log.info("Waiting for RDP window to become active...")
            if find_image_on_screen(rdp_window_identifier_image, timeout=30):
                log.info("RDP window is active.")
                time.sleep(2) # Give it a moment to stabilize
            else:
                log.error("RDP window did not appear after timeout.")
                return False
        else:
            # If no image is provided, just wait a fixed amount of time.
            log.info("Waiting 10 seconds for RDP connection to establish...")
            time.sleep(10)

        log.info("RDP connection initiated.")
        return True

    except FileNotFoundError:
        log.error("`mstsc.exe` not found. Ensure you are running on a Windows machine.")
        return False
    except Exception as e:
        log.error(f"An unexpected error occurred while trying to connect via RDP: {e}")
        return False

# Example usage (would be called from main.py)
if __name__ == '__main__':
    # This assumes you have a `my_session.rdp` file in the project root
    # and an image `rdp_desktop.png` in the `imagens` folder.
    # The image should be a unique part of the remote desktop's background.
    # For this example, we'll assume these files don't exist and expect it to fail gracefully.

    # Create dummy files for demonstration if they don't exist
    from pathlib import Path
    if not Path("my_session.rdp").exists():
        Path("my_session.rdp").touch()

    # In a real run, this image must exist.
    # if not Path("imagens/rdp_desktop.png").exists():
    #     print("Please create a sample 'imagens/rdp_desktop.png' for the test to run.")

    # connect_rdp("my_session.rdp", "imagens/rdp_desktop.png")
    log.info("RDP module script finished. This is an example run.")
