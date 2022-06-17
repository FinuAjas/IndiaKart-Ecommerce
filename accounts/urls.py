from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("otp_login/", views.otp_login, name="otp_login"),
    path("otp_varification/", views.otp_varification, name="otp_varification"),
    path("new_user_otp_varification/", views.new_user_otp_varification, name="new_user_otp_varification",),
    
    path("my_orders/", views.my_orders, name="my_orders",),
    path("manage_address/", views.manage_address, name="manage_address",),
    path("edit_address/<int:id>/", views.edit_address, name="edit_address",),
    path("add_address/", views.add_address, name="add_address",),
]
