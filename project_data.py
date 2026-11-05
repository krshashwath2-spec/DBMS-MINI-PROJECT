"""Example rows transcribed from the SQL INSERT and SELECT examples in the brief."""

DISASTERS = [
    (1, "Kodagu landslide", "Landslide", "2026-08-20", "2026-08-27", "High", "Active",
     "Landslide in hilly region of Kodagu"),
    (2, "Chikkamagaluru landslide", "Landslide", "2026-08-22", "2026-08-27", "Medium", "Active",
     "Landslide in Chikkamagaluru"),
    (3, "Saklespura landslide", "Landslide", "2026-08-19", "2026-08-25", "Medium", "Closed",
     "Landslide in Saklespura"),
    (4, "Bengaluru urban flood", "Flood", "2026-08-24", "2026-08-27", "High", "Active",
     "Flood in Bengaluru urban"),
    (5, "Dakshina Kannada flood", "Flood", "2026-08-22", "2026-08-26", "Medium", "Closed",
     "Flood in Dakshina Kannada"),
]

AREAS = [
    (1, 1, "Madikeri", "Kodagu", 900, "High"),
    (2, 1, "Somwarpet", "Kodagu", 600, "Medium"),
    (3, 2, "Chikkamagaluru", "Chikkamagaluru", 1200, "High"),
    (4, 2, "Koppa", "Chikkamagaluru", 700, "Medium"),
    (5, 3, "Sakleshpur", "Hassan", 500, "High"),
    (6, 3, "Belur", "Hassan", 800, "Medium"),
    (7, 4, "Whitefield", "Bengaluru", 1200, "High"),
    (8, 4, "Yelahanka", "Bengaluru", 750, "High"),
    (9, 5, "Mangaluru", "Dakshina Kannada", 1500, "High"),
    (10, 5, "Udupi Road", "Dakshina Kannada", 650, "Medium"),
]

PEOPLE = [
    (1, 1, "Ramesh Gowda", 45, "Male", "9876543201", "Madikeri, Kodagu", "Shelter", "High"),
    (2, 1, "Lakshmi Devi", 38, "Female", "9876543202", "Madikeri, Kodagu", "Medical", "High"),
    (3, 2, "Manjunath Kumar", 52, "Male", "9876543203", "Somwarpet, Kodagu", "Food", "Medium"),
    (4, 3, "Suresh Bhat", 61, "Male", "9876543204", "Chikkamagaluru", "Medical", "High"),
    (5, 3, "Anitha Rao", 29, "Female", "9876543205", "Chikkamagaluru", "Food", "Medium"),
    (6, 4, "Kavya Shetty", 34, "Female", "9876543206", "Koppa, Chikkamagaluru", "Shelter", "High"),
    (7, 5, "Prakash Hegde", 48, "Male", "9876543207", "Sakleshpur, Hassan", "Food", "High"),
    (8, 7, "Priya Sharma", 27, "Female", "9876543208", "Whitefield, Bengaluru", "Medical", "High"),
    (9, 8, "Arjun Kumar", 41, "Male", "9876543209", "Yelahanka, Bengaluru", "Shelter", "Medium"),
    (10, 9, "Mohammed Irfan", 56, "Male", "9876543210", "Mangaluru, Dakshina Kannada", "Food", "High"),
]

RESOURCES = [
    (1, "Rice", "Food", "Kg"),
    (2, "Drinking Water", "Water", "Litres"),
    (3, "Medical Kit", "Medical", "Kits"),
    (4, "Blankets", "Shelter", "Pieces"),
    (5, "First Aid Kit", "Medical", "Kits"),
    (6, "Tents", "Shelter", "Pieces"),
]

INVENTORY = [
    (1, 1, 5000, "2026-08-25", "Kodagu Relief Center"),
    (2, 2, 10000, "2026-08-25", "Kodagu Relief Center"),
    (3, 3, 500, "2026-08-26", "Chikkamagaluru Relief Center"),
    (4, 4, 2000, "2026-08-26", "Hassan Relief Center"),
    (5, 5, 800, "2026-08-27", "Bengaluru Relief Center"),
    (6, 6, 300, "2026-08-27", "Dakshina Kannada Relief Center"),
]

SHELTERS = [
    (1, "Kodagu Government School", "Madikeri", 500, 320, "Temporary", "9000000001", "Active"),
    (2, "Somwarpet Community Hall", "Somwarpet", 300, 180, "Temporary", "9000000002", "Active"),
    (3, "Chikkamagaluru Relief Camp", "Chikkamagaluru", 600, 420, "Temporary", "9000000003", "Active"),
    (4, "Sakleshpur Government College", "Sakleshpur", 400, 250, "Temporary", "9000000004", "Active"),
    (5, "Bengaluru Relief Center", "Whitefield", 800, 650, "Temporary", "9000000005", "Active"),
    (6, "Mangaluru Community Center", "Mangaluru", 700, 300, "Permanent", "9000000006", "Active"),
]

