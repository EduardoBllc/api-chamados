VERMELHO = "\033[31m"
VERDE = "\033[32m"
AMARELO = "\033[33m"
RESET = "\033[0m"


def texto_colorido(texto, cor):
    return f'{cor}{texto}{RESET}'


def apaga_linhas_em_branco(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r') as file:
            lines = file.readlines()

        # Filtra linhas em branco
        non_blank_lines = [line for line in lines if line.strip()]

        # Escreve o conteúdo filtrado de volta ao arquivo
        with open(caminho_arquivo, 'w') as file:
            file.writelines(non_blank_lines)

    except FileNotFoundError:
        return texto_colorido(f'Erro ao abrir arquivo {caminho_arquivo}', VERMELHO)
    except PermissionError as e:
        return texto_colorido(f'Erro de permissao: {e}', VERMELHO)
