from django.http import HttpResponse
from django.shortcuts import render, redirect

from utils.filehandler import handle_file_upload
from django.shortcuts import render, redirect, get_object_or_404
from utils.adminhandler import admin_required

from .forms import *
from .models import *
import pandas as pd

from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Product, Customer, Invoice, InvoiceDetail
from .forms import InvoiceForm, InvoiceDetailFormSet
import csv
# Create your views here.

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session["user"] = username  # store session
            return redirect("create_customer")
        else:
            error = "Invalid credentials"
            return render(request, "invoice/login.html", {"error": error})
    return render(request, "invoice/login.html")


def logout_view(request):
    request.session.flush()  # clear all session data
    return redirect("login")

# --------------------
# Generate Professional PDF Invoice
# --------------------
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
import qrcode
import io, os
from django.conf import settings

def getTotalIncome():
    allInvoice = Invoice.objects.all()
    totalIncome = 0
    for curr in allInvoice:
        totalIncome += curr.total
    return totalIncome

@admin_required
def base(request):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()
    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
    }

    return render(request, "invoice/base/base.html", context)



@admin_required
def download_all(request):
    allInvoiceDetails = InvoiceDetail.objects.all()

    invoiceAndProduct = {
        "invoice_id": [],
        "invoice_date": [],
        "invoice_customer": [],
        "invoice_contact": [],
        "invoice_email": [],
        "invoice_comments": [],
        "product_name": [],
        "product_price": [],
        "product_unit": [],
        "product_amount": [],
        "invoice_total": [],
    }

    for curr in allInvoiceDetails:
        invoice = Invoice.objects.filter(id=curr.invoice_id).first()
        product = Product.objects.filter(id=curr.product_id).first()

        # Skip if either invoice or product doesn't exist
        if not invoice or not product:
            continue

        invoiceAndProduct["invoice_id"].append(invoice.id)
        invoiceAndProduct["invoice_date"].append(invoice.date)
        invoiceAndProduct["invoice_customer"].append(invoice.customer)
        invoiceAndProduct["invoice_contact"].append(invoice.contact)
        invoiceAndProduct["invoice_email"].append(invoice.email)
        invoiceAndProduct["invoice_comments"].append(invoice.comments)
        # invoiceAndProduct["services_name"].append(product.services_name)
        # invoiceAndProduct["services_price"].append(product.services_price)
        # invoiceAndProduct["services_duration"].append(product.services_duration)
        # invoiceAndProduct[""].append(curr.amount)
        invoiceAndProduct["invoice_total"].append(invoice.total)

    # Export to Excel
    df = pd.DataFrame(invoiceAndProduct)
    output_path = "static/excel/allInvoices.xlsx"
    df.to_excel(output_path, index=False)

    # Return file as download response
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="allInvoices.xlsx"'
    with open(output_path, "rb") as f:
        response.write(f.read())

    return response

@admin_required
def delete_all_invoice(request):
    # Delete all invoice
    Invoice.objects.all().delete()
    return redirect("view_invoice")

@admin_required
def upload_product_from_excel(request):
    # Upload excel file to static folder "excel"
    # add all product to database
    # save product to database
    # redirect to view_product
    excelForm = excelUploadForm(request.POST or None, request.FILES or None)
    print("Reached HERE!")
    if request.method == "POST":
        print("Reached HERE2222!")

        handle_file_upload(request.FILES["excel_file"])
        excel_file = "static/excel/masterfile.xlsx"
        df = pd.read_excel(excel_file)
        Product.objects.all().delete()
        for index, row in df.iterrows():
            product = Product(
                product_name=row["product_name"],
                product_price=row["product_price"],
                product_unit=row["product_unit"],
            )
            print(product)
            product.save()
        return redirect("view_product")
    return render(request, "invoice/upload_products.html", {"excelForm": excelForm})

    # Product view

# Create product
@admin_required
def create_product(request):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("view_product")
    else:
        form = ProductForm()

    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "form": form,
    }
    return render(request, "invoice/create_product.html", context)


@admin_required
def view_product(request):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    product = Product.objects.filter(product_is_delete=False)
    print(product)
    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "product": product,
    }

    return render(request, "invoice/view_product.html", context)

# Edit product
@admin_required
def edit_product(request, pk):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    product_instance = Product.objects.get(id=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product_instance)
        if form.is_valid():
            form.save()
            return redirect("view_product")
    else:
        form = ProductForm(instance=product_instance)

    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "form": form,        # ✅ use 'form' not 'product'
        "editing": True,     # ✅ add this flag
    }

    return render(request, "invoice/create_product.html", context)


# Delete product
@admin_required
def delete_product(request, pk):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    product = Product.objects.get(id=pk)

    if request.method == "POST":
        product.product_is_delete = True
        product.save()
        return redirect("view_product")

    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "product": product,
    }

    return render(request, "invoice/delete_product.html", context)



# Customer view
@admin_required
def create_customer(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = CustomerForm()

    if request.method == "POST":
        customer = CustomerForm(request.POST)
        if customer.is_valid():
            customer.save()
            return redirect("view_customer")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": customer,
    }

    return render(request, "invoice/create_customer.html", context)


from django.db.models import Q
from django.shortcuts import render
@admin_required
def view_customer(request):
    # dashboard counts
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    # search value
    search = request.GET.get('search', '')

    # base queryset
    customer = Customer.objects.all()

    # apply search filter
    if search:
        customer = customer.filter(
            Q(customer_name__icontains=search) |
            Q(customer_number__icontains=search) |
            Q(customer_email__icontains=search)
        )

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": customer,
    }

    return render(request, "invoice/view_customer.html", context)



