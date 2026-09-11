"""
Seed real enterprise data into Azure Storage Tables and Blob Container in exploreagent.
"""
import subprocess
import json
import os

ACCOUNT_NAME = "stexploreagent65064"
KEY = subprocess.check_output("az storage account keys list -g exploreagent -n stexploreagent65064 --query [0].value -o tsv", shell=True).decode().strip()

def run_az(cmd):
    full_cmd = f"az {cmd} --account-name {ACCOUNT_NAME} --account-key \"{KEY}\""
    subprocess.check_call(full_cmd, shell=True)

# 1. Seed Customers
print("Seeding Customers Table in Azure...")
customers = [
    ("US", "CUST-101", "Global Logistics Corp", "VIP_PLATINUM", 500000.0, 12400.0),
    ("US", "CUST-202", "Apex Retailers Ltd", "STANDARD", 50000.0, 4800.0),
    ("US", "CUST-303", "Nexus Medical Devices", "ENTERPRISE_GOLD", 250000.0, 0.0)
]
for pkey, rkey, name, tier, limit, bal in customers:
    try:
        run_az(f'storage entity insert --table-name Customers --entity PartitionKey="{pkey}" RowKey="{rkey}" CustomerName="{name}" Tier="{tier}" CreditLimit={limit} Balance={bal} --if-exists replace')
    except Exception as e:
        print(f"Error inserting customer {rkey}: {e}")

# 2. Seed Inventory
print("Seeding Inventory Table in Azure...")
inventory = [
    ("HARDWARE", "SKU-9901", "Enterprise Edge Server Pro", "Warehouse-East", 42, 2800.0, 18.5),
    ("HARDWARE", "SKU-4420", "Industrial IoT Sensor Hub", "Warehouse-Central", 115, 650.0, 2.1),
    ("HARDWARE", "SKU-8810", "Fiber Optics Transceiver 100G", "Warehouse-East", 8, 1200.0, 0.8),
]
for pkey, rkey, name, wh, qty, price, weight in inventory:
    try:
        run_az(f'storage entity insert --table-name Inventory --entity PartitionKey="{pkey}" RowKey="{rkey}" ProductName="{name}" Warehouse="{wh}" StockQty={qty} UnitPrice={price} WeightKg={weight} --if-exists replace')
    except Exception as e:
        print(f"Error inserting inventory {rkey}: {e}")

# 3. Seed Orders
print("Seeding Orders Table in Azure...")
orders = [
    ("ORDERS", "ORD-5512", "CUST-101", "SKU-9901", 5, 14000.0, "2026-08-15", "DELIVERED"),
    ("ORDERS", "ORD-7788", "CUST-202", "SKU-4420", 10, 6500.0, "2026-09-01", "DELIVERED"),
]
for pkey, rkey, cust, sku, qty, amt, dt, st in orders:
    try:
        run_az(f'storage entity insert --table-name Orders --entity PartitionKey="{pkey}" RowKey="{rkey}" CustomerId="{cust}" Sku="{sku}" Quantity={qty} TotalAmount={amt} OrderDate="{dt}" Status="{st}" --if-exists replace')
    except Exception as e:
        print(f"Error inserting order {rkey}: {e}")

# 4. Seed Policy Documents in Blob Storage
print("Uploading Policy Documents to Azure Blob Container 'policies'...")
return_policy = {
    "policy_name": "Enterprise Return and Exchange Policy",
    "vip_rules": {
        "tier": "VIP_PLATINUM",
        "return_window_days": 60,
        "restocking_fee_pct": 0,
        "free_expedited_freight": True,
        "exchange_upgrade_allowed": True
    },
    "standard_rules": {
        "tier": "STANDARD",
        "return_window_days": 14,
        "restocking_fee_pct": 15,
        "free_expedited_freight": False,
        "exchange_upgrade_allowed": False
    },
    "hazmat_rule": "Items over 15.0 kg require certified freight carrier."
}

os.makedirs("c:/Users/2869026/Desktop/up/exploreagent_showcase/temp", exist_ok=True)
with open("c:/Users/2869026/Desktop/up/exploreagent_showcase/temp/return_policy.json", "w") as f:
    json.dump(return_policy, f, indent=2)

run_az('storage blob upload --container-name policies --name return_policy.json --file "c:/Users/2869026/Desktop/up/exploreagent_showcase/temp/return_policy.json" --overwrite')

print("All cloud data seeded successfully into Azure Storage Tables and Blob Container!")
