# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class TipoCliente(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=30,
                                 verbose_name='Nome')

    class Meta:
        db_table = u'clientes_tipos'
        verbose_name = 'Tipo de Cliente'
        verbose_name_plural = 'Tipos de Cliente'

    def __str__(self):
        return self.descricao


class Cliente(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    ativo = models.BooleanField(default=True,
                                verbose_name='Ativo')
    data_cadastro = models.DateField(auto_now=True,
                                     verbose_name='Data de cadastro')
    data_alteracao = models.DateField(auto_now_add=True,
                                      verbose_name='Data da última alteração')
    tipo_id = models.ForeignKey(TipoCliente,
                                on_delete=models.PROTECT,
                                verbose_name='Id do tipo do cliente')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = u'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'


class Filial(models.Model):
    id = models.AutoField(primary_key=True),
    cliente_id = models.ForeignKey(Cliente,
                                   on_delete=models.CASCADE,
                                   verbose_name='Id do tipo do cliente')
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    fone = models.CharField(max_length=15,
                            null=True,
                            verbose_name='Telefone de contato da filial')
    matriz = models.BooleanField(default=False,
                                 verbose_name='É Matriz')
    ativo = models.BooleanField(default=True,
                                verbose_name='Filial está ou não ativa')
    data_cadastro = models.DateField(auto_now=True,
                                     verbose_name='Data de cadastro')
    data_alteracao = models.DateField(auto_now_add=True,
                                      verbose_name='Data da última alteração')

    class Meta:
        db_table = u'clientes_filiais'
        verbose_name = 'Filial de cliente'
        verbose_name_plural = 'Filiais de cliente'

    def __str__(self):
        return self.nome


# Sinal para sincronizar o campo 'ativo' do Cliente com suas Filiais
@receiver(post_save, sender=Cliente)
def sincronizar_filiais(sender, instance, **kwargs):
    if not instance.ativo:
        # Se o Cliente foi desativado, desativar todas as suas Filiais
        instance.filiais.update(ativo=False)


class ContatoCliente(models.Model):
    id = models.AutoField(primary_key=True)
    filial_id = models.ForeignKey(Filial,
                                  on_delete=models.CASCADE,
                                  verbose_name='Filial do Contato')
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    fone = models.CharField(max_length=15,
                            verbose_name='Telefone de contato da filial',
                            null=True)
    data_nascimento = models.DateField(null=True,
                                       verbose_name="Data de nascimento")
    ativo = models.BooleanField(default=True,
                                verbose_name='Ativo')
    solicitante = models.BooleanField(default=False,
                                      verbose_name='É Solicitante')
    data_cadastro = models.DateField(auto_now=True,
                                     verbose_name='Data de cadastro')
    data_alteracao = models.DateField(auto_now_add=True,
                                      verbose_name='Data da última alteração')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = u'clientes_contatos'
        verbose_name = 'Contato de cliente'
        verbose_name_plural = 'Contatos de cliente'


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
                                        verbose_name='Data de finalização')
    projeto_id = models.ForeignKey(Projeto,
                                   null=True,
                                   on_delete=models.CASCADE)
    prioridade = models.IntegerField(default=0,
                                     verbose_name='Nível de prioridade')
    status_id = models.ForeignKey(StatusChamado,
                                  on_delete=models.PROTECT)

    def __str__(self):
        return self.id

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
