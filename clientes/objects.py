# coding=utf-8
from types import NoneType

from django.db.models import Model
from django.db.models.base import ModelBase
from django.db.models.fields import IntegerField, FloatField, DecimalField, BooleanField, DateField, DateTimeField

from generico.dbfs import clisockets, Dbf
from generico.functions_genericas import get_pars_socket


def repr_coluna(field_name):
    """
    Marca uma propriedade para representar a coluna informada, para ser corretamente processada em uma InterfaceTabela

    OBS: Já está embutida a marcação da função como uma property, NÃO é necessário envolver com o decorator @property
    """

    def decorator(func):
        func._field_name = field_name
        return property(func)

    return decorator


class ConfigTabela:
    """
    Objeto que contém as meta configurações de tabela

    :cvar model: Model Django do qual a classe pertence
    :type model: Model
    :cvar mapa: Mapa das colunas do model e os seus respetivos campos na classe
    :type mapa: dict
    :cvar chave_primaria: Lista com as colunas que formam a chave primaria da tabela
    :type chave_primaria: list
    """

    mapa = {}
    model = None
    chave_primaria = None

    def __init__(self):
        pass

    @property
    def preenchido(self):
        return self.model is not None and self.chave_primaria != []


class ConfigDbf:
    """
    Objeto que contém as meta configurações de DBF

    :cvar var_filial: Campo que contém valor da filial que será usado no dbf
    :type var_filial: str
    :cvar var_codigo: Campo que contém valor do código que será usado no dbf
    :type var_codigo: str
    :cvar indice: Índice que será usado no dbf
    :type indice: int
    :cvar gera_codigo: Gera código por socket
    :type gera_codigo: bool
    :cvar string_seq_socket: String enviada para o socket, para gerar sequência
    :type string_seq_socket: str
    """

    var_filial = None
    var_codigo = None
    indice = None
    gera_codigo = None
    string_seq_socket = None
    params_str_seq_socket = None

    def __init__(self):
        pass

    @property
    def preenchido(self):
        return self.var_filial is not None and self.indice is not None

    @property
    def consegue_gerar_codigo(self):
        return self.var_filial is not None and self.var_codigo is not None and self.string_seq_socket is not None


class MetaConfig:
    """
    Objeto que contém as meta configurações de uma classe
    """
    tabela = ConfigTabela()
    dbf = ConfigDbf()

    def __init__(self):
        pass


