from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('rzp_order_complete/', views.rzp_order_complete, name='rzp_order_complete'),
    path('order_complete/', views.order_complete , name='order_complete'),
    path('cod_order_complete/<int:order_number>',views.cod_order_complete, name='cod_order_complete'),
    path('return_order/<int:order>/',views.return_order, name='return_order'),
    path('cancel_order/<int:order>/',views.cancel_order, name='cancel_order'),
]
