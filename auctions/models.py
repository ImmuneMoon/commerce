from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.categoryName

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    title = models.CharField(max_length=50)
    info = models.CharField(max_length=1000)
    imageURL = models.URLField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchList = models.ManyToManyField(User, blank=True, related_name="watchlist")
    winner = models.CharField(max_length=50, default="None")

    def __str__(self) -> str:
        return self.title
    

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="commenter")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing")
    comment = models.CharField(max_length=500)

    def __str__(self) -> str:
        return f"{self.commenter} comment on {self.listing}"
    
class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="bidder")
    bid = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="auction")

    def __str__(self) -> str:
        return self.bid