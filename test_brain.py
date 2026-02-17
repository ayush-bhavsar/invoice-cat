from classifier import predict_category

# Test inputs covering different categories
test_items = [
    "Dell Optiplex 780",       # Should be Electronics
    "Red Wine Bottle",         # Should be Beverages
    "PUMA Soccer Cleats",      # Should be Clothing
    "Office Chair Ergonomic",  # Should be Furniture
    "Stainless Steel Pan",     # Should be Kitchen
    "Bleach and Mop",          # Should be Maintenance
    "Consulting Services"      # Should be Services (if in list)
]

print("--- BRAIN DIAGNOSTIC TEST ---")
for item in test_items:
    prediction = predict_category(item)
    print(f"Input: '{item:25}' --> AI Thinks: {prediction}")

print("\nIf you see different categories above, your AI is working!")