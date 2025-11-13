import pyautogui
import time

pyautogui.position()  # Obtenha a posição atual do mouse
time.sleep(5)  # Aguarde 5 segundos para o usuário posicionar o mouse
pos = pyautogui.position()
print(f'A posição do mouse é: {pos}')