from rest_framework import serializers
from users.models import PaymentAccounts

class PaymentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentAccounts
        fields = (
            'stripe_account_id',
            'info'
        )