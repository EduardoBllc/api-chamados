from pathlib import WindowsPath
from rest_framework import status
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from api_chamados.settings import DEBUG, DESENVOLVIMENTO, ALLOWED_HOSTS, DATABASES


class VariaveisSettings(APIView):
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get(self, request, format=None):
        dic_variaveis = {'DEBUG': DEBUG,
                         'DESENVOLVIMENTO': DESENVOLVIMENTO,
                         'ALLOWED_HOSTS': ALLOWED_HOSTS,
                         'DATABASES': DATABASES}

        for nome, dados_base in dic_variaveis.get('DATABASES').items():
            if isinstance(dados_base.get('NAME'), WindowsPath):
                dados_base['NAME'] = dados_base.get('NAME').__str__()

        return Response(dic_variaveis, status=status.HTTP_200_OK)
