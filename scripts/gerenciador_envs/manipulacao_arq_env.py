# -*- coding: utf-8 -*-
from scripts.gerenciador_envs.leitura_arq_env import le_arquivo_env
from scripts.gerenciador_envs.variaveis_ambiente import VARIAVEIS_AMBIENTE, VARIAVEIS_PRODUCAO
from scripts.utils import apaga_linhas_em_branco, texto_colorido, VERMELHO, AMARELO, VERDE


def pede_valor_variavel(variavel, tentativa=1):
    valor = None

    texto_solicitacao = f'Informe um valor desejado do tipo {variavel.tipo} para a variavel {variavel}'

    if variavel.obriga_edicao:
        while valor is None:
            valor_tentativa = input(texto_solicitacao + ':')

            if valor_tentativa:
                valor = valor_tentativa
            elif tentativa > 3:
                return None
            else:
                print(texto_colorido(f'Para esta variavel, eh obrigatorio informar um valor do tipo {variavel.tipo}.',
                      AMARELO))
                tentativa += 1
    else:
        valor = input(f'{texto_solicitacao}[{variavel.valor_padrao}]: ')

        if not valor:
            valor = str(variavel.valor_padrao)

    if not variavel.verifica_tipo(valor):
        if tentativa > 3:
            return None

        print(texto_colorido(f'Valor {valor} nao corresponde com o tipo da variavel,  que eh {variavel.tipo}.',
                             VERMELHO))
        print(texto_colorido('Por favor, tente novamente informando um valor do tipo indicado', AMARELO))
        return pede_valor_variavel(variavel, tentativa=tentativa + 1)

    return valor


def altera_variaveis(variaveis, diretorio_base):
    caminho_arquivo = diretorio_base.join('.env')

    linhas = le_arquivo_env(caminho_arquivo)

    if linhas is str:
        return linhas

    try:
        with open('.env', 'w') as file:
            faltantes = variaveis.copy()

            for linha in linhas:
                for variavel in variaveis:
                    if not linha.startswith(f"{variavel}="):
                        file.write(linha)
                    else:
                        if valor := pede_valor_variavel(variavel):
                            file.write(f"{variavel}={valor}\n")
                            faltantes.remove(variavel)
                        else:
                            return texto_colorido('Numero maximo de tentativas excedido!', VERMELHO)
            if faltantes:
                for var_faltante in faltantes:
                    valor = pede_valor_variavel(var_faltante)

                    if not valor:
                        return texto_colorido('Numero maximo de tentativas excedido!', VERMELHO)

                    file.write(f"{var_faltante}={valor}\n")

    except FileNotFoundError:
        return texto_colorido(f'Erro ao abrir arquivo {diretorio_base}', VERMELHO)
    except PermissionError as pe:
        return texto_colorido(f'Erro de permissao: {pe}', VERMELHO)

    return apaga_linhas_em_branco(caminho_arquivo)


def solicitar_permissao_criacao(caminho_pasta_envs, ignora_primeiro=False):

    nome_arquivo_env = '.env'

    if not ignora_primeiro:
        print(texto_colorido(f'Arquivo {nome_arquivo_env} (variaveis de ambientes usadas no settings.py) '
                             f'nao encontrado em {caminho_pasta_envs}.', VERMELHO) + '\nDeseja cria-lo?')

        resposta = input('(S)im/(N)ao: ')

        if resposta.lower() in ('s', 'sim'):
            return cria_arquivo_env(caminho_pasta_envs, nome_arquivo_env)

    print(texto_colorido('Eh necessário um arquivo de variaveis de ambiente, ou então salvar as variaveis de '
                         'ambiente em seu sistema para conseguir executar o projeto.\n', AMARELO))

    print('Se voce estiver tentando usar um arquivo de variaveis de ambiente personalizado(ex: "dev.env") voce deve '
          'ajustar as variaveis "PASTA_ENVS" e "ENV" do settings.py, com a pasta com seus arquivos .env e o arquivo '
          'que deseja utilizar, respectivamente.\n')

    print('Deseja executar o script de geracao do arquivo de variaveis de ambiente?')

    resposta = input('(S)im/(N)ao: ')

    if resposta.lower() in ('s', 'sim'):
        return cria_arquivo_env(caminho_pasta_envs, nome_arquivo_env)

    return False


def cria_arquivo_env(caminho_pasta_envs, nome_arquivo_env):
    print(f'Criando arquivo {nome_arquivo_env} em {caminho_pasta_envs}...', end=' ')
    with open(caminho_pasta_envs.joinpath(nome_arquivo_env), 'w') as arquivo_env:
        print(texto_colorido('(OK)', VERDE))

        desenvolvimento = False

        for variavel in VARIAVEIS_AMBIENTE:
            valor = pede_valor_variavel(variavel)
            if valor is None:
                return False

            if variavel.nome == 'DESENVOLVIMENTO':
                if valor.strip() == 'True':
                    desenvolvimento = eval(valor)

            if valor.strip():
                arquivo_env.write(f'{variavel.nome}={valor}\n')
            else:
                arquivo_env.write(f'{variavel.definicao_padrao()}\n')

        if not desenvolvimento:
            for variavel in VARIAVEIS_PRODUCAO:
                valor = pede_valor_variavel(variavel)

                if valor is None:
                    return False

                if valor.strip():
                    arquivo_env.write(f'{variavel.nome}={valor}\n')
                else:
                    arquivo_env.write(f'{variavel.definicao_padrao()}\n')
    return True