ALLOCATIONS = [
    (1, 1, 1, "2026-08-20", "Allocated", "Family accommodation"),
    (2, 2, 1, "2026-08-20", "Allocated", "Medical assistance required"),
    (3, 3, 2, "2026-08-21", "Allocated", "Temporary shelter provided"),
    (4, 4, 3, "2026-08-22", "Allocated", "Priority case"),
    (5, 6, 4, "2026-08-23", "Allocated", "Shelter provided"),
    (6, 8, 5, "2026-08-24", "Allocated", "Medical priority case"),
    (7, 9, 5, "2026-08-24", "Allocated", "Temporary accommodation"),
    (8, 10, 6, "2026-08-25", "Allocated", "Family accommodation"),
]

RELIEF_REQUESTS = [
    (1, 1, 1, 4, "Shelter", 2, "High", "2026-08-20", "Approved", "Shelter required due to landslide"),
    (2, 1, 2, 3, "Medical", 1, "High", "2026-08-20", "Completed", "Medical kit required"),
    (3, 2, 3, 1, "Food", 50, "Medium", "2026-08-21", "Approved", "Food supplies required"),
    (4, 3, 4, 3, "Medical", 2, "High", "2026-08-22", "Pending", "Medical assistance required"),
    (5, 4, 6, 4, "Shelter", 3, "High", "2026-08-23", "Approved", "Blankets required"),
    (6, 5, 7, 1, "Food", 75, "High", "2026-08-24", "Completed", "Food distribution required"),
    (7, 7, 8, 3, "Medical", 2, "High", "2026-08-24", "Pending", "Medical kits required"),
    (8, 8, 9, 6, "Shelter", 4, "Medium", "2026-08-25", "Approved", "Tents required"),
    (9, 9, 10, 1, "Food", 100, "High", "2026-08-25", "Approved", "Food supplies required"),
    (10, 9, 10, 2, "Water", 200, "Medium", "2026-08-25", "Pending", "Drinking water required"),
]

MEDICAL_REQUESTS = [
    (1, 2, "Injury and dehydration", "High", "2026-08-20", "Completed", "Dr. Ravi"),
    (2, 4, "Leg injury", "High", "2026-08-22", "Completed", "Dr. Anjali"),
    (3, 5, "Fever and weakness", "Medium", "2026-08-22", "Pending", "Dr. Kumar"),
    (4, 8, "Respiratory problem", "High", "2026-08-24", "Pending", "Dr. Priya"),
    (5, 10, "Minor injuries", "Medium", "2026-08-25", "Completed", "Dr. Arun"),
    (6, 1, "Back injury", "High", "2026-08-20", "Completed", "Dr. Ravi"),
    (7, 6, "Fracture", "High", "2026-08-23", "Pending", "Dr. Anjali"),
    (8, 9, "Dehydration", "Medium", "2026-08-25", "Completed", "Dr. Kumar"),
]

DISTRIBUTIONS = [
    (1, 1, 1, 1, 500, "2026-08-20", "Relief Team A", "Rice distributed to affected families"),
    (2, 2, 1, 1, 1000, "2026-08-20", "Relief Team A", "Drinking water distributed"),
    (3, 4, 2, 2, 200, "2026-08-21", "Relief Team B", "Blankets distributed"),
    (4, 3, 3, 3, 50, "2026-08-22", "Medical Team A", "Medical kits distributed"),
    (5, 6, 4, 5, 100, "2026-08-23", "Relief Team C", "Tents distributed"),
    (6, 1, 5, 7, 750, "2026-08-24", "Relief Team D", "Rice distributed"),
    (7, 3, 5, 7, 75, "2026-08-24", "Medical Team B", "First aid kits distributed"),
    (8, 2, 6, 9, 1500, "2026-08-25", "Relief Team E", "Drinking water distributed"),
]

RESCUE_TEAMS = [
    (1, "Kodagu Rescue Team", "Flood Rescue", "Vikram Singh", "9100000001", "Active"),
    (2, "Chikkamagaluru Rescue Team", "Landslide Rescue", "Rakesh Kumar", "9100000002", "Active"),
    (3, "Sakleshpur Rescue Team", "Landslide Rescue", "Manoj Rao", "9100000003", "Active"),
    (4, "Bengaluru Emergency Team", "Flood Rescue", "Arun Kumar", "9100000004", "Active"),
    (5, "Dakshina Kannada Relief Team", "Flood Relief", "Suresh Shetty", "9100000005", "Available"),
]

VEHICLES = [
    (1, 1, "Rescue Van", "KA01AB1234", 10, "Available", "Madikeri"),
    (2, 1, "Rescue Boat", "KA02CD5678", 15, "In Use", "Kodagu"),
    (3, 2, "Rescue Truck", "KA03EF9012", 20, "Available", "Chikkamagaluru"),
    (4, 3, "Rescue Jeep", "KA04GH3456", 8, "In Use", "Sakleshpur"),
    (5, 4, "Ambulance", "KA05IJ7890", 6, "Available", "Bengaluru"),
    (6, 5, "Supply Truck", "KA06KL1234", 30, "Available", "Mangaluru"),
]
