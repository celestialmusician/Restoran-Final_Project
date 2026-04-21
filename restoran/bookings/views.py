from django.views import View

from django.shortcuts import render, redirect

from restuarant.models import MenuItem 

from django.contrib import messages 

from bookings.models import Booking

from payments.models import Transaction


class BookingOrderView(View):

    template_name = "bookings/booking-details.html"

    def get(self, request):

        if not request.user.is_authenticated:

            return redirect("login")

        cart = request.session.get("cart")

        if not cart:
            return redirect("cart-page")

        
        booking = Booking.objects.create(

            user=request.user,

            total_amount=0,

            status="BOOKED"
        )

        cart_items = []
        
        total = 0

        for item_uuid, quantity in cart.items():

            item = MenuItem.objects.get(uuid=item_uuid)

            item_total = item.price * quantity

            total += item_total

            cart_items.append({

                "item": item,

                "quantity": quantity,

                "item_total": item_total
            })

        booking.total_amount = total

        booking.save()

        context = {
            "cart_items": cart_items,

            "total": total,

            "status": booking.status,

            "booking": booking,   
        }

        return render(request, self.template_name, context)




class BookingOrderCancelView(View):

    def get(self, request):

        if not request.user.is_authenticated:

            return redirect("login")

        request.session["booking_status"] = "CANCELLED"

        cart = request.session.get("cart", {})

        cart_items = []

        total = 0

        for item_uuid, quantity in cart.items():

            item = MenuItem.objects.get(uuid=item_uuid)

            item_total = item.price * quantity

            total += item_total

            cart_items.append({

                "item": item,

                "quantity": quantity,

                "item_total": item_total
                
            })

        context = {

            "cart_items": cart_items,

            "total": total,

            "status": "CANCELLED",
        }

        return render(request, "bookings/booking-details.html", context)
    

class BookingDetailView(View):

    template_name = "bookings/booking-details.html"

    def get(self, request, uuid):

        if not request.user.is_authenticated:

            return redirect("login")

        try:

            booking = Booking.objects.get(uuid=uuid, user=request.user)

        except Booking.DoesNotExist:

            return redirect("cart-page")

        cart = request.session.get("cart", {})

        cart_items = []

        for item_uuid, quantity in cart.items():

            item = MenuItem.objects.get(uuid=item_uuid)

            cart_items.append({

                "item": item,

                "quantity": quantity,

                "item_total": item.price * quantity

            })

        context = {

            "booking": booking,

            "cart_items": cart_items,   
            
            "total": booking.total_amount,
            
            "status": booking.status,
        }

        return render(request, self.template_name, context)

class PaymentReceiptView(View):

    template = "payments/receipt.html"

    def get(self, request, uuid):

        if not request.user.is_authenticated:

            return redirect("login")

        booking = Booking.objects.get(uuid=uuid, user=request.user)

        transaction = Transaction.objects.filter(

            booking=booking,

            status="Success"

        ).last()

        context = {

            "booking": booking,
            
            "transaction": transaction
        }

        return render(request, self.template, context)

  
