from django.contrib import admin
from .models import User, Category, Auction_listings, Bids, Comments, watchlist

# Register your models here.
class Auction_listingsAdmin(admin.ModelAdmin):
    list_display = ['nameProduct', 'ownerName', 'inicialPrice', 'start_time', 'end_time']
    list_filter = ['categories']
    search_fields = ['nameProduct', 'ownerName__username']
    
class BidsAdmin(admin.ModelAdmin):
    list_display = ['bidder', 'product', 'bid', 'timestamp']
    search_fields = ['bidder__username', 'product__nameProduct']
    
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['user', 'productComment', 'comment', 'timestamp']
    search_fields = ['user__username', 'productComment__nameProduct']


class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product']
    search_fields = ['user__username', 'product__nameProduct']

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction_listings, Auction_listingsAdmin)
admin.site.register(watchlist, WatchlistAdmin)
admin.site.register(Bids, BidsAdmin)
admin.site.register(Comments, CommentsAdmin)