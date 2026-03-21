import os
import django
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from content.models import Category, Experience

def create_dummy_data():
    print("Generating 200 dummy experiences...")
    # Create categories
    cat_fort, _ = Category.objects.get_or_create(
        name="Fort", 
        defaults={"description": "Historical forts"}
    )
    cat_museum, _ = Category.objects.get_or_create(
        name="Museum", 
        defaults={"description": "Historical museums"}
    )
    
    categories = [cat_fort, cat_museum]
    cities = ["Delhi", "Mumbai", "Kolkata", "Chennai", "Bangalore", "Hyderabad", "Pune", "Jaipur"]
    names = ["Grand", "Royal", "Ancient", "National", "City", "Imperial", "Historic", "Modern"]

    count = 0
    for i in range(1, 201):
        cat = random.choice(categories)
        city = random.choice(cities)
        adjective = random.choice(names)
        name = f"{adjective} {cat.name} {i}"
        
        # We use get_or_create to avoid duplicates if run multiple times
        obj, created = Experience.objects.get_or_create(
            name=name,
            defaults={
                "category_id": cat,
                "location": f"{city}, India",
                "max_daily_capacity": random.randint(500, 5000),
                "entry_fee_base": round(random.uniform(10.0, 100.0), 2),
            }
        )
        if created:
            count += 1
            
    print(f"Successfully created {count} new dummy experiences! (Total 200 created previously or now)")

if __name__ == "__main__":
    create_dummy_data()
