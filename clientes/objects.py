from django.db.models import Model
from django.db.models.base import ModelBase

from chamados.models import Chamado, ContatoCliente


class MetaConfigs:

    model_tabela = None,
    mapa_tabela = {}
    mapa_form = {}
    usa_dbf = False
    chaves_primarias = []
    filial_dbf = ''
    indice_dbf = None

class Dbf:
    filial = ''
    indice = 0
    where = ''
    chave = ''

class BaseMeta(type):
    def __new__(cls, name, bases, dct):

        dct['_filial_dbf'] = ''

        configs = MetaConfigs()

        configs_filho = dct.get('Configs', None)

        if configs_filho:
            if hasattr(configs_filho, 'model_tabela'):
                model_tabela = getattr(configs_filho, 'model_tabela')
                assert isinstance(model_tabela, ModelBase), 'model_tabela deve ser um model do Django'
                configs.model_tabela = getattr(configs_filho, 'model_tabela')

            if hasattr(configs_filho, 'mapa_tabela'):
                configs.mapa_tabela = getattr(configs_filho, 'mapa_tabela')

            if hasattr(configs_filho, 'mapa_form'):
                configs.mapa_tabela = getattr(configs_filho, 'mapa_form')

            if hasattr(configs_filho, 'indice_dbf'):
                configs.indice_dbf = getattr(configs_filho, 'indice_dbf')

            if hasattr(configs_filho, 'chaves_primarias'):
                configs.chaves_primarias = getattr(configs_filho, 'chaves_primarias')


            if hasattr(configs_filho, 'filial_dbf'):
                configs.filial_dbf = getattr(configs_filho, 'filial_dbf')

            if hasattr(configs_filho, 'usa_dbf'):
                usa_dbf = getattr(configs_filho, 'usa_dbf')
                assert isinstance(usa_dbf, bool), 'Propriedade "usa_dbf" deve ser boolean'

                if usa_dbf and not (hasattr(configs_filho, 'model_tabela') and
                                    hasattr(configs_filho, 'chaves_primarias') and
                                    hasattr(configs_filho, 'indice_dbf') and
                                    hasattr(configs_filho, 'filial_dbf')):

                    raise AssertionError('Se a tabela depende de DBF, deve ser passadas as propriedades "indice_dbf", '
                                         '"chaves_primarias", filial_dbf e "model_tabela"')

            else:
                usa_dbf = False

            configs.usa_dbf = usa_dbf

            del dct['Configs']

        dct['_configs'] = configs

        nova_classe = super().__new__(cls, name, bases, dct)

        @property
        def model(self):
            return self._meta['model_tabela']

        nova_classe.model = model

        @property
        def _filial_dbf(self):
            return self.__dict__[self._configs.filial_dbf]

        nova_classe._filial_dbf = _filial_dbf

        @property
        def objeto_model(self):
            objeto = self._configs.model_tabela()

            for coluna in objeto.__dict__.keys():
                if not coluna.startswith('_'):
                    if hasattr(self, coluna):
                        objeto.__dict__[coluna] = getattr(self, coluna)

            for coluna in self._configs.mapa_tabela.keys():
                assert hasattr(objeto, coluna), (f'Não existe coluna no model {self._configs.model_tabela} '
                                                 f'com nome {coluna}')
                objeto.__dict__[coluna] = self.__dict__[self._configs.mapa_tabela[coluna]]

            return objeto

        nova_classe.objeto_model = objeto_model

        @property
        def _chave_dbf(self):
            chave_dbf = ''

            model_classe = self._configs.model_tabela
            campos_model = list(model_classe._meta.fields)

            for coluna in self._configs.chaves_primarias:
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
            dbf = Dbf()
            dbf.filial = self._filial_dbf
            dbf.indice = self._configs.indice_dbf
            dbf.chave = self._chave_dbf
            # dbf.where = self._where_dbf
            return dbf

        nova_classe.dbf = dbf

        return nova_classe


class TesteMetaclasse(metaclass=BaseMeta):

    def __init__(self):
        self.filial = '001'
        self.fone = '99999-9999'
        self.contato = 'Ademir'

    class Configs:
        usa_dbf = True
        model_tabela = ContatoCliente
        indice_dbf = 1
        chaves_primarias = ['fone', 'solicitante']
        filial_dbf = 'filial'
        mapa_tabela = {
            'solicitante': 'contato',
        }


