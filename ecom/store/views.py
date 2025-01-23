from django.shortcuts import render,redirect
from .models import Product,Category,CustomerProfile
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from . form import SignUpForm,UpdateUserForm,ChangePasswordForm,UserInfoForm
from django.db.models import Q
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from payment.models import Order,OrderItem
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

def home(request):
    products=Product.objects.all()
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    try:
        # Step 4: Get the products for the current page
        products_paginated = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page
        products_paginated = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver the last page
        products_paginated = paginator.page(paginator.num_pages)
    return render(request,'store/index.html',context={'products':products_paginated})

def about(request):
    return render(request,'store/about.html')


def login_user(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            current_user=CustomerProfile.objects.get(user__id=request.user.id)
            saved_cart=current_user.old_cart
            if saved_cart:
                converted_cart=json.loads(saved_cart)
                cart=Cart(request)
                for item,quantity in converted_cart.items():
                    cart.db_add(product=item,quantity=quantity)
            messages.success(request,("You have been logged in !"))
            return redirect('home')
        else:
            messages.success(request,("There was an error"))
            return redirect('login')
        

    return render(request,'store/login.html')


def logout_user(request):
    logout(request)
    messages.success(request,("You have been logged out "))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)   
            login(request, user)
            messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
            return redirect('update_info')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
            return redirect('register')
    else:
        return render(request, 'store/register.html', {'form':form})
    


def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'store/product.html', {'product':product})


def category(request,category):
    str=category.replace('-','')
    try:
        # Look Up The Category
        category = Category.objects.get(name=str)
        products = Product.objects.filter(category=category)
        return render(request, 'store/category.html', {'products':products, 'category':category})
    except:
        messages.success(request, ("Coming Soon..."))
        return redirect('home')
    
def category_summary(request):
    categories=Category.objects.all()
    return render(request, 'store/category_summary.html',{'categories':categories})


def update_user(request):
    if request.user.is_authenticated:
        current_user=User.objects.get(id=request.user.id)
        user_form=UpdateUserForm(request.POST or None,instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request,current_user)
            messages.success(request,"Profile has been Updated !")
            return redirect('home')
        return render(request,'store/update_user.html',{'user_form':user_form})
    else:
        messages.success(request,"You must be logged in")  
        return redirect('home')
    
def update_password(request):
    if request.user.is_authenticated:
        current_user=request.user

        if request.method=='POST':
            form=ChangePasswordForm(current_user,request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,"Password has been Updated !")
                login(request,current_user)
                return redirect('update_user')
               
            else:
                for error in list(form.errors.values()):
                    messages.error(request,error) 
                    return redirect('update_password')           
        
        else:
            form=ChangePasswordForm(current_user)
            return render(request,'store/update_password.html',{'form':form})
    else:
        messages.success(request,"You must be logged in to perform this action")

    
def update_info(request):
    if request.user.is_authenticated:
        #current user
        current_user=CustomerProfile.objects.get(user__id=request.user.id)
        #current user's shippping information
        shipping_user=ShippingAddress.objects.get(user__id=request.user.id)

        form=UserInfoForm(request.POST or None,instance=current_user)

        shipping_form=ShippingForm(request.POST or None,instance=shipping_user)


        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request,"Your information has been Updated !")
            return redirect('home')
        return render(request,'store/update_info.html',{'form':form,'shipping_form':shipping_form})
    else:
        messages.success(request,"You must be logged in")  
        return redirect('home')
    

def search(request):

    if request.method=="POST":
        searched=request.POST['searched']
        searched=Product.objects.filter(Q(name__icontains=searched))

        if not searched:
            messages.success(request,"Oops! looks like the item does not exist.")
            return render(request,'store/search.html',{})
        else:
            return render(request,'store/search.html',{'searched':searched})

    else:   
        return render(request,'store/search.html',{})

    

def purchase_history(request):
    if request.user.is_authenticated:
        user_orders=Order.objects.filter(user__id=request.user.id)
        user_order_items={}
       
        
        for order in user_orders:
            items=OrderItem.objects.filter(order__id=order.id)
            
            for order_item in items:
                         
                if order in user_order_items:
                    user_order_items[order].append(order_item)
                   
                    
                else:
                    user_order_items[order]=[order_item]
                    

       
        return render(request,'store/purchase_history.html',{"orders":user_orders,"items":user_order_items})
    else:
        return redirect("home")
    
    