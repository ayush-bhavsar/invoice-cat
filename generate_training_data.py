import csv
import random
import os

def generate_csv():
    print("Generating FINAL V5 Training Data (Heavy Keywords Only)...")

    # STRICT CATEGORIES - No ambiguous words allowed.
    categories = {
        "Electronics": [
            "Computer", "Server", "Laptop", "Desktop", "Workstation", "Monitor", "Screen",
            "Mouse", "Keyboard", "Webcam", "Headset", "Microphone", "Cable", "USB", "HDMI",
            "Hard Drive", "SSD", "Memory", "RAM", "Processor", "CPU", "GPU", "Graphics Card",
            "Router", "Modem", "Switch", "Hub", "Ethernet", "Network", "Wifi", "Bluetooth",
            "Printer", "Scanner", "Copier", "Toner", "Ink", "Cartridge", "Projector",
            "Phone", "Smartphone", "Tablet", "iPad", "iPhone", "Samsung", "Galaxy", "Pixel",
            "Dell", "HP", "Lenovo", "ThinkPad", "MacBook", "Apple", "Asus", "Acer", "Microsoft",
            "Battery", "Charger", "Adapter", "Power Supply", "UPS"
        ],
        "Furniture": [
            "Table", "Desk", "Chair", "Sofa", "Couch", "Seating", "Bench", "Stool", "Ottoman",
            "Cabinet", "Shelf", "Shelving", "Bookcase", "Bookshelf", "Drawer", "Credenza",
            "Wardrobe", "Armoire", "Dresser", "Nightstand", "Bed", "Mattress", "Frame",
            "Rug", "Carpet", "Mat", "Flooring", "Tile", "Marble", "Stone", "Granite", "Quartz",
            "Inlay", "Marquetry", "Wood", "Oak", "Pine", "Mahogany", "Walnut", "Teak",
            "Lamp", "Light", "Fixture", "Chandelier", "Sconce", "Bulb", "LED", 
            "Decor", "Statue", "Vase", "Mirror", "Painting", "Art", "Canvas", "Print"
        ],
        "Kitchen": [
            "Plate", "Dish", "Bowl", "Saucer", "Cup", "Mug", "Glass", "Tumbler", "Goblet",
            "Wine Glass", "Champagne Flute", "Carafe", "Pitcher", "Bottle", "Stopper", "Cork",
            "Knife", "Fork", "Spoon", "Cutlery", "Flatware", "Silverware", "Utensil",
            "Pan", "Pot", "Skillet", "Wok", "Saucepan", "Roaster", "Tray", "Sheet",
            "Blender", "Mixer", "Toaster", "Microwave", "Oven", "Stove", "Range", "Cooktop",
            "Fridge", "Refrigerator", "Freezer", "Dishwasher", "Coffee Maker", "Kettle",
            "Napkin", "Towel", "Cloth", "Sponge", "Soap", "Detergent", "Bleach"
        ],
        "Clothing": [
            "Shirt", "Tee", "Top", "Blouse", "Tunic", "Polo", "Sweater", "Cardigan", "Hoodie",
            "Jacket", "Coat", "Blazer", "Vest", "Suit", "Tuxedo", "Dress", "Gown", "Skirt",
            "Pants", "Trousers", "Jeans", "Denim", "Leggings", "Shorts", "Capris",
            "Underwear", "Boxers", "Briefs", "Socks", "Hosiery", "Tights", "Bra", "Lingerie",
            "Shoe", "Sneaker", "Boot", "Sandal", "Heel", "Pump", "Flat", "Loafer", "Oxford",
            "Hat", "Cap", "Beanie", "Scarf", "Glove", "Mitten", "Belt", "Tie", "Uniform"
        ],
        "Beverages": [
            "Water", "Soda", "Juice", "Cola", "Pepsi", "Coke", "Sprite", "Fanta", "Dr Pepper",
            "Beer", "Ale", "Lager", "Stout", "IPA", "Cider", "Wifi", # Wait, Wifi is electronics. Removing.
            "Wine", "Merlot", "Cabernet", "Chardonnay", "Pinot", "Sauvignon", "Rose", "Prosecco",
            "Champagne", "Sparkling", "Liquor", "Vodka", "Gin", "Rum", "Tequila", "Whiskey",
            "Bourbon", "Scotch", "Brandy", "Cognac", "Liqueur", "Coffee", "Tea", "Espresso"
        ],
        "Office Supplies": [
            "Paper", "Cardstock", "Envelopes", "Mailer", "Label", "Sticker", "Post-it", "Note",
            "Pen", "Pencil", "Marker", "Highlighter", "Sharpie", "Crayon", "Eraser",
            "Binder", "Folder", "File", "Portfolio", "Report Cover", "Divider", "Tab",
            "Stapler", "Staples", "Clip", "Clamp", "Pin", "Tack", "Tape", "Glue", "Adhesive",
            "Scissors", "Ruler", "Calculator", "Whiteboard", "Corkboard", "Calendar", "Planner"
        ],
        "Books & Media": [
            "Book", "Novel", "Textbook", "Manual", "Guide", "Directory", "Dictionary", 
            "Encyclopedia", "Bible", "Scripture", "Magazine", "Journal", "Newspaper", 
            "Catalogue", "Brochure", "Flyer", "DVD", "Blu-ray", "CD", "Vinyl", "Record", 
            "Software", "License", "Subscription", "Key", "Activation", "Download", "Digital"
        ],
        "Services": [
            "Shipping", "Delivery", "Freight", "Postage", "Handling", "Surcharge", "Fee",
            "Labor", "Installation", "Repair", "Maintenance", "Service", "Consulting", "Support",
            "Warranty", "Guarantee", "Protection", "Plan", "Subscription", "Membership", "Dues",
            "Training", "Course", "Workshop", "Seminar", "Hosting", "Domain", "Cloud"
        ],
        "Hardware": [
            "Rack", "Mount", "Stand", "Bracket", "Rail", "Shelving", "Chassis", "Case",
            "Tool", "Drill", "Hammer", "Wrench", "Screwdriver", "Pliers", "Saw", "Level",
            "Bolt", "Nut", "Screw", "Washer", "Nail", "Anchor", "Fastener", "Hinge",
            "Part", "Component", "Module", "Unit", "Spare", "Replacement", "Accessory",
            "Cable", "Wire", "Cord", "Connector", "Adapter", "Plug", "Socket" 
        ]
    }

    data = []

    # --- BUILD THE DATASET (PURE & REPEATED) ---
    # Since we removed the "Random Adjective" multiplier, we need to repeat these words
    # to give them enough weight against the noise/garbage words.
    
    for category, items in categories.items():
        for item in items:
            # Add the item itself multiple times to strengthen the signal
            for _ in range(5): 
                data.append([item, category])
            
            # Simple Plurals (Naive but effective for English)
            data.append([item + "s", category]) 
            
            # Compound words that really matter
            if category == "Kitchen":
                data.append([f"Set of {item}s", category])
            if category == "Furniture":
                data.append([f"Marble {item}", category])
                data.append([f"Wooden {item}", category])

    # --- THE GARBAGE BIN (Footer Text) ---
    # These must NOT be classified as any of the above.
    garbage_words = [
        "Total", "Subtotal", "Tax", "VAT", "Amount", "Due", "Paid", "Balance", "Net", "Gross",
        "Terms", "Conditions", "Registered", "Office", "Page", "Invoice", "Number", "No.",
        "Date", "Ship", "Bill", "To", "From", "Thank", "You", "Business", "Website", 
        "Email", "Phone", "Fax", "Tel", "Mob", "Address", "Street", "City", "State", "Zip",
        "Ltd", "Inc", "PLC", "LLC", "Group", "Sons", "Corp", "Corporation", "Co.",
        "Authorized", "Signatory", "Signature", "Payment", "Method", "Bank", "Account",
        "IBAN", "SWIFT", "Code", "Reference", "Order", "Purchase", "PO", "Job", "Client"
    ]
    
    for word in garbage_words:
        for _ in range(10): # Significant weight
            data.append([word, "Other"])

    random.shuffle(data)

    os.makedirs('training_data', exist_ok=True)
    with open('training_data/categories.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["description", "category"])
        writer.writerows(data)
    
    print(f"SUCCESS! Generated {len(data)} high-quality training examples.")

if __name__ == "__main__":
    generate_csv()