from django.contrib import admin

from clientes.models import TipoCliente, Cliente, Filial


@admin.register(TipoCliente)
class TipoClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao')
    search_fields = ('descricao',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo', 'data_cadastro', 'data_alteracao', 'tipo_id')
    search_fields = ('nome',)

    list_filter = ('ativo', 'data_cadastro', 'tipo_id')


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_id', 'nome', 'fone', 'matriz', 'ativo', 'data_cadastro', 'data_alteracao')
    search_fields = ('nome', 'fone')
    list_filter = ('ativo', 'matriz', 'data_cadastro')
