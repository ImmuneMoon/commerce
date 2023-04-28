from django.urls import path

from . import views

app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("categories", views.categories, name="categories"),
    path("category/<str:cat>/", views.category, name="category"),
    path("listing/<int:id>/", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("user/<str:uid>/", views.user, name="user"),
    path("comment/<int:lstng_id>/", views.comment, name="comment"),
    path("delete_listing/<int:lstng_id>/", views.delete_listing, name="delete_listing"),
    path("close_listing/<int:lstng_id>/", views.close_listing, name="close_listing"),
    path("bid/<int:lstng_id>/", views.bid, name="bid")

]
