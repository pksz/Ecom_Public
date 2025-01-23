from django.urls import path
from . import views
from ecom import settings
from django.conf.urls.static import static
urlpatterns=[
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('register/',views.register_user,name='register'),
    path('update_user/',views.update_user,name='update_user'),
    path('update_info/',views.update_info,name='update_info'),
    path('update_password/',views.update_password,name='update_password'),
    path('products/<int:pk>/',views.product,name='product'),
    path('category/<str:category>/',views.category,name='category'),
    path('category_summary/',views.category_summary,name='category_summary'),
    path('search/',views.search,name='search'),
    path('purchase_history/',views.purchase_history,name='purchase_history'),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)