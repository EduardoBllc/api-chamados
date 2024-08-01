from functools import wraps
from pathlib import Path
from decouple import AutoConfig, UndefinedValueError
from scripts.utils import apaga_linhas_em_branco, texto_colorido, VERMELHO, AMARELO, VERDE


class VariavelSettings:
    chave = None
    valor_padrao = None
    pede_edicao_criacao = None

    def __init__(self, chave, valor_padrao, pede_edicao_criacao=False):
        self.chave = chave
        self.valor_padrao = valor_padrao
        self.pede_edicao_criacao = pede_edicao_criacao

    def definicao(self):
        return f'{self.chave}={self.valor_padrao}'


VARIAVEIS_AMBIENTE = [
    VariavelSettings('DESENVOLVIMENTO', False),
    VariavelSettings('DEBUG', False),
    VariavelSettings('SECRET_KEY', 'django-insecure-key', ),
    VariavelSettings('ALLOWED_HOSTS', ['*'], )
]

VARIAVEIS_AMBIENTE_BASE_DADOS = [
    VariavelSettings('DB_NAME', 'sistema_chamados'),
    VariavelSettings('DB_USER', 'postgres'),
    VariavelSettings('DB_PASSWORD', 'p'),
    VariavelSettings('DB_HOST', 'localhost'),
    VariavelSettings('DB_PORT', '5432'),
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
                    file.write(f"{variavel}={valor}\n")
                    encontrada = True
                else:
                    file.write(linha)

            if not encontrada:
                file.write(f"{variavel}={valor}\n")
    except FileNotFoundError:
        return texto_colorido(f'Erro ao abrir arquivo {caminho_arquivo}', VERMELHO)
    except PermissionError as e:
        return texto_colorido(f'Erro de permissão: {e}', VERMELHO)

    return apaga_linhas_em_branco(caminho_arquivo)


def testa_variaveis_ambiente(config_env):
    desenvolvimento = False
    variavies_erro = []

    for variavel in VARIAVEIS_AMBIENTE:
        try:
            valor = config_env(variavel.chave)
            if variavel.chave == 'DESENVOLVIMENTO':
                desenvolvimento = eval(valor)
        except UndefinedValueError:
            variavies_erro.append(variavel.chave)

    if not desenvolvimento:
        for variavel in VARIAVEIS_AMBIENTE_BASE_DADOS:
            try:
                config_env(variavel.chave)
            except UndefinedValueError:
                variavies_erro.append(variavel.chave)

    if variavies_erro:
        mensagem_erro = texto_colorido(f'Nao foram encontradas as variáveis "{', '.join(variavies_erro)}"', VERMELHO)
        return variavies_erro, mensagem_erro

    return None


def resolve_arquivo_env(diretorio_base, nome_pasta_envs, nome_arquivo_env, nova_tentativa=False):
    nome_arquivo_env = nome_arquivo_env if nome_arquivo_env else '.env'

    caminho_pasta_envs = diretorio_base.joinpath(nome_pasta_envs if nome_pasta_envs else '')
    caminho_arquivo_env = caminho_pasta_envs.joinpath(Path(nome_arquivo_env))

    if not caminho_pasta_envs.is_dir():
        print(texto_colorido(f'ERRO:Caminho para pasta onde se encontra o arquivo de variáveis de ambiente '
                             f'inválido: {caminho_pasta_envs}',
                             VERMELHO))
        return None

    if not caminho_arquivo_env.is_file():
        mensagem_atencao = texto_colorido('ATENCAO: Nao foi encontrado arquivo de variaveis de ambiente no caminho '
                                          'informado:', AMARELO)
        print(f'{mensagem_atencao}\n'
              f'---> {caminho_pasta_envs}\n ')

        if solicitar_permissao_execucao(caminho_pasta_envs, nome_arquivo_env, ignora_primeiro=False):
            print(texto_colorido('Configurações ajustadas com sucesso!', VERDE))
            print('Iniciando servidor Django\n')
        else:
            return None

    config_envs = AutoConfig(search_path=caminho_arquivo_env)

    if erro_validacao := testa_variaveis_ambiente(config_envs):
        variaveis_erro = erro_validacao[0]
        mensagem_erro = erro_validacao[1]
        print(texto_colorido(f'Erro na checagem das variáveis de ambiente:', AMARELO))
        print(mensagem_erro)

        print('Deseja ajustá-las?')

        resposta = input('(S)im/(N)ão: ')

        if resposta in ('S', 's', 'Sim', 'sim'):
            for variavel in variaveis_erro:
                if mensagem_erro := altera_variavel(variavel, caminho_arquivo_env):
                    print(mensagem_erro)
                    return None

            if nova_tentativa:
                print(texto_colorido('Configurações ajustadas com sucesso!', VERDE))
                print('Iniciando servidor Django\n')

            return resolve_arquivo_env(diretorio_base,
                                       nome_pasta_envs,
                                       nome_arquivo_env,
                                       True)

        else:
            return None

    if nova_tentativa:
        print(texto_colorido('Configuracoes ajustadas com sucesso!', VERDE))
        print('Iniciando servidor Django\n')

    return config_envs


def solicitar_permissao_execucao(caminho_pasta_envs, nome_arquivo_env, ignora_primeiro=False):
    def pede_criacao(segunda_chamada=False):
        resposta = input('(S)im/(N)ao: ')

        if resposta in ('S', 's', 'Sim', 'sim'):
            return cria_arquivo_env(caminho_pasta_envs, nome_arquivo_env)
        elif segunda_chamada:
            return False

    if not ignora_primeiro:
        print(texto_colorido('Arquivo .env (variaveis de ambientes usadas no settings.py) não encontrado na raiz '
                             'do projeto.', VERMELHO) + '\nDeseja cria-lo?')

        return pede_criacao()

    print('É necessário um arquivo de variáveis de ambiente, ou então salvar as variaveis de ambiente em seu '
          'sistema para conseguir executar o projeto.\n')

    print('Se voce estiver tentando usar um arquivo de variaveis de ambiente personalizado(ex: "dev.env") voce deve '
          'ajustar as variaveis "PASTA_ENVS" e "ENV" do settings.py, com a pasta com seus arquivos .env e o arquivo '
          'que deseja utilizar, respectivamente.\n')

    print('Deseja executar o script de geracao do arquivo de variaveis de ambiente?')

    return pede_criacao(segunda_chamada=True)


def cria_arquivo_env(caminho_pasta_envs, nome_arquivo_env):
    print(f'Criando arquivo {nome_arquivo_env} em {caminho_pasta_envs}...', end=' ')
    with open(caminho_pasta_envs.joinpath(nome_arquivo_env), 'w') as arquivo_env:
        print(texto_colorido('(OK)', VERDE))

        desenvolvimento = False

        for variavel in VARIAVEIS_AMBIENTE:
            valor = input(f'Informe um valor para a variavel {variavel.chave}'
                          f'(deixe vazio para {variavel.valor_padrao}): ')

            if variavel.chave == 'DESENVOLVIMENTO':
                if valor.strip() == 'True':
                    desenvolvimento = valor

            if valor.strip():
                arquivo_env.write(f'{variavel.chave}={valor}\n')
            else:
                arquivo_env.write(f'{variavel.definicao()}\n')

        if desenvolvimento:
            for variavel in VARIAVEIS_AMBIENTE_BASE_DADOS:
                valor = input(f'Informe um valor para a variavel {variavel.chave}'
                              f'(deixe vazio para {variavel.valor_padrao}): ')

                if valor.strip():
                    arquivo_env.write(f'{variavel.chave}={valor}\n')
                else:
                    arquivo_env.write(f'{variavel.definicao()}\n')

    return True
