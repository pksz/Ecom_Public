from django.contrib import admin
from .models import Category,Customer,Order,Product,CustomerProfile
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(CustomerProfile)

#mix profile and user info
class ProfileInline(admin.StackedInline):
    model=CustomerProfile

class UserAdmin(admin.ModelAdmin):
    model=User
    fields=['username',"first_name","last_name","email"]
    inlines=[ProfileInline]


admin.site.unregister(User)
admin.site.register(User,UserAdmin)