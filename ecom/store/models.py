from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural='Categories'
    
class Customer(models.Model):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    phone=models.CharField(max_length=10)
    email=models.EmailField(max_length=200)
    password=models.CharField(max_length=200)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Product(models.Model):
    name=models.CharField(max_length=100)
    price=models.DecimalField(max_length=200,decimal_places=2,max_digits=8,default=0)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,default=1)
    description=models.CharField(max_length=250,blank=True,null=True)
    image=models.ImageField(upload_to='uploads/product/')

    is_sale=models.BooleanField(default=False)
    sale_price=models.DecimalField(max_length=200,decimal_places=2,max_digits=8,default=0)
    
    def __str__(self):
        return self.name
    
    


class Order (models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    adderess=models.CharField(max_length=200,default='')
    phone=models.CharField(max_length=10,default='',blank=True)
    date=models.DateField(default=datetime.datetime.today)
    status=models.BooleanField(default=False)

    def __str__(self):
        return self.product
    
class CustomerProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    date_modified=models.DateTimeField(User,auto_now=True)
    phone=models.CharField(max_length=10,blank=True,null=True)
    address1=models.CharField(max_length=200,blank=True,null=True)
    address2=models.CharField(max_length=200,blank=True,null=True)
    city=models.CharField(max_length=40,blank=True,null=True)
    state=models.CharField(max_length=200,blank=True,null=True)
    zipcode=models.CharField(max_length=6,blank=True,null=True)
    country=models.CharField(max_length=40,blank=True,null=True)
    old_cart=models.CharField(max_length=200,blank=True,null=True)
    
    def __str__(self):
        return self.user.username


def create_profile(sender,instance,created,**kwargs):
    if created:
        user_profile=CustomerProfile(user=instance)
        user_profile.save()

post_save.connect(create_profile,sender=User)