import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- ETAPA 1: LER A PLANILHA (Igual e Corrigido) ---
try:
    df = pd.read_excel(r'c:\Users\kauen\Downloads\Controle_Apropriacao_UTI_Movel.xlsx', sheet_name='Planilha1', skiprows=5) 
    
    print("DEBUG: Colunas encontradas pelo Pandas:")
    print(df.columns)
    
    df = df.dropna(subset=['Período', 'Apropriação']) 

    # CORREÇÃO DA DATA: Converter número do Excel para data
    df['Período'] = pd.to_datetime(df['Período'], unit='D', origin='1899-12-30')
    
    print("Dados carregados da planilha:")
    print(df[['Período', 'Apropriação', 'Saldo']])
    
except Exception as e:
    print(f"Erro ao ler a planilha: {e}")
    exit()

# --- ETAPA 2: LOGIN NO PORTAL WEB (Igual e Corrigido) ---
driver = None
try:
    driver = webdriver.Chrome()
    driver.get("https://ts-plusx1.kblcontabilidade.com.br")
    # Aumentei o tempo de espera para 20s, o app HTML5 pode ser pesado
    wait = WebDriverWait(driver, 20) 

    # Preencher usuário e senha do portal
    wait.until(EC.presence_of_element_located((By.ID, "Editbox1"))).send_keys("kaue.martins")
    wait.until(EC.presence_of_element_located((By.ID, "Editbox2"))).send_keys("JXX#c0W4")

    # Clicar em "HTML5" (Correto!)
    wait.until(EC.element_to_be_clickable((By.ID, "HTML5"))).click()
    time.sleep(2)  # Aguardar a página carregar após clicar em HTML5
    
    # Clicar em Entrar
    print("Procurando o botão 'Entrar'...")
    # Tentar ID primeiro, se falhar, usar XPath com texto
    try:
        entrar_button = wait.until(EC.element_to_be_clickable((By.ID, "buttonLogOn")))
    except:
        print("ID 'buttonLogOn' não encontrado, tentando XPath...")
        entrar_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Entrar')] | //input[@value='Entrar'] | //a[contains(text(),'Entrar')]")))
    print("Botão 'Entrar' encontrado. Clicando...")
    entrar_button.click()
    print("Clique no botão 'Entrar' realizado.")

    # Aguardar a nova página carregar após o login
    time.sleep(5)  # Aumentar se necessário
    print("Aguardando nova página carregar...")

    # Na nova página, clicar no botão "domínios contábil"
    print("Procurando o botão 'domínios contábil'...")
    dominios_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "domínios contábil")))  # Ajustar seletor se necessário
    print("Botão 'domínios contábil' encontrado. Clicando...")
    dominios_button.click()
    print("Clique no botão 'domínios contábil' realizado.")

    # Aguardar a página de login do domínios carregar
    time.sleep(3)
    print("Aguardando página de login do domínios...")

    # Preencher login novamente (ajustar IDs se necessário)
    wait.until(EC.presence_of_element_located((By.ID, "usuario"))).send_keys("kaue.martins")  # Ajustar ID
    wait.until(EC.presence_of_element_located((By.ID, "senha"))).send_keys("JXX#c0W4")  # Ajustar ID
    wait.until(EC.element_to_be_clickable((By.ID, "entrar_dominios"))).click()  # Ajustar ID

    print("Login no domínios realizado. Aguardando app carregar...")

except Exception as e:
    print(f"Erro no login com Selenium!")
    print(f"Tipo de Erro: {type(e).__name__}")
    print(f"Mensagem: {e}")
    if driver:
        driver.quit()
    exit()

# --- ETAPA 3: AUTOMATIZAR O APP HTML5 (O Novo Código) ---
# TODO O CÓDIGO PYAUTOGUI FOI REMOVIDO DAQUI
try:
    # 1. ESPERAR E MUDAR PARA O IFRAME DO APLICATIVO
    # O app Domínio (a tela cinza) VAI carregar dentro de um <iframe>.
    # Você precisa 'Inspecionar' a tela cinza para achar o ID ou NOME do iframe.
    print("Aguardando o <iframe> do aplicativo principal...")
    
    # Exemplo - Substitua 'id_do_iframe_do_app' pelo ID real que você encontrar
    # wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "id_do_iframe_do_app")))
    # print("Mudei o foco para o <iframe> do app. Procurando menus...")

    # 2. NAVEGAR PELOS MENUS (AGORA COM SELENIUM)
    # Você terá que Inspecionar os menus "Movimentos", "Lançamentos", etc.
    # Assim como fez na tela de login.
    
    # Exemplo (você PRECISA achar os seletores reais):
    print("Vá para o navegador, 'Inspecione' os botões 'Movimentos', 'Lançamentos', etc., e pegue os IDs")
    # wait.until(EC.element_to_be_clickable((By.ID, "id_real_menu_movimentos"))).click()
    # time.sleep(1)
    # wait.until(EC.element_to_be_clickable((By.ID, "id_real_menu_lancamentos"))).click()
    # ...

    print("Janela de Lançamentos aberta. Iniciando cadastro...")

    # 3. FAZER O LOOP DE CADASTRO (AGORA COM SELENIUM)
    for index, row in df.iterrows():
        try:
            periodo = row['Período'].strftime('%d%m%Y')
            # CORREÇÃO: Usar 'Apropriação' com 'A' maiúsculo
            valor = str(row['Apropriação']).replace('.', ',')
            
            print(f"Cadastrando: {periodo} - R$ {valor}")
            
            # Você precisa Inspecionar e pegar os IDs dos campos DENTRO do app
            
            # Exemplo (você PRECISA achar os seletores reais):
            # wait.until(EC.element_to_be_clickable((By.ID, "id_real_botao_novo"))).click()
            # time.sleep(1)
            # wait.until(EC.presence_of_element_located((By.ID, "id_real_campo_data"))).send_keys(periodo)
            # wait.until(EC.presence_of_element_located((By.ID, "id_real_campo_debito"))).send_keys("0.1.1.1.02.00001")
            # wait.until(EC.presence_of_element_located((By.ID, "id_real_campo_credito"))).send_keys("2.2.2.1.01.0001")
            # wait.until(EC.presence_of_element_located((By.ID, "id_real_campo_valor"))).send_keys(valor)
            # wait.until(EC.presence_of_element_located((By.ID, "id_real_campo_historico"))).send_keys("17A")
            # wait.until(EC.element_to_be_clickable((By.ID, "id_real_botao_gravar"))).click()
            # time.sleep(2)
            
            # ATENÇÃO: O código acima é um EXEMPLO. Você precisa substituir pelos IDs reais.
            print(f"Pulei cadastro da linha {index} (implementação pendente)")
            pass # Remova o 'pass' quando implementar o código acima

        except Exception as e:
            print(f"Erro ao cadastrar linha {index}: {e}")
            break
            
    print("Automação concluída.")

except Exception as e:
    print(f"Erro ao tentar automatizar o app HTML5 (iframe?): {e}")
    if driver:
        driver.quit()
    exit()

# Mantenha o navegador aberto no final para ver o resultado
# driver.quit()
print("Script finalizado. Verifique o navegador.")
