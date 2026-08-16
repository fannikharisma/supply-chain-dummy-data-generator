import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

def run():
    file1 = "requirements/invoice_data.csv"   # ERP,VENDOR,INVOICE DATE,INVOICE COUNT
    file2 = "output/po_schedule.csv"         # ERP,VENDOR,PO NUMBER,PO ITEM,CREATION DATE,CONTRACTUAL DELIVERY DATE,REQUESTED DELIVERY DATE
    output_file = "output/invoice.csv"

    # Baca file 1
    invoice_targets = {}
    with open(file1, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["ERP"].strip(), row["VENDOR"].strip())
            invoice_targets[key] = {
                "date": row["INVOIC"].strip(),
                "count": int(row["INVOICE CREATED"]) if row["INVOICE CREATED"].strip() else 0
            }

    # Baca file 2
    po_lines = defaultdict(list)
    with open(file2, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["ERP"].strip(), row["VENDOR"].strip())
            po_lines[key].append({
                "po_number": row["PO NUMBER"].strip(),
                "po_item": row["PO ITEM"].strip(),
                "creation": row["CREATION DATE"].strip(),
                "contractual": row["CONTRACTUAL DELIVERY DATE"].strip(),
                "requested": row["REQUESTED DELIVERY DATE"].strip()
            })

    # Generate output
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ERP","VENDOR","INVOICE NUMBER","PO NUMBER","PO ITEM","INVOICE DATE"])
        
        for key, lines in po_lines.items():
            erp, vendor = key
            target = invoice_targets.get(key, {"date":"", "count":0})
            invoice_date = target["date"]
            invoice_count = target["count"]
            
            if invoice_count == 0:
                continue
            
            # Generate invoice numbers
            invoice_numbers = [f"INV{random.randint(10000,99999)}{i}" for i in range(1, invoice_count+1)]
            
            # Assign invoice numbers randomly to PO lines
            for line in lines:
                inv_num = random.choice(invoice_numbers)
                writer.writerow([
                    erp,
                    vendor,
                    inv_num,
                    line["po_number"],
                    line["po_item"],
                    invoice_date
                ])

    print(f"File {output_file} berhasil dibuat!")
