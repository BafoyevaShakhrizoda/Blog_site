from rest_framework import serializers
from .models import UserCard, Payment
from apps.orders.models import Order
from datetime import datetime
import re

class UserCardSerializer(serializers.ModelSerializer):
    hidden_c_number = serializers.SerializerMethodField()

    class Meta:
        model = UserCard
        fields = [
            'id', 'card_number', 'hidden_c_number', 'cardholder_name',
            'exp_month', 'exp_year', 'is_default'
        ]
        extra_kwargs = {
            'card_number': {'write_only': True}
        }

    def get_hidden_c_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}"
    
    def validate_card_number(self, value):
        card_number = re.sub(r'[\s-]', '', value)

        if not card_number.isdigit():
            raise serializers.ValidationError("Card number must be numbers only")
        
        if len(card_number) < 13 or len(card_number) >19:
            raise serializers.ValidationError("Card number must be between 13 and 19 digits")
        
        return card_number
    def validate_cardholder_name(self, value):
        if not value.replace(' ', '').isalpha():
            raise serializers.ValidationError("Card holder name must be only letters")
        
        if len(value) < 3:
            raise serializers.ValidationError("Cardholder name is too short")
        
        return value.upper()
    
    def validate_exp_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Invalid expiration month")
        return value
    
    def validate_exp_year(self, value):
        c_year = datetime.now().year
        if value < c_year:
            raise serializers.ValidationError('Card expired')
        if value > c_year+ 20:
            raise serializers.ValidationError("Invalid expiration year")
        return value
    
    def validate(self, data):
        exp_month = data.get('exp_month')
        exp_year = data.get('exp_year')

        if exp_month and exp_year:
            c_date = datetime.now()
            if exp_year == c_date.year and exp_month < c_date.month:
                raise serializers.ValidationError("Card has expired")
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        is_default = validated_data.get('is_default', False)

        if is_default:
            UserCard.objects.filter(user=user, is_default = True).update(is_default = False)

        if not UserCard.objects.filter(user=user).exists():
            validated_data['is_default'] = True
        
        validated_data['user'] = user
        return super().create(validated_data)

class PaymentSerializer(serializers.ModelSerializer):
    card_info = serializers.SerializerMethodField()
    order_info = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'card', 'card_info', 'order_info',
            'amount', 'status', 'created_at'
        ]
        read_only_fields= ['id' , 'created_at', 'card_info', 'order_info']
    
    def get_card_info(self, obj):
        if obj.card:
            return{
                'hidden_card_number': f'**** **** **** {obj.card.card_number[-4:]}',
                'card_holder_name': obj.card.cardholder_name
            }
        return None
    
    def get_order_info(self, obj):
        return {
            'id': obj.order.id,
            'order_number': str(obj.order.id).zfill(6),
            'total': str(obj.order.total)
        }

class ProcessPaymentSerializer(serializers.Serializer):
    order_id =serializers.IntegerField(required = True)
    card_id = serializers.IntegerField(required = False, allow_null = True)

    card_number = serializers.CharField(required = False, allow_blank = True)
    cardholder_name = serializers.CharField(required = False, allow_blank = True)
    exp_month = serializers.IntegerField(required = False, allow_null = True)
    exp_year = serializers.IntegerField(required = False, allow_null= True)

    cvv = serializers.CharField(required = False, allow_blank =True, max_length = 4)
    save_card = serializers.BooleanField(required = False, default = False)

    def validate_order_id(self, value):
        user = self.context['request'].user
        try:
            order = Order.objects.get(id = value, user = user)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        
        if hasattr(order, 'payment'):
            raise serializers.ValidationError("Order has already been paid")
        
        return value
    def validate_card_id(self, value):
        if value:
            user = self.context['request'].user
            try:
                UserCard.objects.get(id = value, user = user)
            except UserCard.DoesNotExist:
                raise serializers.ValidationError('Card not found')
        return value
    def validate_cvv(self, value):
        if value:
            if not value.isdigit():
                raise serializers.ValidationError("CVV must be digits only")
            if len(value) < 3 or len(value) > 4:
                raise serializers.ValidationError("CVV must be 3 or 4 numbers only")
        return value
    
    def validate(self, data):

        card_id = data.get('card_id')
        card_number = data.get('card_number')

        if not card_id and not card_number:
            raise serializers.ValidationError("Either provide card_id or complete card details")
        
        if not card_id:
            required_fields = ['card_number', 'cardholder_name', 'exp_month', 'exp_year', 'cvv']
            missing_fields = [field for field in required_fields if not data.get(field)]

            if missing_fields:
                raise serializers.ValidationError(f"Missing fields: {', '.join(missing_fields)}")
            
            card_serializer = UserCardSerializer(
                data={
                        "card_number": data.get("card_number"),
                        "cardholder_name": data.get("cardholder_name"),
                        "exp_month": data.get("exp_month"),
                        "exp_year": data.get("exp_year"),
                    }, context=self.context)
            
            card_serializer.is_valid(raise_exception=True)

        return data
    
class PaymentHistorySerializer(serializers.ModelSerializer):
    order_number = serializers.SerializerMethodField()
    card_last_four= serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'order_number', 'card_last_four',
            'amount', 'status', 'created_at'
        ]
    
    def get_order_number(self, obj):
        return f"ORDER - {str(obj.order.id).zfill(6)}"
    
    def get_card_last_four(self, obj):
        if obj.card:
            return obj.card.card_number[-4:]
        return "N/A"

