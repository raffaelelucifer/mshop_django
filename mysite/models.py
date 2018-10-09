#_*_ coding: utf-8 _*_
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from usermanage.models import UserManage
from filer.fields.image import FilerImageField

@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sku = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = FilerImageField(related_name='product_image')
    #image = models.ImageField(upload_to='photos')
    website = models.URLField(null=True)
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Order(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(UserManage, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    createdat = models.DateTimeField(auto_now_add=True)
    updateat = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('-createdat',)

    def __str__(self):
        return 'Order:{}'.format(self.id)

@python_2_unicode_compatible
class OrderItem(models.Model):
    #user = models.ForeignKey(UserManage, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    #total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return '{}'.format(self.id)    












