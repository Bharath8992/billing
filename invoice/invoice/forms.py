from django import forms
from django.forms import formset_factory

from .models import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'services_name',
            'services_price',
            'membership_price',
            'services_duration',
            'services_image',
        ]
        widgets = {
            'services_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'services_name',
                'placeholder': 'Enter name of the services',
            }),
            'services_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'services_price',
                'placeholder': 'Enter price of the services',
                'type': 'number',
            }),
            'membership_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'membership_price',
                'placeholder': 'Enter price of the membership',
                'type': 'number',
            }),
            'services_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'services_duration',
                'placeholder': 'Enter price of the durations',
                'type': 'number',
            }),
            'services_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'id': 'services_image',
            }),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'customer_name',
            'customer_gender',
            'customer_dob',
            'customer_number',
            'customer_email',
            'customer_status'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'customer_name',
                'placeholder': 'Enter name of the customer',
            }),
            'customer_gender': forms.Select(attrs={
                'class': 'form-control',
                'id': 'customer_gender',
            }),
            'customer_dob': forms.DateInput(attrs={
                'class': 'form-control',
                'id': 'customer_dob',
                'placeholder': '2000-01-01',
                'type': 'date',
            }),
            'customer_number': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'customer_number',
                'placeholder': 'Enter number of the customer',
            }),
            'customer_email': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'customer_email',
                'placeholder': 'Enter email of the customer',
            }),
            'customer_status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'customer_status',
            }),
        }


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'customer',
            'comments',
            'contact',
            'email',
        ]
        widgets = {
            'customer': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'invoice_customer',
                'placeholder': 'Enter name of the customer',
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'invoice_contact',
                'placeholder': 'Enter contact of the customer',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'invoice_email',
                'placeholder': 'Enter email of the customer',
            }),
            'comments': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'invoice_comments',
                'placeholder': 'Enter comments',
            }),

        }


class InvoiceDetailForm(forms.ModelForm):
    class Meta:
        model = InvoiceDetail
        fields = [
            'product',
            'amount',
        ]
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control',
                'id': 'invoice_detail_product',
            }),
            'amount': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'invoice_detail_amount',
                'placeholder': '0',
                'type': 'number',
            })
        }


class excelUploadForm(forms.Form):
    file = forms.FileField()


InvoiceDetailFormSet = formset_factory(InvoiceDetailForm, extra=1)
