from django.urls import path

from . import views


urlpatterns =[

    path('',views.HomeView.as_view(),name='home'),

    path('about/',views.AboutView.as_view(),name='about'),

    path('menu/',views.MenuItemListView.as_view(),name='menu_item-list'),

    path('add-to-cart/<str:uuid>/',views.AddToCartView.as_view(),name='add-to-cart'),

    path('cart/',views.CartPageView.as_view(),name='cart-page'),

    path('cart/increase/<str:uuid>/',views.IncreaseQuantityView.as_view(),name='cart-increase'),

    path('cart/decrease/<str:uuid>/',views.DecreaseQuantityView.as_view(),name='cart-decrease'),

    path('add-menu/',views.AddMenuItemView.as_view(), name='add-menu'),


]    