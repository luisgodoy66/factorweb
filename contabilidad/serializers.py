from rest_framework import serializers

class AsientoDiarioSerializer(serializers.Serializer):
    transaccion = serializers.CharField()
    fecha_contabilizado = serializers.DateField()
    concepto = serializers.CharField()
    valor = serializers.FloatField()
    estado = serializers.CharField()
