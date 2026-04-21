from django.shortcuts import render,redirect

from django.views import View

from .forms import LoginForm,SignUpForm,AddPhoneForm,OTPForm,ChangePasswordForm

from django.contrib.auth import authenticate,login,logout

from django.contrib.auth.hashers import make_password

from restuarant.utils import generate_password,generate_otp,send_otp,send_email

from .models import OTP

from django.utils import timezone

import threading

from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator

from .permissions import permitted_user_roles

from django.views.generic import TemplateView

from .models import TableSeat



# Create your views here.

class LoginView (View) :

    template = 'authentication/login.html'

    form_class = LoginForm

    def get(self,request,*args,**kwargs) :

        form = self.form_class()

        data = {'form' : form}

        return render (request,self.template,context=data)
    
    def post(self,request,*args,**kwargs) :

        form = self.form_class(request.POST)

        error = None

        if form.is_valid() :

            email = form.cleaned_data.get('email')

            password = form.cleaned_data.get('password')

            user = authenticate(username = email, password = password)

            if user :

                login(request,user)

                return redirect('home')
            
            error = 'Invalid Username or Password'
        
        data = {'form':form,'error':error}

        return render (request,self.template,context=data)


@method_decorator(login_required(login_url='login'),name='dispatch')        
class LogoutView (View) :

    def get(self,request,*args,**kwargs) :

        logout(request)

        return redirect ('home')
    
class MustLoginView(View):

    template = "authentication/must-login.html"

    def get(self, request, *args, **kwargs):

        return render(request, self.template)    
    


class SignUpView(View):

    template = 'authentication/signup.html'

    form_class = SignUpForm

    def get(self,request,*args,**kwargs) :

        form = self.form_class

        data = {'page':'Sign Up','form':form}

        return render(request,self.template,context=data)
    
    def post(self,request,*args,**kwargs) :

        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.username = user.email

            password = generate_password()

            print(password)

            user.password = make_password(password)

            user.role = 'User'

            user.save()

            recipient = user.email

            template='emails/logincredentials.html'

            subject='CineFlix Login Credentials'

            context={'user':f'{user.first_name} {user.last_name}','username':user.email,'password':password}
            
            # send_email(recipient,template,subject,context)
            
            thread=threading.Thread(target=send_email,args=(recipient,template,subject,context))
            
            thread.start()

            return redirect('login')
        
        data = {'form':form}

        return render(request,self.template,context=data)
    

@method_decorator(permitted_user_roles(roles=['User','Admin']),name='dispatch')
class ProfileView(View):

    template = 'authentication/profile.html'

    def get(self,request,*args,**kwargs) :

        return render(request,self.template)
    
@method_decorator(permitted_user_roles(roles=['User']),name='dispatch')
class AddPhoneView(View):

    template = 'authentication/phone.html'

    form_class = AddPhoneForm

    def get(self,request,*args,**kwargs) :

        form = self.form_class()

        data = {'form':form}

        return render(request,self.template,context=data)
    
    def post(self,request,*args,**kwargs) :

        form = self.form_class(request.POST)

        if form.is_valid() :

            phone = form.cleaned_data.get('phone')

            request.session['phone'] = phone

            return redirect('verify-otp')
        
        data = {'form':form}

        return render(request,self.template,context=data)


@method_decorator(permitted_user_roles(roles=['User']),name='dispatch')
class VerifyOTPView(View) :

    template = 'authentication/otp.html'

    form_class = OTPForm

    def get(self,request,*args,**kwargs) :

        form = self.form_class()

        otp = generate_otp()

        user = request.user

        phone = request.session.get('phone')

        otp_obj,created = OTP.objects.get_or_create(profile=user)

        otp_obj.otp = otp

        otp_obj.save()

        send_otp(phone,otp)

        request.session['otp_time'] = timezone.now().timestamp()

        remaining_time = 300

        data = {'form':form,
                
                'remaining_time':remaining_time,

                'phone':phone
                
                }

        return render(request,self.template,context=data)
    
    def post(self,request,*args,**kwargs) :

        form = self.form_class(request.POST)

        if form.is_valid() :
        
            user=request.user

            db_otp=user.otp.otp

            input_otp=form.cleaned_data.get('otp')

            otp_time = request.session.get('otp_time')  

            current_time = timezone.now().timestamp()

            if otp_time :

                elapsed = current_time - otp_time

                remaining_time = max(0,300 - int(elapsed))

                if elapsed > 300 :

                    error = 'OTP expired Request a Newone'

                elif db_otp == input_otp :
                    

                    request.session.pop('otp_time')

                    phone = request.session.get('phone')

                    user.phone=phone

                    user.phone_verified = True
                    
                    user.save()

                    request.session.pop('phone')

                    return redirect('profile')
                
                else :


                    error = 'Invalid OTP'

        data={'form':form,'remaining_time':remaining_time,'error':error}

        return render(request,self.template,context=data)
    
