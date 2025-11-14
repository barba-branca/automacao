import json
from typing import Dict, Any
from pathlib import Path

# Importar todos os módulos da automação com imports relativos
from .logger import setup_logger
from . import excel_reader
from . import dominio
from . import lancamento

# Define o diretório base do projeto (um nível acima da pasta 'automation')
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "logs"
SCREENSHOT_DIR = BASE_DIR / "screenshots"

# Configura o logger para usar o diretório base
log = setup_logger(log_dir=LOG_DIR)


def load_config(filepath: Path) -> Dict[str, Any]:
    """Loads the JSON configuration file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            log.info(f"Loading configuration from {filepath}")
            return json.load(f)
    except FileNotFoundError:
        log.error(f"Configuration file not found: {filepath}")
        raise
    except json.JSONDecodeError:
        log.error(f"Error decoding JSON from the configuration file: {filepath}")
        raise

def main():
    """
    Main function to orchestrate the entire accounting automation process.
    """
    log.info("=============================================")
    log.info("=== INICIANDO AUTOMAÇÃO DE LANÇAMENTOS CONTÁBEIS ===")
    log.info("=============================================")

    try:
        # 1. Carregar Configuração
        config = load_config(CONFIG_FILE)
        config["base_dir"] = BASE_DIR # Add base_dir to config for other modules

        # (Opcional) Conectar ao RDP
        # rdp_file = BASE_DIR / "minha_conexao.rdp"
        # rdp_id_image = BASE_DIR / "imagens" / "rdp_area_trabalho.png"
        # if not rdp.connect_rdp(str(rdp_file), str(rdp_id_image)):
        #     log.critical("Não foi possível estabelecer a conexão RDP. Abortando.")
        #     return

        # 2. Ler e Processar Planilhas Excel
        planilhas = [config.get("planilha1"), config.get("planilha2")]
        planilhas_paths = [BASE_DIR / p for p in planilhas if p]

        if not planilhas_paths:
            log.critical("Nenhuma planilha especificada no config.json. Abortando.")
            return

        dados_lancamentos = excel_reader.load_and_process_excel_files(planilhas_paths)

        if dados_lancamentos.empty:
            log.warning("Nenhum dado para processar após a leitura das planilhas. Encerrando.")
            return

        # 3. Navegar até a Tela de Lançamentos no Sistema Domínio
        if not dominio.navigate_to_lancamentos_screen(config):
            log.critical("Não foi possível navegar para a tela de lançamentos. Abortando.")
            return

        # 4. Iterar e Realizar Lançamentos
        sucessos, falhas = 0, 0
        total = len(dados_lancamentos)
        log.info(f"Iniciando o processo de {total} lançamentos...")

        for index, row in dados_lancamentos.iterrows():
            log.info(f"--- Processando Lançamento {index + 1} de {total} ---")
            try:
                lancamento.preencher_lancamento(row.to_dict(), config)
                log.info(f"Lançamento {index + 1} (Hist: {row.get('historico', 'N/A')}) bem-sucedido.")
                sucessos += 1
            except Exception as e:
                log.error(f"Falha no lançamento {index + 1}. Erro: {e}")
                log.error(f"Dados do lançamento: {row.to_dict()}")
                falhas += 1
                # O decorator já salvou um screenshot. O loop continuará.

    except Exception as e:
        log.critical(f"Um erro fatal e inesperado ocorreu na automação: {e}", exc_info=True)

    finally:
        log.info("============================================")
        log.info("========= FIM DA AUTOMAÇÃO =========")
        if 'dados_lancamentos' in locals():
            log.info(f"Total de Lançamentos Planejados: {len(dados_lancamentos)}")
            log.info(f"  -> Sucessos: {sucessos}")
            log.info(f"  -> Falhas:   {falhas}")
        log.info("============================================")
