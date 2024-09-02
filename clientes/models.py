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
                            blank=True,
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
    filial = models.ForeignKey(Filial,
                               on_delete=models.CASCADE,
                               verbose_name='Filial do Contato')
    nome = models.CharField(max_length=60,
                            verbose_name='Nome')
    fone = models.CharField(max_length=15,
                            verbose_name='Telefone de contato da filial',
                            null=True)
    data_nascimento = models.DateField(null=True,
                                       blank=True,
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
