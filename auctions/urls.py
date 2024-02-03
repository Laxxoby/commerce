from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.createlisting, name="createlisting"),
    path('edit-listing/<str:product_name>/', views.editlisting, name='editlisting'),
    path('<str:product_name>/', views.product, name='product'),
]
