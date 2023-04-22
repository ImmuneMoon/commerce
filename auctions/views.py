from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Category

import sqlite3

db = sqlite3.connect('db.sqlite3')

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
    if request.method == 'GET':
        categories = Category.objects.all()
        return render(request, 'auctions/new_listing.html', {
            'categories' : categories
        })
    else:
        user = request.user
        title = request.POST["title"]
        info = request.POST["info"]
        image = request.POST["image"]
        price = request.POST["price"]
        category = ""
        categorySelect = request.POST["category"]
        newCategory = request.POST["new-category"]
        if newCategory != "":
            category = newCategory
            Category.objects.create(categoryName = category)
        else:
            category = categorySelect
        categoryData = Category.objects.get(categoryName = category)
        createListing = Listing(
            title = title,
            info = info,
            imageURL = image,
            price = float(price),
            user = user,
            category = categoryData
        )
        createListing.save()
        return HttpResponseRedirect(reverse("auctions:index"))