@method_decorator(permitted_user_roles(roles=['User']),name='dispatch')    
class ChangePasswordOTPView(View):

    template = 'authentication/password-otp.html'

    form_class = OTPForm

    def get(self,request,*args,**kwargs):

        form = self.form_class()
        
        otp = generate_otp()

        user = request.user

        otp_obj,created = OTP.objects.get_or_create(profile=user)

        otp_obj.email_otp = otp

        otp_obj.save()

        recipient = user.email

        template = 'emails/password-otp-email.html'

        subject = 'Cineflix :OTP For change password'

        context = {'user':f'{user.first_name} {user.last_name}','otp':otp}

            # send_email(recipient,template,subject,context)

        thread = threading.Thread(target=send_email,args=(recipient,template,subject,context))

        thread.start()

        request.session['otp_time'] = timezone.now().timestamp()

        remaining_time = 300

        data = {'form':form,'remaining_time':remaining_time}

        return render(request,self.template,context=data)
    

    def post(self,request,*args,**kwargs):

        form = self.form_class(request.POST)
        
        if form.is_valid():

            user = request.user

            db_otp = user.otp.email_otp

            input_otp =form.cleaned_data.get('otp')

            otp_time = request.session.get('otp_time')  

            current_time = timezone.now().timestamp()

            if otp_time :

                elapsed = current_time - otp_time

                remaining_time = max(0, 300 - int(elapsed))

                if elapsed > 300 :

                    error = 'OTP expired Request a Newone'

                elif db_otp == input_otp:

                    request.session.pop('otp_time')
                    
                    user.otp.email_otp_verified = True

                    user.otp.save()

                    return redirect('change-password')
                
                else :


                    error = 'Invalid OTP'

        data = {'form':form,'remaining_time':remaining_time,'error':error}

        return render(request,self.template,context=data)
    
class ChangePassWordView(View):

    template='authentication/change-password.html'

    form_class=ChangePasswordForm

    def get(self,request,*args,**kwargs):

        user=request.user

        if user.otp.email_otp_verified:

            form=self.form_class()

            data={'form':form}

            return render(request,self.template,context=data)
        
        else:

            return redirect('password-otp')
    
    def post(self,request,*args,**kwargs):

        form=self.form_class(request.POST)

        if form.is_valid():

            user=request.user

            password=form.cleaned_data.get('new_password')

            user.password=make_password(password)

            user.save()

            user.otp.email_otp_verified=False

            user.otp.save()

            return redirect('login')
        
        data={'form':form}

        return render(request,self.template,context=data)
    

    from django.views.generic import TemplateView


from django.views.generic import TemplateView

class ContactView(TemplateView):

    template_name = "contact.html"


from django.views.generic import TemplateView

from django.contrib import messages

class ContactView(TemplateView):

    template_name = "contact.html"

    def post(self, request):

        messages.success(request, "Message sent successfully ✅")
        
        return self.get(request)
    



class TableBookingView(View):

    def get(self, request):
        

        if not request.user.is_authenticated:

            TableSeat.objects.update(is_booked=False)

        seats = TableSeat.objects.all()

        return render(request, "table_booking.html", {"seats": seats})

    def post(self, request):

        if not request.user.is_authenticated:

            return redirect("login")

        seat_ids = request.POST.get("seat_ids", "")

        if seat_ids:

            seat_ids = seat_ids.split(",")

            for sid in seat_ids:

                seat = TableSeat.objects.get(id=int(sid))

                seat.is_booked = True

                seat.save()

        seats = TableSeat.objects.all()

        return render(request, "table_booking.html", {"seats": seats})
   
    
        




        







           