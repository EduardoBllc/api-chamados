from django.contrib import admin
from .models import *


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


@admin.register(ContatoCliente)
class ContatoClienteAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'filial_id', 'nome', 'fone', 'data_nascimento', 'ativo', 'solicitante', 'data_cadastro', 'data_alteracao')
    search_fields = ('__all__',)
    list_filter = ('ativo', 'solicitante', 'data_cadastro')


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'auth_user_id', 'ativo', 'setor', 'desenvolvedor', 'data_cadastro', 'data_alteracao')
    search_fields = ('nome', 'setor')
    list_filter = ('ativo', 'desenvolvedor', 'data_cadastro')


@admin.register(TipoAlteracao)
class TipoAlteracaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo',)


@admin.register(CategoriaChamado)
class CategoriaChamadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo',)


@admin.register(SubcategoriaChamado)
class SubcategoriaChamadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo',)


@admin.register(TipoChamado)
class TipoChamadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'retrabalho', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo', 'retrabalho')


@admin.register(StatusProjeto)
class StatusProjetoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo',)


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'descricao', 'descricao_resumida', 'data_solicitacao', 'tempo_previsao', 'data_finalizacao', 'status_id')
    search_fields = ('descricao', 'descricao_resumida')
    list_filter = ('data_solicitacao', 'status_id')


@admin.register(StatusChamado)
class StatusChamadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo',)


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'descricao', 'descricao_resumida', 'subcategoria_id', 'tipo_chamado_id', 'solicitante_id',
        'data_abertura',
        'data_finalizacao', 'projeto_id', 'prioridade', 'status_id')
    search_fields = ('descricao', 'descricao_resumida')
    list_filter = ('data_abertura', 'status_id', 'prioridade')


@admin.register(AlteracaoChamado)
class AlteracaoChamadoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'chamado_id', 'descricao', 'data_cadastro', 'tempo_trabalhado', 'usuario_id', 'tipo_alteracao_id')
    search_fields = ('descricao',)
    list_filter = ('data_cadastro', 'tipo_alteracao_id')
