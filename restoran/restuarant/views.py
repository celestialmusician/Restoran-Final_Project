from django.shortcuts import render,redirect

from django.views import View

from django.db.models import Q

from .models import MenuItem

from django.contrib import messages

from .forms import MenuItemForm
# Create your views here.



class HomeView(View):

    def get(self,request,*args,**kwargs):

        return render(request,'home.html')
    

class AboutView(View):

    def get(self,request,*args,**kwargs):

        return render(request,'about.html')   
    

class MenuItemListView(View):

    template = 'restuarant/menu_item-list.html'

    def get(self, request, *args, **kwargs):

        category = request.GET.get('category')

        menu_items = MenuItem.objects.filter(is_available=True)

        if category and category != 'All':
            menu_items = menu_items.filter(category=category)

        context = {'menu_items': menu_items,'category': category}

        return render(request, self.template, context)

class AddToCartView(View):

    def get(self, request, *args, **kwargs):

        item_uuid = kwargs.get('uuid')   # string

        menu_item = MenuItem.objects.filter(uuid=item_uuid).first()

        if not menu_item:
            return redirect('menu-item-list')

        cart = request.session.get('cart')

        if not cart:
            cart = {}

        if item_uuid in cart:
            cart[item_uuid] += 1
        else:
            cart[item_uuid] = 1

        request.session['cart'] = cart

        return redirect('cart-page')
    

class CartPageView(View):

    template = 'restuarant/cart.html'

    def get(self, request, *args, **kwargs):

        cart = request.session.get('cart', {})

        cart_items = []
        total_amount = 0

        for item_uuid, quantity in cart.items():

            item = MenuItem.objects.filter(uuid=item_uuid).first()

            if item:
                item_total = item.price * quantity
                total_amount += item_total

                cart_items.append({
                    'item': item,
                    'quantity': quantity,
                    'item_total': item_total
                })

        context = {
            'cart_items': cart_items,
            'total_amount': total_amount
        }

        return render(request, self.template, context)
    
class IncreaseQuantityView(View):

    def get(self, request, *args, **kwargs):

        item_uuid = kwargs.get('uuid')

        cart = request.session.get('cart', {})

        if item_uuid in cart:
            cart[item_uuid] += 1

        request.session['cart'] = cart

        return redirect('cart-page')


class DecreaseQuantityView(View):

    def get(self, request, *args, **kwargs):

        item_uuid = kwargs.get('uuid')

        cart = request.session.get('cart', {})

        if item_uuid in cart:
            if cart[item_uuid] > 1:
                cart[item_uuid] -= 1
            else:
                del cart[item_uuid]

        request.session['cart'] = cart

        return redirect('cart-page')




class AddMenuItemView(View):

    form_class = MenuItemForm
    template = "restuarant/add-menu.html"

    def get(self, request, *args, **kwargs):

        form = self.form_class()

        data = {
            'page': 'Add Menu',
            'form': form
        }

        return render(request, self.template, context=data)

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Menu item added successfully")
            return redirect("menu-list")

        messages.error(request, "Failed to add menu item")
        print(form.errors)

        data = {
            'page': 'Add Menu',
            'form': form
        }

        return render(request, self.template, context=data)


        




