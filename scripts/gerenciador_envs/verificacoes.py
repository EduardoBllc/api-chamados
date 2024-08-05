import psycopg2
from decouple import UndefinedValueError
from psycopg2 import connect, OperationalError
from scripts.gerenciador_envs.variaveis_ambiente import VARIAVEIS_AMBIENTE, VARIAVEIS_PRODUCAO
from scripts.utils import texto_colorido, VERMELHO
from decouple import config


def verifica_variaveis():
    desenvolvimento = False
    variaveis_erro = []

    for variavel in VARIAVEIS_AMBIENTE:
        try:
            valor = config(variavel.nome)
            if variavel.nome == 'DESENVOLVIMENTO':
                desenvolvimento = eval(valor)
        except UndefinedValueError:
            variaveis_erro.append(variavel)

    if not desenvolvimento:
        for variavel in VARIAVEIS_PRODUCAO:
            try:
                config(variavel.nome)
            except UndefinedValueError:
                variaveis_erro.append(variavel)

    if variaveis_erro:
        mensagem_erro = texto_colorido(f'Nao foram encontradas as variaveis "'
                                       f'{', '.join([variavel.nome for variavel in variaveis_erro])}"',
                                       VERMELHO)
        return variaveis_erro, mensagem_erro

    return None


def verifica_banco_dados():
    dic_conexao = {
        'dbname': config('DB_NAME'),
        'user': config('DB_USER'),
        'password': config('DB_PASSWORD'),
        'port': config('DB_PORT'),
        'host': config('DB_HOST'),
    }

    try:
        connect(**dic_conexao)
        return True
    except (OperationalError, UnicodeDecodeError) as erro:
        print(texto_colorido('Erro ao tentar conectar ao banco de dados.', VERMELHO))
        print(f'Variaveis usadas para tentar conectar: {dic_conexao}')
        print(f'Erro levantado: {erro}')
        return False
