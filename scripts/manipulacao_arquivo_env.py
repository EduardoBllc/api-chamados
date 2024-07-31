from pathlib import Path
from decouple import AutoConfig, UndefinedValueError
from scripts.utils import apaga_linhas_em_branco, texto_colorido, VERMELHO, AMARELO, VERDE

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


def altera_variavel(variavel, caminho_arquivo):

    try:
        with open(caminho_arquivo, 'r') as file:
            linhas = file.readlines()
    except FileNotFoundError:
        return texto_colorido(f'Erro ao abrir arquivo {caminho_arquivo}', VERMELHO)

    try:
        with open(caminho_arquivo, 'w') as file:
            encontrada = False

            valor = input(f'Informe o valor desejado para a variável {variavel}: ')

            for linha in linhas:
                if linha.startswith(f"{variavel}="):
                    file.write(f"\n{variavel}={valor}\n")
                    encontrada = True
                else:
                    file.write(linha)

            if not encontrada:
                file.write(f"\n{variavel}={valor}\n")

    except FileNotFoundError:
        return texto_colorido(f'Erro ao abrir arquivo {caminho_arquivo}', VERMELHO)
    except PermissionError as e:
        return texto_colorido(f'Erro de permissao: {e}', VERMELHO)

    return apaga_linhas_em_branco(caminho_arquivo)


def testa_variaveis_ambiente(config_env):
    desenvolvimento = False
    variavies_erro = []

    for variavel in VARIAVEIS_AMBIENTE:
        try:
            valor = config_env(variavel)
            if variavel == 'DESENVOLVIMENTO':
                desenvolvimento = valor
        except UndefinedValueError:
            variavies_erro.append(variavel)

    if not desenvolvimento:
        for variavel in VARIAVEIS_AMBIENTE_BASE_DADOS:
            try:
                config_env(variavel)
            except UndefinedValueError:
                variavies_erro.append(variavel)

    if variavies_erro:
        mensagem_erro = texto_colorido(f'Nao foram encontradas as variáveis "{', '.join(variavies_erro)}"', VERMELHO)
        return variavies_erro, mensagem_erro

    return None


def resolve_arquivo_env(diretorio_base,
                        nome_pasta_envs,
                        nome_arquivo_env,
                        segunda_tentativa=False):

    nome_pasta_envs = nome_pasta_envs if nome_pasta_envs else 'envs'
    nome_arquivo_env = nome_arquivo_env if nome_arquivo_env else '.env'

    caminho_pasta_envs = diretorio_base.joinpath(nome_pasta_envs)
    caminho_arquivo_env = caminho_pasta_envs.joinpath(Path(nome_arquivo_env))

    try:
        config_envs = AutoConfig(search_path=caminho_arquivo_env)

        if erro_validacao := testa_variaveis_ambiente(config_envs):
            variaveis_erro = erro_validacao[0]
            mensagem_erro = erro_validacao[1]
            print(texto_colorido(f'Erro na checagem das variaveis de ambiente:', AMARELO))
            print(mensagem_erro)

            print('Deseja ajusta-las?')

            resposta = input('(S)im/(N)ao: ')

            if resposta in ('S', 's', 'Sim', 'sim'):
                for variavel in variaveis_erro:
                    if mensagem_erro := altera_variavel(variavel, caminho_arquivo_env):
                        print(mensagem_erro)
                        return None

                return resolve_arquivo_env(diretorio_base,
                                           nome_pasta_envs,
                                           nome_arquivo_env,
                                           True)

            else:
                return None

        if segunda_tentativa:
            print(texto_colorido('Configurações ajustada com sucesso!', VERDE))
            print('Iniciando servidor Django\n')

        return config_envs

    except UndefinedValueError:
        print(texto_colorido(f'Nao foi encontrado arquivo: {caminho_arquivo_env}\n', VERMELHO))
        if not solicitar_permissao_execucao(ignora_primeiro=True):
            return None


def solicitar_permissao_execucao(ignora_primeiro=False):
    def pede_criacao(segunda_chamada=False):
        resposta = input('(S)im/(N)ao: ')

        if resposta in ('S', 's', 'Sim', 'sim'):
            return executar()
        elif segunda_chamada:
            return False

    if not ignora_primeiro:
        print(texto_colorido('Arquivo .env (variaveis de ambientes usadas no settings.py) nao encontrado na raiz '
                             'do projeto.', VERMELHO) + '\nDeseja cria-lo?')

        pede_criacao()

    print('Eh necessario um arquivo de variaveis de ambiente, ou entao salvar as variaveis de ambiente em seu '
          'sistema para conseguir executar o projeto.\n')

    print('Se voce estiver tentando usar um arquivo de variaveis de ambiente personalizado(ex: "dev.env") voce deve '
          'ajustar as variaveis "PASTA_ENVS" e "ENV" do settings.py, com a pasta com seus arquivos .env e o arquivo '
          'que deseja utilizar, respectivamente.\n')

    print('Deseja executar o script de geracao do arquivo de variaveis de ambiente?')

    pede_criacao(segunda_chamada=True)


def executar():
    print('Teste')
    return True
