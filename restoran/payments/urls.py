from django.urls import path

from . import views

urlpatterns = [

    path("make-payment/<str:uuid>/", views.RazorPayView.as_view(), name="make-payment"),

    path("payment-verify/", views.PaymentVerifyView.as_view(), name="payment-verify"),
    
    path("receipt/<str:uuid>/", views.PaymentReceiptView.as_view(), name="payment-receipt"),
    
]