def customer_list(request):
    status = request.GET.get('status')  # normal or membership
    search = request.GET.get('search')

    customers = Customer.objects.all()

    # Filter by status
    if status == "Normal":
        customers = customers.filter(customer_status="Normal")
    elif status == "Membership":
        customers = customers.filter(customer_status="Membership")

    # Search filter
    if search:
        customers = customers.filter(
            customer_name__icontains=search
        ) | customers.filter(
            customer_number__icontains=search
        ) | customers.filter(
            customer_email__icontains=search
        )

    context = {
        "customer": customers
    }
    return render(request, "invoice/view_customer.html", context)

# Edit Customer
@admin_required
def edit_customer(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(instance=customer)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("view_customer")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": customer,
        "form": form,
    }

    return render(request, "invoice/edit_customer.html", context)


# Delete Customer
@admin_required
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        customer.delete()
        return redirect("view_customer")

    return render(request, "invoice/delete_customer.html", {"customer": customer})


# Invoice view
import io
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.conf import settings
import os

from .models import Product, Customer, Invoice, InvoiceDetail





from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, date
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from num2words import num2words
from io import BytesIO

@admin_required
def search_customers_ajax(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({"results": []})

    customers = Customer.objects.filter(
        Q(customer_name__icontains=query) |
        Q(customer_number__icontains=query) |
        Q(customer_email__icontains=query)
    )[:50]

    results = []
    for c in customers:
        results.append({
            "id": c.id,
            "name": c.customer_name,
            "number": c.customer_number,
            "email": c.customer_email or "",
            "gender": c.customer_gender,
            "dob": c.customer_dob.strftime('%Y-%m-%d') if c.customer_dob else "",
            "status": c.customer_status
        })

    return JsonResponse({"results": results})

@admin_required
def get_customer_details_ajax(request):
    """Get customer details by ID"""
    customer_id = request.GET.get('customer_id')
    try:
        customer = Customer.objects.get(id=customer_id)
        return JsonResponse({
            "success": True,
            "customer_name": customer.customer_name,
            "customer_number": customer.customer_number,
            "customer_email": customer.customer_email or '',
            "customer_gender": customer.customer_gender,
            "customer_dob": customer.customer_dob.strftime('%Y-%m-%d') if customer.customer_dob else '',
            "customer_status": customer.customer_status
        })
    except Customer.DoesNotExist:
        return JsonResponse({"success": False, "message": "Customer not found"})


from django.shortcuts import render, redirect
from django.http import FileResponse
from django.contrib import messages
from datetime import datetime, date
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from num2words import num2words

from .models import Product, Customer, Invoice, InvoiceDetail
from utils.adminhandler import admin_required



@admin_required
def create_invoice(request):
    products = Product.objects.all()
    customers = Customer.objects.all()

    if request.method == "GET":
        return render(request, "invoice/create_invoice.html", {
            "products": products,
            "total_product": products.count(),
            "total_invoice": Invoice.objects.count(),
            "customers": customers,
        })

    # ================= CUSTOMER =====================
    selected_customer_id = request.POST.get("selected_customer_id")
    new_name = request.POST.get("new_customer_name", "").strip()
    new_mobile = request.POST.get("new_customer_mobile", "").strip()
    new_gender = request.POST.get("new_customer_gender", "Male")
    new_status = request.POST.get("new_customer_status", "Normal")
    
    # Get price type from form (important!)
    price_type = request.POST.get("price_type", "regular")
    
    # Get amount paid
    amount_paid = request.POST.get("amount_paid", "0")
    try:
        amount_paid = float(amount_paid)
    except ValueError:
        amount_paid = 0.0

    # Get payment method
    payment_method = request.POST.get("payment_method", "CASH")

    customer = None

    if selected_customer_id:
        customer = Customer.objects.filter(id=selected_customer_id).first()
    elif new_name and new_mobile:
        existing_customer = Customer.objects.filter(
            customer_number=new_mobile
        ).first()
        
        if existing_customer:
            customer = existing_customer
        else:
            customer, _ = Customer.objects.get_or_create(
                customer_number=new_mobile,
                defaults={
                    "customer_name": new_name,
                    "customer_gender": new_gender,
                    "customer_status": new_status,
                }
            )

    if not customer:
        messages.error(request, "Please select or create a customer")
        return redirect("create_invoice")

    # ================= PRODUCTS =====================
    product_ids = request.POST.getlist("products")
    if not product_ids:
        messages.error(request, "Please select at least one service")
        return redirect("create_invoice")

    # ================= INVOICE ======================
    invoice = Invoice.objects.create(
        customer=customer.customer_name,
        contact=customer.customer_number,
        comments=request.POST.get("comments", "")
    )

    items = []
    total = 0
    regular_total = 0  # To calculate discount

    for index, pid in enumerate(product_ids, start=1):
        product = Product.objects.get(id=pid)
        qty = int(request.POST.get(f"quantity_{pid}", 1))
        
        # DETERMINE WHICH PRICE TO USE
        if price_type == 'membership' and customer.customer_status == 'Membership':
            # Use membership price if available
            price = float(product.membership_price)
            regular_price = float(product.services_price)
        else:
            # Use regular price
            price = float(product.services_price)
            regular_price = float(product.services_price)
        
        subtotal = qty * price
        regular_subtotal = qty * regular_price
        total += subtotal
        regular_total += regular_subtotal

        # Create invoice detail
        InvoiceDetail.objects.create(
            invoice=invoice,
            product=product,
            amount=qty
        )

        # Prepare display price for PDF
        if price_type == 'membership' and customer.customer_status == 'Membership':
            # Show both prices: Regular (strikethrough) and Membership
            price_display = f"₹{regular_price:.2f} → ₹{price:.2f}"
        else:
            price_display = f"₹{price:.2f}"

        # REMOVED HSN/SAC column - now only essential columns
        items.append([
            index,
            product.services_name[:30] + "..." if len(product.services_name) > 30 else product.services_name,
            str(qty),
            price_display,
            f"₹{subtotal:.2f}",
        ])

    # Calculate payment details
    invoice.total = total
    
    # Calculate discount
    discount = regular_total - total if regular_total > total else 0
    
    # Handle amount paid logic
    if amount_paid > 0:
        if amount_paid >= total:
            # Fully paid or overpaid
            invoice.amount_paid = total
            invoice.balance_due = 0
            if amount_paid > total:
                invoice.change_returned = amount_paid - total
            else:
                invoice.change_returned = 0
            invoice.payment_status = 'PAID'
        else:
            # Partially paid
            invoice.amount_paid = amount_paid
            invoice.balance_due = total - amount_paid
            invoice.change_returned = 0
            invoice.payment_status = 'PARTIAL'
    else:
        # No payment
        invoice.amount_paid = 0
        invoice.balance_due = total
        invoice.change_returned = 0
        invoice.payment_status = 'UNPAID'
    
    invoice.payment_method = payment_method
    invoice.discount_amount = discount
    invoice.save()

    # ================= PDF GENERATION =================
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Add background image (optional)
    try:
        from reportlab.lib.utils import ImageReader
        bg_image = ImageReader("https://i.pinimg.com/1200x/5a/f3/12/5af312bd3ebb3a67d92bc1e266065d30.jpg")
        c.drawImage(bg_image, 0, 0, width=width, height=height, mask='auto')
    except:
        pass

    # === Logo ===
    try:
        c.drawImage("https://curatherapycentre.com/images/logo.png", 40, height - 100, 
                   width=50, height=50, mask='auto')
    except:
        pass

    # === Header ===
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "CURA THERAPY CENTER")
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, height - 65, "CMC Eye Hospital Road, Arni Road, Vellore - 632001")
    c.drawCentredString(width / 2, height - 80, "Email: curatherapycenter@gmail.com | Mobile: +91 8610609373")
    
    # Invoice Title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 110, "TAX INVOICE")

    # === Border ===
    c.setLineWidth(1)
    c.rect(20, 20, width - 40, height - 40)

    # === Billing Info (Left Side) ===
    y = height - 150
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30, y, "Bill To:")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(30, y, f"{invoice.customer}")
    y -= 15
    c.drawString(30, y, f"Mobile: {invoice.contact}")
    y -= 15
    
    # Show customer status and price type
    if customer.customer_status == 'Membership':
        status_text = f"Status: {customer.customer_status}"
        if price_type == 'membership':
            status_text += " (Membership Price Applied)"
        else:
            status_text += " (Regular Price)"
        c.setFont("Helvetica-Bold", 9)
        c.drawString(30, y, status_text)
        y -= 15
    
    c.setFont("Helvetica", 9)
    c.drawString(30, y, f"Comments: {invoice.comments or 'N/A'}")

    # === Invoice Info (Right Side) ===
    info_x = 350
    y = height - 150
    c.setFont("Helvetica-Bold", 11)
    c.drawString(info_x, y, "Invoice Details:")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(info_x, y, f"Invoice No: INV-{invoice.id:06d}")
    y -= 18
    
    # Handle created_at field
    invoice_date = ""
    if hasattr(invoice, 'created_at') and invoice.created_at:
        invoice_date = invoice.created_at.strftime('%d-%b-%Y')
    else:
        invoice_date = date.today().strftime('%d-%b-%Y')
    
    c.drawString(info_x, y, f"Date: {invoice_date}")
    y -= 18
    c.drawString(info_x, y, f"Time: {datetime.now().strftime('%I:%M %p')}")

    # === Table Header (Removed HSN/SAC) ===
    y = height - 270
    headers = ["#", "Service Description", "Qty", "Price", "Amount (₹)"]
    col_x = [30, 60, 280, 360, 470]
    row_height = 22

    # Table header background
    c.setFillColor(colors.HexColor('#2c3e50'))
    c.rect(25, y - 10, width - 50, row_height, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    
    # Draw headers with proper alignment
    c.drawString(col_x[0], y - 5, headers[0])
    c.drawString(col_x[1], y - 5, headers[1])
    c.drawString(col_x[2], y - 5, headers[2])
    c.drawString(col_x[3], y - 5, headers[3])
    c.drawRightString(col_x[4] + 70, y - 5, headers[4])
    
    c.setFillColor(colors.black)

    # === Table Data ===
    y -= 25
    c.setFont("Helvetica", 9)
    for idx, row in enumerate(items):
        # Alternate row colors for better readability
        if idx % 2 == 0:
            c.setFillColor(colors.HexColor('#f8f9fa'))
            c.rect(25, y - 15, width - 50, row_height, fill=True, stroke=False)
            c.setFillColor(colors.black)
        
        c.drawString(col_x[0], y, str(row[0]))
        
        # Handle long service names
        service_name = row[1]
        c.drawString(col_x[1], y, service_name)
        
        c.drawString(col_x[2], y, row[2])
        c.drawString(col_x[3], y, row[3])
        c.drawRightString(col_x[4] + 70, y, row[4])
        
        y -= row_height
        if y < 220:
            c.showPage()
            y = height - 100
            c.setFont("Helvetica", 9)

    # === PAYMENT SUMMARY SECTION (Right Aligned) ===
    summary_y = y - 20
    
    # Draw payment summary box
    c.setFillColor(colors.HexColor('#f8f9fa'))
    c.rect(width - 250, summary_y - 140, 220, 150, fill=True, stroke=True)
    c.setFillColor(colors.black)
    
    # Summary title
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 240, summary_y - 15, "PAYMENT SUMMARY")
    
    # Draw a line
    c.line(width - 240, summary_y - 25, width - 40, summary_y - 25)
    
    current_y = summary_y - 40
    
    # Subtotal
    c.setFont("Helvetica", 10)
    c.drawString(width - 240, current_y, "Subtotal:")
    c.drawRightString(width - 40, current_y, f"₹{regular_total:,.2f}")
    current_y -= 15
    
    # Membership Discount (if applicable) - NOW SHOWING PROPERLY
    if discount > 0:
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor('#27ae60'))
        c.drawString(width - 240, current_y, "Membership Discount:")
        c.drawRightString(width - 40, current_y, f"-₹{discount:,.2f}")
        c.setFillColor(colors.black)
        current_y -= 15
    
    # Total
    c.setFont("Helvetica-Bold", 11)
    c.drawString(width - 240, current_y, "TOTAL:")
    c.setFillColor(colors.HexColor('#27ae60'))
    c.drawRightString(width - 40, current_y, f"₹{total:,.2f}")
    c.setFillColor(colors.black)
    
    # Draw a line before payment details
    current_y -= 10
    c.line(width - 240, current_y, width - 40, current_y)
    current_y -= 15
    
    # Payment Method
    method_colors = {
        'CASH': colors.HexColor('#27ae60'),
        'CARD': colors.HexColor('#2980b9'),
        'UPI': colors.HexColor('#8e44ad')
    }
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(method_colors.get(payment_method, colors.black))
    c.drawString(width - 240, current_y, f"Payment Mode: {payment_method}")
    c.setFillColor(colors.black)
    current_y -= 18
    
    # Amount Paid
    c.setFont("Helvetica", 10)
    c.drawString(width - 240, current_y, "Amount Paid:")
    if invoice.amount_paid > 0:
        c.setFillColor(colors.HexColor('#27ae60'))
    c.drawRightString(width - 40, current_y, f"₹{invoice.amount_paid:,.2f}")
    c.setFillColor(colors.black)
    current_y -= 18
    
    # Payment Status with proper display
    status_colors = {
        'PAID': colors.HexColor('#27ae60'),
        'PARTIAL': colors.HexColor('#f39c12'),
        'UNPAID': colors.HexColor('#e74c3c')
    }
    
    if invoice.payment_status == 'PAID':
        if invoice.change_returned > 0:
            # Show change returned
            c.drawString(width - 240, current_y, "Change Returned:")
            c.setFillColor(colors.HexColor('#27ae60'))
            c.drawRightString(width - 40, current_y, f"₹{invoice.change_returned:,.2f}")
            current_y -= 18
            
            # Show status
            c.drawString(width - 240, current_y, "Status:")
            c.setFillColor(status_colors['PAID'])
            c.drawRightString(width - 40, current_y, "PAID (Excess)")
            
    elif invoice.payment_status == 'PARTIAL':
        c.drawString(width - 240, current_y, "Balance Due:")
        c.setFillColor(colors.HexColor('#e74c3c'))
        c.drawRightString(width - 40, current_y, f"₹{invoice.balance_due:,.2f}")
        current_y -= 18
        
        c.drawString(width - 240, current_y, "Status:")
        c.setFillColor(status_colors['PARTIAL'])
        c.drawRightString(width - 40, current_y, "PARTIALLY PAID")
        
    else:  # UNPAID
        c.drawString(width - 240, current_y, "Balance Due:")
        c.setFillColor(colors.HexColor('#e74c3c'))
        c.drawRightString(width - 40, current_y, f"₹{invoice.balance_due:,.2f}")
        current_y -= 18
        
        c.drawString(width - 240, current_y, "Status:")
        c.setFillColor(status_colors['UNPAID'])
        c.drawRightString(width - 40, current_y, "UNPAID")
    
    c.setFillColor(colors.black)

    # === Amount in Words (Left Side) ===
    c.setFont("Helvetica", 9)
    amount_words = num2words(total, lang="en").title() + " Only"
    c.drawString(35, 160, "Amount in Words:")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(35, 145, f"Rupees {amount_words}")

    # === Bank Details (Left Side) ===
    bank_y = 120
    c.setFont("Helvetica-Bold", 10)
    c.drawString(35, bank_y, "Bank Details:")
    c.setFont("Helvetica", 8)
    c.drawString(35, bank_y - 12, "Bank: HDFC Bank")
    c.drawString(35, bank_y - 22, "A/c No: 50200012345678")
    c.drawString(35, bank_y - 32, "IFSC: HDFC0001234")
    c.rect(30, bank_y - 45, 200, 50, stroke=True)

    # === Terms & Conditions (Right Side) ===
    terms_y = 120
    c.setFont("Helvetica-Bold", 9)
    c.drawString(width - 250, terms_y, "Terms & Conditions:")
    c.setFont("Helvetica", 7)
    terms = [
        "1. Services once rendered cannot be refunded.",
        "2. Subject to Vellore jurisdiction only.",
        "3. This is a computer generated invoice.",
        "4. Thank you for your business!"
    ]
    term_y = terms_y - 12
    for term in terms:
        c.drawString(width - 250, term_y, term)
        term_y -= 10
    c.rect(width - 255, terms_y - 55, 230, 70, stroke=True)

    # === Signature ===
    c.line(width - 140, 40, width - 40, 40)
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 40, 30, "Authorized Signatory")

    c.showPage()
    c.save()
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"Invoice_{invoice.id:06d}.pdf"
    )

    
    
