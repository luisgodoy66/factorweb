from rest_framework import serializers

class EstadoOperativoClienteSerializer(serializers.Serializer):
    cliente_id = serializers.CharField()
    valor_linea = serializers.FloatField()
    porc_disponible = serializers.FloatField()
    dias_ultima_operacion = serializers.IntegerField(allow_null=True)
    nombre_cliente = serializers.CharField()
    estado = serializers.CharField()
    clase = serializers.CharField()
    color_estado = serializers.IntegerField()
    total_cartera_protestos = serializers.FloatField()
    total_reestructuracion = serializers.FloatField()