from django.contrib import admin
from .models import User, Category, Auction_listings

# Register your models here.
class Auction_listingsAdmin(admin.ModelAdmin):
    list_display = ['nameProduct', 'ownerName', 'inicialPrice', 'start_time', 'end_time']
    list_filter = ['categories']
    search_fields = ['nameProduct', 'ownerName__username']
    


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction_listings, Auction_listingsAdmin)
