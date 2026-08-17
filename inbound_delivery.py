import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

def run():
    # Read input: PO Confirmation file, which acts as the source for PO data
    po_confirmation_file = "output/po_confirmation.csv"
    # Read input: Inbound delivery configuration file to know how many ASNs to generate
    inbound_file = "requirements/inbound_delivery_data.csv"
    output_file = "output/inbound_delivery.csv"

    # Load PO data into a list
    po_list = []
    with open(po_confirmation_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            po_list.append({
                "erp": row["ERP"].strip(),
                "plant": row["PLANT"].strip(),
                "vendor": row["VENDOR"].strip(),
                "po_number": row["PO NUMBER"].strip(),
                "po_item": row["PO ITEM"].strip(),
                "rdd": row["PO CONFIRMATION DATE"].strip(),
            })

    # Load ASN generation rules (ASN count per ERP/Vendor)
    asn_info = {}
    with open(inbound_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["ERP"].strip(), row["PLANT"].strip(), row["VENDOR"].strip())
            asn_info[key] = {
                "desadv": row["DESADV"].strip(),
                "asn": int(row["ASN CREATED"]) if row["ASN CREATED"].strip() else 0
            }

    # Group PO list per ERP and Vendor for easier processing
    grouped = defaultdict(list)
    for po in po_list:
        grouped[(po["erp"], po["plant"], po["vendor"])].append(po)

    # Generate output file with calculated inbound delivery data
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ERP", "PLANT", "VENDOR", "PO NUMBER", "PO ITEM", "INBOUND DELIVERY NUMBER","INBOUND DELIVERY DATE", "INBOUND CREATION DATE"])
        
        for key, po_lines in grouped.items():
            erp, plant, vendor = key
            asn_count = asn_info.get(key, {}).get("asn", 0)
            desadv_str = asn_info.get(key, {}).get("desadv", "")
            desadv_date = datetime.strptime(desadv_str, "%m/%d/%Y") if desadv_str else None
            
            # Randomly select which PO items will have an inbound delivery created based on asn_count
            # selected = set(random.sample(range(len(po_lines)), min(asn_count, len(po_lines))))
            selected = [random.choice(range(len(po_lines))) for _ in range(asn_count)]
            
            for idx in selected:
                po = po_lines[idx]

                # Generate a unique Inbound Delivery Number based on random and PO identifiers
                rand_num = str(random.randint(1000, 9999))
                combined = rand_num + po["po_number"][-4:] + po["po_item"]
                combined = combined.zfill(12)
                inbound_delivery_number = "D" + combined
                
                # Calculate delivery date based on requested delivery date with a random ± 5–10 day offset
                inbound_delivery_date = ""
                if po["rdd"]:
                    req_date = datetime.strptime(po["rdd"], "%Y-%m-%d")
                    offset = random.randint(5, 10)
                    if random.choice([True, False]):
                        inbound_delivery_date = (req_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                    else:
                        inbound_delivery_date = (req_date - timedelta(days=offset)).strftime("%Y-%m-%d")
                
                # Calculate creation date based on DESADV date with a random 1–20 day offset
                inbound_creation_date = ""
                if desadv_date:
                    offset = random.randint(1, 20)
                    inbound_creation_date = (desadv_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                
                writer.writerow([
                    erp,
                    plant,
                    vendor,
                    po["po_number"],
                    po["po_item"],
                    inbound_delivery_number,
                    inbound_delivery_date,
                    inbound_creation_date
                ])


    print(f"File {output_file} successfully created!")
