from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from num2words import num2words

def generate_invoice(
    filename="invoice_dynamic.pdf",
    company_info=None,
    billing_info=None,
    invoice_info=None,
    items=None,
    bank_info=None,
    terms=None
):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Default data if nothing passed
    company_info = company_info or {
        "name": "Test Company",
        "address": "Test Address, Chennai, Tamil Nadu, 123456, India",
        "contact": "Mobile: +91 9864513213 | Email: company@email.com",
        "copy_type": "Original Copy"
    }

    billing_info = billing_info or {
        "name": "Cash",
        "address": "sdgdsg, Tamil Nadu, India"
    }

    invoice_info = invoice_info or {
        "Invoice Number": "0001/25-26",
        "Invoice Date": "12-Nov-25",
        "Due Date": "12-Nov-25",
        "Place of Supply": "33 - Tamil Nadu"
    }

    items = items or [
        [1, "Sample Item", "", "1.00", "Pcs.", "10000.00", "10.00 (%)", "0.00", "9000.00"],
        [2, "Item", "", "1.00", "Pcs.", "87987.00", "", "0.00", "87987.00"],
    ]

    bank_info = bank_info or {
        "Bank": "ICICI Bank",
        "Account Number": "98765412005151",
        "IFSC": "IFSE4564",
        "Branch": "Anna Nagar",
        "Name": "Account Name"
    }

    terms = terms or [
        "E & O.E",
        "1. Goods once sold will not be taken back.",
        "2. Interest @ 18% p.a. will be charged if payment is not made in time.",
        "3. Subject to 'Tamil Nadu' Jurisdiction only."
    ]

    # ========== BORDER ==========
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.rect(20, 20, width - 40, height - 40)

    # ========== HEADER ==========
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 50, company_info["name"])

    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, height - 65, company_info["address"])
    c.drawCentredString(width / 2, height - 78, company_info["contact"])
    c.drawRightString(width - 35, height - 50, company_info["copy_type"])

    # ========== BILLING SECTION ==========
    y = height - 120
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y, "Billing Details")
    y -= 15
    c.setFont("Helvetica", 9)
    c.drawString(30, y, billing_info["name"])
    c.drawString(30, y - 15, billing_info["address"])

    # ========== INVOICE INFO ==========
    info_x = 320
    y = height - 120
    c.setFont("Helvetica-Bold", 9)
    for i, (label, value) in enumerate(invoice_info.items()):
        c.drawString(info_x, y - (i * 15), f"{label} :")
        c.setFont("Helvetica", 9)
        c.drawString(info_x + 100, y - (i * 15), str(value))
        c.setFont("Helvetica-Bold", 9)

    # ========== ITEM TABLE ==========
    y = height - 200
    headers = ["Sr.", "Item Description", "HSN/SAC", "Qty", "Unit", "List Price", "Disc.", "Tax %", "Amount (₹)"]
    col_x = [30, 60, 210, 280, 310, 350, 410, 460, 510]
    row_height = 15

    # Header background
    c.setFillColor(colors.lightgrey)
    c.rect(25, y - row_height + 3, width - 50, row_height, fill=True, stroke=False)
    c.setFillColor(colors.black)

    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers):
        c.drawString(col_x[i], y, h)

    # Table position
    table_top = y + 5
    table_bottom = y - (row_height * (len(items) + 1)) - 10

    # Table border
    c.setLineWidth(0.5)
    c.rect(25, table_bottom, width - 50, table_top - table_bottom)

    # Vertical lines
    for x in col_x[1:]:
        c.line(x - 5, table_bottom, x - 5, table_top)

    # Draw items
    c.setFont("Helvetica", 9)
    y -= row_height
    total_amount = 0
    for row in items:
        for i, val in enumerate(row):
            c.drawString(col_x[i], y, str(val))
        try:
            total_amount += float(str(row[-1]).replace(",", ""))
        except:
            pass
        y -= row_height

    # Horizontal line below last row
    c.line(25, y + 3, width - 25, y + 3)

    # ========== TOTAL ==========
    c.setFont("Helvetica-Bold", 11)
    c.drawString(120, y - 30, "Total")
    c.drawRightString(width - 40, y - 30, f"{total_amount:,.2f}")

    c.setFont("Helvetica", 9)
    amount_words = num2words(total_amount, lang="en").title() + " Only"
    c.drawString(35, y - 45, f"Rs. {amount_words}")

    # ========== BANK DETAILS ==========
    c.setFont("Helvetica-Bold", 10)
    bank_y = 115
    c.drawString(30, bank_y, "Bank Details:")
    c.setFont("Helvetica", 9)
    y_text = bank_y - 12
    for k, v in bank_info.items():
        c.drawString(30, y_text, f"{k}: {v}")
        y_text -= 12
    c.rect(25, 45, 270, 90, stroke=True)

    # ========== TERMS ==========
    c.setFont("Helvetica-Bold", 10)
    c.drawString(320, 115, "Terms and Conditions:")
    c.setFont("Helvetica", 9)
    y = 100
    for term in terms:
        c.drawString(320, y, term)
        y -= 12
    c.rect(315, 45, width - 340, 90, stroke=True)

    c.showPage()
    c.save()
    print(f"✅ Dynamic PDF created successfully: {filename}")


# Example usage
generate_invoice()
