import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

#Read data from CSV requirements
input_file = "requirements/material_data.csv"
output_file = "output/plant_material.csv"

plant = []
with open(input_file, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    print("Header terbaca:", reader.fieldnames)  
    for row in reader:        
        plant.append({
            "erp": row["ERP"],
            "plant": row["PLANT"],
            "nbr_materials": int(row["NBR MATERIALS"]),
        })

#Aggregate the number materials by ERP
erp_groups = defaultdict(list)
for p in plant:
    erp_groups[p["erp"]].append(p)

#Writing to CSV output
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    
    #define the header for the output CSV
    writer.writerow([
        "ERP", "PLANT", "MATERIAL CODE", "MOQ", "SPQ", "LEAD TIME", "SAFETY STOCK", "UNIT PRICE USD", "AMU"
    ])
    
    for erp, plist in erp_groups.items():
        counter = 1
        
        for p in plist:            
            total_lines = p["nbr_materials"]
            
            while total_lines > 0:                
                rand_num = str(random.randint(1, 50000))
                combined = rand_num + str(counter)
                combined = combined.zfill(11)
                material = "A" + combined

                factor = random.choice([5, 10, 20, 50, 100])

                moq = (random.randint(10, 400))*factor
                spq = moq // factor
                lt = random.randint(7, 365)
                ss = moq * random.randint(1, 10)
                price = round((random.uniform(100, 4000))/1000, 6)
                amu = moq * random.randint(1, 10)
                                                    
                writer.writerow([
                        erp,
                        p["plant"],
                        material,
                        moq,
                        spq,
                        lt,
                        ss,
                        price,
                        amu
                ])
                
                total_lines -= random.randint(1, 10)
                counter += 1

print(f"File {output_file} berhasil dibuat!")
