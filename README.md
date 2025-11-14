# Automação de Lançamentos Contábeis para Domínio Contábil (100% Autônoma)

Este projeto contém uma automação completa e robusta, desenvolvida em Python, para realizar lançamentos contábeis no sistema Domínio Contábil (Thomson Reuters). A automação é projetada para ser **100% hands-free**, iniciando o processo desde a abertura do navegador, passando por múltiplos estágios de login, até a inserção dos dados a partir de planilhas Excel.

A arquitetura é baseada em uma **máquina de estados simplificada**, que permite que a automação detecte em qual tela do processo ela se encontra e execute a ação correta, garantindo alta resiliência e capacidade de recuperação.

## Arquitetura

-   `run.py`: Ponto de entrada principal da aplicação.
-   `requirements.txt`: Lista de dependências Python.
-   `config.json`: Arquivo de configuração para parâmetros não-sensíveis (URLs, caminhos, timeouts).
-   `/automation/`: Pacote Python contendo toda a lógica.
    -   `main.py`: Orquestrador principal, implementado como um controlador de estados.
    -   `login_auto.py`: **Novo!** Módulo que gerencia o fluxo de login 100% automático.
    -   `utils.py`: Funções de base para automação de UI (PyAutoGUI + OpenCV).
    -   `excel_reader.py`: Módulo de leitura e processamento de Excel.
    -   `dominio.py`: Funções para navegação nos menus internos do Domínio.
    -   ... (outros módulos de negócio)
-   `/imagens/`: Diretório para os templates visuais (imagens) da automação.
-   `/logs/` e `/screenshots/`: Diretórios para logs detalhados e capturas de tela de erros.

---

## Passo a Passo para Configuração e Execução

### 1. Pré-requisitos

-   Python 3.8 ou superior.
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
  "planilha2": "Controle_Apropriacao_UTI_Movel.xlsx",
  "timeout": 25,
  "delay": 0.3
}
```

-   `browser_path`: **Obrigatório.** O caminho completo para o executável do seu navegador. Use barras normais (`/`) mesmo no Windows.
-   `login_url`: A URL do portal de login.
-   `planilha1 / planilha2`: Nomes dos arquivos Excel na raiz do projeto.
-   `timeout`: Tempo de espera padrão para encontrar imagens.

### 4. Configuração de Credenciais (Variáveis de Ambiente)

Para máxima segurança, as credenciais **não** são salvas em arquivos. Você deve configurá-las como variáveis de ambiente no sistema onde a automação irá rodar.

**Variáveis Necessárias:**
-   `DOMINIO_USER`: Seu nome de usuário para o portal web KBL.
-   `DOMINIO_PASS`: Sua senha para o portal web KBL.
-   `RDP_PASS`: Sua senha para o pop-up do Windows/RemoteApp.

**Como configurar no Windows (Terminal):**
```cmd
set DOMINIO_USER="seu_usuario_web"
set DOMINIO_PASS="sua_senha_web"
set RDP_PASS="sua_senha_rdp"
```
*(Nota: Variáveis definidas assim duram apenas para a sessão do terminal atual. Para configurar permanentemente, use o painel "Editar as variáveis de ambiente do sistema").*

### 5. Captura das Imagens (Passo Crítico)

A automação depende 100% de imagens para funcionar. Salve capturas de tela pequenas e únicas na pasta `/imagens`. **O novo fluxo de login automático requer novas imagens.** O código em `login_auto.py` irá listar os nomes de arquivo que ele espera.

**Novas imagens necessárias (Exemplos):**
-   `login_kbl_entrar_btn.png`: O botão "Entrar" da tela de login web.
-   `remoteapp_launch_btn.png`: O botão para iniciar a sessão RemoteApp após o login web.
-   `login_remoteapp_ok_btn.png`: O botão "OK" do pop-up de senha do Windows.
-   ...e outras, conforme definido nas constantes dos arquivos `.py`.

### 6. Execução

Após configurar o `config.json` e as variáveis de ambiente, execute a automação:
```bash
python run.py
```
O robô irá abrir o navegador, realizar todo o processo de login e iniciar os lançamentos sem qualquer intervenção humana.

---
## Sugestões de Melhoria

A gestão de credenciais via variáveis de ambiente é um grande avanço em segurança. Para ambientes corporativos de alta segurança, o próximo passo seria integrar a automação com um cofre de segredos dedicado, como **HashiCorp Vault**, **Azure Key Vault**, ou **AWS Secrets Manager**.
