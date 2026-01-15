from django.urls import path
from .views import (
    CardListCreateView, CardDetailView, SetDefaultCardView,
    ProcessPaymentView, PaymentHistoryView, PaymentDetailView,
    payment_page, payment_success, payment_failed, saved_cards, payment_history
)

app_name = 'payments'

urlpatterns = [
    path('api/cards/', CardListCreateView.as_view(), name='card_list_create_api'),
    path('api/cards/<int:pk>/', CardDetailView.as_view(), name='card_detail_api'),
    path('api/cards/<int:pk>/set-default/', SetDefaultCardView.as_view(), name='set_default_card_api'),
    path('api/process/', ProcessPaymentView.as_view(), name='process_payment_api'),
    path('api/history/', PaymentHistoryView.as_view(), name='payment_history_api'),
    path('api/payment/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail_api'),
    
    path('pay/<int:order_id>/', payment_page, name='payment_page'),
    path('success/<int:payment_id>/', payment_success, name='payment_success'),
    path('failed/<int:payment_id>/', payment_failed, name='payment_failed'),
    path('cards/', saved_cards, name='saved_cards'),
    path('history/', payment_history, name='payment_history'),
]