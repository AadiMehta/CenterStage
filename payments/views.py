from django.shortcuts import redirect, render, get_object_or_404
from users.models import User, PaymentAccounts, BillingProfile
from payments.models import LessonOrder, PaymentIntent 
from payments.serializers import PaymentsSerializer
import stripe
from django.db.models import Q
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from users.authentication import BearerAuthentication, AuthCookieAuthentication
from rest_framework import permissions
from users.models import PaymentTypes
from engine.models import LessonData
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentDisconnectAPIVIew(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
            customer = stripe.Customer.create(email=request.user.email)
            BillingProfile.objects.get_or_create(
                customer_id=customer, user=request.user, payment_type=PaymentTypes.STRIPE)
            return Response(dict(msg="created stripe billing profile"), status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(str(e))
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LessonPaymentView(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = []
  
    def get_order(self, order_id):
        return get_object_or_404(LessonOrder, order_id=order_id)
    
    def get_lesson(self, lesson_uuid):
        return get_object_or_404(LessonData, lesson_uuid=lesson_uuid)

    def post(self, request, *args, **kwargs):
        data = request.data
        order_id = data.get('order_id')
        lesson_id = data.get('lesson_id')
        order_obj = self.get_order(order_id)

        if order_obj.is_completed:
            return Response({'error': 'order already completed'}, status=status.HTTP_400_BAD_REQUEST)

        stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY

        payment_intent, is_created = PaymentIntent.objects.do(request, order_obj)
        if is_created:
            # Send publishable key and PaymentIntent details to client
            return Response({'publishableKey': stripe_publishable_key, 'clientSecret': payment_intent.client_secret}, status=status.HTTP_200_OK)
        else:
            return Response({'error': str(payment_intent)}, status=status.HTTP_403_FORBIDDEN)


class LessonPaymentCompleteView(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = []
  
    def get_order(self, order_id):
        return get_object_or_404(LessonOrder, order_id=order_id)
    
    def get_lesson(self, lesson_uuid):
        return get_object_or_404(LessonData, lesson_uuid=lesson_uuid)
    
    def get_payment_intent(self, stripe_id):
        return get_object_or_404(LessonData, stripe_id=stripe_id)

    def post(self, request, *args, **kwargs):
        data = request.data
        order_id = data.get('order_id')
        lesson_id = data.get('lesson_id')
        payment_intent_json = data.get('payment_intent_json')
        payment_intent_id = payment_intent_json.get('payment_intent_id')
        status = payment_intent_json.get('status')

        if status == 'succeeded':
            order_obj = self.get_order(order_id)
            payment_intent_obj = self.get_payment_intent(payment_intent_id)
            # update enrollments
            order_obj.update_enrollments()
            order_obj.mark_paid()
            # update payment intent
            payment_intent_obj.info = payment_intent_json
            payment_intent_obj.paid = True
            payment_intent_obj.save()
            return Response({'status': 'succeeded'}, status=status.HTTP_200_OK)
        return Response({'status': 'failed'}, status=status.HTTP_200_OK)

class LessonPaymentWebhookView(APIView):

    # authentication_classes = [BearerAuthentication]
    permission_classes = []


    def post(self, request, *args, **kwargs):
        payload = request.data
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
            self.handle_successful_payment_intent(payment_intent)
        return Response({"success": True}, status=status.HTTP_200_OK)

    def handle_successful_payment_intent(self, payment_intent):
        # Fulfill the purchase.
        logger.info('PaymentIntent: ' + str(payment_intent))