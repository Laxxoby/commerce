from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length=64, unique=True)
    
    def __str__(self) -> str:
        return f"{self.categoryName}"

class Auction_listings(models.Model):
    nameProduct = models.CharField(max_length=64)
    descriptionProduct = models.CharField(max_length=300)
    ownerName = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    inicialPrice = models.DecimalField(max_digits=10, decimal_places=2)
    currentPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name="typesCategory")
    img_product = models.CharField(max_length=604)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    For_sale = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return f"name: {self.nameProduct} and owner {self.ownerName} bud estimate {self.inicialPrice}"
    
class Bids(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    product = models.ForeignKey(Auction_listings, on_delete=models.CASCADE, related_name="products")
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personComment")
    productComment = models.ForeignKey(Auction_listings, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userWatchlist")
    product = models.ForeignKey(Auction_listings, on_delete=models.CASCADE, blank=True, related_name="personproductList")
    
    def __str__(self):
        return f"{self.user.username} sigue {self.product.nameProduct}"
    
    class Meta:
        unique_together = ['user', 'product']
