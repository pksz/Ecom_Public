from django.shortcuts import render,redirect
from cart.cart import Cart
from .forms import ShippingForm,PaymentForm
from .models import Order,OrderItem,ShippingAddress
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import CustomerProfile,Product
import datetime
import stripe
from django.urls import reverse_lazy
from ecom.settings import STRIPE_API_KEY
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse	
import json
from django.contrib.sessions.models import Session
from django.contrib import messages
from django.http import HttpRequest
import ecom.settings
# Create your views here.

endpoint_secret=ecom.settings.endpoint_secret

#


def payment_success(request):
    return render(request,'payment/payment_success.html',{})
	

def payment_failed(request):
    return render(request,'payment/payment_failure.html',{})


def checkout(request):
    cart=Cart(request)
    cart_products=cart.get_prods()
    quantities= cart.get_quants()
    totals=cart.cart_total()

    if request.user.is_authenticated:
		# Checkout as logged in user
		# Shipping User
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		# Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form })
    else:
		# Checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})




@login_required(login_url='login')
def billing_info(request):

    if request.POST:

        cart=Cart(request)
        cart_products=cart.get_prods()
        quantities= cart.get_quants()
        totals=cart.cart_total() 

        my_shipping=request.POST
        request.session['my_shipping']=my_shipping


        if request.user.is_authenticated:
            billing_form=PaymentForm()
            return render(request, "payment/billing_info.html",{"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST,"billing_form":billing_form})
        else:
            billing_form=PaymentForm()
            return render(request, "payment/billing_info.html",{"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST,"billing_form":billing_form})

    else:
        return redirect('home')
    

def process_order(request):
	if request.POST:
		# Get the cart
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()

		# Get Billing Info from the last page
		payment_form = PaymentForm(request.POST or None)
		# Get Shipping Session Data
		my_shipping = request.session.get('my_shipping')

		# Gather Order Info
		full_name = my_shipping['shipping_full_name']
		email = my_shipping['shipping_email']
		# Create Shipping Address from session info
		shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
		amount_paid = totals

		# Create an Order
		if request.user.is_authenticated:
			# logged in
			user = request.user
			# Create Order
			create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

			# Add order items
			
			# Get the order ID
			order_id = create_order.pk
			
			# Get product Info
			for product in cart_products():
				# Get product ID
				product_id = product.id
				# Get product price
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Get quantity
				for key,value in quantities().items():
					if int(key) == product.id:
						# Create order item
						create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
						create_order_item.save()

			# Delete our cart
			for key in list(request.session.keys()):
				if key == "session_key":
					# Delete the key
					del request.session[key]

			# Delete Cart from Database (old_cart field)
			current_user = CustomerProfile.objects.filter(user__id=request.user.id)
			# Delete shopping cart in database (old_cart field)
			current_user.update(old_cart="")


			messages.success(request, "Order Placed!")
			return redirect('home')

			

		else:
			# not logged in
			# Create Order
			create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

			# Add order items
			
			# Get the order ID
			order_id = create_order.pk
			
			# Get product Info
			for product in cart_products():
				# Get product ID
				product_id = product.id
				# Get product price
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Get quantity
				for key,value in quantities().items():
					if int(key) == product.id:
						# Create order item
						create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
						create_order_item.save()

			# Delete our cart
			for key in list(request.session.keys()):
				if key == "session_key":
					# Delete the key
					del request.session[key]



			messages.success(request, "Order Placed!")
			return redirect('home')


	else:
		messages.success(request, "Access Denied")
		return redirect('home')
	

def shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders_shipped=Order.objects.filter(shipped=True)
		if request.POST:
			num=request.POST["num"]
			status=request.POST["shipping_status"]
			order=Order.objects.filter(id=num)
			now=datetime.datetime.now()
			order.update(shipped=False,date_shipped=now)
			messages.success(request,"Shipping Status Updated")
		return render(request,'payment/shipped_dash.html',{"orders":orders_shipped})
	else:
		return redirect("home")


def not_shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders_not_shipped=Order.objects.filter(shipped=False)
		if request.POST:
			num=request.POST["num"]
			status=request.POST["shipping_status"]
			order=Order.objects.filter(id=num)
			now=datetime.datetime.now()
			order.update(shipped=True,date_shipped=now)
			messages.success(request,"Shipping Status Updated")
		return render(request,'payment/not_shipped_dash.html',{"orders":orders_not_shipped})
	else:
		return redirect("home")
	


def orders(request,pk):
	if request.user.is_authenticated and request.user.is_superuser:
		order=Order.objects.get(id=pk)
		items=OrderItem.objects.filter(order=pk)

		if request.POST:
				status=request.POST['shipping_status']

				if status=="True":
					order=Order.objects.filter(id=pk)
					now=datetime.datetime.now()
					order.update(shipped=True,date_shipped=now)
				if status=="False":
					order=Order.objects.filter(id=pk)
					order.update(shipped=False)
				messages.success(request,"Shipping Status Updated")
				return redirect("home")
		return render(request,'payment/orders.html',{"order":order,"items":items})

	else:
		return redirect("home")

@login_required
def stripe_payment(request):
	if request.user.is_authenticated:
		user=request.user
		customer=CustomerProfile.objects.get(user=user)
		email=user.email
		stripe.api_key=STRIPE_API_KEY
		if not request.session.session_key:
			request.session.create()
		session_key=request.session.session_key
		#gets current user's cart
		cart=Cart(request)
		#gets current user's orders from cart
		user_order=cart.get_prods()
		quantity=cart.get_quants()
		line_items=[]
		my_shipping=json.dumps(request.session.get('my_shipping'))
		#creates line items for stripe
		for cart_product in user_order:
			price=cart_product.sale_price if cart_product.is_sale else cart_product.price
			line_item={
				'price_data':{
					'currency':'usd',
					'product_data':{
						'name':cart_product.name,
						#'images':[cart_product.image.url]
					},
					'unit_amount':int(price*100)},
				'quantity':quantity[str(cart_product.id)]
			}
			line_items.append(line_item)

			

		try:
			checkout_session = stripe.checkout.Session.create(
			payment_method_types=['card'],
			line_items=line_items,
			mode='payment',
			success_url=request.build_absolute_uri(reverse_lazy('payment_success')),
			cancel_url=request.build_absolute_uri(reverse_lazy('payment_failed')),
			client_reference_id=str(request.user.id),
			metadata={
				'session_key':session_key,
				'user_id':request.user.id,	
				'shipping':my_shipping
				}
			
				)
			return redirect(checkout_session.url, code=303)
		except Exception as e:
			print(str(e))
			messages.error(request, "There was an error with Stripe. Please try again.")
		return redirect('checkout')


def fulfill_checkout(cart,shipping,session,user_id,session_key,stripe_session_id):
	print('inside fulfill_checkout')
	stripe.api_key=STRIPE_API_KEY
	checkout_session=stripe.checkout.Session.retrieve(stripe_session_id,expand=['line_items'])
	
	if checkout_session.payment_status=="paid":
		cart = cart
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()
		print('inside stripe payment')
		# Get Shipping Session Data
		my_shipping =shipping

		# Gather Order Info
		full_name = my_shipping['shipping_full_name']
		email = my_shipping['shipping_email']
		# Create Shipping Address from session info
		shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
		amount_paid = totals

		# Create an Order
		if user_id:
			print('inside user_id')
			# logged in
			user = User.objects.get(id=user_id)
			# Create Order
			create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

			# Add order items
			
			# Get the order ID
			order_id = create_order.pk
			
			# Get product Info
			for product in cart_products():
				# Get product ID
				product_id = product.id
				# Get product price
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Get quantity
				for key,value in quantities().items():
					if int(key) == product.id:
						# Create order item
						create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
						create_order_item.save()

			#Delete our cart
			session = Session.objects.get(session_key=session_key)
		
			session_data = session.get_decoded()
			# Delete the session key

			key='session_key'
			
			if key in session_data:
				# Delete the key
					del session_data[key]
					print('session_data')
					session.session_data = Session.objects.encode(session_data)
					session.save()
			
			# Delete Cart from Database (old_cart field)
			current_user = CustomerProfile.objects.filter(user__id=user_id)
			# Delete shopping cart in database (old_cart field)
			current_user.update(old_cart="")
			print('reached here')
			return True

@csrf_exempt
def stripe_webhook(request):
	
	payload=request.body
	sig_header=request.META['HTTP_STRIPE_SIGNATURE']
	event=None

	try:
		event=stripe.Webhook.construct_event(
			payload, sig_header, endpoint_secret
		)

	except ValueError as e:
		return HttpResponse(status=400)
	
	except stripe.error.SignatureVerificationError as e:
    # Invalid signature
		return HttpResponse(status=400)
	

	if (
	event['type'] == 'checkout.session.completed'
	or event['type'] == 'checkout.session.async_payment_succeeded'):
		stripe_session = event['data']['object']
		stripe_session_id=stripe_session['id']
		session_key=stripe_session['metadata']['session_key']
		user_id=stripe_session['metadata']['user_id']
		shipping=json.loads(stripe_session['metadata']['shipping'])
		
		try:
			session_data = Session.objects.get(session_key=session_key).get_decoded()
			print(session_data)
			if session_data.get('_auth_user_id') != user_id:
				print('User ID mismatch')
				print(session_data.get('_auth_user_id'))
				print(user_id)
				return HttpResponse(status=403)
			#a class to mock the request object,created to get the cart of the user and original request object
			class MockRequest:
					session = session_data

			#get the cart of the user
			cart=Cart(MockRequest)
			for key in session_data:
				if key == "session_key":
					# Delete the key
					print('yay')
			success=fulfill_checkout(cart,shipping,stripe_session,user_id,session_key,stripe_session_id)
			if success:
				print('Order fulfilled')
			else:
				print("Order fulfillment failed")

		except Session.DoesNotExist:
			return HttpResponse("Session not found", status=404)
		
	
		
		
	return HttpResponse(status=200)
	
	