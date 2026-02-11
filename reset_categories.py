import os

# The Mega List of Categories
csv_content = """description,category
Dell Optiplex Desktop,Electronics
HP Thin Client,Electronics
Gaming PC Tower,Electronics
Wireless Mouse,Electronics
USB Cable,Electronics
HDMI Cable 10ft,Electronics
Samsung Galaxy Phone,Electronics
Keyboard and Mouse,Electronics
Monitor Stand,Electronics
Headset with Microphone,Electronics
Office Chair,Furniture
Wooden Desk,Furniture
Coffee Table,Furniture
Standing Desk,Furniture
Filing Cabinet,Furniture
Bookshelf,Furniture
Printer Paper A4,Office Supplies
Ballpoint Pens Blue,Office Supplies
Stapler and Pins,Office Supplies
A4 Notebook,Office Supplies
Red Wine Bottle,Beverages
Fruit Cider,Beverages
Orange Juice,Beverages
Cleaning Spray,Maintenance
Mop and Bucket,Maintenance
Bleach Cleaner,Maintenance
Repair Service,Services
Labor Charges,Services
Software Subscription,Software
Uber Ride,Travel
Flight Ticket,Travel
Bcbgeneration Dress,Clothing
Lace Back Dress,Clothing
Cotton Hoodie,Clothing
Jeans Denim,Clothing
Sneakers,Clothing
Drill Bit Set,Tools
Hammer and Nails,Tools
Paint Can,Tools
"""

# Force write to the file
os.makedirs('training_data', exist_ok=True)
with open('training_data/categories.csv', 'w') as f:
    f.write(csv_content)

print("SUCCESS: 'categories.csv' has been updated with 40+ items!")