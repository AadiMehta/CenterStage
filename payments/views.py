from django.shortcuts import render
from users.models import User, PaymentAccounts, BillingProfile
from payments.serializers import PaymentsSerializer
import stripe
from django.db.models import Q
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from users.authentication import BearerAuthentication, AuthCookieAuthentication
from users.models import PaymentTypes
import logging

logger = logging.getLogger(__name__)


class PaymentDisconnectAPIVIew(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def get(self, request, *args, **kwargs):
        payment_account = PaymentAccounts.objects.get(
            user=request.user,
        )
        if payment_account:
            payment_account.delete()
        return Response(dict(msg="Disconnected Payment Account"), status=status.HTTP_200_OK)


class PaymentAccountView(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def create_stripe_account(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        dob = request.data['dob'].split('/')
        account = stripe.Account.create(
            country=request.data['country'][0:2].upper(),
            type='custom',
            business_type='individual',
            email=request.user.email,
            individual={
                'dob': {
                    'day': dob[0],
                    'month': dob[1],
                    'year': dob[2],
                },
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'id_number': request.data['personalID'],
                'address': {
                    'line1': request.data['address'],
                    'line2': request.data['address'],
                    'city': request.data['city'],
                    'state': 'RJ',
                    'country': request.data['country'][0:2].upper(),
                    'postal_code': request.data['postalCode'],

                }
            },
            capabilities={
                'transfers': {
                    'requested': True,
                },
                'card_payments': {
                    'requested': True,
                }
            },
            tos_acceptance={
                'service_agreement': 'full',
                'date': '1547923073',
                'ip': '127.0.0.1',
            },)

        # print (account)
        stripe.Account.create_external_account(
            account['id'], external_account={
                'object': 'bank_account',
                'country': 'IN',
                'currency': 'INR',
                'account_holder_name': request.data['accountHolderName'],
                'routing_number': request.data['ifscCode'],
                'account_number': request.data['bankAccountNo']
            }
        )
        acc_details = stripe.Account.list_external_accounts(
            account['id'], object="bank_account", limit=3,)
        logger.info(acc_details)
        logger.info(account['id'])
        return account

    def post(self, request):
        payment_account = PaymentAccounts.objects.filter(
            Q(user=request.user) & Q(
                payment_type=PaymentTypes.STRIPE) & Q(active=True)
        ).first()

        if payment_account:
            return Response(dict({
                "error": "Payment Account Already Created"
            }), status=status.HTTP_400_BAD_REQUEST)

        try:
            data = request.data
            stripe_account = self.create_stripe_account(request)
            data['account_id'] = stripe_account.get('id')
            data['info'] = data
            data['payment_type'] = PaymentTypes.STRIPE
            serializer = PaymentsSerializer(
                data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            resp = dict({"message": "payment accound added"})
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(str(e))
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StripeCustomerAccountAPIVIew(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def get(self, request, *args, **kwargs):
        billing_profile = BillingProfile.objects.filter(
            Q(user=request.user) & Q(
                payment_type=PaymentTypes.STRIPE) & Q(active=True)
        ).first()

        if billing_profile:
            return Response(dict({
                "error": "Customer Account Already Created"
            }), status=status.HTTP_400_BAD_REQUEST)
        try:
            data = request.data
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.create(email=request.user.email)
            BillingProfile.objects.get_or_create(
                customer_id=customer, user=request.user, payment_type=PaymentTypes.STRIPE)
            return Response(dict(msg="created stripe billing profile"), status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(str(e))
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    return 1400


def calculate_application_fee_amount(amount):
    # Take a 10% cut.
    return int(.1 * amount)


class LessonPaymentView(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def post(self, request):
        data = request.data()
        amount = calculate_order_amount(data.get('items'))
        stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        # Create a PaymentIntent with the order amount, currency, and transfer destination
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=data['currency'],
            transfer_data={'destination': 'acct_1IdrNiSHJOz61Nda'},
            application_fee_amount=calculate_application_fee_amount(amount)
        )
        try:
            # Send publishable key and PaymentIntent details to client
            return Response({'publishableKey': stripe_publishable_key, 'clientSecret': intent.client_secret}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)


class LessonPaymentWebhookView(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def post(self, request):
        payload = request.data()
        signature = request.headers.get("stripe-signature")
        stripe_webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        # Verify webhook signature and extract the event.
        # See https://stripe.com/docs/webhooks/signatures for more information.
        try:
            event = stripe.Webhook.construct_event(
                payload=payload, sig_header=signature, secret=stripe_webhook_secret
            )
        except ValueError as e:
            # Invalid payload.
            logger.error(e)
            return Response({"error": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid Signature.
            logger.error(e, signature, stripe_webhook_secret, payload)
            return Response({"error": "Invalid Signature"}, status=status.HTTP_400_BAD_REQUEST)

        if event["type"] == "payment_intent.succeeded":
            # Fulfill the purchase.
            payment_intent = event["data"]["object"]
            logger.info('PaymentIntent: ' + str(payment_intent))
        return Response({"success": True}, status=status.HTTP_200_OK)
