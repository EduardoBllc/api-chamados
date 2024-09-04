# coding=utf-8
from datetime import datetime

from chamados.models import Usuario
from clientes.interfaces.representacao_tabela import RepresentacaoTabela
from clientes.models import ContatoCliente

class AttrConectadoBase(object):

    def __init__(self,
                 correspondente,
                 valor_def=None):
        self._correspondente = correspondente
        self._valor_def = valor_def

    @property
    def correspondente(self):
        return self._correspondente

    @property
    def valor_def(self):
        return self._valor_def


class AtributoTabelaMeta(type):
    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in list(attrs.items()):
            if isinstance(attr_value, AtributoTabela):
                if attr_value._coluna_correspondente == '':
                    attr_value._coluna_correspondente = attr_name

                attrs[attr_name] = attr_value
            elif isinstance(attr_value, (list, dict, int, str, bool, type(None))):
                attrs[attr_name] = AtributoTabela(attr_name, valor_def=attr_value)

        return super(AtributoTabelaMeta, cls).__new__(cls, name, bases, attrs)


class AtributoTabela(AttrConectadoBase, metaclass=AtributoTabelaMeta):

    _indice_pk_atual = 0
    _auto_nomeado = False

    def __init__(self,
                 coluna,
                 valor_def=None,
                 filial_dbf=False,
                 codigo_dbf=False,
                 chave_primaria=False,
                 ordem_pks=None):

        super().__init__(coluna, valor_def)
        self._chave_primaria = chave_primaria
        self._filial_dbf = filial_dbf
        self._codigo_dbf = codigo_dbf

        if chave_primaria and not ordem_pks:
            self._ordem_pks = AtributoTabela._indice_pk_atual
            AtributoTabela._indice_pk_atual += 1


    @property
    def chave_primaria(self):
        return self._chave_primaria

    @property
    def filial_dbf(self):
        return self._filial_dbf

    @property
    def codigo_dbf(self):
        return self._codigo_dbf

    @property
    def ordem_pks(self):
        return self._ordem_pks

    @staticmethod
    def auto_nomeado(valor_def=None,
                     filial_dbf=False,
                     codigo_dbf=False,
                     chave_primaria=False,
                     ordem_pks=None):

        atributo =  AtributoTabela(None,
                                   valor_def,
                                   filial_dbf,
                                   codigo_dbf,
                                   chave_primaria,
                                   ordem_pks)
        atributo._auto_nomeado = True
        return atributo


class InterfaceContatoCliente(RepresentacaoTabela):

    nome_cliente = AtributoTabela('nome', chave_primaria=True, filial_dbf=True)
    fone_cliente = AtributoTabela('fone', chave_primaria=True, codigo_dbf=True)
    esta_ativo = AtributoTabela('esta_ativo', valor_def=True)
    datinha = AtributoTabela('data_cadastro', valor_def=datetime.today())

    class Meta:
        model_tabela = ContatoCliente
        indice_dbf = 1


class InterfaceUsuario(RepresentacaoTabela):
    nome_usu = AtributoTabela('nome', chave_primaria=True, filial_dbf=True)
    setor_usu = AtributoTabela('setor', chave_primaria=True, codigo_dbf=True)
    ativooo = AtributoTabela.auto_nomeado(valor_def=True)
    datona = None

    class Meta:
        model_tabela = Usuario
        chave_primaria = 'setor', 'nome'
        var_filial_dbf = 'setor_usu'
        indice_dbf = 0
        mapa_tabela = {
            'nome': 'nome_usu',
            'setor': 'setor_usu',
            'ativo': 'ativooo',
            'data_cadastro': 'datona'
        }