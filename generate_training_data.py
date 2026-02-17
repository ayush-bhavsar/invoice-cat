import csv
import random
import os

def generate_csv():
    print("Generating FINAL V4 Training Data (Balanced)...")

    categories = {
        "Electronics": [
            # Added "Computer", "Gaming", "Windows" here:
            "Computer", "Gaming", "Windows", "Microsoft", "Software", "Digital",
            "Dell", "HP", "Lenovo", "Apple", "ThinkPad", "MacBook", "Optiplex", "Monitor", 
            "Mouse", "Keyboard", "HDMI", "USB", "Cable", "Charger", "Webcam", "Headset", 
            "Earbuds", "Hard Drive", "SSD", "Router", "Modem", "Switch", "Server", "Laptop", 
            "Desktop", "Tablet", "Phone", "Sim", "Battery", "Microphone", "Speaker", 
            "Screen", "Touch", "Core", "Intel", "AMD", "Ryzen", "GeForce", "Nvidia", 
            "Gigabyte", "Wifi", "Bluetooth", "Xbox", "Playstation", "Nintendo", "Console", 
            "Controller", "Game", "System", "Magnavox", "Odyssey", "Arcade", "VR", "Ready"
        ],
        "Furniture": [
            # Boosted Rugs and Carpets:
            "Rug", "Carpet", "Mat", "Flooring", "Textile", "Tapestry", "Bedside", "Area", 
            "Handknotted", "Oriental", "Persian", "Doormat", "Runner",
            "Chair", "Desk", "Table", "Sofa", "Couch", "Bookshelf", "Cabinet", "Drawer", 
            "Stool", "Bench", "Stand", "Rack", "Credenza", "Cubicle", "Whiteboard", "Lamp", 
            "Lighting", "Seat", "Ottoman", "Recliner", "Workstation", "Shelf", "Cart",
            "Furniture", "Decor", "Marquetry", "Inlay", "Carved", "Antique", "Vintage",
            "Wood", "Marble", "Stone", "Granite", "Glass", "Mirror", "Patio", "Garden", 
            "Dining", "Living", "Room", "Foyer"
        ],
        "Kitchen": [
            "Wine", "Glass", "Mug", "Cup", "Plate", "Bowl", "Fork", "Spoon", "Knife", 
            "Pan", "Pot", "Skillet", "Blender", "Toaster", "Microwave", "Coffee", "Maker", 
            "Carafe", "Bottle", "Pitcher", "Tray", "Tupperware", "Container", "Napkin", 
            "Dish", "Spatula", "Whisk", "Peeler", "Grater", "Stopper", "Cork", "Opener",
            "Cookware", "Cutlery", "Silverware", "Fridge", "Refrigerator", "Freezer",
            "Oven", "Stove", "Drainer", "Sink", "Faucet", "Pantry", "Goblet", "Stemware"
        ],
        "Clothing": [
            "Shirt", "T-Shirt", "Pants", "Jeans", "Shorts", "Dress", "Skirt", "Suit", 
            "Coat", "Jacket", "Hoodie", "Sweater", "Vest", "Uniform", "Boots", "Shoes", 
            "Sneakers", "Socks", "Gloves", "Hat", "Cap", "Scarf", "Belt", "Tie", "Cleats",
            "Footwear", "Heels", "Sandals", "Loafers", "Oxfords", "Suede", "Leather",
            "Cotton", "Linen", "Silk", "Denim", "Wool", "Polyester", "Rayon", "Spandex",
            "Size", "Small", "Medium", "Large", "XL", "XXL", "Toddler", "Kids", "Boys",
            "Girls", "Mens", "Womens", "Youth", "Baby", "Infant", "Apparel", "Wear",
            "Sleeve", "Collar", "Pocket", "Zipper", "Button", "Lace", "Floral", "Print",
            "Summer", "Winter", "Casual", "Formal", "Fashion"
        ],
        "Beverages": [
            "Water", "Juice", "Soda", "Cola", "Beer", "Wine", "Cider", "Milk", "Coffee", 
            "Tea", "Espresso", "Latte", "Cappuccino", "Drink", "Beverage", "Bottle", "Can",
            "Alcohol", "Liquor", "Spirits", "Vodka", "Whiskey", "Gin", "Rum", "Tequila"
        ],
        "Office Supplies": [
            "Paper", "Pen", "Pencil", "Notebook", "Pad", "Binder", "Folder", "Clip", 
            "Stapler", "Staples", "Tape", "Glue", "Scissors", "Marker", "Highlighter", 
            "Eraser", "Envelopes", "Labels", "Ink", "Toner", "Cartridge", "Planner",
            "Calendar", "Sticky", "Post-it", "Card", "Stock", "Rubber", "Band"
        ],
        "Books": [
            "Book", "Novel", "Textbook", "Guide", "Manual", "Paperback", "Hardcover",
            "Ebook", "Edition", "Volume", "Series", "Author", "Publisher", "Fiction",
            "Non-fiction", "Story", "Tales", "Writing", "Portrait", "Biography"
        ],
        "Maintenance": [
            "Cleaner", "Spray", "Wipes", "Bleach", "Soap", "Detergent", "Broom", "Mop", 
            "Bucket", "Sponge", "Brush", "Towel", "Tissue", "Trash", "Bag", "Bulb", 
            "Battery", "Repair", "Service", "Labor", "Install", "Maintenance", "Fix"
        ]
    }

    # --- THE NEUTRALIZERS ---
    # Words added here will vote for EVERY category, effectively cancelling them out.
    adjectives = [
        # COLORS
        "Blue", "Red", "Green", "Black", "White", "Yellow", "Silver", "Gold", "Gray", "Brown", "Orange", "Pink", "Purple",
        # SIZES
        "Large", "Small", "Medium", "Tiny", "Huge", "XL", "XS", "Custom",
        # QUALITIES
        "Beautiful", "Premium", "Cheap", "Expensive", "Luxury", "Basic", "Unique", "Elegant",
        "New", "Used", "Refurbished", "Old", "Vintage", "Modern", "Antique", "Classic", "Retro",
        # SHAPES & DESIGNS
        "Dolphin", "Eagle", "Star", "Heart", "Diamond", "Square", "Round", "Oval", "Abstract", "Gradient", "Pattern",
        # MATERIALS (CRITICAL FIX: Prevent 'Plastic' -> Clothing)
        "Plastic", "Metal", "Wooden", "Steel", "Iron", "Glass", "Rubber", "Fabric", "Mesh", "Synthetic",
        # QUANTITIES & UNITS
        "each", "box", "pack", "set", "pair", "pcs", "qty", "lot", "unit", "bag", "case", "bundle",
        "eacn", "sz", "w/", "w/o", "oz", "ml", "kg", "lb", "lbs", "cm", "mm", "inch", "inches"
    ]

    data = []

    # --- BUILD THE DATASET ---
    for category, items in categories.items():
        for item in items:
            # 1. The Item
            data.append([item, category])
            
            # 2. Item + Neutralizer
            for adj in adjectives:
                if random.random() < 0.20: # Increased to 20% to generate more data
                    data.append([f"{adj} {item}", category])
                    data.append([f"{item} {adj}", category])
                    
            # 3. Just the Neutralizer (Assign to this category to balance probability)
            if random.random() < 0.10:
                data.append([adj, category])

    # --- THE GARBAGE BIN (Footer Text) ---
    garbage_words = [
        "Total", "Subtotal", "Tax", "VAT", "Amount", "Due", "Paid", "Balance", 
        "Terms", "Conditions", "Registered", "Office", "Page", "Invoice", "Number", 
        "Date", "Ship", "Bill", "To", "From", "Thank", "You", "Business", "Website", 
        "Email", "Phone", "Fax", "Tel", "Mob", "Address", "Street", "City", "State", "Zip"
    ]
    for word in garbage_words:
        for _ in range(15): # Increased weight to ignore footers
            data.append([word, "Other"])

    random.shuffle(data)

    os.makedirs('training_data', exist_ok=True)
    with open('training_data/categories.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["description", "category"])
        writer.writerows(data)
    
    print(f"SUCCESS! Generated {len(data)} balanced training examples.")

if __name__ == "__main__":
    generate_csv()