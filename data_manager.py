import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

class DataManager:
    def __init__(self):
        self.data_file = "data/canteen_data.xlsx"
        self.config_file = "config/system_config.json"
        self.backup_dir = "backups/"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def load_config(self):
        """Load system configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                "menu_items": [
                    "Chapati & Beans", "Rice & Stew", "Ugali & Sukuma",
                    "Tea & Mandazi", "Chips & Chicken", "Fruit Salad",
                    "Juice", "Samosa"
                ],
                "prices": [80, 120, 100, 50, 150, 80, 60, 40]
            }
    
    def load_sales_data(self):
        """Load sales data from Excel file"""
        try:
            if os.path.exists(self.data_file):
                df = pd.read_excel(self.data_file)
                df['date'] = pd.to_datetime(df['date'])
                return df
            else:
                return self.generate_sample_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            return self.generate_sample_data()
    
    def generate_sample_data(self):
        """Generate sample data for demonstration"""
        config = self.load_config()
        np.random.seed(42)
        
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=90),
            end=datetime.now(),
            freq='D'
        )
        
        data = []
        for date in dates:
            is_weekday = date.weekday() < 5
            base_demand = 120 if is_weekday else 60
            
            for i, item in enumerate(config["menu_items"]):
                item_base = base_demand * np.random.uniform(0.3, 1.5)
                daily_sales = max(0, int(np.random.normal(item_base, item_base * 0.3)))
                price = config["prices"][i]
                revenue = daily_sales * price
                waste_quantity = int(daily_sales * np.random.uniform(0.05, 0.2))
                
                data.append({
                    'date': date,
                    'day_of_week': date.strftime('%A'),
                    'menu_item': item,
                    'quantity_sold': daily_sales,
                    'price': price,
                    'revenue': revenue,
                    'waste_quantity': waste_quantity,
                    'waste_cost': waste_quantity * price * 0.3,
                    'is_weekday': is_weekday
                })
        
        df = pd.DataFrame(data)
        self.save_data(df)
        return df
    
    def save_data(self, df):
        """Save data to Excel file"""
        os.makedirs('data', exist_ok=True)
        df.to_excel(self.data_file, index=False)
    
    def add_sales_record(self, date, menu_item, quantity_sold, waste_quantity):
        """Add a new sales record"""
        try:
            current_data = self.load_sales_data()
            config = self.load_config()
            
            price = config["prices"][config["menu_items"].index(menu_item)]
            
            new_record = {
                'date': pd.to_datetime(date),
                'day_of_week': pd.to_datetime(date).strftime('%A'),
                'menu_item': menu_item,
                'quantity_sold': quantity_sold,
                'price': price,
                'revenue': quantity_sold * price,
                'waste_quantity': waste_quantity,
                'waste_cost': waste_quantity * price * 0.3,
                'is_weekday': pd.to_datetime(date).weekday() < 5
            }
            
            updated_data = pd.concat([current_data, pd.DataFrame([new_record])], ignore_index=True)
            self.save_data(updated_data)
            return True
        except Exception as e:
            print(f"Error adding record: {e}")
            return False
    
    def get_sales_summary(self, start_date=None, end_date=None):
        """Get sales summary for given period"""
        data = self.load_sales_data()
        
        if start_date:
            data = data[data['date'] >= pd.to_datetime(start_date)]
        if end_date:
            data = data[data['date'] <= pd.to_datetime(end_date)]
        
        summary = {
            'total_revenue': data['revenue'].sum(),
            'total_items_sold': data['quantity_sold'].sum(),
            'total_waste_cost': data['waste_cost'].sum(),
            'average_daily_sales': data.groupby('date')['quantity_sold'].sum().mean(),
            'waste_percentage': (data['waste_cost'].sum() / data['revenue'].sum()) * 100
        }
        
        return summary
    
    def create_backup(self):
        """Create data backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.backup_dir}canteen_backup_{timestamp}.xlsx"
            
            data = self.load_sales_data()
            data.to_excel(backup_file, index=False)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def export_to_excel(self, filename=None):
        """Export data to Excel for manual analysis"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"canteen_export_{timestamp}.xlsx"
        
        data = self.load_sales_data()
        data.to_excel(filename, index=False)
        return filename