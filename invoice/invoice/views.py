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
# Create your views here.

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session["user"] = username  # store session
            return redirect("home")
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
def crate_product(request):
    total_product = Product.objects.count()
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    product = ProductForm()

    if request.method == "POST":
        product = ProductForm(request.POST)
        if product.is_valid():
            product.save()
            return redirect("view_product")

    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
        "total_invoice": total_invoice,
        "total_income": total_income,
        "product": product,
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

@admin_required
def view_customer(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = Customer.objects.all()

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": customer,
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




from django.http import FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from num2words import num2words
import io
import os
from django.conf import settings

@admin_required
def create_invoice(request):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()
    products = Product.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        # ------------------------------
        # 1️⃣ Fetch Form Data
        # ------------------------------
        customer_id = request.POST.get("customer")
        customer = Customer.objects.get(id=customer_id)
        selected_products = request.POST.getlist("products")
        quantities = request.POST.getlist("quantities")

        if not selected_products or not quantities:
            return render(request, "invoice/create_invoice.html", {
                "error": "Please select at least one product.",
                "products": products,
                "customers": customers,
            })

        # ------------------------------
        # 2️⃣ Create Invoice Entry
        # ------------------------------
        invoice = Invoice.objects.create(
            customer=customer.customer_name,
            contact=customer.customer_number,
            email=customer.customer_email,
            comments=request.POST.get("comments", ""),
        )

        total = 0
        items = []

        # ------------------------------
        # 3️⃣ Build Invoice Details
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
        # 4️⃣ Generate Invoice PDF
        # ------------------------------
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        from reportlab.lib.utils import ImageReader
        bg_image = ImageReader("https://i.pinimg.com/1200x/c2/aa/16/c2aa16f86d0bce94af0250fbd8aa6476.jpg")
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
        # c.drawString(info_x, y, f"Invoice Date: {invoice.created_at.strftime('%d-%b-%Y')}")
        y -= 12
        c.drawString(info_x, y, f"Due Date: -")
        y -= 12
        # c.drawString(info_x, y, f"Time: {invoice.created_at.strftime('%I:%M %p')}")

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
        c.drawString(30, 108, "Bank: ICICI Bank")
        c.drawString(30, 96, "Account Number: 123456789")
        c.drawString(30, 84, "IFSC: ICIC0001234")
        c.drawString(30, 72, "Branch: Vellore")
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
        c.setFont("Helvetica", 9)
        c.drawRightString(width - 40, 80, "For CURA THERAPY CENTER")

        c.line(width - 140, 50, width - 40, 50)
        c.drawRightString(width - 40, 40, "Authorized Signature")

        c.showPage()
        c.save()
        buffer.seek(0)

        # Return file as response
        return FileResponse(buffer, as_attachment=True, filename=f"Invoice_{invoice.id}.pdf")

    # ------------------------------
    # GET Request
    # ------------------------------
    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "products": products,
        "customers": customers,
    }
    return render(request, "invoice/create_invoice.html", context)

