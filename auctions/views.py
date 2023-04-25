from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Category

import sqlite3

db = sqlite3.connect('db.sqlite3')

def index(request):
    # Grabs active listings and displays them if any exist
    activeListings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "activeListings" : activeListings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


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
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")

def new_listing(request):
    # Renders the listing page on GET
    if request.method == 'GET':
        categories = Category.objects.all()
        return render(request, 'auctions/new_listing.html', {
            'categories' : categories
        })
    # Submits the form on POST
    else:
        # Gets the user, and form info
        user = request.user
        title = request.POST["title"]
        info = request.POST["info"]
        image = request.POST["image"]
        price = request.POST["price"]
        category = ""
        categorySelect = request.POST["category"]
        newCategory = request.POST["new-category"]
        # Server check for empty fields
        if title == '' or info =='' or image =='' or price == '':
            return render(request, "auctions/error.html", {
                "error": "Please complete all fields."
            })
        # If no empty fields
        else:
            # Checks if the user created a new category and adds the category if they did
            if newCategory != "":
                category = newCategory
                Category.objects.create(categoryName = category)
            else:
                category = categorySelect
            # Fetches the category and creates the listing
            categoryData = Category.objects.get(categoryName = category)
            createListing = Listing(
                title = title,
                info = info,
                imageURL = image,
                price = float(price),
                user = user,
                category = categoryData
            )
            # Saves the listing to the database
            createListing.save()

            # Checks whether the user indicated if they want to make another listing or not
            button_value = request.POST.get('button')
            if button_value == 'save':
                # If they didnt, theyre redirected to index
                return HttpResponseRedirect(reverse("auctions:index"))
            elif button_value == 'add-another':
                # If they did, the new listing page is rendered again
                return HttpResponseRedirect(reverse("auctions:new_listing"))


def categories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/categories.html', {
        'categories' : categories
    })

def category(request, name):
    categoryInfo = Listing.objects.get(category=name)
    print('categoryInfo',categoryInfo)
    return render(request, "auctions/category.html", {
        "category" : categoryInfo
    })


def listing(request, id):
    listingInfo = Listing.objects.get(pk=id)
    print('listinginfo: ',listingInfo)
    return render(request, "auctions/listing.html", {
        "listing" : listingInfo
    })

def watchlist(request):
    something=""
