from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    path('', views.create_invoice, name='home'),

    path('create_product/', views.create_product, name='create_product'),
    path('view_product/', views.view_product, name='view_product'),
    path('edit_product/<int:pk>', views.edit_product, name='edit_product'),
    path('delete_product/<int:pk>/', views.delete_product, name='delete_product'),
    path('upload_product_excel', views.upload_product_from_excel,
         name='upload_product_excel'),
    path('create_customer', views.create_customer, name='create_customer'),
    path('view_customer/', views.view_customer, name='view_customer'),
    path('customer_list/', views.customer_list, name='customer_list'),
    path('edit_customer/<int:pk>', views.edit_customer, name='edit_customer'),
    path('delete_customer/<int:pk>/', views.delete_customer, name='delete_customer'),

    path('create_invoice/', views.create_invoice, name='create_invoice'),
    path('view_invoice/', views.view_invoice, name='view_invoice'),
    path('delete_invoice/<int:pk>/', views.delete_invoice, name='delete_invoice'),
    path('delete_all_invoice/', views.delete_all_invoice,
         name='delete_all_invoice'),
    path('download_all_invoice/', views.download_all,
         name='download_all_invoice'),
    path('view_invoice_detail/<int:pk>/',
         views.view_invoice_detail, name='view_invoice_detail'),
    
    path("get-customer-details/", views.get_customer_details, name="get_customer_details"),
    
    path('invoice/<int:invoice_id>/download/', views.download_invoice_pdf, name='download_invoice_pdf'),
     
     path('search-customers-ajax/', views.search_customers_ajax, name='search_customers_ajax'),
     path('get-customer-details-ajax/', views.get_customer_details_ajax, name='get_customer_details_ajax'),
     
     
     
     path("expences/create/", views.create_expences, name="create_expences"),
     path("expences/",views.view_expences, name="view_expences"),
     path("expences/edit/<int:pk>/", views.edit_expences, name="edit_expences"),
     path("expences/delete/<int:pk>/", views.delete_expences, name="delete_expences"),

     path('customers/download/', views.download_customers_csv, name='download_customers'),
    
     path('invoice/download/all/', views.download_all_invoices_csv, name='download_all_invoices'),
     path('invoice/download/all/pdf/', views.download_all_invoices_pdf, name='download_all_invoices_pdf'),
     
     
     path('stock/', views.view_stock, name='view_stock'),
     path('stock/create/', views.create_stock, name='create_stock'),
     path('stock/edit/<int:pk>/', views.edit_stock, name='edit_stock'),
     path('stock/delete/<int:pk>/', views.delete_stock, name='delete_stock'),
     path('stock/download/', views.download_stock, name='download_stock'),




     
]
