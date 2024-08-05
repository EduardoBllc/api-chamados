from decouple import config

from scripts.gerenciador_envs.manipulacao_arq_env import altera_variaveis, solicitar_permissao_criacao
from scripts.gerenciador_envs.verificacoes import verifica_variaveis
from scripts.utils import texto_colorido, AMARELO, VERDE


def get_config_env(diretorio_base, nova_tentativa=False):

    config_envs = config

    if not diretorio_base.joinpath('.env').exists():
        if not solicitar_permissao_criacao(diretorio_base):
            return None

        return get_config_env(diretorio_base, True)

    if erro_validacao := verifica_variaveis(config_envs):
        variaveis_erro = erro_validacao[0]
        mensagem_erro = erro_validacao[1]
        print(texto_colorido(f'Erro na checagem das variaveis de ambiente:', AMARELO))
        print(mensagem_erro)

        print('Deseja ajusta-las?')

        resposta = input('(S)im/(N)ao: ')

        if resposta in ('S', 's', 'Sim', 'sim'):
            if mensagem_erro := altera_variaveis(variaveis_erro, diretorio_base):
                print(mensagem_erro)
                return None

            return get_config_env(diretorio_base, True)

        else:
            return None

    if nova_tentativa:
        print(texto_colorido('Configuracoes ajustadas com sucesso!', VERDE))
        print('Tentando iniciar servidor Django novamente...\n')

    return config_envs
