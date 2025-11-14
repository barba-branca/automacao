import pyautogui
import cv2
import numpy as np
import time
import functools
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

from .logger import log

def get_screenshot_dir(config: Dict[str, Any]) -> Path:
    """Gets the screenshot directory from the config."""
    base_dir = config.get("base_dir", Path("."))
    screenshot_dir = base_dir / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)
    return screenshot_dir

def handle_errors_and_screenshot(func):
    """
    A decorator that wraps a function in a try-except block.
    If an exception occurs, it takes a screenshot and re-raises the exception.
    It intelligently finds the 'config' object from the decorated function's arguments.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Find the config object in the arguments to determine where to save screenshots
            config = kwargs.get('config')
            if not config:
                # Find config in positional args if not in kwargs
                for arg in args:
                    if isinstance(arg, dict) and 'base_dir' in arg:
                        config = arg
                        break

            if config:
                screenshot_dir = get_screenshot_dir(config)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                screenshot_path = screenshot_dir / f"error_{func.__name__}_{timestamp}.png"
                pyautogui.screenshot(str(screenshot_path))
                log.error(
                    f"An error occurred in '{func.__name__}': {e}. "
                    f"Screenshot saved to: {screenshot_path}"
                )
            else:
                log.error(f"An error occurred in '{func.__name__}': {e}. No config object found to save screenshot.")

            raise
    return wrapper

def _get_full_image_path(image_name: str, config: Dict[str, Any]) -> str:
    """Constructs the full, absolute path to an image."""
    base_dir = config.get("base_dir", Path("."))
    return str(base_dir / "imagens" / image_name)


@handle_errors_and_screenshot
def find_image_on_screen(
    image_name: str,
    config: Dict[str, Any],
    timeout: int = 10,
    confidence: float = 0.8
) -> Optional[Tuple[int, int, int, int]]:
    """
    Finds an image on the screen and returns its coordinates.
    The image path is now relative to the 'imagens' folder.
    """
    full_path = _get_full_image_path(image_name, config)
    log.debug(f"Searching for image: {full_path} with timeout={timeout}s")
    start_time = time.time()
    template = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise FileNotFoundError(f"Image template not found at {full_path}")
    w, h = template.shape[::-1]

    while time.time() - start_time < timeout:
        screenshot_pil = pyautogui.screenshot()
        screenshot_cv = cv2.cvtColor(np.array(screenshot_pil), cv2.COLOR_RGB2GRAY)
        result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= confidence:
            log.info(f"Image '{image_name}' found at {max_loc} with confidence {max_val:.2f}")
            return (max_loc[0], max_loc[1], w, h)
        time.sleep(0.5)

    log.warning(f"Image '{image_name}' not found on screen after {timeout} seconds.")
    return None

@handle_errors_and_screenshot
def click_on_image(
    image_name: str,
    config: Dict[str, Any],
    timeout: int = 10,
    confidence: float = 0.8,
    button: str = 'left',
    clicks: int = 1
):
    """Finds an image by its relative name and clicks on it."""
    location = find_image_on_screen(image_name, config, timeout, confidence)
    if location:
        center_x = location[0] + location[2] // 2
        center_y = location[1] + location[3] // 2
        log.info(f"Clicking on '{image_name}' at ({center_x}, {center_y})")
        pyautogui.click(center_x, center_y, button=button, clicks=clicks)
        time.sleep(0.3)
    else:
        raise Exception(f"Could not click on '{image_name}' as it was not found.")

@handle_errors_and_screenshot
def wait_for_window(image_name: str, config: Dict[str, Any], timeout: int = 20) -> bool:
    """Waits for a window identified by a relative image name to appear."""
    log.info(f"Waiting for window identified by '{image_name}' to appear...")
    location = find_image_on_screen(image_name, config, timeout)
    if location:
        log.info("Window found.")
        return True
    log.warning("Wait for window timed out.")
    return False

# Functions that don't depend on config are unchanged
@handle_errors_and_screenshot
def safe_type(text: str, delay: float = 0.05):
    log.debug(f"Typing text: '{text}'")
    for char in str(text):
        pyautogui.write(char)
        time.sleep(delay + np.random.uniform(0, 0.05))

@handle_errors_and_screenshot
def press_hotkey(keys: list):
    log.info(f"Pressing hotkey: {keys}")
    with pyautogui.hold(keys[0]):
        for key in keys[1:]:
            pyautogui.press(key)
    time.sleep(0.5)
