# Automação de Lançamentos Contábeis para Domínio Contábil

Este projeto contém uma automação completa e robusta, desenvolvida em Python, para realizar lançamentos contábeis no sistema Domínio Contábil (Thomson Reuters) a partir de dados extraídos de planilhas Excel.

A automação é projetada para ser resiliente, modular e pronta para um ambiente de produção, lidando com as instabilidades de uma interface gráfica acessada via RDP.

## Arquitetura

O projeto é estruturado como um pacote Python (`automation`) para garantir a modularidade e a clareza do código.

-   `run.py`: Ponto de entrada principal da aplicação. Execute este arquivo para iniciar a automação.
-   `requirements.txt`: Lista de todas as dependências Python.
-   `config.json`: Arquivo de configuração central para definir caminhos de planilhas, timeouts e outros parâmetros sem alterar o código.
-   `/automation/`: Pacote Python contendo toda a lógica da automação.
    -   `main.py`: Orquestrador principal que gerencia o fluxo da automação.
    -   `logger.py`: Módulo de logging centralizado.
    -   `utils.py`: Funções utilitárias de baixo nível para interação com a UI (clique, busca de imagem, digitação) usando PyAutoGUI e OpenCV.
    -   `excel_reader.py`: Módulo para ler e processar as planilhas do Excel, com normalização de colunas e tratamento de aliases.
    -   `rdp.py`: Função para iniciar a conexão RDP (se necessário).
    -   `dominio.py`: Funções de alto nível para navegar nos menus do sistema Domínio.
    -   `plano_contas_selector.py`: Módulo crítico e dedicado para interagir com a janela de seleção do Plano de Contas.
    -   `lancamento.py`: Módulo que orquestra o preenchimento de um único lançamento contábil.
-   `/imagens/`: Diretório onde você **deve** salvar as imagens (templates) que a automação usará para encontrar os elementos da UI.
-   `/logs/`: Diretório onde os arquivos de log serão salvos.
-   `/screenshots/`: Diretório onde as capturas de tela de erros serão salvas automaticamente.

---

## Passo a Passo para Configuração e Execução

### 1. Pré-requisitos

-   Python 3.8 ou superior.
-   Acesso a um ambiente Windows onde a automação será executada (necessário para PyAutoGUI e `mstsc.exe`).
-   O sistema Domínio Contábil acessível via Conexão de Área de Trabalho Remota (RDP) ou localmente.

### 2. Instalação das Dependências

Abra um terminal ou prompt de comando, navegue até a pasta raiz do projeto e execute:

```bash
pip install -r requirements.txt
```

### 3. Configuração do `config.json`

Edite o arquivo `config.json` na raiz do projeto:

```json
{
  "planilha1": "Controle_de_Emprestimos_CDR_2025.xlsx",
  "planilha2": "Controle_Apropriacao_UTI_Movel.xlsx",
  "timeout": 25,
  "delay": 0.3,
  "atalhos": {
    "plano_contas": ["fn", "f2"]
  }
}
```

-   **planilha1 / planilha2**: Coloque os nomes dos seus arquivos Excel aqui. Eles devem estar na **raiz do projeto**. Deixe uma string vazia ("") se não for usar.
-   **timeout**: Tempo máximo (em segundos) que a automação esperará por um elemento visual na tela. Aumente este valor se a conexão RDP for lenta.
-   **delay**: Pequeno atraso entre as ações para simular um comportamento mais humano.
-   **atalhos.plano_contas**: Teclas de atalho para abrir a janela do Plano de Contas. Ajuste conforme necessário.

### 4. Captura das Imagens (Passo Crítico)

A automação depende 100% de imagens para "ver" a tela. Você precisa capturar pequenas áreas da tela do sistema Domínio e salvá-las como arquivos `.png` dentro da pasta `/imagens`.

**Regras para as imagens:**
-   Capture uma área pequena e **única** do elemento. Evite capturar áreas que mudam (como texto ao redor).
-   Os nomes dos arquivos devem corresponder exatamente aos usados no código. A lista completa de imagens necessárias está no código de cada módulo (`dominio.py`, `plano_contas_selector.py`, `lancamento.py`).
-   **Exemplo:** Para `menu_contabilidade.png`, capture apenas o texto "Contabilidade" do menu principal.

### 5. Preparação dos Arquivos Excel

-   Coloque os arquivos `.xlsx` nomeados no `config.json` na pasta **raiz do projeto**.
-   Garanta que eles contenham as colunas necessárias. O `excel_reader.py` é flexível com os nomes das colunas (ex: "debito", "Debitar", "conta_debito" são todos válidos), mas os dados devem ser precisos.

### 6. Execução da Automação

Com tudo configurado, abra um terminal na raiz do projeto e execute:

```bash
python run.py
```

A automação irá iniciar. Acompanhe os logs no console e, para mais detalhes, verifique o arquivo `logs/automation.log`. Em caso de erro, uma captura de tela será salva em `/screenshots`.

---

## Sugestões de Melhoria e Otimização

1.  **Gestão de Credenciais**: Atualmente, a automação de RDP (`rdp.py`) abre um arquivo `.rdp` pré-configurado. Para um ambiente de produção mais seguro, integre a automação com um cofre de senhas (como HashiCorp Vault, Azure Key Vault ou Windows Credential Manager) para buscar as credenciais em tempo de execução.

2.  **Máquina de Estados**: Para automações muito longas e complexas, um simples loop `for` pode ser frágil. Implementar uma arquitetura de máquina de estados permitiria que a automação se recuperasse de erros de forma mais inteligente. Por exemplo, se o sistema Domínio travar, uma máquina de estados poderia detectar isso, reiniciar a aplicação e continuar do ponto onde parou.

3.  **Filas de Trabalho (Queues)**: Em vez de ler diretamente de um Excel, a automação poderia consumir itens de uma fila (RabbitMQ, SQS, ou até mesmo uma tabela em um banco de dados). Uma aplicação separada (um "produtor") poderia ler o Excel e popular a fila. Isso desacopla a extração de dados da execução da automação, permitindo reprocessamento fácil de itens com falha e paralelização do trabalho.

4.  **Técnicas de Visão Computacional Avançadas**:
    -   **Adaptação a Temas/Resoluções**: Se a automação precisa rodar em máquinas com temas (claro/escuro) ou resoluções diferentes, o template matching pode falhar. Uma solução seria ter conjuntos de imagens para cada tema/resolução ou usar algoritmos de feature matching (como SIFT ou ORB) que são mais resilientes a pequenas variações.
    -   **OCR (Optical Character Recognition)**: Em vez de depender de imagens para tudo, usar uma biblioteca de OCR (como Tesseract via `pytesseract`) para ler textos na tela poderia tornar a automação mais robusta. Por exemplo, para confirmar que uma janela com um título específico ("Plano de Contas") realmente abriu.

5.  **Relatórios de Execução**: Ao final da execução, a automação poderia gerar um relatório detalhado em formato HTML ou Excel, listando cada lançamento processado, seu status (sucesso/falha), a mensagem de erro (se houver) e um link para o screenshot da falha.