@admin_required
def get_customer_details(request):
    customer_id = request.GET.get("customer_id")
    customer = Customer.objects.get(id=customer_id)
    data = {
        "contact": customer.customer_number,
        "email": customer.customer_email,
        "status": customer.customer_status,
    }
    return JsonResponse(data)


@admin_required
def view_invoice(request):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    search = request.GET.get('search', '')

    invoice = Invoice.objects.all()

    if search:
        invoice = invoice.filter(
            Q(customer__icontains=search) |
            Q(contact__icontains=search) |
            Q(email__icontains=search) |
            Q(id__icontains=search)
        )

    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "invoice": invoice,
    }

    return render(request, "invoice/view_invoice.html", context)

@admin_required
def view_invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)

    # Get the actual customer object
    customer = None
    if invoice.customer:
        try:
            customer = Customer.objects.get(customer_name=invoice.customer)
        except Customer.DoesNotExist:
            customer = None

    context = {
        "invoice": invoice,
        "invoice_detail": invoice_detail,
        "customer": customer,  # pass customer object
    }
    return render(request, "invoice/view_invoice_detail.html", context)

@admin_required
def download_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
    
    
        # --------------------
        # Generate PDF Invoice
        # --------------------
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 100
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "INVOICE")
    y -= 30
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Customer Name: {invoice.customer}")
    y -= 20
    # p.drawString(50, y, f"Email: {invoice.email}")
    y -= 20
    p.drawString(50, y, f"Contact: {invoice.contact}")
    y -= 30

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Product")
    p.drawString(250, y, "Price")
    p.drawString(350, y, "Qty")
    p.drawString(420, y, "Subtotal")
    y -= 20

    p.setFont("Helvetica", 11)

    for detail in invoice.invoicedetail_set.all():
        product = detail.product
        subtotal = product.services_price * detail.amount

        # Draw product details
        p.drawString(50, y, product.services_name)
        p.drawString(250, y, f"{product.services_price}")
        p.drawString(350, y, str(detail.amount))
        p.drawString(420, y, f"{subtotal}")

        # Include product image (if available)
        if product.services_image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(product.services_image))
            if os.path.exists(image_path):
                try:
                    p.drawImage(image_path, 500, y - 10, width=0.8*inch, height=0.8*inch)
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")

        y -= 60  # move down

        if y < 100:  # start new page if too low
            p.showPage()
            y = height - 100

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, y, f"Total: ₹{invoice.total}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return response


