from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from decimal import Decimal

from .models import User, Category, Auction_listings, watchlist, Bids, Comments
from .forms import AuctionListingForm
from . import util

def index(request):
    products = Auction_listings.objects.filter(For_sale=True).order_by('-start_time', 'nameProduct')

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
            redirect_product_id = request.session.pop("redirect_product_id", None)
            redirect_product_name = request.session.pop("redirect_product_name", None)
            if redirect_product_id and redirect_product_name:
                redirect_url = (
                    reverse("product", args=[redirect_product_name])
                    + f"?product_id={redirect_product_id}"
                )
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
        
        # by default add in the watchlist
        productF = Auction_listings.objects.get(start_time=start_time, nameProduct=title)
        wlist = watchlist(
            user=owner_user,
            product=productF,
        )
        wlist.save()

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
    comentsPro = Comments.objects.filter(productComment=productF).order_by('-timestamp')
    message = None
    productInList = None
    messageF = None

    # Category List
    categories = productF.categories.all()
    listCa = [category.categoryName for category in categories]

    if listCa:
        strCategories = ", ".join(listCa)
    else:
        strCategories = "There are no categories associated with this product."

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "opcion1":
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            productInList = watchlist.objects.get(user=user, product=productF)
            productInList.delete()

        if action == "opcion2":
            user_id = request.user.id
            user = User.objects.get(id=user_id)

            wlist = watchlist(
                user=user,
                product=productF,
            )
            wlist.save()

        if action == "opcion3":
            request.session["redirect_product_id"] = product_id
            request.session["redirect_product_name"] = product_name

            return HttpResponseRedirect(reverse("login"))

        if action == "opcion4":
            productF.For_sale = False
            productF.save()

            # view report
            redirect_url = (
                    reverse("report", args=[product_name]) + f"?product_id={product_id}"
                )
            return HttpResponseRedirect(redirect_url)

        Bid = request.POST.get("Bid")
        if Bid:
            Bid = Decimal(Bid)
            current_price = productF.currentPrice
            if Bid <= current_price:
                message = (
                    f"your bid must exceed the current bid of {productF.currentPrice}"
                )
            else:
                message = None
                Bid = request.POST.get("Bid")
                productF.currentPrice = Bid

                productF.save()
                user_id = request.user.id
                bidder = User.objects.get(id=user_id)

                bidlist = Bids(
                    bidder=bidder,
                    product=productF,
                    bid=Bid,
                )

                bidlist.save()

        comment = request.POST.get("comment")
        if comment:
            user_id = request.user.id
            userC = User.objects.get(id=user_id)

            Commentslist = Comments(
                user=userC,
                productComment=productF,
                comment=comment,
            )

            Commentslist.save()

    if request.user.is_authenticated:
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        if productF.For_sale == False:
            winner = util.obtener_ganador_de_subasta(productF)

            if winner and winner == user:
                messageF = "Congratulations! You are the winner of this auction."
            else:
                messageF = "You are not the winner of this auction."

        try:
            productInList = watchlist.objects.get(user=user, product=productF)
        except watchlist.DoesNotExist:
            productInList = None

        return render(
            request,
            "auctions/product.html",
            {
                "product": productF,
                "IsProduct": productInList,
                "message": message,
                "messageF": messageF,
                "strCategories": strCategories,
                "comments": comentsPro
            },
        )
    else:
        return render(
            request,
            "auctions/product.html",
            {
                "product": productF,
                "IsProduct": productInList,
                "strCategories": strCategories,
                "comments": comentsPro
            },
        )


def watchlistv(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        productInList = watchlist.objects.filter(user=user)
    return render(
        request,
        "auctions/watchlist.html",
        {
            "products": productInList,
        },
    )


def report(request, product_name):
    product_id = request.GET.get("product_id")
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    productF = Auction_listings.objects.get(pk=product_id, nameProduct=product_name)
    BidsList = Bids.objects.filter(product=productF)
    
    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "opcion1":
            productF.delete()
            return HttpResponseRedirect(reverse("index"))
    
    return render(
        request,
        "auctions/report.html",
        {
            "BidsList": BidsList,
            "Product": productF
        },
    )
    
def categoria(request, categoria):
    try:
        categoriaF = Category.objects.get(categoryName=categoria)
        products = Auction_listings.objects.filter(categories=categoriaF,For_sale=True).order_by('-start_time', 'nameProduct')
    except Category.DoesNotExist:
        products =  None
    return render(request, "auctions/categoria.html", {
        "products": products,
        "categoria": categoria
    })