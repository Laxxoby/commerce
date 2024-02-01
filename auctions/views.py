from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime

from .models import User, Category, Auction_listings
from .forms import AuctionListingForm

def index(request):
    return render(request, "auctions/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def createlisting(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        inicialbid = request.POST.get('inicialbid')
        image_url = request.POST.get('image_url')
        categories = request.POST.getlist('categories')
        deadline = request.POST.get('deadline')
        
        owner_name_id = request.user.id
        start_time = datetime.now()
        
        owner_user = User.objects.get(id=owner_name_id)
        
        auction_listing = Auction_listings(
            nameProduct=title,
            descriptionProduct=description,
            inicialPrice=inicialbid,
            img_product=image_url,
            ownerName=owner_user,
            start_time=start_time,
            end_time = deadline
        )
        auction_listing.save()
        auction_listing.categories.set(categories)
        
        return HttpResponseRedirect(reverse("index"))
        
        """ # de forma con el form de Django 
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            auction_listing = form.save(commit=False)
            auction_listing.ownerName = request.user  # Asigna el usuario actual como propietario
            auction_listing.start_time = datetime.now()  # Configura start_time con la fecha y hora actuales
            auction_listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/createListing.html", {
                "categories" : Category.objects.all(),
                'form': auction_listing
            }) """
    else:
        # initial_values = {'end_time': datetime.now()}
        # form = AuctionListingForm(initial=initial_values)
        return render(request, "auctions/createListing.html", {
            "categories" : Category.objects.all(),
            # 'form': form
        })