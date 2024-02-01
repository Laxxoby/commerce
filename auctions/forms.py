from django import forms
from django.forms.widgets import SelectDateWidget
from .models import Auction_listings, User

class AuctionListingForm(forms.ModelForm):
    class Meta:
        model = Auction_listings
        fields = ['nameProduct', 'descriptionProduct', 'inicialPrice', 'img_product', 'categories', 'end_time']
        labels = {
            'nameProduct': 'Title',
            'descriptionProduct': 'Description',
            'inicialPrice': 'Starting Bid',
            'img_product': 'Image URL',
            'categories': 'Categories',
            'end_time': 'End Time',
        }

    For_sale = forms.BooleanField(initial=True, widget=forms.HiddenInput())
    end_time = forms.DateTimeField(widget=SelectDateWidget())