# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from clientes.models import ContatoCliente


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    auth_user_id = models.ForeignKey(User,
                                     on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True,
                                verbose_name='Ativo')
    setor = models.CharField(max_length=30,
                             verbose_name='Setor')
    desenvolvedor = models.BooleanField(default=False,
                                        verbose_name='Usuário atua ou não como desenvolvedor')
    data_cadastro = models.DateField(auto_now=True,
                                     verbose_name='Data de cadastro')
    data_alteracao = models.DateField(auto_now_add=True,
                                      verbose_name='Data da última alteração')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = u'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class TipoAlteracao(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    ativo = models.BooleanField(default=True,
                                verbose_name='Ativo')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = u'alteracoes_tipos'
        verbose_name = 'Tipo de Alteração'
        verbose_name_plural = 'Tipos de Alteração'


class CategoriaChamado(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    ativo = models.BooleanField(default=True,
                                verbose_name='Ativo')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = u'chamados_categorias'
        verbose_name = 'Categoria de Chamado'
        verbose_name_plural = 'Categorias de Chamado'


class SubcategoriaChamado(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    ativo = models.BooleanField(default=True,
                                verbose_name='Ativo')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = u'chamados_subcategorias'
        verbose_name = 'Subcategoria de Chamado'
        verbose_name_plural = 'Subcategorias de Chamado'


class TipoChamado(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    retrabalho = models.BooleanField(default=False,
                                     verbose_name='Se é ou não retrabalho')
    ativo = models.BooleanField(default=True,
                                verbose_name='Ativo')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = u'chamados_tipos'
        verbose_name = 'Tipo de Chamado'
        verbose_name_plural = 'Tipos de Chamado'


class StatusProjeto(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    ativo = models.BooleanField(default=True,
                                verbose_name='Ativo')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = u'projetos_status'
        verbose_name = 'Status de projeto'
        verbose_name_plural = 'Status de projeto'


class Projeto(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.TextField(verbose_name='Decrição completa')
    descricao_resumida = models.TextField(verbose_name='Descrição resumida')
    data_solicitacao = models.DateField(verbose_name='Data de cadastro')
    tempo_previsao = models.DurationField(verbose_name='Tempo previsto para desenvolvimento')
    data_finalizacao = models.DateField(null=True,
                                        blank=True,
                                        verbose_name='Data de finalização')
    status_id = models.ForeignKey(StatusProjeto,
                                  on_delete=models.PROTECT)

    def __str__(self):
        return self.id

    class Meta:
        db_table = u'projetos'
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'


class StatusChamado(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    ativo = models.BooleanField(default=True,
                                verbose_name='Ativo')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = u'chamados_status'
        verbose_name = 'Status de Chamado'
        verbose_name_plural = 'Status de Chamado'


class Chamado(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.TextField(verbose_name='Decrição completa')
    descricao_resumida = models.TextField(verbose_name='Descrição resumida')
    subcategoria_id = models.ForeignKey(SubcategoriaChamado,
                                        on_delete=models.PROTECT)
    tipo_chamado_id = models.ForeignKey(TipoChamado,
                                        on_delete=models.PROTECT)
    solicitante_id = models.ForeignKey(ContatoCliente,
                                       on_delete=models.PROTECT)
    data_abertura = models.DateField(verbose_name='Data de cadastro')
    data_finalizacao = models.DateField(null=True,
                                        blank=True,
                                        verbose_name='Data de finalização')
    projeto_id = models.ForeignKey(Projeto,
                                   null=True,
                                   blank=True,
                                   on_delete=models.CASCADE)
    prioridade = models.IntegerField(default=0,
                                     verbose_name='Nível de prioridade')
    status_id = models.ForeignKey(StatusChamado,
                                  on_delete=models.PROTECT)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = u'chamados'
        verbose_name = 'Chamado'
        verbose_name_plural = 'Chamados'


class AlteracaoChamado(models.Model):
    id = models.AutoField(primary_key=True)
    chamado_id = models.ForeignKey(Chamado,
                                   on_delete=models.CASCADE)
    descricao = models.TextField(verbose_name='Decrição completa')
    data_cadastro = models.DateTimeField(verbose_name='Data de registro')
    tempo_trabalhado = models.DurationField(verbose_name='Tempo trabalhado')
    usuario_id = models.ForeignKey(Usuario,
                                   on_delete=models.PROTECT)
    tipo_alteracao_id = models.ForeignKey(TipoAlteracao,
                                          on_delete=models.PROTECT)

    def __str__(self):
        return f'Chamado {self.chamado_id} - Alteração {self.id}'

    class Meta:
        db_table = u'chamados_alteracoes'
        verbose_name = 'Alteração de Chamado'
        verbose_name_plural = 'Alterações de Chamado'
