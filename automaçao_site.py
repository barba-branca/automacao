import pyautogui
import time
import webbrowser

pyautogui.PAUSE = 1  # Pausa de 1 segundo entre as ações

# Função para fazer login no sistema
webbrowser.open('https://ts-plusx1.kblcontabilidade.com.br/')  # Abra o site do formulário
pyautogui.moveTo(x=982, y=452)  # Mova o mouse para o campo de login
time.sleep(3)   # Aguarde 2 segundos para o site carregar
pyautogui.click(x=982, y=452)  # Clique no campo de login
pyautogui.write('kaue.martins')  # Digite o login
pyautogui.press('tab')  # Pressione a tecla Tab para ir para o campo de senha
pyautogui.write('JXX#c0W4')  # Digite a senha
pyautogui.moveTo(x=995, y=569)  # Mova o mouse para o botão de login
pyautogui.click(x=995, y=569)  # Clique no botão

# Entrar no sistema

# pyautogui.moveTo(x=1294, y=531) # afasta o mouse para o anti-bot nao perceber
# time.sleep(5)  # Aguarde 5 segundos para o sistema carregar
# pyautogui.moveTo(x=761, y=548)  # Mova o mouse para o botão de entrar no sistema
# pyautogui.click(x=761, y=548)  # Clique no botão de entrar no sistema
# pyautogui.moveTo(x=761, y=548)  # Mova o mouse para o botão de entrar no sistema
# pyautogui.click(x=761, y=548)  # Clique no botão de entrar no sistema
# pyautogui.moveTo(x=1718, y=1018)
# pyautogui.write('JXX#c0W4')  # Digite a senha novamente se necessário
# pyautogui.press('enter')  # Pressione Enter para confirmar

# Navegar dentro do sistema
# Aguardar o carregamento da página após o login
# time.sleep(7)
# # Navegar dentro do sistema
# pyautogui.moveTo(x=69, y=151)   # Mova o mouse para o menu domínio
# pyautogui.click(x=69, y=151)   # Clique no menu domínio
# pyautogui.moveTo(x=58, y=379) # Mova o mouse para o submenu contabilidade
# pyautogui.click(x=58, y=379) # Clique no submenu contabilidade

# pyautogui.PAUSE = 0.5 # Pausa de 0.5 segundos entre as ações
# pyautogui.moveTo(x=153, y=458) # Mova o mouse para o submenu movimentos
# pyautogui.click(x=153, y=458) # Clique no submenu movimentos

# pyautogui.PAUSE = 1 # Pausa de 1 segundo entre as ações
# pyautogui.moveTo(x=321, y=145) # Mova o mouse para o botão de movimentos
# pyautogui.click(x=321, y=145) # Clique no botão de movimentos

# pyautogui.PAUSE = 0.5 # Pausa de 0.5 segundos entre as ações
# pyautogui.moveTo(x=355, y=193) # Mova o mouse para o campo de data inicial
# pyautogui.click(x=355, y=193) # Clique no campo de data inicial

# pyautogui.PAUSE = 0.5 # Pausa de 0.5 segundos entre as ações 
# pyautogui.moveTo(x=1164, y=647) # Mova o mouse para a data de hoje no calendário
# pyautogui.click(x=1164, y=647) # Clique na data de hoje no calendário