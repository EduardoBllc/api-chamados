from scripts.gerenciador_envs.variaveis_ambiente import VARIAVEIS_AMBIENTE, VARIAVEIS_PRODUCAO
from scripts.utils import texto_colorido, VERMELHO


def le_arquivo_env(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        return texto_colorido(f'Erro ao abrir arquivo {caminho_arquivo}', VERMELHO)