# Delete invoice
@admin_required
def delete_invoice(request, pk):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)
    if request.method == "POST":
        invoice_detail.delete()
        invoice.delete()
        return redirect("view_invoice")

    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "invoice": invoice,
        "invoice_detail": invoice_detail,
    }

    return render(request, "invoice/delete_invoice.html", context)


# # Edit customer
# def edit_customer(request, pk):
#     total_product = Product.objects.count()
#     # total_customer = Customer.objects.count()
#     total_invoice = Invoice.objects.count()

#     customer = Customer.objects.get(id=pk)
#     form = CustomerForm(instance=customer)

#     if request.method == "POST":
#         customer = CustomerForm(request.POST, instance=customer)
#         if customer.is_valid():
#             customer.save()
#             return redirect("view_customer")

#     context = {
#         "total_product": total_product,
#         "total_customer": total_customer,
#         "total_invoice": total_invoice,
#         "customer": form,
#     }

#     return render(request, "invoice/create_customer.html", context)


# Delete customer
# def delete_customer(request, pk):
#     total_product = Product.objects.count()
#     total_customer = Customer.objects.count()
#     total_invoice = Invoice.objects.count()

#     customer = Customer.objects.get(id=pk)

#     if request.method == "POST":
#         customer.delete()
#         return redirect("view_customer")