class MetaInterfaceTabela(type):
    def __new__(cls, name, bases, dct):

        config = MetaConfig()

        attrs_config = dct.get('Meta', None)

        if attrs_config:
            cls._configurar_meta(config, attrs_config)

            del dct['Meta']

        dct['_meta'] = config

        nova_classe = super(MetaInterfaceTabela, cls).__new__(cls, name, bases, dct)

        cls._adicionar_metodos(nova_classe)

        return nova_classe

    def __call__(cls, *args, **kwargs):
        instance = super(MetaInterfaceTabela, cls).__call__(*args, **kwargs)

        instance.pre_mapeamento()

        if instance._meta.dbf.gera_codigo:
            instance.get_codigo()

        return instance

    @staticmethod
    def _configurar_meta(config, attrs_config):
        """
        Configura o objeto MetaConfig com base nos atributos definidos na classe Meta.
        """

        attr_model = 'model_tabela'
        attr_mapa_tabela = 'mapa_tabela'
        attr_chave_primaria = 'chave_primaria'
        attr_indice_dbf = 'indice_dbf'
        attr_var_filial_dbf = 'var_filial_dbf'
        attr_var_codigo_dbf = 'var_codigo_dbf'
        attr_str_seq_socket = 'string_seq_socket'
        attr_params_str_seq_socket = 'params_str_seq_socket'
        attr_gera_codigo_sckt = 'gera_codigo_socket'

        if hasattr(attrs_config, attr_model):
            model_tabela = getattr(attrs_config, attr_model)
            assert isinstance(model_tabela, (ModelBase, NoneType)), '"{0}" deve ser um model Django.'.format(attr_model)
            config.tabela.model = model_tabela

        if hasattr(attrs_config, attr_mapa_tabela):
            config.tabela.mapa = getattr(attrs_config, attr_mapa_tabela)

        if hasattr(attrs_config, attr_chave_primaria):
            chave_primaria = getattr(attrs_config, attr_chave_primaria)
            config.tabela.chave_primaria = (chave_primaria if isinstance(chave_primaria, (list, tuple))
                                            else (chave_primaria,))

        if hasattr(attrs_config, attr_indice_dbf):
            config.dbf.indice = getattr(attrs_config, attr_indice_dbf)

        if hasattr(attrs_config, attr_var_filial_dbf):
            config.dbf.var_filial = getattr(attrs_config, attr_var_filial_dbf)

        if hasattr(attrs_config, attr_var_codigo_dbf):
            config.dbf.var_codigo = getattr(attrs_config, attr_var_codigo_dbf)

        if hasattr(attrs_config, attr_str_seq_socket):
            config.dbf.string_seq_socket = getattr(attrs_config, attr_str_seq_socket)

        if hasattr(attrs_config, attr_params_str_seq_socket):
            params_str_seq_socket = getattr(attrs_config, attr_params_str_seq_socket)
            assert isinstance(params_str_seq_socket, (tuple, list, dict)), ('"{0}" deve ser tupla, lista ou dict'
                                                                            .format(attr_params_str_seq_socket))
            config.dbf.params_str_seq_socket = params_str_seq_socket

        if hasattr(attrs_config, attr_gera_codigo_sckt):
            gera_codigo_sckt = getattr(attrs_config, attr_gera_codigo_sckt)
            assert isinstance(gera_codigo_sckt, bool), 'Propriedade "gera_codigo_socket" deve ser boolean.'
            config.dbf.gera_codigo = gera_codigo_sckt

            if gera_codigo_sckt:
                assert config.dbf.consegue_gerar_codigo, ('Para gerar código via socket, é necessário configurar os'
                                                          ' parâmetros "var_filial_dbf", "var_codigo_dbf" e '
                                                          '"string_seq_socket"')

    @staticmethod
    def _adicionar_metodos(nova_classe):
        """
        Adiciona métodos como pre_mapeamento, get_codigo, etc. à nova classe.
        """
        def pre_mapeamento(self):
            """
            Função que realiza o pré-mapeamento da tabela

            Detalhes:
                Processa os atributos com decorator "repr_coluna" ou com o mesmo nome da coluna do model.

            Ordem de prioridades:
                1. Propriedade "mapa_tabela" da classe Meta
                2. Atributos com decorator @repr_coluna
                3. Atributos com o mesmo nome da coluna
            """
            config_tabela = self._meta.tabela
            mapa_tabela = config_tabela.mapa
            instancia_model = config_tabela.model()

            atributos_classe = dir(self)

            for nome_atributo in atributos_classe:
                if nome_atributo in mapa_tabela:
                    continue

                if nome_atributo.startswith('_'):
                    continue

                try:
                    atributo = getattr(self.__class__, nome_atributo)
                except AttributeError:
                    atributo = getattr(self, nome_atributo)

                # Verifica se é uma propriedade ou uma função/método
                if isinstance(atributo, property) or callable(atributo):
                    continue

                # Verifica se o atributo tem o atributo '_field_name'
                if hasattr(atributo, '_field_name'):
                    mapa_tabela[atributo._field_name] = nome_atributo

                # Verifica se o nome do atributo está no dicionário de atributos do model
                elif nome_atributo in instancia_model.__dict__.keys():
                    mapa_tabela[nome_atributo] = nome_atributo

        setattr(nova_classe, 'pre_mapeamento', pre_mapeamento)

        def get_codigo(self):
            """
            Responsável por gerar o código do objeto, quando a tabela depende que seja gerado código via socket

            Depende dos getters:
                - _codigo_dbf
                - _filial_dbf
                - _string_seq_socket
            """

            codigo = self._codigo_dbf
            filial = self._filial_dbf

            assert not codigo, ('Código do contrato já gerado: {0}'.format(codigo))
            assert filial, ('A geração do código depende da filial, defina primeiro a filial antes de chamar '
                            'esta função')

            hostname_sckt, porta_sckt = get_pars_socket()

            string_sequencia_socket = self._string_seq_socket
            retorno_socket = clisockets(hostname_sckt, string_sequencia_socket, porta_sckt)
            sequencia = str(retorno_socket).strip()

            if not sequencia.isdigit():
                raise Exception("Erro ao buscar sequência do tab_seq: %s" % sequencia)

            self.__dict__[self._meta.dbf.var_codigo] = int(sequencia)

        setattr(nova_classe, 'get_codigo', get_codigo)

        @property
        def model(self):
            """
            :return: Model representado pela classe
            :rtype: ModelBase
            """
            return self._meta.tabela.model

        setattr(nova_classe, 'model', model)

        @property
        def _string_seq_socket(self):
            config_dbf = self._meta.dbf

            string_seq_socket = 'VBSrv:' + config_dbf.string_seq_socket

            if config_dbf.params_str_seq_socket:
                params_str_seq = config_dbf.params_str_seq_socket

                if type(params_str_seq) == dict:
                    if '{filial}' in string_seq_socket and 'filial' not in params_str_seq:
                        params_str_seq['filial'] = self._filial_dbf

                    return string_seq_socket.format(**params_str_seq)

                elif type(params_str_seq) == tuple or type(params_str_seq) == list:
                    if '{filial}' in string_seq_socket:
                        return string_seq_socket.format(*params_str_seq, filial=self._filial_dbf)
                    else:
                        return string_seq_socket.format(*params_str_seq)

            else:
                return string_seq_socket.format(filial=self._filial_dbf) if '{filial}' in string_seq_socket \
                    else string_seq_socket

        setattr(nova_classe, '_string_seq_socket', _string_seq_socket)

        @property
        def _filial_dbf(self):
            """
            :return: Filial para ser usada no objeto de DBF
            :rtype: str
            """
            var_filial = self._meta.dbf.var_filial
            assert var_filial in dir(self), 'Não há variável com nome "{0}" na classe'.format(var_filial)
            return self.__dict__.get(var_filial)

        setattr(nova_classe, '_filial_dbf', _filial_dbf)

        @property
        def _codigo_dbf(self):
            """
            :return: Filial para ser usada no objeto de DBF
            :rtype: str
            """
            var_codigo = self._meta.dbf.var_codigo
            assert var_codigo in dir(self), 'Não há variável com nome "{0}" na classe'.format(var_codigo)
            return self.__dict__.get(var_codigo)

        setattr(nova_classe, '_codigo_dbf', _codigo_dbf)

        @property
        def objeto_model(self):
            """
            :return: Objeto do model representado pela classe, com os valores segundo seu mapeamento.
            :rtype: ModelBase
            """

            config_tabela = self._meta.tabela

            objeto = self.model()
            modificou = False

            for coluna in config_tabela.mapa.keys():
                assert hasattr(objeto, coluna), ('Não existe coluna no model {model} '
                                                 'com nome {coluna}').format(model=self.model, coluna=coluna)
                objeto.__dict__[coluna] = self.__dict__.get(config_tabela.mapa.get(coluna))
                modificou = True

            assert modificou, ('Nenhuma variável da classe {classe} bate com os nomes das colunas de '
                               '{model}.\nRenomeie as variáveis ou mapeie a tabela pelo atributo "mapa_tabela" '
                               'da classe Meta').format(classe=self.__name__,
                                                        model=self.model)

            return objeto

        setattr(nova_classe, 'objeto_model', objeto_model)

        @property
        def _chave_dbf(self):
            """
            :return: Valor da chave para ser utilizada no objeto de DBF.
            :rtype: str
            """
            chave_dbf = ''

            model_classe = self._meta.tabela.model
            campos_model = list(model_classe._meta.fields)

            nome_model = model_classe._meta.object_name

            for coluna in self._meta.tabela.chave_primaria:
                try:
                    valor_coluna = self.objeto_model.__dict__.get(coluna)
                except KeyError:
                    raise AssertionError(('Chave primária "{coluna}" não encontrada entre as propriedades '
                                          'do model {model_classe}').format(coluna=coluna,
                                                                            model_classe=nome_model))

                campo_coluna = list(filter(lambda campo: campo.column == coluna, campos_model))

                assert campo_coluna, ('Não existe coluna em {model_classe} com '
                                      'nome {coluna}').format(model_classe=model_classe,
                                                              coluna=coluna)
                assert len(campo_coluna) == 1, ('Há mais de uma coluna com nome {coluna} '
                                                'no model {model_classe}').format(coluna=coluna,
                                                                                  model_classe=nome_model)

                campo_coluna = campo_coluna[0]
                largura_max_coluna = campo_coluna.max_length

                chave_dbf += str(valor_coluna.rjust(largura_max_coluna) if largura_max_coluna else valor_coluna)

            return chave_dbf

        setattr(nova_classe, '_chave_dbf', _chave_dbf)

        @property
        def _where_dbf(self):
            """
            :return: String formatada de "where" sql, para ser usado no objeto de DBF.
            :rtype: str
            """

            model_classe = self._meta.tabela.model
            nome_model = model_classe._meta.object_name
            campos_model = list(model_classe._meta.fields)
            clausulas_where = []

            for coluna in self._meta.tabela.chave_primaria:
                try:
                    coluna_model = filter(lambda campo: campo.column == coluna, campos_model)[0]
                except IndexError:
                    raise ValueError("Coluna '{coluna}' não encontrada no model "
                                     "'{nome_model}'.".format(coluna=coluna,
                                                              nome_model=nome_model))

                valor_coluna = self.objeto_model.__dict__.get(coluna)

                assert valor_coluna, ('Chave primária "{coluna}" não encontrada '
                                      'no model {nome_model}').format(coluna=coluna,
                                                                      nome_model=nome_model)

                if isinstance(coluna_model, (IntegerField, FloatField, DecimalField, BooleanField)):
                    valor_coluna_formatada = str(valor_coluna)
                elif isinstance(coluna_model, DateField):
                    valor_coluna_formatada = "'{0}'".format(valor_coluna.strftime('%d-%m-%Y'))
                elif isinstance(coluna_model, DateTimeField):
                    valor_coluna_formatada = "'{0}'".format(valor_coluna.strftime('%d-%m-%Y:%H:%M:%S'))
                else:
                    valor_coluna_formatada = "'{0}'".format(valor_coluna)

                clausulas_where.append("{coluna} = {valor}".format(coluna=coluna,
                                                                   valor=valor_coluna_formatada))

            where_dbf = ' AND '.join(clausulas_where)

            return where_dbf

        setattr(nova_classe, '_where_dbf', _where_dbf)

        @property
        def dbf(self):
            """
            :return: Objeto de DBF preenchido conforme as configurações fornecidas.
            :rtype: Dbf
            """
            config_dbf = self._meta.dbf
            config_tabela = self._meta.tabela

            if not (config_dbf.var_filial and
                    config_dbf.indice and
                    config_tabela.chave_primaria and
                    config_tabela.model):
                raise AssertionError('Se a tabela depende de DBF, devem ser passadas as propriedades "indice_dbf", '
                                     '"chave_primaria", "var_filial_dbf", "model_tabela"')

            obj_dbf = Dbf()
            obj_dbf.filial = self._filial_dbf
            obj_dbf.indice = self._meta.dbf.indice
            obj_dbf.chave = self._chave_dbf
            obj_dbf.where = self._where_dbf
            obj_dbf.tabela = self._meta.tabela.model._meta.db_table
            return obj_dbf

        setattr(nova_classe, 'dbf', dbf)


class InterfaceTabela(object):
    """
    Interface que representa uma tabela

    Para configurar como a interface se comporta, deve ser definidas suas propriedades na classe Meta

    Propriedades disponíveis:
        - model_tabela: Model Django que representa a tabela

        - mapa_tabela: Dicionário que mapeia as colunas da tabela com seus respectivos atributos presentes na interface. Formato dos valores: nome_coluna: nome_atributo

        - chave_primaria:

        - indice_dbf

        - var_filial_dbf

        - var_codigo_dbf

        - string_seq_socket

        - params_str_seq_socket

        - gera_codigo_socket
    """
    __metaclass__ = MetaInterfaceTabela

    class Meta:
        model_tabela = None
        chave_primaria = None
        gera_codigo_socket = False
        string_seq_socket = None
        var_filial_dbf = None
        var_codigo_dbf = None
        indice_dbf = None
        mapa_tabela = {}
