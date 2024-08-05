# -*- coding: utf-8 -*-
from scripts.gerenciador_envs.models import VariavelSettings, TipoVariavel

# Listas com as variáveis de ambiente que serão checadas na validação do arquivo .env das variáveis do settings e que
# serão criadas ao rodar script de criação de arquivo .env

VARIAVEIS_AMBIENTE = [
    VariavelSettings('DESENVOLVIMENTO',
                     valor_padrao=False,
                     tipo=TipoVariavel.Boolean),
    VariavelSettings('DEBUG',
                     valor_padrao=False,
                     tipo=TipoVariavel.Boolean),
    VariavelSettings('SECRET_KEY',
                     valor_padrao='django-insecure-key'),
]

VARIAVEIS_PRODUCAO = [
    VariavelSettings('DB_NAME'),
    VariavelSettings('DB_USER'),
    VariavelSettings('DB_PASSWORD'),
    VariavelSettings('ALLOWED_HOSTS',
                     valor_padrao='*',
                     tipo=TipoVariavel.List),
    VariavelSettings('DB_HOST',
                     valor_padrao='localhost'),
    VariavelSettings('DB_PORT',
                     valor_padrao=5432),
]
