"""
Script RPA - Automação de Lançamentos Financeiros
Sistema: Domínio Contabilidade Fiscal (RemoteApp)
Desenvolvido por: Especialista RPA
"""

import time
import logging
from typing import List, Dict, Tuple
from datetime import datetime
import sys

# Bibliotecas para manipulação de Excel
import openpyxl
# import pandas as pd  # Alternativa ao openpyxl

# Biblioteca para automação Web
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Biblioteca para automação de aplicativo Desktop
from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError as PywinautoTimeoutError


# ==================== CONFIGURAÇÕES ====================

class Config:
    """Configurações centralizadas do script"""
    
    # Arquivos
    EXCEL_FILE = "Controle_Apropriacoes_UTI_X.xlsx"
    EXCEL_SHEET = "Planilha1"
    EXCEL_START_ROW = 7
    EXCEL_COL_PERIODO = "B"
    EXCEL_COL_APROPRIACAO = "C"
    
    # Credenciais Web
    WEB_URL = "https://ts-plusx1.kblcontabilidade.com.br"
    WEB_USERNAME = "seu_usuario_web"
    WEB_PASSWORD = "sua_senha_web"
    
    # Credenciais Domínio
    DOMINIO_USERNAME = "KAUE MARTINS"
    DOMINIO_PASSWORD = "sua_senha_dominio"
    DOMINIO_CONNECTION = "Contábil"
    
    # Contas Contábeis
    CONTA_DEBITO = "1.1.1.1.00001 - BANCO DO BRASIL"
    CONTA_CREDITO = "BANCO ITAU S.A."
    
    # Histórico Padrão
    HISTORICO_PADRAO = "Apropriação referente ao período"
    
    # Timeouts (em segundos)
    TIMEOUT_WEB = 30
    TIMEOUT_APP = 20
    TIMEOUT_CURTO = 5
    
    # Delays
    DELAY_ENTRE_LANCAMENTOS = 2
    DELAY_PADRAO = 1


# ==================== CONFIGURAÇÃO DE LOGGING ====================

def configurar_logging():
    """Configura o sistema de logging"""
    log_filename = f"rpa_dominio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


# ==================== MÓDULO 1: LEITURA DE EXCEL ====================

