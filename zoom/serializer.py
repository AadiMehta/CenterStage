from rest_framework import serializers


class ZoomAuthResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    refresh_token = serializers.CharField(required=True)
    expires_in = serializers.IntegerField(required=True)
