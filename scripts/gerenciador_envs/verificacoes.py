from decouple import UndefinedValueError

from scripts.gerenciador_envs.variaveis_ambiente import VARIAVEIS_AMBIENTE, VARIAVEIS_PRODUCAO
from scripts.utils import texto_colorido, VERMELHO


def verifica_variaveis(config_env):
    desenvolvimento = False
    variaveis_erro = []

    for variavel in VARIAVEIS_AMBIENTE:
        try:
            valor = config_env(variavel.nome)
            if variavel.nome == 'DESENVOLVIMENTO':
                desenvolvimento = eval(valor)
        except UndefinedValueError:
            variaveis_erro.append(variavel)

    if not desenvolvimento:
        for variavel in VARIAVEIS_PRODUCAO:
            try:
                config_env(variavel.nome)
            except UndefinedValueError:
                variaveis_erro.append(variavel)

    if variaveis_erro:
        mensagem_erro = texto_colorido(f'Nao foram encontradas as variaveis "'
                                       f'{', '.join([variavel.nome for variavel in variaveis_erro])}"',
                                       VERMELHO)
        return variaveis_erro, mensagem_erro

    return None
