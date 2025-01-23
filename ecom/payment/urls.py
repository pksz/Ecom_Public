from django.urls import path
from . import views

urlpatterns=[
    path('payment_success',views.payment_success,name="payment_success"),
    path('payment_failed',views.payment_failed,name="payment_failed"),
    path('checkout_review',views.checkout,name="checkout_review"),
    path('billing_info',views.billing_info,name="billing_info"),
    path('process_order',views.process_order,name="process_order"),
    path('shipped_dash',views.shipped_dash,name="shipped_dash"),
    path('not_shipped_dash',views.not_shipped_dash,name="not_shipped_dash"),
    path('order/<int:pk>/',views.orders,name="orders"),
    path('finalize_payment/',views.stripe_payment,name="finalize_payment"),
    path('webhook/stripe/',views.stripe_webhook,name="stripe_webhook"),
    
]
