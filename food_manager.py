import pandas as pd
import json
import os
from datetime import datetime

class FoodItemManager:
    def __init__(self):
        self.food_items_file = "data/food_items.json"
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
        self.load_food_items()
    
    def load_food_items(self):
        """Load food items from JSON file"""
        try:
            if os.path.exists(self.food_items_file):
                with open(self.food_items_file, 'r') as f:
                    self.food_items = json.load(f)
            else:
                self.food_items = []
                self.save_food_items()
        except:
            self.food_items = []
    
    def save_food_items(self):
        """Save food items to JSON file"""
        os.makedirs('data', exist_ok=True)
        with open(self.food_items_file, 'w') as f:
            json.dump(self.food_items, f, indent=2)
    
    def add_food_item(self, name, category, selling_price, cost_price=0, 
                     ingredients=None, preparation_time=0, dietary_tags=None):
        """Add a new food item manually"""
        new_item = {
            "item_id": len(self.food_items) + 1,
            "name": name,
            "category": category,
            "selling_price": selling_price,
            "cost_price": cost_price,
            "profit_margin": selling_price - cost_price,
            "ingredients": ingredients or [],
            "preparation_time": preparation_time,
            "dietary_tags": dietary_tags or [],
            "is_active": True,
            "date_added": datetime.now().strftime("%Y-%m-%d"),
            "total_sold": 0,
            "popularity_score": 0
        }
        
        self.food_items.append(new_item)
        self.save_food_items()
        return new_item
    
    def upload_food_items_from_excel(self, excel_file):
        """Upload food items from Excel file"""
        try:
            # Save uploaded file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"food_upload_{timestamp}.xlsx"
            file_path = os.path.join(self.upload_dir, filename)
            
            with open(file_path, "wb") as f:
                f.write(excel_file.getbuffer())
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Process each row
            added_items = []
            for _, row in df.iterrows():
                item = {
                    "item_id": len(self.food_items) + 1,
                    "name": row.get('name', ''),
                    "category": row.get('category', 'general'),
                    "selling_price": float(row.get('selling_price', 0)),
                    "cost_price": float(row.get('cost_price', 0)),
                    "profit_margin": float(row.get('selling_price', 0)) - float(row.get('cost_price', 0)),
                    "ingredients": str(row.get('ingredients', '')).split(',') if pd.notna(row.get('ingredients')) else [],
                    "preparation_time": int(row.get('preparation_time', 0)),
                    "dietary_tags": str(row.get('dietary_tags', '')).split(',') if pd.notna(row.get('dietary_tags')) else [],
                    "is_active": True,
                    "date_added": datetime.now().strftime("%Y-%m-%d"),
                    "total_sold": 0,
                    "popularity_score": 0
                }
                
                self.food_items.append(item)
                added_items.append(item)
            
            self.save_food_items()
            return True, f"Successfully added {len(added_items)} food items", added_items
            
        except Exception as e:
            return False, f"Error uploading Excel file: {str(e)}", []
    
    def get_food_categories(self):
        """Get unique food categories"""
        categories = set(item['category'] for item in self.food_items if item['is_active'])
        return sorted(list(categories))
    
    def get_active_items(self):
        """Get all active food items"""
        return [item for item in self.food_items if item['is_active']]
    
    def update_item_sales(self, item_name, quantity_sold):
        """Update sales data for an item"""
        for item in self.food_items:
            if item['name'] == item_name and item['is_active']:
                item['total_sold'] += quantity_sold
                # Simple popularity score based on recent sales
                item['popularity_score'] = min(item['total_sold'] / 100, 1.0)
                break
        self.save_food_items()
    
    def deactivate_item(self, item_id):
        """Deactivate a food item (soft delete)"""
        for item in self.food_items:
            if item['item_id'] == item_id:
                item['is_active'] = False
                break
        self.save_food_items()