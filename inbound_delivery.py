import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

def run():
    # File input
    po_confirmation_file = "output/po_confirmation.csv"
    inbound_file = "requirements/inbound_delivery_data.csv"
    output_file = "output/inbound_delivery.csv"

    # Baca input 1 (PO Confirmation)
    po_list = []
    with open(po_confirmation_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            po_list.append({
                "erp": row["ERP"].strip(),
                "vendor": row["VENDOR"].strip(),
                "po_number": row["PO NUMBER"].strip(),
                "po_item": row["PO ITEM"].strip(),
                "confirmation_date": row["PO CONFIRMATION DATE"].strip(),
            })

    # Baca input 2 (jumlah acked)
    asn_info = {}
    with open(inbound_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["ERP"].strip(), row["VENDOR"].strip())
            asn_info[key] = {
                "desadv": row["DESADV"].strip(),
                "asn": int(row["ASN CREATED"]) if row["ASN CREATED"].strip() else 0
            }

    # Group PO list per ERP+Vendor
    grouped = defaultdict(list)
    for po in po_list:
        grouped[(po["erp"], po["vendor"])].append(po)

    # Generate output
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ERP", "VENDOR", "PO NUMBER", "PO ITEM", "INBOUND DELIVERY NUMBER","INBOUND DELIVERY DATE", "INBOUND CREATION DATE"])
        
        for key, po_lines in grouped.items():
            erp, vendor = key
            asn_count = asn_info.get(key, {}).get("asn", 0)
            desadv_str = asn_info.get(key, {}).get("desadv", "")
            desadv_date = datetime.strptime(desadv_str, "%m/%d/%Y") if desadv_str else None
            
            # pilih random sejumlah asn_count
            selected = set(random.sample(range(len(po_lines)), min(asn_count, len(po_lines))))
            
            for idx in selected:   # <-- hanya loop baris yang terpilih
                po = po_lines[idx]

                # Generate Inbound Delivery Number
                rand_num = str(random.randint(1000, 9999))
                combined = rand_num + po["po_number"][-4:] + po["po_item"]
                combined = combined.zfill(12)
                inbound_delivery_number = "D" + combined
                
                # Confirmation Date = requested ± 5–10 hari
                inbound_delivery_date = ""
                if po["confirmation_date"]:
                    req_date = datetime.strptime(po["confirmation_date"], "%Y-%m-%d")
                    offset = random.randint(5, 10)
                    if random.choice([True, False]):
                        inbound_delivery_date = (req_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                    else:
                        inbound_delivery_date = (req_date - timedelta(days=offset)).strftime("%Y-%m-%d")
                
                # Confirmation Enter Date = DESADV ± 1–20 hari
                inbound_creation_date = ""
                if desadv_date:
                    offset = random.randint(1, 20)
                    inbound_creation_date = (desadv_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                
                writer.writerow([
                    erp,
                    vendor,
                    po["po_number"],
                    po["po_item"],
                    inbound_delivery_number,
                    inbound_delivery_date,
                    inbound_creation_date
                ])


    print(f"File {output_file} berhasil dibuat!")
