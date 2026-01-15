from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserCard, Payment
from .serializers import UserCardSerializer, PaymentSerializer, ProcessPaymentSerializer, PaymentHistorySerializer
from apps.orders.models import Order
import random


# FOr API Swagger
class CardListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserCardSerializer

    def get_queryset(self):
        return UserCard.objects.filter(user=self.request.user)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        card = serializer.save()

        return Response({
            'success': True, 
            'message': 'Card added successfully',
            'data': UserCardSerializer(card).data
        }, status=status.HTTP_201_CREATED)

class CardDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(UserCard, pk = pk, user = self.request.user)
    
    def get(self, request, pk):
        card = self.get_object(pk)
        serializer =UserCardSerializer(card)
        return Response({
            'success': True, 
            'data': serializer.data
        })
    def patch(self, request, pk):
        card = self.get_object(pk)
        serializer= UserCardSerializer(card, data =request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'success': True, 
            'message': 'Card updated successfully',
            'data': serializer.data
        })
    def delete(self, request, pk):
        card = self.get_object(pk)
        card.delete()

        return Response({
            'success': True, 
            'message': 'Card delted'
        }, status=status.HTTP_200_OK)

class SetDefaultCardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        card = get_object_or_404(UserCard, pk=pk, user=request.user)

        UserCard.objects.filter(user=request.user, is_default=True).update(is_default = False)

        card.is_default = True
        card.save()

        return Response({
            'success': True, 
            'message': 'Default Card updated',
            'data': UserCardSerializer(card).data
        })





class ProcessPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ProcessPaymentSerializer(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data['order_id']
        card_id = serializer.validated_data.get('card_id')
        save_card =serializer.validated_data.get('save_card', False)

        order = Order.objects.get(id=order_id, buyer = request.user)
        if card_id:
            card = UserCard.objects.get(id = card_id, user=request.user)
        else:
            if save_card:
                card_data = {
                    'card_number': serializer.validated_data['card_number'],
                    'cardholder_name': serializer.validated_data['cardholder_name'],
                    'exp_month': serializer.validated_data['exp_month'],
                    'exp_year': serializer.validated_data['exp_year']
                }
                card_serializer = UserCardSerializer(data = card_data, context={'request': request})
                card_serializer.is_valid(raise_exception=True)
                card = card_serializer.save()
            else:
                card = None
        
        paymnet_success = self._process_payment(
            order.total, serializer.validated_data.get('cvv')
        )
        payment=Payment.objects.create(
            user = order.buyer,
            order = order,
            card = card,
            amount = order.total,
            status='success' if paymnet_success else 'failed'
        )

        if paymnet_success:
            order.status = 'paid'
            order.save()

            return Response({
                'success': True,
                'message': 'Payment processes successfully',
                'data': PaymentSerializer(payment).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': "Payment Failed, Please Try again",
                'data': PaymentSerializer(payment).data

            }, status=status.HTTP_400_BAD_REQUEST)
    def _process_payment(self, amount, cvv):

        return random.random() < 0.95

class PaymentHistoryView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentHistorySerializer

    def get_queryset(self):
        return Payment.objects.filter(order__buyer=self.request.user).order_by('-created_at')

class PaymentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, order__buyer=request.user)
        serializer = PaymentSerializer(payment)

        return Response({
            'success': True,
            'message': serializer.data
        })


# For html views
@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    if hasattr(order, 'payment'):
        return render(request, 'payments/payment_success.html', {
            'payment': order.payment,
            'order': order
        })
    
    user_cards = UserCard.objects.filter(user=request.user)
    
    context = {
        'title': 'Payment',
        'order': order,
        'user_cards': user_cards,
    }
    return render(request, 'payments/payment.html', context)


@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, order__buyer=request.user)
    
    context = {
        'title': 'Payment Success',
        'payment': payment,
        'order': payment.order
    }
    return render(request, 'payments/payment_success.html', context)


@login_required
def payment_failed(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, order__buyer=request.user)
    
    context = {
        'title': 'Payment Failed',
        'payment': payment,
        'order': payment.order
    }
    return render(request, 'payments/payment_failed.html', context)


@login_required
def saved_cards(request):
    cards = UserCard.objects.filter(user=request.user)
    
    context = {
        'title': 'Saved Cards',
        'cards': cards
    }
    return render(request, 'payments/saved_cards.html', context)


@login_required
def payment_history(request):
    payments = Payment.objects.filter(order__buyer=request.user).order_by('-created_at')
    
    context = {
        'title': 'Payment History',
        'payments': payments
    }
    return render(request, 'payments/payment_history.html', context)