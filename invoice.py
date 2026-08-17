import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

def run():
    # Read input: PO Schedule file, which acts as the source for PO data
    po_schedule = "output/po_schedule.csv"
    # Read input: Invoice configuration file to know how many invoices to generate
    inbound_file = "requirements/invoice_data.csv"
    output_file = "output/invoice.csv"

    # Load PO data into a list
    po_list = []
    with open(po_schedule, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            po_list.append({
                "erp": row["ERP"].strip(),
                "plant": row["PLANT"].strip(),
                "vendor": row["VENDOR"].strip(),
                "po_number": row["PO NUMBER"].strip(),
                "po_item": row["PO ITEM"].strip(),
                "rdd": row["REQUESTED DELIVERY DATE"].strip(),
            })

    # Load Invoice generation rules (Invoice count per ERP/Vendor)
    inv_info = {}
    with open(inbound_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["ERP"].strip(), row["PLANT"].strip(), row["VENDOR"].strip())
            inv_info[key] = {
                "invoic": row["INVOIC"].strip(),
                "inv": int(row["INVOICE CREATED"]) if row["INVOICE CREATED"].strip() else 0
            }

    # Group PO list per ERP and Vendor for easier processing
    grouped = defaultdict(list)
    for po in po_list:
        grouped[(po["erp"], po["plant"], po["vendor"])].append(po)

    # Generate output file with calculated inbound delivery data
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ERP", "PLANT", "VENDOR", "PO NUMBER", "PO ITEM", "INVOICE NUMBER","INVOICE DATE"])
        
        for key, po_lines in grouped.items():
            erp, plant, vendor = key
            inv_count = inv_info.get(key, {}).get("inv", 0)
            invoic_str = inv_info.get(key, {}).get("invoic", "")
            invoic_date = datetime.strptime(invoic_str, "%m/%d/%Y") if invoic_str else None
            
            # Randomly select which PO items will have an inbound delivery created based on inv_count
            selected = [random.choice(range(len(po_lines))) for _ in range(inv_count)]
            
            for idx in selected:
                po = po_lines[idx]

                # Generate a unique Invoice Number based on random and PO identifiers
                rand_num = str(random.randint(1000, 9999))
                combined = rand_num + po["po_number"][-4:] + po["po_item"]
                combined = combined.zfill(12)
                invoice_number = "I" + combined
                
                # Calculate invoice date based on requested delivery date with a random ± 5–10 day offset
                invoice_date = ""
                if po["rdd"]:
                    req_date = datetime.strptime(po["rdd"], "%Y-%m-%d")
                    offset = random.randint(5, 10)
                    if random.choice([True, False]):
                        invoice_date = (req_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                    else:
                        invoice_date = (req_date - timedelta(days=offset)).strftime("%Y-%m-%d")
                
                
                writer.writerow([
                    erp,
                    plant,
                    vendor,
                    po["po_number"],
                    po["po_item"],
                    invoice_number,
                    invoice_date
                ])


    print(f"File {output_file} successfully created!")
