from django.shortcuts import render
from users.models import User, PaymentAccounts
from payments.serializers import PaymentsSerializer
import stripe
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from users.authentication import BearerAuthentication, AuthCookieAuthentication


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

    def CreateStripAccount(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        dob = request.data['dob'].split('/')
        account = stripe.Account.create(
        country=request.data['country'][0:2].upper(),
        type='custom',
        business_type='individual',
        email=request.user.email,
        individual={
        'dob': {
            'day':dob[0],
            'month':dob[1],
            'year':dob[2],
            },
        'email': request.user.email,
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'id_number':request.data['personalID'],
        'address':{
            'line1':request.data['address'],
            'line2':request.data['address'],
            'city':request.data['city'],
            'state':'RJ',
            'country':request.data['country'][0:2].upper(),
            'postal_code':request.data['postalCode'],

            }
        },
        capabilities={
        'transfers': {
          'requested': True,
        },
        'card_payments':{
        'requested': True,
        }
      },
      tos_acceptance={
        'service_agreement': 'full',
        'date': '1547923073',
        'ip':'127.0.0.1',
      },)

        # print (account)
        stripe.Account.create_external_account(
            account['id'],external_account={
            'object':'bank_account',
            'country':'IN',
            'currency':'INR',
            'account_holder_name':request.data['accountHolderName'],
            'routing_number':request.data['ifscCode'],
            'account_number':request.data['bankAccountNo']
            }
            )
        acc_details = stripe.Account.list_external_accounts(account['id'],object="bank_account",limit=3,)
        print (acc_details)
        print (account['id'])
        return account['id']
    
    def post(self, request):
        
        try:
            payment_account = PaymentAccounts.objects.get(user=request.user)
            return Response(dict({
                "error": "Payment Account Already Created"
            }), status=status.HTTP_400_BAD_REQUEST)
        except PaymentAccounts.DoesNotExist:
            data = request.data
            data['stripe_account_id'] = self.CreateStripAccount(request)
            data['info'] = {}
            serializer = PaymentsSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            resp = dict({"message": "payment accound added"})
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)