from django.urls import include, path
from rest_framework import routers
from . import views


urlpatterns = [
    path('menu/', views.MenuView.as_view()),
    path('promo/', views.PromoView.as_view()),
    path('review/', views.ReviewView.as_view()),
    path('api-auth/', include('rest_framework.urls'))
]
