from datetime import datetime

from django.db.models import Model
from django.db.models.base import ModelBase

from clientes.models import ContatoCliente


def repr_coluna(field_name: str):
    def decorator(func):
        func._field_name = field_name
        return property(func)

    return decorator


class ConfigTabela:
    def __init__(self, model: Model = None, mapa: dict = None, chaves_primarias: list | tuple = None):
        """
        Objeto que contém as meta configurações de tabela

        :param model: Model Django do qual a classe pertence
        :type model: Model
        :param mapa: Mapa das colunas do model e seus respectivos campos na classe
        :type mapa: dict
        :param chaves_primarias: Lista com as colunas que formam a chave primaria da tabela
        :type chaves_primarias: list
        """

        if mapa is None:
            mapa = {}

        self.model = model
        self.mapa = mapa
        self.chaves_primarias = chaves_primarias

    @property
    def preenchido(self):
        return self.model is not None and self.chaves_primarias != []


class ConfigDbf:
    def __init__(self, var_filial: str = None, indice: int = None):
        """
        Objeto que contém as meta configurações de DBF

        :param var_filial: Campo que contém valor da filial que será usado no dbf
        :type var_filial: str
        :param indice: Índice que será usado no dbf
        """

        self.var_filial = var_filial
        self.indice = indice

    @property
    def preenchido(self):
        return self.var_filial and self.indice


class MetaConfig:
    """
    Objeto que contém as meta configurações de uma classe
    """
    tabela: ConfigTabela = ConfigTabela()

    usa_dbf: bool = False
    dbf: ConfigDbf = ConfigDbf()


class Dbf:
    filial = ''
    indice = 0
    where = ''
    chave = ''


