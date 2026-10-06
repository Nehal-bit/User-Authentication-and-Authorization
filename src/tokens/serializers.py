# src/tokens/serializers.py
from rest_framework import serializers

class ClientTokenSerializer(serializers.Serializer):
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
