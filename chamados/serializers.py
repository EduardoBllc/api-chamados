from rest_framework import serializers
from .models import Chamado


class ChamadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chamado
        fields = '__all__'  # Ou liste os campos que você deseja incluir
