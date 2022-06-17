from django.urls import path
from . import views

urlpatterns = [
    #Home
    path('', views.adminhome, name='adminhome'),

    #Admin Login and Logout
    path('admin_login', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),

    #Admin Product Management 
    path('admin_product_list/', views.admin_product_list, name='admin_product_list'),
    path('admin_edit_product/<int:id>/', views.admin_edit_product, name='admin_edit_product'),
    path('admin_add_product/', views.admin_add_product, name='admin_add_product'),
    path('admin_add_product_images/', views.admin_add_product_images, name='admin_add_product_images'),
    path('admin_delete_product/<int:id>/', views.admin_delete_product, name='admin_delete_product'),

    #Admin User Managemanet
    path('users/', views.users, name='users'),
    path('user_activation/<int:id>/', views.user_activation, name='user_activation'),
    path('user_deactivation/<int:id>/', views.user_deactivation, name='user_deactivation'),

    #Admin Category Managemanet
    path('admin_categories/', views.admin_categories, name='admin_categories'),
    path('admin_add_category/', views.admin_add_category, name='admin_add_category'),
    path('admin_edit_category/<int:id>/', views.admin_edit_category, name='admin_edit_category'),
    path('admin_delete_category/<int:id>/', views.admin_delete_category, name='admin_delete_category'),

    #Admin Order Management
    path('admin_orders/', views.admin_orders, name='admin_orders'),
    path('admin_orders_status_change/<int:id>/', views.admin_orders_status_change, name='admin_orders_status_change'),

    #Admin Varient Management
    path('admin_variation/', views.admin_variation, name='admin_variation'),
    path('admin_add_variation/', views.admin_add_variation, name='admin_add_variation'),
]

