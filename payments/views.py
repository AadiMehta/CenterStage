from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from users.models import User, PaymentAccounts, BillingProfile
from payments.models import LessonOrder, PaymentIntent 
from payments.serializers import PaymentsSerializer
import stripe
from datetime import datetime
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
    
    def post(self, request, *args, **kwargs):
        data = request.data
        payment_type = data.get('payment_type')
        payment_account = PaymentAccounts.objects.filter(user=request.user, payment_type=payment_type).first()
        if payment_account:
            payment_account.delete()
            return Response({"msg": "Disconnected Payment Account"}, status=status.HTTP_200_OK)
        return Response({"msg": "account not exists"}, status=status.HTTP_400_BAD_REQUEST)


class PaymentAccountView(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def create_stripe_account(self, request, data):
        dob = data['dob'].split('/')
        timestamp = int(datetime.now().timestamp())
        account = stripe.Account.create(
            country=data['country'][0:2].upper(),
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
                'id_number': data['personalID'],
                'address': {
                    'line1': data['address'],
                    'line2': data['address'],
                    'city': data['city'],
                    'state': data['state'],
                    'country': data['country'],
                    'postal_code': data['postalCode'],

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
                'date': timestamp,
                'ip': '127.0.0.1',
            },)

        # print (account)
        stripe.Account.create_external_account(
            account['id'], external_account={
                'object': 'bank_account',
                'country': data['country'],
                'currency': data['currency'],
                'account_holder_name': data['accountHolderName'],
                'routing_number': data['ifscCode'],
                'account_number': data['bankAccountNo']
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
            stripe_account = self.create_stripe_account(request, data)
            data['account_id'] = stripe_account.get('id')
            data['info'] = stripe_account
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


class LessonPaymentView(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def get_order(self, order_id):
        return get_object_or_404(LessonOrder, order_id=order_id)
    
    def get_lesson(self, lesson_uuid):
        return get_object_or_404(LessonData, lesson_uuid=lesson_uuid)
    
    def selected_slots(self, lesson, set_to_all_sessions, time_slot):
        upcoming_slots = lesson.slots.all().filter(Q(lesson_from__gt=timezone.now()))
        if set_to_all_sessions:
            return upcoming_slots
        selected_slots = upcoming_slots.filter(session_no=time_slot)
        return selected_slots

    def post(self, request, *args, **kwargs):
        data = request.data
        if not data:
            return Response({'error': 'please provide data'}, status=status.HTTP_400_BAD_REQUEST)

        lesson_id = data.get('lesson_id')
        set_to_all_sessions = data.get('set_to_all_sessions')
        time_slot = data.get('time_slot')

        lesson = self.get_lesson(lesson_id)

        selected_slots = self.selected_slots(lesson, set_to_all_sessions, time_slot)
        order_data = {
            "lesson": lesson,
            "student": request.user.student_profile_data,
            "total": len(selected_slots) * int(lesson.price['value'])
        }
        order_obj, created = LessonOrder.objects.new_or_get(order_data)
        # set lesson slots
        order_obj.lesson_slots.set(selected_slots)
        order_obj.save()

        stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY

        payment_intent, is_created = PaymentIntent.objects.do(request, order_obj)
        if is_created:
            # Send publishable key and PaymentIntent details to client
            return Response(
                {
                    'publishableKey': stripe_publishable_key,
                    'clientSecret': payment_intent.client_secret,
                    'orderId': order_obj.order_id
                },
                status=status.HTTP_200_OK)
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
        return get_object_or_404(PaymentIntent, stripe_id=stripe_id)

    def post(self, request, *args, **kwargs):
        data = request.data
        order_id = data.get('order_id')
        payment_intent_json = data.get('payment_intent_json')
        payment_intent_id = payment_intent_json.get('id')
        payment_status = payment_intent_json.get('status')

        if payment_status == 'succeeded':
            order_obj = self.get_order(order_id)
            payment_intent_obj = self.get_payment_intent(payment_intent_id)
            # update enrollments
            order_obj.update_enrollments()
            # update order status
            order_obj.mark_paid()
            # update payment intent
            payment_intent_obj.info = payment_intent_json
            payment_intent_obj.paid = True
            payment_intent_obj.save()
            return Response({'status': 'succeeded'}, status=status.HTTP_200_OK)
        return Response({'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)

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