#     context = {
#         "total_product": total_product,
#         "total_customer": total_customer,
#         "total_invoice": total_invoice,
#         "customer": customer,
#     }

#     return render(request, "invoice/delete_customer.html", context)


# from django.http import JsonResponse
# from .models import Customer

# def search_customers(request):
#     q = request.GET.get('q', '')
#     customers = Customer.objects.filter(customer_name__icontains=q)[:50]
#     results = [{"id": c.id, "customer_name": c.customer_name, "customer_number": c.customer_number} for c in customers]
#     return JsonResponse({"results": results})

# def get_customer_details(request):
#     customer_id = request.GET.get('customer_id')
#     try:
#         c = Customer.objects.get(id=customer_id)
#         return JsonResponse({"contact": c.customer_number, "email": c.customer_email, "status": "Active"})
#     except Customer.DoesNotExist:
#         return JsonResponse({"contact": "", "email": "", "status": ""})


from django.http import JsonResponse
from django.db.models import Q
from .models import Customer

def search_customers(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({"results": []})
    
    # Search in multiple fields: name, mobile, email
    customers = Customer.objects.filter(
        Q(customer_name__icontains=query) |
        Q(customer_number__icontains=query) |
        Q(customer_email__icontains=query)
    ).order_by('customer_name')[:50]
    
    results = []
    for customer in customers:
        results.append({
            "id": customer.id,
            "text": f"{customer.customer_name} - {customer.customer_number}",
            "customer_name": customer.customer_name,
            "customer_number": customer.customer_number,
            "customer_email": customer.customer_email
        })
    
    return JsonResponse({"results": results})

def get_customer_details(request):
    customer_id = request.GET.get('customer_id')
    try:
        customer = Customer.objects.get(id=customer_id)
        return JsonResponse({
            "contact": customer.customer_number,
            "email": customer.customer_email or "",
            "customer_name": customer.customer_name,
            "customer_gender": customer.customer_gender,
            "customer_status": customer.customer_status
        })
    except Customer.DoesNotExist:
        return JsonResponse({"contact": "", "email": "", "customer_name": "", "customer_gender": "", "customer_status": ""})
    
    
    
from django.shortcuts import render, redirect
from django.http import FileResponse
from django.contrib import messages
from datetime import datetime, date
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from num2words import num2words

from .models import Product, Customer, Invoice, InvoiceDetail
from utils.adminhandler import admin_required


@admin_required
def invoice(request):
    
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    products = Product.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        # ------------------------------
        # 1️⃣ Handle Customer Creation/Selection
        # ------------------------------
        customer_id = request.POST.get("customer")
        new_customer_name = request.POST.get("new_customer_name", "").strip()
        new_customer_mobile = request.POST.get("new_customer_mobile", "").strip()
        # new_customer_email = request.POST.get("new_customer_email", "").strip()
        new_customer_gender = request.POST.get("new_customer_gender", "Male")
        # new_customer_dob = request.POST.get("new_customer_dob", "")
        new_customer_status = request.POST.get("new_customer_status", "Normal")
        
        customer = None
        
        # Option 1: Existing customer selected
        if customer_id and customer_id != "new":
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                pass
        
        # Option 2: New customer provided
        elif new_customer_name and new_customer_mobile:
            # Check if customer already exists with this mobile
            existing_customer = Customer.objects.filter(
                customer_number=new_customer_mobile
            ).first()
            
            if existing_customer:
                customer = existing_customer
            else:
                # Create new customer with all required fields
                try:
                    # Handle date conversion
                    dob = None
                    if new_customer_dob:
                        try:
                            dob = datetime.strptime(new_customer_dob, '%Y-%m-%d').date()
                        except ValueError:
                            dob = date.today()  # Use today as default
                    else:
                        dob = date.today()  # Use today as default
                    
                    customer = Customer.objects.create(
                        customer_name=new_customer_name,
                        customer_gender=new_customer_gender,
                        customer_dob=dob,
                        customer_number=new_customer_mobile,
                        customer_email=new_customer_email if new_customer_email else None,
                        customer_status=new_customer_status
                    )
                except Exception as e:
                    return render(request, "invoice/create_invoice.html", {
                        "error": f"Error creating customer: {str(e)}",
                        "products": products,
                        "customers": customers,
                    })
        
        if not customer:
            return render(request, "invoice/create_invoice.html", {
                "error": "Please select a customer or enter new customer details.",
                "products": products,
                "customers": customers,
            })

        # ------------------------------
        # 2️⃣ Get Selected Products
        # ------------------------------
        selected_products = request.POST.getlist("products")
        quantities = request.POST.getlist("quantities")

        if not selected_products:
            return render(request, "invoice/create_invoice.html", {
                "error": "Please select at least one product.",
                "products": products,
                "customers": customers,
            })
            
    products = Product.objects.all()

    # ✅ HANDLE GET REQUEST (VERY IMPORTANT)
    if request.method == "GET":
        return render(request, "invoice/create_invoice.html", {
            "products": products,
            "total_product": products.count(),
            "total_invoice": Invoice.objects.count(),
        })

    # ================= POST REQUEST =================
    # ================= CUSTOMER =====================
    selected_customer_id = request.POST.get("selected_customer_id")

    new_name = request.POST.get("new_customer_name", "").strip()
    new_mobile = request.POST.get("new_customer_mobile", "").strip()
    new_email = request.POST.get("new_customer_email", "").strip()
    new_gender = request.POST.get("new_customer_gender", "Male")
    new_dob = request.POST.get("new_customer_dob")
    new_status = request.POST.get("new_customer_status", "Normal")

    customer = None

    # EXISTING CUSTOMER
    if selected_customer_id:
        customer = Customer.objects.filter(id=selected_customer_id).first()

    # NEW CUSTOMER
    elif new_name and new_mobile:
        dob = date.today()
        if new_dob:
            dob = datetime.strptime(new_dob, "%Y-%m-%d").date()

        customer, _ = Customer.objects.get_or_create(
            customer_number=new_mobile,
            defaults={
                "customer_name": new_name,
                "customer_gender": new_gender,
                "customer_dob": dob,
                "customer_email": new_email,
                "customer_status": new_status,
            }
        )

    if not customer:
        messages.error(request, "Please select or create a customer")
        return redirect("create_invoice")

    # ================= PRODUCTS =====================
    product_ids = request.POST.getlist("products")
    if not product_ids:
        messages.error(request, "Please select at least one service")
        return redirect("create_invoice")

    # ================= INVOICE ======================
    invoice = Invoice.objects.create(
            customer=customer.customer_name,
            contact=customer.customer_number,
            email=customer.customer_email or "",
            comments=request.POST.get("comments", ""),
        )

    total = 0
    items = []

    # ------------------------------
    # 4️⃣ Build Invoice Details
    # ------------------------------
    for i, (product_id, quantity) in enumerate(zip(selected_products, quantities), start=1):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        qty = int(quantity) if quantity else 1
        price = getattr(product, "services_price", getattr(product, "price", 0))
        subtotal = price * qty
        total += subtotal

        # Save to DB
        InvoiceDetail.objects.create(invoice=invoice, product=product, amount=qty)

        # Add to items table
        items.append([
            i,
            getattr(product, "services_name", getattr(product, "name", "Unnamed Product")),
            "9983",  # Example HSN/SAC code
            str(qty),
            "pcs",
            f"{price:.2f}",
            "0.00",  # Discount
            "0.00",  # Tax %
            f"{subtotal:.2f}",
        ])

    invoice.total = total
    invoice.save()

    # ------------------------------
    # 5️⃣ Generate Invoice PDF
    # ------------------------------
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    from reportlab.lib.utils import ImageReader
    bg_image = ImageReader("https://i.pinimg.com/1200x/5a/f3/12/5af312bd3ebb3a67d92bc1e266065d30.jpg")
    c.drawImage(bg_image, 0, 0, width=width, height=height, mask='auto')


    # === Logo ===
    try:
        c.drawImage("https://curatherapycentre.com/images/logo.png", 40, height - 100, width=50, height=50, mask='auto')
    except:
        pass

    # === Header ===
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 50, "BILL OF SUPPLY")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 70, "CURA THERAPY CENTER")

    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, height - 85, "CMC Eye Hospital Road, Arni Road, Vellore")
    c.drawCentredString(width / 2, height - 100, "Email: curatherapycenter@gmail.com | Mobile: +91 8610609373")

    # === Border ===
    c.setLineWidth(1)
    c.rect(20, 20, width - 40, height - 40)

    # === Billing Info ===
    y = height - 130
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y, "Billing Details")
    y -= 15
    c.setFont("Helvetica", 9)
    c.drawString(30, y, f"Name: {invoice.customer}")
    y -= 12
    c.drawString(30, y, f"Mobile: {invoice.contact}")
    y -= 12
    c.drawString(30, y, f"Email: {invoice.email}")
    y -= 12
    c.drawString(30, y, f"Comments: {invoice.comments}")

    # === Invoice Info ===
    info_x = 320
    y = height - 130
    c.setFont("Helvetica-Bold", 9)
    c.drawString(info_x, y, "Invoice Info:")
    y -= 15
    c.setFont("Helvetica", 9)
    c.drawString(info_x, y, f"Invoice No: {invoice.id}")
    y -= 12
    c.drawString(info_x, y, f"Invoice Date: {invoice.created_at.strftime('%d-%b-%Y') if hasattr(invoice, 'created_at') else date.today().strftime('%d-%b-%Y')}")
    y -= 12
    c.drawString(info_x, y, f"Due Date: -")
    y -= 12
    c.drawString(info_x, y, f"Time: {datetime.now().strftime('%I:%M %p')}")

    # === Table Header ===
    y = height - 220
    headers = ["Sr.", "Item Description", "HSN/SAC", "Qty", "Unit", "List Price", "Disc.", "Tax %", "Amount (₹)"]
    col_x = [30, 60, 210, 280, 310, 350, 410, 460, 510]
    row_height = 18

    c.setFillColor(colors.lightgrey)
    c.rect(25, y - 10, width - 50, 18, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers):
        c.drawString(col_x[i], y - 5, h)

    # === Table Data ===
    y -= 25
    c.setFont("Helvetica", 9)
    for row in items:
        for i, val in enumerate(row):
            c.drawString(col_x[i], y, str(val))
        y -= row_height
        if y < 100:  # new page if space ends
            c.showPage()
            y = height - 100
            c.setFont("Helvetica", 9)

    # === Total ===
    c.setFont("Helvetica-Bold", 11)
    c.drawString(120, y - 20, "Total")
    c.drawRightString(width - 40, y - 20, f"{invoice.total:,.2f}")

    # === Amount in Words ===
    c.setFont("Helvetica", 9)
    amount_words = num2words(invoice.total, lang="en").title() + " Only"
    c.drawString(35, y - 35, f"Rs. {amount_words}")

    # === Bank Details ===
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, 120, "Bank Details:")
    c.setFont("Helvetica", 9)
    c.drawString(30, 108, "Bank:")
    c.drawString(30, 96, "Account Number: ")
    c.drawString(30, 84, "IFSC: ")
    c.drawString(30, 72, "Branch: ")
    c.rect(25, 60, 270, 70, stroke=True)

    # === Terms ===
    c.setFont("Helvetica-Bold", 10)
    c.drawString(320, 120, "Terms & Conditions:")
    c.setFont("Helvetica", 9)
    terms = [
        "1. Goods once sold will not be taken back.",
        "2. Interest @18% p.a. will be charged if payment is delayed.",
        "3. Subject to 'Tamil Nadu' Jurisdiction only."
    ]
    y_terms = 108
    for term in terms:
        c.drawString(320, y_terms, term)
        y_terms -= 12
    c.rect(315, 60, width - 340, 70, stroke=True)

    # === Signature ===
    c.line(width - 140, 50, width - 40, 50)
    c.drawRightString(width - 40, 40, "Authorized Signature")

    c.showPage()
    c.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f"Invoice_{invoice.id}.pdf")

    #
    context = {
            "total_product": total_product,
            "total_invoice": total_invoice,
            "products": products,
            "customers": customers,
        }
    return render(request, "invoice/create_invoice.html", context)

