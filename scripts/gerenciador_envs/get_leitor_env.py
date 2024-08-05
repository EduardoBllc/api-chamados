from decouple import config

from scripts.gerenciador_envs.manipulacao_arq_env import solicitar_permissao_criacao, adiciona_variaveis
from scripts.gerenciador_envs.verificacoes import verifica_variaveis, verifica_banco_dados
from scripts.utils import texto_colorido, AMARELO, VERDE


def verifica_vars_env(diretorio_base, nova_tentativa=False):

    if not diretorio_base.joinpath('.env').exists():
        if not solicitar_permissao_criacao(diretorio_base):
            return False

        return verifica_vars_env(diretorio_base, True)

    if erro_validacao := verifica_variaveis():
        variaveis_erro = erro_validacao[0]
        mensagem_erro = erro_validacao[1]
        print(texto_colorido(f'Erro na checagem das variaveis de ambiente:', AMARELO))
        print(mensagem_erro)

        print('Deseja ajusta-las?')

        resposta = input('(S)im/(N)ao: ')

        if resposta.lower() in ('s', 'sim'):
            if mensagem_erro := adiciona_variaveis(variaveis_erro, diretorio_base):
                print(mensagem_erro)
                return False

            return verifica_vars_env(diretorio_base, True)

        else:
            return False

    if not config('DESENVOLVIMENTO', cast=bool) and not verifica_banco_dados():
        return False

    if nova_tentativa:
        print(texto_colorido('Configuracoes ajustadas com sucesso!', VERDE))
        print('Tentando iniciar servidor Django novamente...\n')

    return True
