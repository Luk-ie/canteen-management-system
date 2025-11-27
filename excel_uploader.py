import pandas as pd
import os
from datetime import datetime, timedelta

class ExcelUploader:
    def __init__(self):
        self.upload_dir = "uploads"
        self.data_dir = "data"
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
    
    def upload_sales_data(self, excel_file, food_manager):
        """Upload sales data from Excel file"""
        try:
            # Save uploaded file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_upload_{timestamp}.xlsx"
            file_path = os.path.join(self.upload_dir, filename)
            
            with open(file_path, "wb") as f:
                f.write(excel_file.getbuffer())
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Expected columns: date, menu_item, quantity_sold, waste_quantity
            required_columns = ['date', 'menu_item', 'quantity_sold']
            
            if not all(col in df.columns for col in required_columns):
                return False, f"Excel file must contain columns: {required_columns}"
            
            # Process sales data
            processed_data = []
            for _, row in df.iterrows():
                # Convert date if needed
                if isinstance(row['date'], str):
                    date = datetime.strptime(row['date'], '%Y-%m-%d')
                else:
                    date = row['date']
                
                sales_record = {
                    'date': date.strftime('%Y-%m-%d'),
                    'day_of_week': date.strftime('%A'),
                    'menu_item': row['menu_item'],
                    'quantity_sold': int(row['quantity_sold']),
                    'waste_quantity': int(row.get('waste_quantity', 0)),
                    'price': 0,  # Will be set from food items
                    'revenue': 0,
                    'waste_cost': 0,
                    'is_weekday': date.weekday() < 5
                }
                
                # Update food manager sales data
                food_manager.update_item_sales(row['menu_item'], int(row['quantity_sold']))
                
                processed_data.append(sales_record)
            
            # Save to main data file
            self._append_to_main_data(processed_data, food_manager)
            
            return True, f"Successfully processed {len(processed_data)} sales records"
            
        except Exception as e:
            return False, f"Error processing Excel file: {str(e)}"
    
    def _append_to_main_data(self, new_data, food_manager):
        """Append new data to main data file"""
        main_file = os.path.join(self.data_dir, "canteen_data.xlsx")
        
        # Get price information from food manager
        for record in new_data:
            for item in food_manager.get_active_items():
                if item['name'] == record['menu_item']:
                    record['price'] = item['selling_price']
                    record['revenue'] = record['quantity_sold'] * item['selling_price']
                    record['waste_cost'] = record['waste_quantity'] * item['selling_price'] * 0.3
                    break
        
        # Load existing data or create new
        if os.path.exists(main_file):
            existing_df = pd.read_excel(main_file)
            updated_df = pd.concat([existing_df, pd.DataFrame(new_data)], ignore_index=True)
        else:
            updated_df = pd.DataFrame(new_data)
        
        # Remove duplicates based on date and menu_item
        updated_df = updated_df.drop_duplicates(subset=['date', 'menu_item'], keep='last')
        updated_df.to_excel(main_file, index=False)
    
    def download_template(self, template_type):
        """Download Excel template for upload"""
        if template_type == "food_items":
            # Create food items template
            template_data = {
                'name': ['Chapati & Beans', 'Rice & Stew', 'Tea & Mandazi'],
                'category': ['lunch', 'lunch', 'breakfast'],
                'selling_price': [80, 120, 50],
                'cost_price': [45, 70, 25],
                'ingredients': ['flour,beans', 'rice,vegetables,meat', 'tea_leaves,flour,sugar'],
                'preparation_time': [15, 30, 10],
                'dietary_tags': ['vegetarian,high_protein', 'non_vegetarian', 'vegetarian']
            }
            filename = "food_items_template.xlsx"
            
        elif template_type == "sales_data":
            # Create sales data template
            start_date = datetime.now() - timedelta(days=7)
            dates = [start_date + timedelta(days=i) for i in range(7)]
            
            template_data = {
                'date': [d.strftime('%Y-%m-%d') for d in dates] * 3,
                'menu_item': ['Chapati & Beans'] * 7 + ['Rice & Stew'] * 7 + ['Tea & Mandazi'] * 7,
                'quantity_sold': [45, 50, 48, 52, 47, 30, 35] * 3,
                'waste_quantity': [5, 3, 4, 2, 6, 8, 5] * 3
            }
            filename = "sales_data_template.xlsx"
        
        df = pd.DataFrame(template_data)
        file_path = os.path.join(self.upload_dir, filename)
        df.to_excel(file_path, index=False)
        
        return file_path, filename