from django.db.models import Q, Sum

from django.db.models import Q, Sum

@admin_required
def create_expences(request):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    if request.method == "POST":
        form = ExpencesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("view_expences")
    else:
        form = ExpencesForm()

    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "form": form,
    }
    return render(request, "invoice/create_expences.html", context)


@admin_required
def view_expences(request):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    # Get filter parameters
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    expences = Expences.objects.filter(expence_is_delete=False)
    
    # Apply filters
    if category_filter:
        expences = expences.filter(category__icontains=category_filter)
    if status_filter:
        expences = expences.filter(status=status_filter)
    if search_query:
        expences = expences.filter(
            Q(staf_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Get unique categories for filter dropdown
    unique_categories = Expences.objects.filter(
        expence_is_delete=False
    ).exclude(
        category__isnull=True
    ).exclude(
        category__exact=''
    ).values_list('category', flat=True).distinct().order_by('category')
    
    # Calculate total expenses
    total_expenses = expences.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "expences": expences,
        "unique_categories": unique_categories,
        "selected_category": category_filter,
        "selected_status": status_filter,
        "search_query": search_query,
        "total_expenses": total_expenses,
    }
    return render(request, "invoice/view_expences.html", context)


@admin_required
def edit_expences(request, pk):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    expences_instance = Expences.objects.get(id=pk)

    if request.method == "POST":
        form = ExpencesForm(request.POST, instance=expences_instance)
        if form.is_valid():
            form.save()
            return redirect("view_expences")
    else:
        form = ExpencesForm(instance=expences_instance)

    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "form": form,
        "editing": True,
    }
    return render(request, "invoice/create_expences.html", context)


