from pathlib import Path
from decouple import AutoConfig, UndefinedValueError

VARIAVEIS_AMBIENTE = [
    'DESENVOLVIMENTO',
    'DEBUG',
    'SECRET_KEY',
    'ALLOWED_HOSTS',
]

VARIAVEIS_AMBIENTE_BASE_DADOS = [
    'DB_NAME',
    'DB_USER',
    'DB_PASSWORD',
    'DB_HOST',
    'DB_PORT',
]


def testa_variaveis_ambiente(config_env):
    passou = True
    desenvolvimento = False

    for variavel in VARIAVEIS_AMBIENTE:
        try:
            valor = config_env(variavel)
            if variavel == 'DESENVOLVIMENTO':
                desenvolvimento = valor
        except ValueError:
            print(f'Nao foi encontrado valor para variavel "{variavel}"')
            passou = False

    if not desenvolvimento:
        for variavel in VARIAVEIS_AMBIENTE_BASE_DADOS:
            try:
                config_env(variavel)
            except ValueError:
                print(f'Nao foi encontrado valor para variavel "{variavel}"')
                passou = False

    return passou


def resolve_arquivo_env(diretorio_base, nome_pasta_envs, nome_arquivo_env):

    nome_pasta_envs = nome_pasta_envs if nome_pasta_envs else 'envs'
    nome_arquivo_env = nome_arquivo_env if nome_arquivo_env else '.env'

    caminho_pasta_envs = diretorio_base.joinpath(nome_pasta_envs)
    caminho_arquivo_env = caminho_pasta_envs.joinpath(Path(nome_arquivo_env))

    try:
        config_envs = AutoConfig(search_path=caminho_arquivo_env)
        if not testa_variaveis_ambiente(config_envs):
            raise UndefinedValueError('Falha na validacao de variaveis de ambiente, para mais infomacoes observer os '
                                      'prints que se encontram antes do erro')

        return config_envs

    except UndefinedValueError:
        print(f'Nao foi encontrado arquivo: {caminho_arquivo_env}')
        solicitar_permissao_execucao(ignora_primeiro=True)


def solicitar_permissao_execucao(ignora_primeiro=False):
    def pede_criacao(segunda_chamada=False):
        resposta = input('(S)im/(N)ao: ')

        if resposta in ('S', 's', 'Sim', 'sim'):
            executar()
        elif segunda_chamada:
            raise InterruptedError('Execucao encerrada')

    if not ignora_primeiro:
        print('Arquivo .env (variaveis de ambientes usadas no settings.py) nao encontrado na raiz do projeto.\n\n'
              'Deseja cria-lo?')

        pede_criacao()

    print('Eh necessario um arquivo de variaveis de ambiente, ou entao salvar as variaveis de ambiente em seu '
          'sistema para conseguir executar o projeto.\n')

    print('Se voce estiver tentando usar um arquivo de variaveis de ambiente personalizado(ex: "dev.env") voce deve '
          'ajustar as variaveis "PASTA_ENVS" e "ENV" do settings.py, com a pasta com seus arquivos .env e o arquivo '
          'que deseja utilizar, respectivamente.\n')

    print('Deseja executar o script de geracao do arquivo de varaveis de ambiente?')

    pede_criacao(segunda_chamada=True)


def executar():
    input('Teste')
