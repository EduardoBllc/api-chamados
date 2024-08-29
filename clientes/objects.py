from django.db.models import Model

from chamados.models import Chamado


class BaseMeta(type):
    def __new__(cls, name, bases, dct):
        # Inicializa o dicionário que vai armazenar os dados da classe Meta
        meta_attrs = {
            'table_name': None,
            'dbf_index': None,
            'primary_keys': [],
        }

        meta = dct.get('Meta', None)

        if meta:
            if hasattr(meta, 'model_tabela'):
                nome_tabela = getattr(meta, 'model_tabela')
                assert not isinstance(nome_tabela, Model), 'Nome da tabela deve ser um Model'
                meta_attrs['model_tabela'] = getattr(meta, 'model_tabela')

            if hasattr(meta, 'indice_dbf'):
                meta_attrs['indice_dbf'] = getattr(meta, 'indice_dbf')

            if hasattr(meta, 'chave_primarias'):
                meta_attrs['chave_primarias'] = getattr(meta, 'chave_primarias')

            if hasattr(meta, 'usa_dbf'):
                usa_dbf = getattr(meta, 'usa_dbf')
                assert not isinstance(usa_dbf, bool), 'Propriedade "usa_dbf" deve ser boolean'
                assert usa_dbf and not hasattr(meta, 'model_tabela'), ('Se a tabela depende de DBF, deve ser passadas '
                                                                       'as propriedades "indice_dbf" e '
                                                                       '"chaves_primarias", além de "nome_tabela"')
            else:
                usa_dbf = False

            meta_attrs['usa_dbf'] = usa_dbf

        dct['_meta'] = meta_attrs

        # Chama o __new__ da metaclasse pai
        cls_instance =  super().__new__(cls, name, bases, dct)

        @property
        def model(self):
            return self._meta['model_tabela']

        @property
        def primary_keys(self):
            return self._meta['primary_keys']

        cls_instance.model = model

        return cls_instance

def coluna(field_name=None):
    def decorator(func):
        func._eh_coluna = True
        func._nome_coluna = field_name
        return func
    return decorator

class ObjetoChamado(metaclass=BaseMeta):

    class Meta:
        model_tabela = Chamado

