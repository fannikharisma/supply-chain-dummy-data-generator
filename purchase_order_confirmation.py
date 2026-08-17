import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

def run():
    # Read input: PO schedule file (source) and PO confirmation requirements
    po_schedule_file = "output/po_schedule.csv"
    acked_file = "requirements/po_confirmation_data.csv"
    output_file = "output/po_confirmation.csv"

    # Load PO schedule data
    po_list = []
    with open(po_schedule_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            po_list.append({
                "erp": row["ERP"].strip(),
                "plant": row["PLANT"].strip(),
                "vendor": row["VENDOR"].strip(),
                "po_number": row["PO NUMBER"].strip(),
                "po_item": row["PO ITEM"].strip(),
                "creation": row["CREATION DATE"].strip(),
                "contractual": row["CONTRACTUAL DELIVERY DATE"].strip(),
                "requested": row["REQUESTED DELIVERY DATE"].strip()
            })

    # Load PO confirmation configuration (acked count per ERP/Vendor)
    acked_info = {}
    with open(acked_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["ERP"].strip(), row["PLANT"].strip(), row["VENDOR"].strip())
            acked_info[key] = {
                "ordrsp": row["ORDRSP"].strip(),
                "acked": int(row["PO LINES ACKED"]) if row["PO LINES ACKED"].strip() else 0
            }

    # Group PO list per ERP and Vendor for easier processing
    grouped = defaultdict(list)
    for po in po_list:
        grouped[(po["erp"], po["plant"], po["vendor"])].append(po)

    # Generate output file for confirmed PO lines
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ERP", "PLANT", "VENDOR", "PO NUMBER", "PO ITEM", "PO CONFIRMATION DATE", "CONFIRMATION ENTER DATE"])
        
        for key, po_lines in grouped.items():
            erp, plant, vendor = key
            acked_count = acked_info.get(key, {}).get("acked", 0)
            ordrsp_str = acked_info.get(key, {}).get("ordrsp", "")
            ordrsp_date = datetime.strptime(ordrsp_str, "%m/%d/%Y") if ordrsp_str else None
            
            # Randomly select PO items to be confirmed based on acked_count
            selected = set(random.sample(range(len(po_lines)), min(acked_count, len(po_lines))))
            
            for idx in selected:
                po = po_lines[idx]
                
                # Calculate confirmation date based on requested date with a random ± 5–10 day offset
                confirmation_date = ""
                if po["requested"]:
                    req_date = datetime.strptime(po["requested"], "%Y-%m-%d")
                    offset = random.randint(5, 10)
                    if random.choice([True, False]):
                        confirmation_date = (req_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                    else:
                        confirmation_date = (req_date - timedelta(days=offset)).strftime("%Y-%m-%d")
                
                # Calculate confirmation enter date based on ORDRSP date with a random 1–20 day offset
                confirmation_enter = ""
                if ordrsp_date:
                    offset = random.randint(1, 20)
                    confirmation_enter = (ordrsp_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                
                writer.writerow([
                    erp,
                    plant,
                    vendor,
                    po["po_number"],
                    po["po_item"],
                    confirmation_date,
                    confirmation_enter
                ])


    print(f"File {output_file} successfully created!")
