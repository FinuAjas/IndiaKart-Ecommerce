from django import forms
from django.db.models import fields
from .models import Product, ProductGallery, ReviewRating, Variation

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name', 'description', 'price','images','stock','is_available','category')

    def __init__(self,*args,**kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'       

        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject','review','rating']  


class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ['product','variation_category','variation_value','is_active']

    def __init__(self,*args,**kwargs):
        super(VariationForm, self).__init__(*args, **kwargs)
        self.fields["product"].widget.attrs['class']='form-control'     
        self.fields["variation_category"].widget.attrs['class']='form-control'
        self.fields["variation_value"].widget.attrs['class']='form-control'

class ProductGalleryForm(forms.ModelForm):
    class Meta:
        model = ProductGallery
        fields = ['product','image']           