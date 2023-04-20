from rest_framework.serializers import ModelSerializer
from bar.models import Menu, Promo, Review, Orders, ClientData


class MenuSerializer(ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


class PromoSerializer(ModelSerializer):
    class Meta:
        model = Promo
        fields = '__all__'


class ReviewSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class OrdersSerializer(ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'


class ClientDataSerializer(ModelSerializer):
    class Meta:
        model = ClientData
        fields = '__all__'