@admin_required
def delete_expences(request, pk):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    expences = Expences.objects.get(id=pk)

    if request.method == "POST":
        expences.expence_is_delete = True
        expences.save()
        return redirect("view_expences")

    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "expences": expences,
    }
    return render(request, "invoice/delete_expences.html", context)


@admin_required
def download_customers_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID',
        'Customer Name',
        'Gender',
       
        'Mobile Number',
      
        'Status',
    ])

    customers = Customer.objects.all()

    for c in customers:
        writer.writerow([
            c.id,
            c.customer_name,
            c.customer_gender,
          
            c.customer_number,
            
            c.customer_status,
        ])

    return response

@admin_required
def download_all_invoices_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_invoices.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Invoice ID',
        'Invoice Date',
        'Customer Name',
        'Mobile',
        'Email',
        'Comments',
        'Total Amount',
        'Items',
    ])

    invoices = Invoice.objects.all().order_by('-id')

    for invoice in invoices:
        items = InvoiceDetail.objects.filter(invoice=invoice)
        item_names = ", ".join([
            f"{i.product.services_name} (Qty: {i.amount})"
            for i in items if i.product
        ])

        writer.writerow([
            invoice.id,
            invoice.date,
            invoice.customer,
            invoice.contact,
            invoice.email,
            invoice.comments,
            invoice.total,
            item_names,
        ])

    return response

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from datetime import datetime

