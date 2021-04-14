from rest_framework import serializers
from users.models import PaymentAccounts, BillingProfile

class PaymentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentAccounts
        fields = (
            'account_id',
            'info'
        )

class StripeCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = BillingProfile
        fields = (
            'customer_id',
            'info'
        )
    
    def create(self, validated_data):
        request = self.context.get('request')   # noqa
        payment_account = PaymentAccounts.objects.get_or_create(validated_data)
        return payment_account