@admin_required
def reate_invoice(request):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()

    products = Product.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        customer = Customer.objects.get(id=customer_id)
        selected_products = request.POST.getlist("products")
        quantities = request.POST.getlist("quantities")

        # Create invoice
        invoice = Invoice.objects.create(
            customer=customer.customer_name,
            contact=customer.customer_number,
            email=customer.customer_email,
            comments=request.POST.get("comments", ""),
        )

        total = 0
        for product_id, quantity in zip(selected_products, quantities):
            product = Product.objects.get(id=product_id)
            amount = int(quantity)
            subtotal = product.services_price * amount
            total += subtotal
            InvoiceDetail.objects.create(invoice=invoice, product=product, amount=amount)

        invoice.total = total
        invoice.save()

        # --------------------
        # Generate PDF Invoice
        # --------------------
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # ========== HEADER ==========
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width / 2, height - 40, "BILL OF SUPPLY")

        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 60, "Add Company Name")

        p.setFont("Helvetica", 10)
        p.drawCentredString(width / 2, height - 75, "Add Address")
        p.drawCentredString(width / 2, height - 90, "Email: company@email.com | GSTIN: 29AAAAA1234M1Z4 | PAN: AAAAA1234M")

        # ========== BILLING DETAILS ==========
        y = height - 130
        p.setFont("Helvetica-Bold", 11)
        p.drawString(40, y, "Billing Details:")
        p.setFont("Helvetica", 10)
        y -= 15
        p.drawString(40, y, f"Name: {invoice.customer}")
        y -= 15
        p.drawString(40, y, f"Mobile: {invoice.contact}")
        y -= 15
        p.drawString(40, y, f"Email: {invoice.email}")
        y -= 15
        p.drawString(40, y, f"Comments: {invoice.comments}")

        # ========== INVOICE INFO ==========
        y = height - 130
        p.setFont("Helvetica-Bold", 11)
        p.drawString(350, y, "Invoice Info:")
        p.setFont("Helvetica", 10)
        y -= 15
        p.drawString(350, y, f"Invoice No: {invoice.id}")
        y -= 15
        p.drawString(350, y, f"Invoice Date: {invoice.date.strftime('%d-%b-%Y') if hasattr(invoice, 'date') else 'N/A'}")
        y -= 15
        p.drawString(350, y, f"Due Date: -")
        y -= 15
        p.drawString(350, y, f"Time: {invoice.created_at.strftime('%I:%M %p') if hasattr(invoice, 'created_at') else ''}")

        # ========== TABLE HEADER ==========
        y -= 30
        p.setFont("Helvetica-Bold", 10)
        p.drawString(40, y, "Sr.")
        p.drawString(70, y, "Item Description")
        p.drawString(240, y, "HSN/SAC")
        p.drawString(300, y, "Qty")
        p.drawString(340, y, "Unit")
        p.drawString(380, y, "List Price")
        p.drawString(440, y, "Disc.%")
        p.drawString(480, y, "Tax %")
        p.drawString(520, y, "Amount (₹)")

        # Draw line under header
        y -= 5
        p.line(40, y, width - 40, y)
        y -= 15
        p.setFont("Helvetica", 9)

        # ========== TABLE CONTENT ==========
        count = 1
        for detail in invoice.invoicedetail_set.all():
            product = detail.product
            subtotal = product.services_price * detail.amount

            p.drawString(45, y, str(count))
            p.drawString(70, y, product.services_name[:25])
            p.drawString(240, y, "9983")  # Example HSN/SAC
            p.drawRightString(325, y, str(detail.amount))
            p.drawString(340, y, "N.A.")
            p.drawRightString(410, y, f"{product.services_price:.2f}")
            p.drawRightString(460, y, "0.00")
            p.drawRightString(500, y, "0.00")
            p.drawRightString(565, y, f"{subtotal:.2f}")

            y -= 18
            count += 1
            if y < 100:
                p.showPage()
                y = height - 100

        # ========== TOTAL SECTION ==========
        y -= 20
        p.line(40, y, width - 40, y)
        y -= 20
        p.setFont("Helvetica-Bold", 10)
        p.drawRightString(520, y, "Total:")
        p.drawRightString(565, y, f"{invoice.total:.2f}")

        # ========== AMOUNT IN WORDS ==========
        from num2words import num2words
        amount_words = num2words(invoice.total, lang='en').title() + " Only"
        y -= 25
        p.setFont("Helvetica", 9)
        p.drawString(40, y, f"Rs. {amount_words}")

        # ========== TERMS AND CONDITIONS ==========
        y -= 40
        p.setFont("Helvetica-Bold", 10)
        p.drawString(40, y, "Terms and Conditions:")
        p.setFont("Helvetica", 8)
        y -= 12
        p.drawString(40, y, "1. Goods once sold will not be taken back.")
        y -= 12
        p.drawString(40, y, "2. Interest @18% p.a. will be charged if payment is delayed.")
        y -= 12
        p.drawString(40, y, "3. Subject to 'Delhi' Jurisdiction only.")

        # ========== BANK DETAILS & QR ==========
        y -= 40
        p.setFont("Helvetica-Bold", 9)
        p.drawString(40, y, "Bank Details:")
        p.setFont("Helvetica", 8)
        y -= 12
        p.drawString(40, y, "Bank: ICICI Bank")
        y -= 12
        p.drawString(40, y, "IFSC: ICIC1234")
        y -= 12
        p.drawString(40, y, "Branch: Noida")
        y -= 12
        p.drawString(40, y, "Account Number: 123456789")
        y -= 12
        p.drawString(40, y, "Account Name: Add Name")

        # QR Code
        

        # Signature area
        
        p.line(width - 120, 70, width - 40, 70)
        p.drawRightString(width - 40, 60, "Authorized Signature")

        # Finish up
        p.showPage()
        p.save()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename=f"Invoice_{invoice.id}.pdf")
    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "products": products,
        "customers": customers,
    }
    return render(request, "invoice/create_invoice.html", context)

@admin_required
def creae_invoice(request):
    total_product = Product.objects.count()
    total_invoice = Invoice.objects.count()

    products = Product.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        customer = Customer.objects.get(id=customer_id)
        selected_products = request.POST.getlist("products")
        quantities = request.POST.getlist("quantities")

        # Create invoice
        invoice = Invoice.objects.create(
            customer=customer.customer_name,
            contact=customer.customer_number,
            email=customer.customer_email,
            comments=request.POST.get("comments", ""),
        )

        total = 0
        for product_id, quantity in zip(selected_products, quantities):
            product = Product.objects.get(id=product_id)
            amount = int(quantity)
            subtotal = product.services_price * amount
            total += subtotal
            InvoiceDetail.objects.create(invoice=invoice, product=product, amount=amount)

        invoice.total = total
        invoice.save()
        return redirect("view_invoice")

    context = {
        "total_product": total_product,
        "total_invoice": total_invoice,
        "products": products,
        "customers": customers,
    }
    return render(request, "invoice/create_invoice.html", context)


# AJAX view for auto-filling customer details
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
    # total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    total_income = getTotalIncome()

    invoice = Invoice.objects.all()

    context = {
        "total_product": total_product,
        # "total_customer": total_customer,
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
    p.drawString(50, y, f"Email: {invoice.email}")
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

