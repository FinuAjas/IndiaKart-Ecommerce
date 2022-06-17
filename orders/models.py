from django.db import models
from ctypes import sizeof
from itertools import product
from pyexpat import model
from sre_parse import State
from telnetlib import STATUS
from turtle import color
from typing import OrderedDict
from venv import create
from django.db import models
from accounts.models import Account
from store.models import Product, Variation
from django.core.validators import MinValueValidator, MaxValueValidator


class Payment(models.Model):
    user            = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id      = models.CharField(max_length=100)
    payment_method  = models.CharField(max_length=100)
    amount_paid     = models.CharField(max_length=100)
    status          = models.CharField(max_length=100)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('New','New'),
        ('Accepted','Accepted'),
        ('Order Shipped','Order Shipped'),
        ('Order Out for Delivery','Order Out for Delivery'),
        ('Order Delivered','Order Delivered'),
        ('Return','Return'),
        ('Return collected','Return collected'),
        ('Cancelled','Cancelled'),
    )        

    user            = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment         = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank = True , null=True)
    order_number    = models.CharField(max_length=30)
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    phone           = models.CharField(max_length=15)
    email           = models.EmailField(max_length=50)
    address_line_1  = models.CharField(max_length=50)
    address_line_2  = models.CharField(max_length=50)
    country         = models.CharField(max_length=50)
    state           = models.CharField(max_length=50)
    city            = models.CharField(max_length=50)
    order_note      = models.CharField(max_length=150 , blank = True)
    order_total     = models.FloatField()
    tax             = models.FloatField()
    status          = models.CharField(max_length=25, choices = STATUS, default='New')
    ip              = models.CharField(blank=True , max_length=20)
    is_ordered      = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    discount_amount = models.FloatField(null=True,blank=True)
    nett_paid       = models.FloatField(null=True,blank=True)
    discount        = models.IntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])


    def full_name(self):
        return f'{self.first_name} {self.last_name}'    

    def full_address(self):
        return f'{self.address_line_1}, {self.address_line_2}, { self.city }, { self.state}, { self.country }'       


    def __str__(self):
        return self.first_name 


class OrderProduct(models.Model):
    order         = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment       = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user          = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product       = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations    = models.ManyToManyField(Variation, blank=True)
    quantity      = models.IntegerField()
    product_price = models.FloatField()
    ordered       = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.product.product_name



        