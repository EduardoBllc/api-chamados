from enum import Enum


class TipoVariavel(Enum):
    String = str
    Integer = int
    Float = float
    Boolean = bool
    List = list
    Dict = dict

    def __str__(self):
        return self.name


class VariavelSettings:
    """
    Objeto que representa uma variável presente no api_chamados.settings.py
    """
    def __init__(self,
                 nome,
                 valor_padrao=None,
                 tipo=TipoVariavel.String):
        """
        :param nome: Nome da variável
        :type nome: str
        :param valor_padrao: Valor que a variável assumirá se outro não for informado em sua criação
        :type valor_padrao: Any
        :param tipo: Tipo da variável
        :type tipo: TipoVariavel
        """
        self.nome = nome
        self.valor_padrao = valor_padrao
        self.tipo = tipo
        self.obriga_edicao = valor_padrao is None

    def definicao_padrao(self):
        """
        :return: String da declaração da variável com seu valor padrão
        :rtype: str
        """
        return f'{self.nome}={self.valor_padrao}'

    def verifica_tipo(self, valor):
        """
        Executa uma verificação de tipo no valor passado
        :param valor: Valor a ser verificado
        :type valor: Any
        :return: True ou False
        :rtype: bool
        """
        if self.tipo == TipoVariavel.String:
            return True
        else:
            try:
                if not type(eval(valor)) == self.tipo.value:
                    return False
            except NameError:
                return False

        return True

    def __str__(self):
        return self.nome
