# Automação de Lançamentos Contábeis para Domínio Contábil (100% Autônoma)

Este projeto contém uma automação completa e robusta, desenvolvida em Python, para realizar lançamentos contábeis no sistema Domínio Contábil (Thomson Reuters). A automação é projetada para ser **100% hands-free**, iniciando o processo desde a abertura do navegador, passando por múltiplos estágios de login, até a inserção dos dados a partir de planilhas Excel.

A arquitetura é baseada em uma **máquina de estados simplificada**, que permite que a automação detecte em qual tela do processo ela se encontra e execute a ação correta, garantindo alta resiliência e capacidade de recuperação.

## Arquitetura

-   `run.py`: Ponto de entrada principal da aplicação.
-   `requirements.txt`: Lista de dependências Python.
-   `config.json`: Arquivo de configuração para parâmetros não-sensíveis (URLs, caminhos, timeouts).
-   `/automation/`: Pacote Python contendo toda a lógica.
    -   `main.py`: Orquestrador principal, implementado como um controlador de estados.
    -   `login_auto.py`: Módulo que gerencia o fluxo de login 100% automático.
    -   `state_detector.py`: Módulo que identifica a tela/estado atual da automação.
    -   `utils.py`: Funções de base para automação de UI (PyAutoGUI + OpenCV).
    -   ... (outros módulos de negócio)
-   `/imagens/`: Diretório para os templates visuais (imagens) da automação.
-   `/logs/` e `/screenshots/`: Diretórios para logs detalhados e capturas de tela de erros.

---

## Passo a Passo para Configuração e Execução

### 1. Pré-requisitos
-   Python 3.8 ou superior e ambiente `pip` configurado.
-   Ambiente Windows.
-   Navegador web (Chrome, Edge, etc.) instalado.

### 2. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 3. Configuração do `config.json` (CRÍTICO)
Edite o arquivo `config.json` na raiz do projeto. Ele **não contém senhas**.
```json
{
  "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "login_url": "https://ts-plusx1.kblcontabilidade.com.br/",
  "planilha1": "Controle_de_Emprestimos_CDR_2025.xlsx",
  "planilha2": "",
  "timeout": 30
}
```
-   `browser_path`: **Obrigatório.** O caminho completo para o `.exe` do seu navegador. Use barras normais (`/`).
-   `login_url`: A URL do portal de login.
-   `planilha1 / planilha2`: Nomes dos arquivos Excel na raiz do projeto.
-   `timeout`: Tempo de espera padrão para encontrar imagens. Aumente se a conexão for lenta.

### 4. Configuração de Credenciais (Variáveis de Ambiente)
Para máxima segurança, configure as credenciais como variáveis de ambiente no sistema.
-   `DOMINIO_USER`: Seu nome de usuário para o portal web KBL.
-   `DOMINIO_PASS`: Sua senha para o portal web KBL.
-   `RDP_PASS`: Sua senha para o pop-up do Windows/RemoteApp.

### 5. Captura das Imagens (Passo Crítico)
A automação depende de imagens para funcionar. As imagens que **você já forneceu** cobrem a maior parte do fluxo. No entanto, o robô precisa de recortes específicos para **clicar em botões**.

**Imagens Essenciais que VOCÊ PRECISA CAPTURAR:**
-   `/imagens/login_kbl_entrar_btn.png`: Um recorte **apenas do botão "Entrar"** da tela de login web.
-   `/imagens/remoteapp_launch_icon.png`: Um recorte do **ícone/botão que inicia a sessão RemoteApp** após o login web.
-   `/imagens/remoteapp_pass_field.png`: Um recorte **apenas do campo de senha** do pop-up do Windows.
-   `/imagens/remoteapp_ok_btn.png`: Um recorte **apenas do botão "OK"** do pop-up de senha do Windows.

Sem essas imagens específicas, a automação não saberá onde clicar.

### 6. Execução
Após configurar o `config.json`, as variáveis de ambiente e as imagens, execute:
```bash
python run.py
```
O robô iniciará todo o processo automaticamente.

---
## Sugestões de Melhoria
Para ambientes corporativos, o próximo passo em segurança é integrar a automação com um cofre de segredos dedicado, como **HashiCorp Vault** ou **Azure Key Vault**.
