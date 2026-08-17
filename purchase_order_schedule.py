import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

def run():
    # Read input: PO schedule data requirements
    input_file = "requirements/po_schedule_data.csv"
    output_file = "output/po_schedule.csv"

    # Load vendor/PO requirements data
    vendors = []
    with open(input_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:        
            vendors.append({
                "erp": row["ERP"],
                "plant": row["PLANT"],
                "vendor": row["VENDOR"],
                "startdate": row["ORDERS"],
                "lines": int(row["PO LINES SHARED"])
            })

    # Group requirements by ERP
    erp_groups = defaultdict(list)
    for v in vendors:
        erp_groups[v["erp"]].append(v)

    # Generate output file with PO schedules
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ERP", "PLANT", "VENDOR", "PO NUMBER", "PO ITEM", "CREATION DATE", "CONTRACTUAL DELIVERY DATE", "REQUESTED DELIVERY DATE"
        ])
        
        for erp, vlist in erp_groups.items():
            counter = 1
            
            for v in vlist:
                po_creation = datetime.strptime(v["startdate"], "%m/%d/%Y")
                
                total_lines = v["lines"]
                
                # Generate POs for each vendor/plant requirement
                while total_lines > 0:
                    items_in_po = min(total_lines, random.randint(1, 99))
                    
                    # Generate unique PO number
                    rand_num = str(random.randint(100, 9000))
                    combined = rand_num + str(counter)
                    combined = combined.zfill(9)
                    po_number = "5" + combined
                    
                    # Generate line items for each PO
                    for item in range(1, items_in_po + 1):
                        contractual_date = po_creation + timedelta(days=random.randint(7, 365))
                        
                        # Generate delivery date based on contractual date with random offset
                        if random.choice([True, False]):
                            delivery_date = contractual_date
                        else:
                            offset = random.randint(10, 30)
                            if random.choice([True, False]):
                                delivery_date = contractual_date + timedelta(days=offset)
                            else:
                                delivery_date = contractual_date - timedelta(days=offset)                    
                        
                        writer.writerow([
                            erp,
                            v["plant"],
                            v["vendor"],
                            po_number,
                            str(item).zfill(2),
                            po_creation.strftime("%Y-%m-%d"),
                            contractual_date.strftime("%Y-%m-%d"),
                            delivery_date.strftime("%Y-%m-%d"),
                        ])
                    
                    total_lines -= items_in_po
                    counter += 1

    print(f"File {output_file} successfully created!")
