from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime

from .models import User, Category, Auction_listings, watchlist
from .forms import AuctionListingForm


def index(request):
    products = Auction_listings.objects.all()
    return render(
        request,
        "auctions/index.html",
        {
            "products": products,
        },
    )


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            """ if product_id is not None:
                return HttpResponseRedirect(reverse("product"))
            else: """
            redirect_product_id = request.session.pop('redirect_product_id', None)
            redirect_product_name = request.session.pop('redirect_product_name', None)
            if redirect_product_id and redirect_product_name:
                redirect_url = reverse('product', args=[redirect_product_name]) + f"?product_id={redirect_product_id}"
                return HttpResponseRedirect(redirect_url)
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
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
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def createlisting(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        inicialbid = request.POST.get("inicialbid")
        image_url = request.POST.get("image_url")
        categories = request.POST.getlist("categories")
        deadline = request.POST.get("deadline")

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
            end_time=deadline,
            currentPrice=inicialbid,
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
        return render(
            request,
            "auctions/createListing.html",
            {
                "categories": Category.objects.all(),
                # 'form': form
            },
        )


def editlisting(request, product_name):
    product_id = request.GET.get("product_id")
    productF = Auction_listings.objects.get(pk=product_id, nameProduct=product_name)
    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "opcion1":
            productF.delete()
            return HttpResponseRedirect(reverse("index"))
        title = request.POST.get("title")
        description = request.POST.get("description")
        image_url = request.POST.get("image_url")
        categories = request.POST.getlist("categories")
        deadline = request.POST.get("deadline")

        productF.nameProduct = title
        productF.descriptionProduct = description
        productF.img_product = image_url
        productF.end_time = deadline

        productF.save()
        productF.categories.set(categories)

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(
            request,
            "auctions/editListing.html",
            {"categories": Category.objects.all(), "product": productF},
        )


def product(request, product_name):
    product_id = request.GET.get("product_id")
    productF = Auction_listings.objects.get(pk=product_id, nameProduct=product_name)
    
    if request.method == "POST":
        action = request.POST.get("action", "")
        
        if action == "opcion1":
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            productInList = watchlist.objects.get(user=user, product=productF)
            productInList.delete()
            pass
        if action == "opcion2":
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            
            wlist = watchlist(
                user=user,
                product=productF,
            )
            wlist.save()
            pass
        if action == "opcion3":
            request.session['redirect_product_id'] = product_id
            request.session['redirect_product_name'] = product_name
            
            return HttpResponseRedirect(reverse("login"))

    if request.user.is_authenticated:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        try:
            productInList = watchlist.objects.get(user=user, product=productF)
        except watchlist.DoesNotExist:
            productInList = None

        return render(request, "auctions/product.html",
            {"product": productF, "IsProduct": productInList},
        )
    else:
        productInList = None
        return render(request, "auctions/product.html",
            {"product": productF, "IsProduct": productInList},
        )