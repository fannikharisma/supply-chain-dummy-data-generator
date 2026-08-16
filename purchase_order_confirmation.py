import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

def run():
    # File input
    po_schedule_file = "output/po_schedule.csv"
    acked_file = "requirements/po_confirmation_data.csv"
    output_file = "output/po_confirmation.csv"

    # Baca input 1 (PO schedule)
    po_list = []
    with open(po_schedule_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            po_list.append({
                "erp": row["ERP"].strip(),
                "vendor": row["VENDOR"].strip(),
                "po_number": row["PO NUMBER"].strip(),
                "po_item": row["PO ITEM"].strip(),
                "creation": row["CREATION DATE"].strip(),
                "contractual": row["CONTRACTUAL DELIVERY DATE"].strip(),
                "requested": row["REQUESTED DELIVERY DATE"].strip()
            })

    # Baca input 2 (jumlah acked)
    acked_info = {}
    with open(acked_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["ERP"].strip(), row["VENDOR"].strip())
            acked_info[key] = {
                "ordrsp": row["ORDRSP"].strip(),
                "acked": int(row["PO LINES ACKED"]) if row["PO LINES ACKED"].strip() else 0
            }

    # Group PO list per ERP+Vendor
    grouped = defaultdict(list)
    for po in po_list:
        grouped[(po["erp"], po["vendor"])].append(po)

    # Generate output
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ERP", "VENDOR", "PO NUMBER", "PO ITEM", "PO CONFIRMATION DATE", "CONFIRMATION ENTER DATE"])
        
        for key, po_lines in grouped.items():
            erp, vendor = key
            acked_count = acked_info.get(key, {}).get("acked", 0)
            ordrsp_str = acked_info.get(key, {}).get("ordrsp", "")
            ordrsp_date = datetime.strptime(ordrsp_str, "%m/%d/%Y") if ordrsp_str else None
            
            # pilih random sejumlah acked_count
            selected = set(random.sample(range(len(po_lines)), min(acked_count, len(po_lines))))
            
            for idx in selected:   # <-- hanya loop baris yang terpilih
                po = po_lines[idx]
                
                # Confirmation Date = requested ± 5–10 hari
                confirmation_date = ""
                if po["requested"]:
                    req_date = datetime.strptime(po["requested"], "%Y-%m-%d")
                    offset = random.randint(5, 10)
                    if random.choice([True, False]):
                        confirmation_date = (req_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                    else:
                        confirmation_date = (req_date - timedelta(days=offset)).strftime("%Y-%m-%d")
                
                # Confirmation Enter Date = ORDRSP ± 1–20 hari
                confirmation_enter = ""
                if ordrsp_date:
                    offset = random.randint(1, 20)
                    confirmation_enter = (ordrsp_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                
                writer.writerow([
                    erp,
                    vendor,
                    po["po_number"],
                    po["po_item"],
                    confirmation_date,
                    confirmation_enter
                ])


    print(f"File {output_file} successfully created!")
