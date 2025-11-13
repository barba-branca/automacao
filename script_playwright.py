# pip install playwright - instalar biblioteca
# playwright install - instalar navegadores
# playwright codegen <url> - gerar código automatizado

# aprendendo a abrir um navegador

from playwright.sync_api import sync_playwright # importando a biblioteca
import time # importar biblioteca time


with sync_playwright() as pw: # iniciar o playwright
    navegador = pw.chromium.launch(headless= False) # abrir o navegador (headless false = visível)
    pagina = navegador.new_page()  # abrir uma nova aba
    contexto = navegador.new_context() # criar um novo contexto (janela)
    
    # navegar para o site desejado
    pagina.goto('https://ts-plusx1.kblcontabilidade.com.br/') # navegar para o site desejado
    
    print(pagina.title()) # imprimir o título da página
    
    # selecionar o campo de login e preencher com o usuário
    pagina.get_by_role("textbox", name="Nome de Usuário:").fill("kaue.martins") # preencher o campo de usuário
    pagina.get_by_role("textbox", name="Senha:").fill("JXX#c0W4") # preencher o campo de senha
    # pagina.get_by_text("HTML5").click() # clicar no botão HTML5
    pagina.get_by_role("button", name="Entrar").click() # clicar no botão entrar
    
    
    time.sleep(4) # aguardar 4 segundos    
    navegador.close()  # fechar o navegador
