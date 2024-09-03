# Representação de Tabela

É uma classe que representa uma tabela do sistema, para facilitar alguns procidementos repetitivos
como gravações em DBF, geração de sequência via socket, e preenchimento da instância do seu Model Django

## Utilização

Pode ser utilizada com a classe de RepresentacaoObjeto como um componente, ou isolada.

Exemplo de utilização isolada:

```python
# coding=utf-8
from financeiro.contas_a_receber.entrada_contas_a_receber.objects import ObservacaoContrato

observacao_contrato = ObservacaoContrato()
observacao_contrato.observacao = 'Exemplo de observação'
observacao_contrato.codigo_contrato = 123456
observacao_contrato.filial_contrato = '001'

# Isso retornará uma instância do model CtoObs com as propriedades setadas acima
obj_model_observacao = observacao_contrato.objeto_model

# Isso retornará uma instância do objeto Dbf conforme as propriedades setadas acima
obj_dbf_observacao = observacao_contrato.dbf
```

## Criação

Para criar uma representaçãode de tabela, é necessário criar uma classe que herda de [RepresentacaoTabela](representacao_tabela.py),
e moldar o seu comportamento através dos atributos da sua classe Meta (semelhante a como é feito com os models do Django).

### Atributos configuráveis

* `model_tabela: Model`: Model Django que representa a tabela
* `mapa_tabela: dict`: Dicionário que mapeia as colunas da tabela com os seus respetivos atributos presentes 
na interface. Formato dos valores: nome_coluna: nome_atributo.
* `chave_primaria: str | tuple | list`: Nomes das colunas que compoem a chave primária, em string, para chaves 
únicas compostas de uma coluna só, ou tupla/lista para chaves composta de mais de uma coluna. **IMPORTANTE**: A ordem em
que as colunas são passadas importa. Será a ordem em que os seus valores serão inseridos na string de gravação/deleção do DBF.
* `indice_dbf: int` : Indice usado no DBF
* `var_filial_dbf: string`: **Nome** da variável que será usada como filial no DBF.
* `var_codigo_dbf: string`: **Nome** da variável que será usada como código no DBF, OBS: A variável de código deve estar declarada
na declaração da classe, não só no método __init\__.
* `string_seq_socket: str`: String usada para chamar a geração de sequência via socket
* `params_str_seq_socket: tuple | list | dict`: Parâmetros de formatação da string de geração de sequência. 
Pode ser tupla/lista para argumentos posicionais ou dicionário para argumentos nomeados
* `gera_codigo_socket: bool`: Se gera ou não sequência do código via socket ao instânciar a classe de interface

### Exemplos

Representação da AutCto:

```python
class RepresentacaoAutCto(RepresentacaoTabela):
    codigo = None

    cto_cod_vd = 0
    cto_op = 1

    nro_parcelas = None
    valor = None
    data_emissao = None
    codigo_cliente = None
    filial_cliente = None

    def __init__(self, filial):
        self.filial = filial

    class Meta:
        model_tabela = AutCto
        chave_primaria = 'cto_loja', 'cto_cod_ct'
        gera_codigo_socket = True
        string_seq_socket = 'SEQVENDA:{filial}S1'
        var_filial_dbf = 'filial'
        var_codigo_dbf = 'codigo'
        indice_dbf = 1
        mapa_tabela = {
            'cto_loja': 'filial',
            'cto_cod_ct': 'codigo',
            'cto_vlr_ct': 'valor',
            'cto_vlr_ab': 'valor',
            'cto_num_pr': 'nro_parcelas',
            'cto_dat_em': 'data_emissao',
        }
```