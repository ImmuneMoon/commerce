from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Max

from .models import User, Listing, Category, Comment, Bid

import sqlite3

db = sqlite3.connect('db.sqlite3')

def index(request):
    # Grabs active listings of all users and displays them if any exist
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


# Simply pulls all the categories, then renders the categories page and passes them to the page
def categories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/categories.html', {
        'categories' : categories
    })


def category(request, cat):
    # Grabs the category id from the name given
    categoryId = Category.objects.get(categoryName=cat).id
    # Filters for listings that are active and contain the category id
    categoryInfo = Listing.objects.filter(active=True, category=categoryId)
    # Passes the category name and listings to the page
    return render(request, "auctions/category.html", {
        "listings" : categoryInfo,
        "category" : cat
    })


def listing(request, id):
    # Grabs the listing from the given id
    listingInfo = Listing.objects.get(pk=id)
    # Grabs the comments for the listing
    comments = Comment.objects.filter(listing=listingInfo)
    # Grabs the bids for the listing
    bids = Bid.objects.filter(auction=id).order_by('-bid')
    # Passes the data to the listing page
    return render(request, "auctions/listing.html", {
        "listing" : listingInfo,
        "comments" : comments,
        "bids" : bids
    })


def close_listing(request, lstng_id):
    next_url = request.POST.get('next', 'auctions/index.html')
    winner = request.POST["top-bidder"]
    listing = Listing.objects.get(id=lstng_id)
    if request.method == 'POST':
        listing.active = False
        listing.winner = winner
        listing.save()
        return redirect(next_url)


def delete_listing(request, lstng_id):
    # Grabs the current user
    user = request.user
    # Deletes listing
    Listing.objects.filter(user=user, pk=lstng_id).delete()
    # Grabs active listings of all users and displays them if any exist
    activeListings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "activeListings" : activeListings
    })


def watchlist(request):
    # Grabs the current user
    user = request.user
    # Pulls the users watchlist by searching listings that have the user in their watchlist
    watch_list = Listing.objects.filter(watchList=user)
    # Gets the amount of items in watchlist
    watch_amount = len(watch_list)
    # Gets the current page's URL, if the current page cant be redirected to, the user is redirected to index instead
    next_url = request.POST.get('next', 'auctions/index.html')
    # Renders the watchlist page on GET and passes the user's list
    if request.method == "GET":
        return render(request, "auctions/watchlist.html", {
            "watchlist" : watch_list,
            "watch_amount" : watch_amount
        })
    else:
        # Otherwise, the listing id is grabbed from it's invisible input
        listingId = request.POST.get("listing-id")
        # The pushed button's value is grabbed from it's invisible input
        watchBttn = request.POST.get("watch")
        # Grabs the listing information using the id
        listingInfo = Listing.objects.get(pk=listingId)
        # If the "add" button was clicked
        if watchBttn == "add":
            # The user is added the the listing's watchlist
            listingInfo.watchList.add(user)
            # Redirects to the page the user is on if possible
            return redirect(next_url)
        elif watchBttn == "remove":
            # The user is removed the the listing's watchlist
            listingInfo.watchList.remove(user)
            # Redirects to the page the user is on if possible
            return redirect(next_url)


# For rendering the user's profile
def user(request, uid):
    # Gets the user's listings
    userListings = Listing.objects.filter(user=uid)
    # Gets the listing's user
    author = User.objects.get(pk=uid)
    # Gets the current user
    user = request.user
    return render(request, "auctions/user.html", {
        "userListings" : userListings,
        "author" : author,
        "user_prof" : user
    })

def comment(request, lstng_id):
    next_url = request.POST.get('next', 'auctions/index.html')
    cmmntBttn = request.POST.get("comment-bttn")
    user = request.user
    if cmmntBttn == "post":
        newComment = request.POST["new-comment"]
        listing = Listing.objects.get(id=lstng_id)
        createComment = Comment(
            commenter = user,
            listing = listing,
            comment = newComment
        )
        createComment.save()
        return redirect(next_url)

    elif cmmntBttn == "delete":
        comment_id = request.POST.get("comment-id")
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        return redirect(next_url)

def bid(request, lstng_id):
    user = request.user
    next_url = request.POST.get('next', 'auctions/index.html')
    bid_amount = request.POST["bid-input"]
    starting_bid = request.POST.get("start-price")
    highest_bid = Bid.objects.filter(auction_id=lstng_id).aggregate(max_bid=Max('bid'))['max_bid']
    
    if bid_amount is None:
        return render(request, "auctions/error.html", {
                "error": "Please enter a bid amount."
            })
    elif float(bid_amount) <= float(starting_bid):
        return render(request, "auctions/error.html", {
                "error": "Please enter an amount greater than the starting bid."
            })
    elif highest_bid is not None and float(bid_amount) <= highest_bid:
        return render(request, "auctions/error.html", {
                "error": "Please enter an amount greater than the current highest bid."
            })
    else:
        listing = Listing.objects.get(pk=lstng_id)
        new_bid = Bid(bidder=user, bid=bid_amount, auction=listing)
        new_bid.save()
        return redirect(next_url)