class MetaInterfaceTabela(type):
    def __new__(cls, name, bases, dct):

        config = MetaConfig()

        attrs_config = dct.get('Meta', None)

        attr_model = 'model_tabela'
        attr_mapa_tabela = 'mapa_tabela'
        attr_chaves_primarias = 'chaves_primarias'
        attr_indice_dbf = 'indice_dbf'
        attr_var_filial_dbf = 'var_filial_dbf'
        attr_usa_dbf = 'usa_dbf'

        if attrs_config:
            if hasattr(attrs_config, attr_model):
                model_tabela = getattr(attrs_config, attr_model)
                assert isinstance(model_tabela, ModelBase), f'"{attr_model}" deve ser um model Django.'
                config.tabela.model = model_tabela

            if hasattr(attrs_config, attr_mapa_tabela):
                config.tabela.mapa = getattr(attrs_config, attr_mapa_tabela)

            if hasattr(attrs_config, attr_chaves_primarias):
                config.tabela.chaves_primarias = getattr(attrs_config, attr_chaves_primarias)

            if hasattr(attrs_config, attr_indice_dbf):
                config.dbf.indice = getattr(attrs_config, attr_indice_dbf)

            if hasattr(attrs_config, attr_var_filial_dbf):
                config.dbf.var_filial = getattr(attrs_config, attr_var_filial_dbf)

            if hasattr(attrs_config, attr_usa_dbf):
                usa_dbf = getattr(attrs_config, attr_usa_dbf)
                assert isinstance(usa_dbf, bool), 'Propriedade "usa_dbf" deve ser boolean.'
            else:
                usa_dbf = True

            if usa_dbf and not (config.tabela.preenchido and config.dbf.preenchido):
                raise AssertionError('Se a tabela depende de DBF, devem ser passadas as propriedades "indice_dbf", '
                                     '"chaves_primarias", "var_filial_dbf" e "model_tabela".\nCaso não dependa, passe'
                                     'o atributo "usa_dbf" como False')

            config.usa_dbf = usa_dbf

            del dct['Meta']

        dct['_meta'] = config

        nova_classe = super().__new__(cls, name, bases, dct)

        def pre_mapeamento(self):
            config_tabela = self._meta.tabela
            mapa_tabela = config_tabela.mapa
            instancia_model = config_tabela.model()

            for nome_atributo in self.__dict__.keys():
                atributo = getattr(self, nome_atributo)
                if hasattr(atributo, '_field_name'):
                    mapa_tabela[atributo._field_name] = nome_atributo
                elif nome_atributo in instancia_model.__dict__.keys() and nome_atributo not in mapa_tabela.keys():
                    mapa_tabela[nome_atributo] = nome_atributo

        setattr(nova_classe, 'pre_mapeamento', pre_mapeamento)

        @property
        def model(self):
            """
            Model representado pela classe
            """
            return self._meta.tabela.model

        setattr(nova_classe, 'model', model)

        @property
        def _filial_dbf(self):
            """
            Filial para ser usada no objeto de DBF
            """
            var_filial = self._meta.dbf.var_filial
            assert var_filial in self.__dict__.keys(), f'Não há variável com nome "{var_filial}" na classe'
            return self.__dict__[var_filial]

        setattr(nova_classe, 'filial_dbf', _filial_dbf)

        @property
        def objeto_model(self):
            """
            Objeto do model representado pela classe, com os valores segundo seu mapeamento.
            :rtype: ModelBase
            """

            config_tabela = self._meta.tabela

            objeto = self.model()
            modificou = False

            for coluna in config_tabela.mapa.keys():
                assert hasattr(objeto, coluna), (f'Não existe coluna no model {self.model} '
                                                 f'com nome {coluna}')
                objeto.__dict__[coluna] = self.__dict__[config_tabela.mapa[coluna]]
                modificou = True

            assert modificou, (f'Nenhuma variável da classe {self.__name__} bate com os nomes das colunas de '
                               f'{self.model}.\nRenomeie as variáveis ou mapeie a tabela pelo atributo "mapa_tabela" '
                               f'da classe Meta')

            return objeto

        setattr(nova_classe, 'objeto_model', objeto_model)

        @property
        def _chave_dbf(self):
            """
            Valor da chave para ser utilizada no objeto de DBF.
            :rtype: str
            """
            chave_dbf = ''

            model_classe = self._meta.tabela.model
            campos_model = list(model_classe._meta.fields)

            for coluna in self._meta.tabela.chaves_primarias:
                valor_coluna = self.objeto_model.__dict__.get(coluna)
                assert valor_coluna, f'Chave primária "{coluna}" não encontrada entre as propriedades do model {model_classe}'

                campo_coluna = list(filter(lambda campo: campo.repr_coluna == coluna, campos_model))

                assert campo_coluna, f'Não existe coluna em {model_classe} com nome {coluna}'
                assert len(campo_coluna) == 1, f'Há mais de uma coluna com nome {coluna} no model {model_classe}'

                campo_coluna = campo_coluna[0]
                largura_max_coluna = campo_coluna.max_length

                chave_dbf += valor_coluna.rjust(largura_max_coluna) if largura_max_coluna else valor_coluna

            return chave_dbf

        setattr(nova_classe, '_chave_dbf', _chave_dbf)

        @property
        def _where_dbf(self):
            """
            String formatada de "where" sql, para ser usado no objeto de DBF.
            :rtype: str
            """
            where_dbf = ""

            model_classe = self._meta.tabela.model
            clausulas_where = []

            for coluna in self._meta.tabela.chaves_primarias:
                valor_coluna = self.objeto_model.__dict__.get(coluna)
                assert valor_coluna, f'Chave primária "{coluna}" não encontrada entre as propriedades do model {model_classe}'

                clausulas_where.append(f"{coluna} = '{valor_coluna}'")

            where_dbf += ' AND '.join(clausulas_where)

            return 'WHERE ' + where_dbf

        setattr(nova_classe, '_where_dbf', _where_dbf)

        @property
        def dbf(self):
            """
            Objeto de DBF preenchido conforme as configurações fornecidas.
            :rtype: Dbf
            """
            obj_dbf = Dbf()
            obj_dbf.filial = self._filial_dbf
            obj_dbf.indice = self._meta.dbf.indice
            obj_dbf.chave = self._chave_dbf
            obj_dbf.where = self._where_dbf
            return obj_dbf

        setattr(nova_classe, 'dbf', dbf)

        return nova_classe

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)

        instance.pre_mapeamento()

        return instance


class InterfaceContatoCliente(metaclass=MetaInterfaceTabela):
    """
    :ivar nome: Nome do contato
    """
    def __init__(self, nome, fone, ativo, solicitante, data_cadastro):

        self.nome = nome
        self.fone = fone
        self.ativo = ativo
        self.solicitante = solicitante
        self.data_cadastro = data_cadastro


    @repr_coluna('data_alteracao')
    def teste(self):
        return datetime.today()

    class Meta:
        model_tabela = ContatoCliente
        chaves_primarias = ['nome', 'fone']
        var_filial_dbf = 'nome'
        indice_dbf = 1
