from django.shortcuts import render, redirect

from django.views import View

from django.contrib import messages

from bookings.models import Booking

from payments.models import Transaction, PaymentStatus

import razorpay

from decouple import config

from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator



class RazorPayView(View):

    template = "payments/razorpay.html"

    def get(self, request, uuid):

        booking = Booking.objects.get(uuid=uuid)

        client = razorpay.Client(

            auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET"))
        )

        data = {

            "amount": int(booking.total_amount * 100),

            "currency": "INR",

            "receipt": str(booking.uuid)

        }

        payment = client.order.create(data=data)

        rzp_order_id = payment.get("id")

        Transaction.objects.create(

            booking=booking,

            rzp_order_id=rzp_order_id,

            amount=booking.total_amount
        )

        context = {

            "RZP_CLIENT_ID": config("RZP_CLIENT_ID"),

            "amount": booking.total_amount,

            "order_id": rzp_order_id

        }

        return render(request, self.template, context)



class PaymentVerifyView(View):

    def post(self, request):

        rzp_order_id = request.POST.get("razorpay_order_id")
        
        rzp_payment_id = request.POST.get("razorpay_payment_id")

        rzp_payment_signature = request.POST.get("razorpay_signature")

        try:
            transaction = Transaction.objects.get(rzp_order_id=rzp_order_id)

        except Transaction.DoesNotExist:

            messages.error(request, "Transaction not found")

            return redirect("cart-page")

        transaction.rzp_payment_id = rzp_payment_id

        transaction.rzp_payment_signature = rzp_payment_signature

        client = razorpay.Client(

            auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET"))
        )

        try:
            client.utility.verify_payment_signature({

                "razorpay_order_id": rzp_order_id,

                "razorpay_payment_id": rzp_payment_id,

                "razorpay_signature": rzp_payment_signature
            })

            
            transaction.status = PaymentStatus.SUCCESS

            transaction.save()

            booking = transaction.booking

            booking.is_paid = True

            booking.status = "PAID"

            booking.save()

            messages.success(request, "Payment successful")

            
            return redirect("payment-receipt", booking.uuid)

        except razorpay.errors.SignatureVerificationError:

            transaction.status = PaymentStatus.FAILED

            transaction.save()

            messages.error(request, "Payment verification failed")

            return redirect("booking-details", transaction.booking.uuid)

        
class RazorPayView(View):

    template = "payments/razorpay.html"

    def get(self, request, uuid):

        booking = Booking.objects.get(uuid=uuid)

        client = razorpay.Client(

            auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET"))
        )

        data = {

            "amount": int(booking.total_amount * 100),

            "currency": "INR",

            "receipt": str(booking.uuid)
        }

        payment = client.order.create(data=data)

        rzp_order_id = payment["id"]

        Transaction.objects.create(

            booking=booking,

            rzp_order_id=rzp_order_id,

            amount=booking.total_amount
        )

        context = {

            "RZP_CLIENT_ID": config("RZP_CLIENT_ID"),

            "amount": int(booking.total_amount * 100),

            "order_id": rzp_order_id
        }

        return render(request, self.template, context)

    

@method_decorator(csrf_exempt, name="dispatch")

class PaymentVerifyView(View):

    def post(self, request):

        rzp_order_id = request.POST.get("razorpay_order_id")

        rzp_payment_id = request.POST.get("razorpay_payment_id")

        rzp_payment_signature = request.POST.get("razorpay_signature")

        try:

            transaction = Transaction.objects.get(rzp_order_id=rzp_order_id)

        except Transaction.DoesNotExist:

            messages.error(request, "Transaction not found")

            return redirect("cart-page")

        transaction.rzp_payment_id = rzp_payment_id

        transaction.rzp_payment_signature = rzp_payment_signature

        client = razorpay.Client(

            auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET"))

        )

        try:
            client.utility.verify_payment_signature({

                "razorpay_order_id": rzp_order_id,

                "razorpay_payment_id": rzp_payment_id,

                "razorpay_signature": rzp_payment_signature

            })

            transaction.status = PaymentStatus.SUCCESS

            transaction.save()

            booking = transaction.booking

            booking.is_paid = True

            booking.status = "PAID"

            booking.save()

            return redirect("payment-receipt", booking.uuid)

        except razorpay.errors.SignatureVerificationError:

            transaction.status = PaymentStatus.FAILED

            transaction.save()

            return redirect("booking-details", transaction.booking.uuid)



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

