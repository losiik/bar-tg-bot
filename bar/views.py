from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from bar.models import Menu, Promo, Review, Orders, ClientData
from bar.serializer import MenuSerializer, PromoSerializer, ReviewSerializer, \
    OrdersSerializer, ClientDataSerializer


class MenuView(APIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def get(self, request):
        menu = Menu.objects.all()
        serializer = MenuSerializer(menu, many=True)
        return Response({"menu": serializer.data})


class PromoView(APIView):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer

    def get(self, request):
        promo = Promo.objects.all()
        serializer = PromoSerializer(promo, many=True)
        return Response({"promo": serializer.data})


class ReviewView(APIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response('review saved successful')
        return Response('error')

    def get(self, request):
        review = Review.objects.all()
        serializer =ReviewSerializer(review, many=True)
        return Response({"review": serializer.data})


class ClientDataView(APIView):
    queryset = ClientData.objects.all()
    serializer_class = ClientDataSerializer

    def get(self, request):
        client_data = ClientData.objects.all()
        serializer = ClientDataSerializer(client_data, many=True)
        return Response({"client_data": serializer.data})


class OrdersView(APIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer

    def post(self, request):
        serializer = OrdersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response('order saved successful')
        return Response('error')

    def get(self, request):
        orders = Orders.objects.all()
        serializer =OrdersSerializer(orders, many=True)
        return Response({"orders": serializer.data})

