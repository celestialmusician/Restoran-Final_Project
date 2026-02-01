from django.urls import path
from .import views 



urlpatterns = [
    path("order/",views.BookingOrderView.as_view(),name="booking-order"),

    path("order/cancel/",views.BookingOrderCancelView.as_view(), name="booking-cancel"),

    path("booking/<str:uuid>/", views.BookingDetailView.as_view(), name="booking-details"),

]