class ExcelReader:
    """Classe para manipulação de arquivos Excel"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def ler_dados_planilha(self, arquivo: str, aba: str, linha_inicial: int) -> List[Dict]:
        """
        Lê os dados da planilha Excel
        
        Args:
            arquivo: Nome do arquivo Excel
            aba: Nome da aba
            linha_inicial: Linha inicial para leitura
            
        Returns:
            Lista de dicionários com os dados
        """
        try:
            self.logger.info(f"Abrindo arquivo Excel: {arquivo}")
            workbook = openpyxl.load_workbook(arquivo, data_only=True)
            sheet = workbook[aba]
            
            dados = []
            linha_atual = linha_inicial
            
            # Itera sobre as linhas até encontrar uma linha vazia
            while True:
                periodo = sheet[f'{Config.EXCEL_COL_PERIODO}{linha_atual}'].value
                apropriacao = sheet[f'{Config.EXCEL_COL_APROPRIACAO}{linha_atual}'].value
                
                # Se ambos os valores estão vazios, para a leitura
                if not periodo and not apropriacao:
                    break
                
                # Valida se os dados são válidos
                if periodo and apropriacao:
                    dados.append({
                        'periodo': str(periodo).strip(),
                        'apropriacao': float(apropriacao) if isinstance(apropriacao, (int, float)) else apropriacao,
                        'linha': linha_atual
                    })
                    self.logger.info(f"Linha {linha_atual}: Período={periodo}, Apropriação={apropriacao}")
                
                linha_atual += 1
            
            workbook.close()
            self.logger.info(f"Total de {len(dados)} registros lidos com sucesso")
            return dados
            
        except FileNotFoundError:
            self.logger.error(f"Arquivo não encontrado: {arquivo}")
            raise
        except Exception as e:
            self.logger.error(f"Erro ao ler planilha: {str(e)}")
            raise


# ==================== MÓDULO 2: AUTOMAÇÃO WEB ====================

class WebAutomation:
    """Classe para automação da interface web"""
    
    def __init__(self, logger):
        self.logger = logger
        self.driver = None
    
    def iniciar_navegador(self):
        """Inicializa o navegador Chrome"""
        try:
            self.logger.info("Iniciando navegador Chrome")
            
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            # chrome_options.add_argument("--headless")  # Descomente para modo headless
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(Config.TIMEOUT_CURTO)
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar navegador: {str(e)}")
            raise
    
    def fazer_login_web(self, url: str, username: str, password: str) -> bool:
        """
        Realiza o login na interface web
        
        Args:
            url: URL do sistema
            username: Nome de usuário
            password: Senha
            
        Returns:
            True se login bem-sucedido
        """
        try:
            self.logger.info(f"Navegando para: {url}")
            self.driver.get(url)
            
            wait = WebDriverWait(self.driver, Config.TIMEOUT_WEB)
            
            # Aguarda e preenche o campo de usuário
            self.logger.info("Preenchendo credenciais")
            campo_usuario = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            campo_usuario.clear()
            campo_usuario.send_keys(username)
            
            # Preenche senha
            campo_senha = self.driver.find_element(By.ID, "password")
            campo_senha.clear()
            campo_senha.send_keys(password)
            
            # Seleciona HTML5 (se necessário)
            try:
                radio_html5 = self.driver.find_element(By.ID, "html5")
                if not radio_html5.is_selected():
                    radio_html5.click()
                    self.logger.info("Opção HTML5 selecionada")
            except NoSuchElementException:
                self.logger.warning("Radio button HTML5 não encontrado")
            
            # Clica no botão Entrar
            botao_entrar = self.driver.find_element(By.ID, "submit")
            botao_entrar.click()
            self.logger.info("Login web realizado com sucesso")
            
            # Aguarda um pouco para o RemoteApp iniciar
            time.sleep(Config.DELAY_PADRAO * 2)
            
            return True
            
        except TimeoutException:
            self.logger.error("Timeout ao tentar fazer login web")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao fazer login web: {str(e)}")
            return False
    
    def fechar_navegador(self):
        """Fecha o navegador"""
        if self.driver:
            try:
                self.logger.info("Fechando navegador")
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Erro ao fechar navegador: {str(e)}")


# ==================== MÓDULO 3: AUTOMAÇÃO DESKTOP ====================

class DominioAutomation:
    """Classe para automação do aplicativo Domínio"""
    
    def __init__(self, logger):
        self.logger = logger
        self.app = None
        self.janela_principal = None
    
    def aguardar_janela(self, titulo: str, timeout: int = Config.TIMEOUT_APP):
        """
        Aguarda uma janela específica aparecer
        
        Args:
            titulo: Título da janela (pode ser parcial)
            timeout: Tempo máximo de espera
            
        Returns:
            Objeto da janela encontrada
        """
        try:
            self.logger.info(f"Aguardando janela: {titulo}")
            
            inicio = time.time()
            while time.time() - inicio < timeout:
                try:
                    desktop = Desktop(backend="uia")
                    janela = desktop.window(title_re=f".*{titulo}.*")
                    
                    if janela.exists():
                        janela.wait('visible', timeout=5)
                        self.logger.info(f"Janela '{titulo}' encontrada")
                        return janela
                        
                except ElementNotFoundError:
                    pass
                
                time.sleep(0.5)
            
            raise TimeoutError(f"Janela '{titulo}' não encontrada em {timeout}s")
            
        except Exception as e:
            self.logger.error(f"Erro ao aguardar janela '{titulo}': {str(e)}")
            raise
    
    def fazer_login_dominio(self, username: str, password: str, conexao: str) -> bool:
        """
        Realiza login no aplicativo Domínio
        
        Args:
            username: Nome de usuário
            password: Senha
            conexao: Nome da conexão (ex: "Contábil")
            
        Returns:
            True se login bem-sucedido
        """
        try:
            self.logger.info("Iniciando login no Domínio Control")
            
            # Aguarda janela de conexão
            janela_conectando = self.aguardar_janela("Conectando", timeout=30)
            
            # Preenche campos
            self.logger.info("Preenchendo credenciais do Domínio")
            
            # Campo usuário
            campo_usuario = janela_conectando.child_window(auto_id="txtUsuario", control_type="Edit")
            campo_usuario.set_focus()
            campo_usuario.set_edit_text(username)
            
            # Campo senha
            campo_senha = janela_conectando.child_window(auto_id="txtSenha", control_type="Edit")
            campo_senha.set_focus()
            campo_senha.set_edit_text(password)
            
            # Dropdown de conexão
            combo_conexao = janela_conectando.child_window(auto_id="cboConexao", control_type="ComboBox")
            combo_conexao.select(conexao)
            
            # Botão OK
            botao_ok = janela_conectando.child_window(title="OK", control_type="Button")
            botao_ok.click()
            
            self.logger.info("Login no Domínio enviado")
            time.sleep(Config.DELAY_PADRAO * 2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer login no Domínio: {str(e)}")
            return False
    
    def conectar_aplicativo_principal(self):
        """Conecta ao aplicativo principal do Domínio"""
        try:
            self.logger.info("Conectando ao Domínio Contabilidade Fiscal")
            
            # Aguarda janela principal
            self.janela_principal = self.aguardar_janela("Domínio Contabilidade Fiscal", timeout=40)
            
            # Fecha possível popup de aviso
            self.fechar_popup_aviso()
            
            self.logger.info("Conectado ao aplicativo principal")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar aplicativo principal: {str(e)}")
            return False
    
    def fechar_popup_aviso(self):
        """Fecha popup de aviso se existir"""
        try:
            janela_aviso = Desktop(backend="uia").window(title_re=".*Aviso.*")
            if janela_aviso.exists(timeout=3):
                self.logger.info("Fechando popup de aviso")
                botao_ok = janela_aviso.child_window(title="OK", control_type="Button")
                botao_ok.click()
                time.sleep(0.5)
        except:
            pass  # Popup não existe, continua normalmente
    
    def acessar_consulta_lancamentos(self):
        """Acessa o menu Movimentos > Consulta e Lançamentos"""
        try:
            self.logger.info("Acessando Consulta e Lançamentos")
            
            # Clica no menu Movimentos
            menu_movimentos = self.janela_principal.child_window(title="Movimentos", control_type="MenuItem")
            menu_movimentos.click_input()
            time.sleep(0.5)
            
            # Clica em Consulta e Lançamentos
            submenu_consulta = self.janela_principal.child_window(
                title="Consulta e Lançamentos", 
                control_type="MenuItem"
            )
            submenu_consulta.click_input()
            
            time.sleep(Config.DELAY_PADRAO)
            self.logger.info("Tela de Consulta e Lançamentos aberta")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao acessar Consulta e Lançamentos: {str(e)}")
            return False
    
    def criar_novo_lancamento(self, periodo: str, apropriacao: float, 
                             conta_debito: str, conta_credito: str, 
                             historico: str) -> bool:
        """
        Cria um novo lançamento financeiro
        
        Args:
            periodo: Data do lançamento
            apropriacao: Valor da apropriação
            conta_debito: Conta de débito
            conta_credito: Conta de crédito
            historico: Histórico do lançamento
            
        Returns:
            True se lançamento criado com sucesso
        """
        try:
            self.logger.info(f"Criando lançamento - Período: {periodo}, Valor: {apropriacao}")
            
            # Clica no botão Novo
            janela_lancamentos = Desktop(backend="uia").window(title_re=".*Consulta.*Lançamentos.*")
            botao_novo = janela_lancamentos.child_window(title="Novo", control_type="Button")
            botao_novo.click()
            time.sleep(Config.DELAY_PADRAO)
            
            # Aguarda janela de lançamento
            janela_lancamento = self.aguardar_janela("Lançamento", timeout=10)
            
            # Preenche Data
            campo_data = janela_lancamento.child_window(auto_id="txtData", control_type="Edit")
            campo_data.set_focus()
            campo_data.set_edit_text(periodo)
            
            # Seleciona tipo: Um débito para um crédito
            combo_tipo = janela_lancamento.child_window(auto_id="cboTipo", control_type="ComboBox")
            combo_tipo.select("Um débito para um crédito")
            
            # Preenche Valor
            campo_valor = janela_lancamento.child_window(auto_id="txtValor", control_type="Edit")
            campo_valor.set_focus()
            campo_valor.set_edit_text(str(apropriacao))
            
            # Seleciona conta de Débito
            self.selecionar_conta(janela_lancamento, "Débito", conta_debito)
            
            # Seleciona conta de Crédito
            self.selecionar_conta(janela_lancamento, "Crédito", conta_credito)
            
            # Preenche Histórico
            campo_historico = janela_lancamento.child_window(auto_id="txtHistorico", control_type="Edit")
            campo_historico.set_focus()
            campo_historico.set_edit_text(historico)
            
            # Clica em Gravar
            botao_gravar = janela_lancamento.child_window(title="Gravar", control_type="Button")
            botao_gravar.click()
            
            time.sleep(Config.DELAY_ENTRE_LANCAMENTOS)
            self.logger.info("Lançamento gravado com sucesso")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao criar lançamento: {str(e)}")
            return False
    
    def selecionar_conta(self, janela_lancamento, tipo_campo: str, conta: str):
        """
        Seleciona uma conta (débito ou crédito) usando F2
        
        Args:
            janela_lancamento: Janela de lançamento
            tipo_campo: "Débito" ou "Crédito"
            conta: Nome da conta a ser selecionada
        """
        try:
            self.logger.info(f"Selecionando conta de {tipo_campo}: {conta}")
            
            # Foca no campo
            campo = janela_lancamento.child_window(
                auto_id=f"txt{tipo_campo}", 
                control_type="Edit"
            )
            campo.set_focus()
            
            # Pressiona F2 para abrir janela de contas
            campo.type_keys("{F2}")
            time.sleep(Config.DELAY_PADRAO)
            
            # Aguarda janela de Contas
            janela_contas = self.aguardar_janela("Contas", timeout=10)
            
            # Busca a conta na lista ou campo de pesquisa
            campo_pesquisa = janela_contas.child_window(auto_id="txtPesquisa", control_type="Edit")
            campo_pesquisa.set_focus()
            campo_pesquisa.set_edit_text(conta)
            time.sleep(0.5)
            
            # Pressiona Enter ou clica em OK
            campo_pesquisa.type_keys("{ENTER}")
            time.sleep(0.5)
            
            self.logger.info(f"Conta de {tipo_campo} selecionada")
            
        except Exception as e:
            self.logger.error(f"Erro ao selecionar conta de {tipo_campo}: {str(e)}")
            raise
    
    def fechar_aplicativo(self):
        """Fecha o aplicativo Domínio"""
        try:
            if self.janela_principal:
                self.logger.info("Fechando aplicativo Domínio")
                self.janela_principal.close()
                time.sleep(1)
        except Exception as e:
            self.logger.error(f"Erro ao fechar aplicativo: {str(e)}")


# ==================== MÓDULO PRINCIPAL ====================

class RPADominioFinanceiro:
    """Classe principal que orquestra todo o processo RPA"""
    
    def __init__(self):
        self.logger = configurar_logging()
        self.excel_reader = ExcelReader(self.logger)
        self.web_automation = WebAutomation(self.logger)
        self.dominio_automation = DominioAutomation(self.logger)
        
        self.dados_lancamentos = []
        self.lancamentos_realizados = 0
        self.lancamentos_com_erro = 0
    
    def executar(self):
        """Executa o processo completo de automação"""
        try:
            self.logger.info("="*60)
            self.logger.info("INICIANDO PROCESSO RPA - DOMÍNIO CONTABILIDADE")
            self.logger.info("="*60)
            
            # Etapa 1: Ler dados do Excel
            self.logger.info("\n[ETAPA 1/6] Leitura de dados do Excel")
            self.dados_lancamentos = self.excel_reader.ler_dados_planilha(
                Config.EXCEL_FILE,
                Config.EXCEL_SHEET,
                Config.EXCEL_START_ROW
            )
            
            if not self.dados_lancamentos:
                self.logger.warning("Nenhum dado encontrado na planilha. Processo encerrado.")
                return
            
            # Etapa 2: Login Web
            self.logger.info("\n[ETAPA 2/6] Login na interface web")
            self.web_automation.iniciar_navegador()
            
            if not self.web_automation.fazer_login_web(
                Config.WEB_URL,
                Config.WEB_USERNAME,
                Config.WEB_PASSWORD
            ):
                raise Exception("Falha no login web")
            
            # Etapa 3: Login Domínio
            self.logger.info("\n[ETAPA 3/6] Login no Domínio Control")
            if not self.dominio_automation.fazer_login_dominio(
                Config.DOMINIO_USERNAME,
                Config.DOMINIO_PASSWORD,
                Config.DOMINIO_CONNECTION
            ):
                raise Exception("Falha no login do Domínio")
            
            # Etapa 4: Conectar ao aplicativo principal
            self.logger.info("\n[ETAPA 4/6] Conectando ao aplicativo principal")
            if not self.dominio_automation.conectar_aplicativo_principal():
                raise Exception("Falha ao conectar ao aplicativo principal")
            
            # Etapa 5: Acessar Consulta e Lançamentos
            self.logger.info("\n[ETAPA 5/6] Acessando Consulta e Lançamentos")
            if not self.dominio_automation.acessar_consulta_lancamentos():
                raise Exception("Falha ao acessar Consulta e Lançamentos")
            
            # Etapa 6: Loop de lançamentos
            self.logger.info("\n[ETAPA 6/6] Processando lançamentos")
            self.processar_lancamentos()
            
            # Finalização
            self.logger.info("\n" + "="*60)
            self.logger.info("PROCESSO CONCLUÍDO COM SUCESSO")
            self.logger.info(f"Total de lançamentos realizados: {self.lancamentos_realizados}")
            self.logger.info(f"Total de lançamentos com erro: {self.lancamentos_com_erro}")
            self.logger.info("="*60)
            
        except Exception as e:
            self.logger.error(f"\n{'='*60}")
            self.logger.error(f"ERRO CRÍTICO NO PROCESSO: {str(e)}")
            self.logger.error(f"{'='*60}")
            raise
            
        finally:
            self.finalizar()
    
    def processar_lancamentos(self):
        """Processa todos os lançamentos da lista"""
        total = len(self.dados_lancamentos)
        
        for indice, lancamento in enumerate(self.dados_lancamentos, 1):
            try:
                self.logger.info(f"\n--- Processando lançamento {indice}/{total} ---")
                
                sucesso = self.dominio_automation.criar_novo_lancamento(
                    periodo=lancamento['periodo'],
                    apropriacao=lancamento['apropriacao'],
                    conta_debito=Config.CONTA_DEBITO,
                    conta_credito=Config.CONTA_CREDITO,
                    historico=Config.HISTORICO_PADRAO
                )
                
                if sucesso:
                    self.lancamentos_realizados += 1
                else:
                    self.lancamentos_com_erro += 1
                    self.logger.warning(f"Lançamento {indice} não foi processado corretamente")
                
            except Exception as e:
                self.lancamentos_com_erro += 1
                self.logger.error(f"Erro ao processar lançamento {indice}: {str(e)}")
                
                # Decide se continua ou para
                if self.lancamentos_com_erro >= 3:
                    self.logger.error("Muitos erros consecutivos. Interrompendo processo.")
                    break
    
    def finalizar(self):
        """Finaliza recursos e fecha aplicações"""
        self.logger.info("\nFinalizando recursos...")
        
        try:
            self.dominio_automation.fechar_aplicativo()
        except Exception as e:
            self.logger.error(f"Erro ao fechar Domínio: {str(e)}")
        
        try:
            self.web_automation.fechar_navegador()
        except Exception as e:
            self.logger.error(f"Erro ao fechar navegador: {str(e)}")


# ==================== EXECUÇÃO ====================

if __name__ == "__main__":
    try:
        # Cria instância do RPA
        rpa = RPADominioFinanceiro()
        
        # Executa o processo
        rpa.executar()
        
    except KeyboardInterrupt:
        print("\n\nProcesso interrompido pelo usuário.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\nErro fatal: {str(e)}")
        sys.exit(1)