@admin_required
def download_all_invoices_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_invoices.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 40, "All Invoices Report")

    c.setFont("Helvetica", 9)
    c.drawCentredString(
        width / 2,
        height - 60,
        f"Generated on {datetime.now().strftime('%d-%b-%Y %I:%M %p')}"
    )

    y = height - 90

    invoices = Invoice.objects.all().order_by('-id')

    for invoice in invoices:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, f"Invoice #{invoice.id} | {invoice.customer} | ₹{invoice.total}")
        y -= 14

        c.setFont("Helvetica", 9)
        details = InvoiceDetail.objects.filter(invoice=invoice)
        for d in details:
            if d.product:
                c.drawString(
                    60,
                    y,
                    f"- {d.product.services_name} (Qty: {d.amount})"
                )
                y -= 12

        y -= 10

        if y < 60:
            c.showPage()
            y = height - 60

    c.save()
    return response


@admin_required
def view_stock(request):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    # Get filter parameters
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    stock = Stock.objects.filter(expence_is_delete=False)
    
    # Apply filters
    if category_filter:
        stock = stock.filter(category=category_filter)
    if search_query:
        stock = stock.filter(
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Get unique categories for dropdown
    unique_categories = Stock.objects.filter(
        expence_is_delete=False
    ).exclude(
        category__isnull=True
    ).exclude(
        category__exact=''
    ).values_list('category', flat=True).distinct().order_by('category')
    
    # Calculate totals
    total_items = stock.count()
    total_quantity = stock.aggregate(total=Sum('quantity'))['total'] or 0
    total_value = sum(item.quantity * item.price for item in stock)
    
    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "stock": stock,
        "unique_categories": unique_categories,
        "selected_category": category_filter,
        "search_query": search_query,
        "total_items": total_items,
        "total_quantity": total_quantity,
        "total_value": total_value,
    }
    return render(request, "invoice/view_stock.html", context)


@admin_required
def create_stock(request):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("view_stock")
    else:
        form = StockForm()

    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "form": form,
    }
    return render(request, "invoice/create_stock.html", context)


@admin_required
def edit_stock(request, pk):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    stock_instance = Stock.objects.get(id=pk)

    if request.method == "POST":
        form = StockForm(request.POST, instance=stock_instance)
        if form.is_valid():
            form.save()
            return redirect("view_stock")
    else:
        form = StockForm(instance=stock_instance)

    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "form": form,
        "editing": True,
    }
    return render(request, "invoice/create_stock.html", context)


@admin_required
def delete_stock(request, pk):
    stock = Stock.objects.get(id=pk)

    if request.method == "POST":
        stock.expence_is_delete = True
        stock.save()
        return redirect("view_stock")

    return render(request, "invoice/delete_stock.html", {
        "stock": stock
    })


@admin_required
def download_stock(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stock_list.csv"'

    writer = csv.writer(response)

    # Header row (updated with category)
    writer.writerow(['ID', 'Item Name', 'Category', 'Quantity', 'Price', 'Total Value'])

    # Data rows
    stock_items = Stock.objects.filter(expence_is_delete=False)

    for stock in stock_items:
        writer.writerow([
            stock.id,
            stock.name,
            stock.category or '-',
            stock.quantity,
            stock.price,
            stock.quantity * stock.price,
        ])

    return response