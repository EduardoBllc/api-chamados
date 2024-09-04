# coding=utf-8
from clientes.objects import InterfaceContatoCliente, InterfaceUsuario


class ComponenteBase(object):
    def __init__(self, interface, multiplo=False, args=None, condicional=False):
        if not args:
            args = ()
        elif not isinstance(args, (list, tuple)):
            args = args,

        self.interface = interface
        self._multiplo = multiplo
        self.args = args
        self._condicional = condicional

    @property
    def multiplo(self):
        return self._multiplo

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, args):
        if args and not isinstance(args, (list, tuple)):
            args = args,

        self._args = args

    @property
    def condicional(self):
        return self._condicional

    @property
    def instancia(self):
        return self.interface(*self.args)


class ComponenteCondicional(ComponenteBase):
    @property
    def obrigatorio(self):
        return False


class ComponenteObrigatorio(ComponenteBase):
    @property
    def obrigatorio(self):
        return True


class ComponenteMultiplo(ComponenteBase):

    def __init__(self, interface, args=None, condicional=False, qtd_minima=0):
        super(ComponenteMultiplo, self).__init__(interface,
                                                 multiplo=True,
                                                 args=args,
                                                 condicional=condicional)

        self._qtd_minima = qtd_minima

    @property
    def multiplo(self):
        return True

    @property
    def qtd_minima(self):
        return self._qtd_minima

    @property
    def instancia(self):
        return [self.interface(nro=i) for i in range(self.qtd_minima)]


class MetaInterfaceObjeto(type):
    def __new__(cls, name, bases, attrs):
        nova_classe = super(MetaInterfaceObjeto, cls).__new__(cls, name, bases, attrs)

        nova_classe._componentes = {}

        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, ComponenteBase):
                nova_classe._componentes[attr_name] = attr_value

        return nova_classe

    def __call__(cls, *args, **kwargs):
        instancia = super(MetaInterfaceObjeto, cls).__call__(*args, **kwargs)

        for chave, componente in cls._componentes.items():
            if chave in kwargs:
                valor_kwargs = kwargs[chave]
                assert isinstance(valor_kwargs, componente.interface), (
                    '{} não é do tipo {}'.format(componente, componente.interface.__name__))

                setattr(instancia, chave, valor_kwargs)
            else:
                setattr(instancia, chave, componente.instancia)

        return instancia


class InterfaceObjeto(object):
    __metaclass__ = MetaInterfaceObjeto


class ObjContrato(InterfaceObjeto):
    filial = ''
    codigo = 0
    codigo_cliente = 0
    filial_cliente = ''
    valor = 0
    data_emissao = None
    cod_banco = 0
    observacao = ''

    contrato_complementado = 0

    def __init__(self, filial):
        self.cabecalho.args = filial

    cabecalho = ComponenteObrigatorio(InterfaceUsuario)
    parcelas = ComponenteMultiplo(InterfaceContatoCliente, qtd_minima=2)
