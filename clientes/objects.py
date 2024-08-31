from django.db.models import Model
from django.db.models.base import ModelBase

from chamados.models import Chamado, ContatoCliente


class ConfigTabela:
    def __init__(self, model: ModelBase = None, mapa: dict = None, chaves_primarias: list | tuple = None):
        """
        Classe que contém as meta configurações de tabela

        :param model: Model Django do qual a classe pertence
        :type model: ModelBase
        :param mapa: Mapa das colunas do model e seus respectivos campos na classe
        :type mapa: dict
        :param chaves_primarias: Lista com as colunas que formam a chave primaria da tabela
        :type chaves_primarias: list
        """

        self.model = model
        self.mapa = mapa
        self.chaves_primarias = chaves_primarias


class ConfigDbf:
    def __init__(self, var_filial: str = None, indice: int = None):
        """
        Classe que contém as meta configurações de DBF

        :param var_filial: Campo que contém valor da filial que será usado no dbf
        :type var_filial: str
        :param indice: Índice que será usado no dbf
        """
        assert isinstance(var_filial, str), 'Parâmetro "campo_filial" deve ser uma string'
        assert isinstance(indice, int), 'Parâmetro "indice" deve ser um inteiro'

        self.var_filial = var_filial
        self.indice = indice


class MetaConfig:
    """
    Objeto que contém as meta configurações de uma classe
    """
    mapa_form = {}
    tabela: ConfigTabela = ConfigTabela()
    usa_dbf: bool = False
    dbf: ConfigDbf = ConfigDbf()


class Dbf:
    filial = ''
    indice = 0
    where = ''
    chave = ''


class BaseMeta(type):
    def __new__(cls, name, bases, dct):

        dct['_filial_dbf'] = ''

        config = MetaConfig()

        attr_config = dct.get('Configs', None)

        if attr_config:
            if hasattr(attr_config, 'model_tabela'):
                model_tabela = getattr(attr_config, 'model_tabela')
                assert isinstance(model_tabela, ModelBase), 'model_tabela deve ser um model do Django'
                config.tabela.model = model_tabela

            if hasattr(attr_config, 'mapa_tabela'):
                config.tabela.mapa = getattr(attr_config, 'mapa_tabela')

            if hasattr(attr_config, 'chaves_primarias'):
                config.tabela.chaves_primarias = getattr(attr_config, 'chaves_primarias')

            if hasattr(attr_config, 'mapa_form'):
                config.mapa_form = getattr(attr_config, 'mapa_form')

            if hasattr(attr_config, 'indice_dbf'):
                config.dbf.indice = getattr(attr_config, 'indice_dbf')

            if hasattr(attr_config, 'var_filial_dbf'):
                config.dbf.var_filial = getattr(attr_config, 'var_filial_dbf')

            if hasattr(attr_config, 'usa_dbf'):
                usa_dbf = getattr(attr_config, 'usa_dbf')
                assert isinstance(usa_dbf, bool), 'Propriedade "usa_dbf" deve ser boolean'

                if usa_dbf and not (hasattr(attr_config, 'model_tabela') and
                                    hasattr(attr_config, 'chaves_primarias') and
                                    hasattr(attr_config, 'indice_dbf') and
                                    hasattr(attr_config, 'var_filial_dbf')):
                    raise AssertionError('Se a tabela depende de DBF, deve ser passadas as propriedades "indice_dbf", '
                                         '"chaves_primarias", "var_filial_dbf" e "model_tabela"')

            else:
                usa_dbf = False

            config.usa_dbf = usa_dbf

            del dct['Configs']

        dct['_configs'] = config

        nova_classe = super().__new__(cls, name, bases, dct)

        @property
        def model(self):
            return self._meta['model_tabela']

        nova_classe.model = model

        @property
        def _filial_dbf(self):
            var_filial = self._configs.dbf.var_filial
            assert var_filial in self.__dict__.keys(), f'Não há variável com nome "{var_filial}" na classe'
            return self.__dict__[var_filial]

        nova_classe._filial_dbf = _filial_dbf

        @property
        def objeto_model(self):
            objeto = self._configs.tabela.model()

            for coluna in objeto.__dict__.keys():
                if not coluna.startswith('_'):
                    if hasattr(self, coluna):
                        objeto.__dict__[coluna] = getattr(self, coluna)

            for coluna in self._configs.tabela.model.keys():
                assert hasattr(objeto, coluna), (f'Não existe coluna no model {self._configs.tabela.model} '
                                                 f'com nome {coluna}')
                objeto.__dict__[coluna] = self.__dict__[self._configs.tabela.mapa[coluna]]

            return objeto

        nova_classe.objeto_model = objeto_model

        @property
        def _chave_dbf(self):
            chave_dbf = ''

            model_classe = self._configs.tabela.model
            campos_model = list(model_classe._meta.fields)

            for coluna in self._configs.tabela.chaves_primarias:
                valor_coluna = self.objeto_model.__dict__.get(coluna)
                assert valor_coluna, f'Chave primária {coluna} não encontrada entre as propriedades do model {model_classe}'

                campo_coluna = list(filter(lambda campo: campo.column == coluna, campos_model))

                assert campo_coluna, f'Não existe coluna em {model_classe} com nome {coluna}'
                assert len(campo_coluna) == 1, f'Há mais de uma coluna com nome {coluna} no model {model_classe}'

                campo_coluna = campo_coluna[0]
                largura_max_coluna = campo_coluna.max_length

                chave_dbf += valor_coluna.rjust(largura_max_coluna) if largura_max_coluna else valor_coluna

            return chave_dbf

        nova_classe._chave_dbf = _chave_dbf

        @property
        def dbf(self):
            obj_dbf = Dbf()
            obj_dbf.filial = self._filial_dbf
            obj_dbf.indice = self._configs.indice
            obj_dbf.chave = self._chave_dbf
            # dbf.where = self._where_dbf
            return obj_dbf

        nova_classe.dbf = dbf

        def fetch_form(self):
            mapa_form = self._configs.mapa_form

        return nova_classe


class TesteMetaclasse(metaclass=BaseMeta):

    def __init__(self):
        pass