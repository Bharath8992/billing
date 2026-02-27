from django.contrib import admin
from .models import *


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'services_name', 'services_price',
                    'services_duration']


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name',
                    'customer_gender',  'customer_status']


class InvoiceDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'product', 'amount']


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id',  'customer', 'total']
    
class ExpencesAdmin(admin.ModelAdmin):
    list_display = ['id', 'staf_name', 'amount',
                'status']


# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(InvoiceDetail, InvoiceDetailAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Expences, ExpencesAdmin)
