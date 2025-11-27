import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json

# Import the new modules
from food_manager import FoodItemManager
from excel_uploader import ExcelUploader
from simple_auth import SimpleAuth

auth = SimpleAuth()

if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

# Page configuration
st.set_page_config(
    page_title="Canteen Management System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'login_attempted' not in st.session_state:
    st.session_state.login_attempted = False

class CanteenManagementSystem:
    def __init__(self):
        self.auth = SimpleAuth()
        self.food_manager = FoodItemManager()
        self.excel_uploader = ExcelUploader()
        self.data_file = "data/canteen_data.xlsx"
        self.config_file = "config/system_config.json"
        self.load_config()
        
    def load_config(self):
        """Load system configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {
                "menu_items": [
                    "Chapati & Beans", "Rice & Stew", "Ugali & Sukuma", 
                    "Tea & Mandazi", "Chips & Chicken", "Fruit Salad", 
                    "Juice", "Samosa"
                ],
                "prices": [80, 120, 100, 50, 150, 80, 60, 40],
                "opening_hours": "7:00 AM - 4:00 PM"
            }
    
    def load_data(self):
        """Load data from Excel file"""
        try:
            if os.path.exists(self.data_file):
                return pd.read_excel(self.data_file)
            else:
                return self.create_sample_data()
        except:
            return self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample data if no data file exists"""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
        
        data = []
        for date in dates:
            is_weekday = date.weekday() < 5
            base_demand = 120 if is_weekday else 60
            
            for i, item in enumerate(self.config["menu_items"]):
                item_base = base_demand * np.random.uniform(0.3, 1.5)
                daily_sales = max(0, int(np.random.normal(item_base, item_base * 0.3)))
                price = self.config["prices"][i]
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
    
    def add_new_sales_record(self, date, menu_item, quantity_sold, waste_quantity):
        """Add new sales record to the system"""
        try:
            current_data = self.load_data()
            
            # Get price from food manager if available, else from config
            price = 0
            for item in self.food_manager.get_active_items():
                if item['name'] == menu_item:
                    price = item['selling_price']
                    break
            else:
                # Fallback to config
                if menu_item in self.config["menu_items"]:
                    idx = self.config["menu_items"].index(menu_item)
                    price = self.config["prices"][idx]
            
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
            
            # Update food manager sales data
            self.food_manager.update_item_sales(menu_item, quantity_sold)
            
            return True
        except Exception as e:
            st.error(f"Error adding record: {e}")
            return False

def show_login(cms):
    """Login interface with proper session state management"""
    st.sidebar.header("Login")
    
    if st.session_state.logged_in:
        user = st.session_state.current_user
        st.sidebar.success(f"Logged in as: {user['full_name']} ({user['role']})")
        
        if st.sidebar.button("Logout"):
            cms.auth.logout()
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.login_attempted = False
            st.rerun()
    else:
        username = st.sidebar.text_input("Username", value="admin")
        password = st.sidebar.text_input("Password", type="password", value="admin")
        
        if st.sidebar.button("Login", type="primary"):
            st.session_state.login_attempted = True
            success, message = cms.auth.login(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.current_user = cms.auth.get_current_user()
                # NEW: persist into auth.current_user so admin checks work
                cms.auth.current_user = st.session_state.current_user
                st.sidebar.success("Login successful! Loading dashboard...")
                st.rerun()
            else:
                st.sidebar.error(message)

def show_dashboard(cms, data):
    """Display main dashboard"""
    st.header("Dashboard")
    
    # Ensure auth.current_user is set from session
    if st.session_state.current_user:
        cms.auth.current_user = st.session_state.current_user
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = data['revenue'].sum()
        st.metric("Total Revenue", f"KSh {total_revenue:,.0f}")
    
    with col2:
        total_sales = data['quantity_sold'].sum()
        st.metric("Items Sold", f"{total_sales:,}")
    
    with col3:
        total_waste = data['waste_cost'].sum()
        st.metric("Food Waste Cost", f"KSh {total_waste:,.0f}")
    
    with col4:
        waste_percent = (data['waste_cost'].sum() / data['revenue'].sum()) * 100
        st.metric("Waste Percentage", f"{waste_percent:.1f}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales trend
        daily_sales = data.groupby('date')['quantity_sold'].sum().reset_index()
        fig = px.line(daily_sales, x='date', y='quantity_sold', title='Daily Sales Trend')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top items
        top_items = data.groupby('menu_item')['quantity_sold'].sum().nlargest(5)
        fig = px.bar(x=top_items.values, y=top_items.index, orientation='h', 
                    title='Top 5 Selling Items')
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    recent_data = data.sort_values('date', ascending=False).head(10)
    st.dataframe(recent_data[['date', 'menu_item', 'quantity_sold', 'revenue', 'waste_quantity']])

def show_data_entry(cms):
    """Data entry form"""
    st.header("Data Entry")
    
    # Get active food items for dropdown
    active_items = cms.food_manager.get_active_items()
    if not active_items:
        # Fallback to config items
        menu_items = cms.config["menu_items"]
    else:
        menu_items = [item['name'] for item in active_items]
    
    with st.form("sales_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            entry_date = st.date_input("Date", datetime.now())
            menu_item = st.selectbox("Menu Item", menu_items)
            quantity_sold = st.number_input("Quantity Sold", min_value=0, value=0)
        
        with col2:
            waste_quantity = st.number_input("Waste Quantity", min_value=0, value=0)
            
            # Display price information
            price = 0
            for item in active_items:
                if item['name'] == menu_item:
                    price = item['selling_price']
                    break
            else:
                if menu_item in cms.config["menu_items"]:
                    idx = cms.config["menu_items"].index(menu_item)
                    price = cms.config["prices"][idx]
            
            st.info(f"Price: KSh {price}")
            total_revenue = quantity_sold * price
            st.info(f"Total Revenue: KSh {total_revenue}")
        
        submitted = st.form_submit_button("Save Record")
        
        if submitted:
            if cms.add_new_sales_record(entry_date, menu_item, quantity_sold, waste_quantity):
                st.success("Record saved successfully!")
            else:
                st.error("Error saving record!")

def show_food_management(cms):
    """Food items management interface"""
    st.header("Food Items Management")
    
    tab1, tab2, tab3 = st.tabs(["Add Food Item", "Upload from Excel", "View/Edit Items"])
    
    with tab1:
        st.subheader("Add New Food Item")
        with st.form("add_food_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Food Item Name")
                category = st.selectbox("Category", 
                                      ["breakfast", "lunch", "snacks", "beverages"])
                selling_price = st.number_input("Selling Price (KSh)", min_value=0)
            
            with col2:
                cost_price = st.number_input("Cost Price (KSh)", min_value=0)
                preparation_time = st.number_input("Preparation Time (minutes)", min_value=0)
                dietary_tags = st.text_input("Dietary Tags (comma-separated)")
            
            if st.form_submit_button("Add Food Item"):
                if name and selling_price > 0:
                    ingredients = []  # Can be enhanced
                    tags = [tag.strip() for tag in dietary_tags.split(',')] if dietary_tags else []
                    
                    cms.food_manager.add_food_item(
                        name, category, selling_price, cost_price,
                        ingredients, preparation_time, tags
                    )
                    st.success("Food item added successfully!")
    
    with tab2:
        st.subheader("Upload Food Items from Excel")
        st.info("Download the template first, fill it with your food items, then upload here.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Download Food Items Template"):
                file_path, filename = cms.excel_uploader.download_template("food_items")
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="Download Template",
                        data=f,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx'])
        if uploaded_file:
            if st.button("Upload Food Items"):
                success, message, items = cms.food_manager.upload_food_items_from_excel(uploaded_file)
                if success:
                    st.success(message)
                    st.write(f"Added {len(items)} items")
                else:
                    st.error(message)
    
    with tab3:
        st.subheader("Current Food Items")
        active_items = cms.food_manager.get_active_items()
        if active_items:
            df = pd.DataFrame(active_items)
            st.dataframe(df[['name', 'category', 'selling_price', 'cost_price', 'profit_margin']])
            
            # Item management options
            st.subheader("Manage Items")
            item_to_deactivate = st.selectbox("Select item to deactivate", 
                                            [item['name'] for item in active_items])
            if st.button("Deactivate Item"):
                for item in active_items:
                    if item['name'] == item_to_deactivate:
                        cms.food_manager.deactivate_item(item['item_id'])
                        st.success(f"Deactivated {item_to_deactivate}")
                        st.rerun()
                        break
        else:
            st.info("No food items added yet.")

def show_excel_upload(cms):
    """Excel data upload interface"""
    st.header("Excel Data Upload")
    
    st.info("""
    **Upload your existing sales data from Excel files.**
    - Download the template first
    - Fill in your historical data
    - Upload to populate the system
    """)
    
    # Download template
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download Sales Data Template"):
            file_path, filename = cms.excel_uploader.download_template("sales_data")
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download Sales Template",
                    data=f,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    # Upload sales data
    st.subheader("Upload Sales Data")
    uploaded_file = st.file_uploader("Choose sales data Excel file", type=['xlsx'])
    if uploaded_file:
        if st.button("Upload Sales Data"):
            with st.spinner("Processing Excel file..."):
                success, message = cms.excel_uploader.upload_sales_data(uploaded_file, cms.food_manager)
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

def show_reports(cms, data):
    """Generate reports"""
    st.header("Reports & Analytics")
    
    report_type = st.selectbox("Report Type", 
        ["Sales Summary", "Waste Analysis", "Menu Performance", "Daily Patterns"])
    
    if report_type == "Sales Summary":
        st.subheader("Sales Summary Report")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", data['date'].min())
        with col2:
            end_date = st.date_input("End Date", data['date'].max())
        
        filtered_data = data[(data['date'] >= pd.to_datetime(start_date)) & 
                           (data['date'] <= pd.to_datetime(end_date))]
        
        st.dataframe(filtered_data.describe())
        
    elif report_type == "Waste Analysis":
        st.subheader("Food Waste Analysis")
        
        waste_by_item = data.groupby('menu_item').agg({
            'waste_quantity': 'sum',
            'waste_cost': 'sum'
        }).reset_index()
        
        fig = px.bar(waste_by_item, x='menu_item', y='waste_cost', 
                    title='Waste Cost by Menu Item')
        st.plotly_chart(fig, use_container_width=True)
        
    elif report_type == "Menu Performance":
        st.subheader("Menu Performance")
        
        performance = data.groupby('menu_item').agg({
            'quantity_sold': 'sum',
            'revenue': 'sum',
            'waste_quantity': 'sum'
        }).reset_index()
        
        performance['profitability'] = performance['revenue'] - performance['waste_cost']
        st.dataframe(performance.sort_values('profitability', ascending=False))
        
    elif report_type == "Daily Patterns":
        st.subheader("Daily Sales Patterns")
        
        daily_patterns = data.groupby('day_of_week').agg({
            'quantity_sold': 'mean',
            'revenue': 'mean'
        }).reset_index()
        
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_patterns['day_of_week'] = pd.Categorical(daily_patterns['day_of_week'], 
                                                     categories=days_order, ordered=True)
        daily_patterns = daily_patterns.sort_values('day_of_week')
        
        fig = px.line(daily_patterns, x='day_of_week', y='quantity_sold', 
                     title='Average Sales by Day of Week')
        st.plotly_chart(fig, use_container_width=True)

def show_inventory(cms, data):
    """Inventory management"""
    st.header("Inventory Management")
    
    st.subheader("Current Stock Levels")
    
    # Mock inventory data - this can be enhanced with real inventory tracking
    inventory_data = {
        'Item': ['Flour', 'Rice', 'Vegetables', 'Chicken', 'Fruits', 'Juice'],
        'Current Stock': [50, 30, 25, 15, 20, 40],
        'Unit': ['kg', 'kg', 'kg', 'kg', 'kg', 'liters'],
        'Reorder Level': [10, 15, 10, 5, 8, 10],
        'Status': ['Adequate', 'Adequate', 'Adequate', 'Low', 'Adequate', 'Adequate']
    }
    
    inventory_df = pd.DataFrame(inventory_data)
    st.dataframe(inventory_df)
    
    # Low stock alert
    low_stock = inventory_df[inventory_df['Status'] == 'Low']
    if not low_stock.empty:
        st.warning("Low Stock Alert!")
        st.dataframe(low_stock)
    
    # Inventory suggestions based on sales data
    st.subheader("Inventory Suggestions")
    weekly_sales = data.groupby('menu_item')['quantity_sold'].sum().nlargest(5)
    st.write("Top 5 items (consider stocking more ingredients for these):")
    for item, sales in weekly_sales.items():
        st.write(f"- {item}: {sales} units sold")

def show_settings(cms):
    """System settings with user management - FINAL FIXED VERSION"""
    st.header("System Settings")
    
    # Get current user from SESSION STATE
    current_user = st.session_state.current_user

    # Ensure backend knows who is logged in
    if current_user:
        cms.auth.current_user = current_user

    # Spelling-tolerant role check
    def is_user_admin(user):
        if not user:
            return False
        role = user.get('role')
        if not role:
            return False
        normalized_role = str(role).strip().lower()
        return normalized_role == 'admin'
    
    # Debug info in sidebar
    if current_user:
        st.sidebar.success(f"Session User: {current_user.get('username')}")
        st.sidebar.info(f"Session Role: '{current_user.get('role')}'")
        st.sidebar.info(f"Admin Check: {is_user_admin(current_user)}")
    else:
        st.sidebar.error("No user in session state!")
    
    # Admin-only section
    if current_user and is_user_admin(current_user):
        st.success("ADMIN ACCESS GRANTED!")
        st.subheader("User Management")
        
        tab1, tab2, tab3 = st.tabs(["Add New User", "Manage Users", "Change Passwords"])
        
        # --- Add New User ---
        with tab1:
            st.info("Only administrators can create new user accounts")
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_username = st.text_input("Username *")
                    new_password = st.text_input("Password *", type="password")
                    confirm_password = st.text_input("Confirm Password *", type="password")
                
                with col2:
                    new_fullname = st.text_input("Full Name *")
                    new_email = st.text_input("Email")
                    new_role = st.selectbox("Role *", ["staff", "manager", "admin"])
                
                st.write("**Required fields marked with ***")
                
                if st.form_submit_button("Create User Account"):
                    if not all([new_username, new_password, new_fullname]):
                        st.error("Please fill all required fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 4:
                        st.error("Password must be at least 4 characters")
                    else:
                        success, message = cms.auth.add_user(
                            new_username, new_password, new_role, new_fullname, new_email
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        # --- Manage Users ---
        with tab2:
            st.subheader("Current Users")
            users = cms.auth.get_all_users()
            if users:
                user_data = []
                for user in users:
                    user_data.append({
                        'ID': user['user_id'],
                        'Username': user['username'],
                        'Full Name': user['full_name'],
                        'Role': user['role'],
                        'Status': 'Active' if user['is_active'] else 'Inactive',
                        'Last Login': user['last_login'] or 'Never',
                        'Date Created': user['date_created']
                    })
                users_df = pd.DataFrame(user_data)
                st.dataframe(users_df, use_container_width=True)
            else:
                st.info("No users found")
        
        # --- Change Passwords ---
        with tab3:
            st.subheader("Change User Passwords")
            users = cms.auth.get_all_users()
            if users:
                user_to_change = st.selectbox(
                    "Select user",
                    [f"{u['user_id']} - {u['username']}" for u in users]
                )
                
                if user_to_change:
                    user_id = int(user_to_change.split(' - ')[0])
                    selected_user = next((u for u in users if u['user_id'] == user_id), None)
                    
                    if selected_user:
                        with st.form("change_password_form"):
                            new_password = st.text_input("New Password", type="password")
                            confirm_password = st.text_input("Confirm Password", type="password")
                            
                            if st.form_submit_button("Change Password"):
                                if new_password != confirm_password:
                                    st.error("Passwords do not match")
                                elif len(new_password) < 4:
                                    st.error("Password must be at least 4 characters")
                                else:
                                    success, message = cms.auth.change_password(
                                        selected_user['username'], new_password
                                    )
                                    if success:
                                        st.success(message)
                                    else:
                                        st.error(message)
    
    # Non-admin section
    else:
        st.error("ADMIN ACCESS DENIED")
        st.warning("Administrator access required")
        
        with st.expander("Debug Information"):
            if current_user:
                st.write("**Current User Data:**")
                st.json(current_user)
                st.write(f"**Role Value:** '{current_user.get('role')}'")
                st.write(f"**Role Type:** {type(current_user.get('role'))}")
                st.write(f"**Normalized Check:** {str(current_user.get('role')).strip().lower() == 'admin'}")
            else:
                st.write("No user in session state!")
                st.write(f"Auth current user: {cms.auth.get_current_user()}")
        
        if current_user:
            st.subheader("Change Your Password")
            with st.form("change_my_password"):
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Change My Password"):
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 4:
                        st.error("Password must be at least 4 characters")
                    else:
                        success, message = cms.auth.change_password(
                            current_user['username'], new_password
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

def main():
    st.title("Canteen Management System")
    st.markdown("---")
    
    # Initialize system
    cms = CanteenManagementSystem()
    
    # Show login section
    show_login(cms)
    
    # Check if user is logged in using session state
    if not st.session_state.logged_in:
        if st.session_state.get('login_attempted', False):
            st.error("Login failed. Please check your credentials.")
        else:
            st.info("Please login to access the system")
        return
    
    # USER IS LOGGED IN - SHOW MAIN APPLICATION
    try:
        # Show welcome message
        user = st.session_state.current_user
        st.sidebar.success(f"Welcome, {user['full_name']}!")
        
        # Load data
        data = cms.load_data()
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        app_mode = st.sidebar.selectbox("Choose Module", 
            ["Dashboard", "Data Entry", "Food Management", "Excel Upload", "Reports", "Inventory", "Settings"])
        
        # Logout button in sidebar
        #if st.sidebar.button("Logout"):
            #cms.auth.logout()
            #st.session_state.logged_in = False
            #st.session_state.current_user = None
            #st.session_state.login_attempted = False
            #st.rerun()
        
        # Show selected module
        if app_mode == "Dashboard":
            show_dashboard(cms, data)
        elif app_mode == "Data Entry":
            show_data_entry(cms)
        elif app_mode == "Food Management":
            show_food_management(cms)
        elif app_mode == "Excel Upload":
            show_excel_upload(cms)
        elif app_mode == "Reports":
            show_reports(cms, data)
        elif app_mode == "Inventory":
            show_inventory(cms, data)
        elif app_mode == "Settings":
            show_settings(cms)
            
    except Exception as e:
        st.error(f"Error loading application: {e}")
        st.info("Please try logging out and back in, or check the system configuration.")

if __name__ == "__main__":
    main()