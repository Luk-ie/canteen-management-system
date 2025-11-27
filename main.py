import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Page configuration
st.set_page_config(
    page_title="Canteen Sales Analysis Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
    }
</style>
""", unsafe_allow_html=True)

class CanteenDashboard:
    def __init__(self):
        self.sample_data = self.generate_sample_data()
    
    def generate_sample_data(self):
        """Generate sample sales data for demonstration"""
        np.random.seed(42)
        
        # Generate 90 days of historical data
        dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
        
        data = []
        menu_items = ['Chapati & Beans', 'Rice & Stew', 'Ugali & Sukuma', 'Tea & Mandazi', 
                     'Chips & Chicken', 'Fruit Salad', 'Juice', 'Samosa']
        
        for date in dates:
            # Weekday patterns
            is_weekday = date.weekday() < 5
            base_demand = 120 if is_weekday else 60
            
            for item in menu_items:
                # Different base demand for different items
                item_base = base_demand * np.random.uniform(0.3, 1.5)
                
                # Add some randomness and trends
                daily_sales = max(0, int(np.random.normal(item_base, item_base * 0.3)))
                price = np.random.uniform(50, 200)
                revenue = daily_sales * price
                
                # Food waste (5-20% of sales)
                waste_percentage = np.random.uniform(0.05, 0.2)
                waste_quantity = int(daily_sales * waste_percentage)
                
                data.append({
                    'date': date,
                    'day_of_week': date.strftime('%A'),
                    'menu_item': item,
                    'quantity_sold': daily_sales,
                    'price': price,
                    'revenue': revenue,
                    'waste_quantity': waste_quantity,
                    'waste_cost': waste_quantity * price * 0.3,  # Cost of wasted food
                    'is_weekday': is_weekday
                })
        
        return pd.DataFrame(data)
    
    def display_header(self):
        """Display the dashboard header"""
        st.markdown('<div class="main-header"> Canteen Sales Pattern Analysis Dashboard</div>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            **Project:** Excel-Based Manual Analysis System for Daily Meal Planning Accuracy  
            **Researcher:** Luke Kioko | **Admission:** DDA-03-0070/2024  
            **University:** Zetech University | **Department:** ICT and Engineering
            """)
    
    def display_key_metrics(self):
        """Display key performance metrics"""
        st.markdown('<div class="section-header"> Key Performance Indicators</div>', 
                   unsafe_allow_html=True)
        
        total_revenue = self.sample_data['revenue'].sum()
        total_sales = self.sample_data['quantity_sold'].sum()
        total_waste_cost = self.sample_data['waste_cost'].sum()
        avg_daily_revenue = self.sample_data.groupby('date')['revenue'].sum().mean()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Revenue",
                value=f"KSh {total_revenue:,.0f}",
                delta=f"KSh {avg_daily_revenue:,.0f}/day"
            )
        
        with col2:
            st.metric(
                label="Total Items Sold",
                value=f"{total_sales:,}",
                delta="All Time"
            )
        
        with col3:
            waste_percentage = (total_waste_cost / total_revenue) * 100
            st.metric(
                label="Food Waste Cost",
                value=f"KSh {total_waste_cost:,.0f}",
                delta=f"{waste_percentage:.1f}% of revenue"
            )
        
        with col4:
            unique_days = self.sample_data['date'].nunique()
            st.metric(
                label="Analysis Period",
                value=f"{unique_days} days",
                delta="Historical Data"
            )
    
    def display_sales_trends(self):
        """Display sales trends and patterns"""
        st.markdown('<div class="section-header"> Sales Trends Analysis</div>', 
                   unsafe_allow_html=True)
        
        # Daily sales trend
        daily_sales = self.sample_data.groupby('date').agg({
            'quantity_sold': 'sum',
            'revenue': 'sum',
            'waste_quantity': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sales trend chart
            fig = px.line(daily_sales, x='date', y='quantity_sold', 
                         title='Daily Sales Quantity Trend')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue vs Waste
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_sales['date'], y=daily_sales['revenue'], 
                                   name='Revenue', line=dict(color='green')))
            fig.add_trace(go.Scatter(x=daily_sales['date'], y=daily_sales['waste_quantity'] * 100, 
                                   name='Waste (Scaled)', line=dict(color='red')))
            fig.update_layout(title='Revenue vs Food Waste Trend', height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def display_menu_analysis(self):
        """Display menu item performance analysis"""
        st.markdown('<div class="section-header"> Menu Performance Analysis</div>', 
                   unsafe_allow_html=True)
        
        menu_performance = self.sample_data.groupby('menu_item').agg({
            'quantity_sold': 'sum',
            'revenue': 'sum',
            'waste_quantity': 'sum'
        }).reset_index()
        
        menu_performance['waste_percentage'] = (menu_performance['waste_quantity'] / 
                                              menu_performance['quantity_sold']) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top selling items
            top_items = menu_performance.nlargest(10, 'quantity_sold')
            fig = px.bar(top_items, x='menu_item', y='quantity_sold',
                        title='Top 10 Selling Menu Items')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Waste analysis by item
            high_waste_items = menu_performance.nlargest(10, 'waste_percentage')
            fig = px.bar(high_waste_items, x='menu_item', y='waste_percentage',
                        title='Food Waste Percentage by Menu Item')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def display_daily_patterns(self):
        """Display daily and weekly patterns"""
        st.markdown('<div class="section-header"> Daily & Weekly Patterns</div>', 
                   unsafe_allow_html=True)
        
        # Day of week analysis
        day_analysis = self.sample_data.groupby('day_of_week').agg({
            'quantity_sold': 'mean',
            'revenue': 'mean',
            'waste_quantity': 'mean'
        }).reset_index()
        
        # Order days properly
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_analysis['day_of_week'] = pd.Categorical(day_analysis['day_of_week'], 
                                                   categories=days_order, ordered=True)
        day_analysis = day_analysis.sort_values('day_of_week')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(day_analysis, x='day_of_week', y='quantity_sold',
                         title='Average Sales by Day of Week')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(day_analysis, x='day_of_week', y='waste_quantity',
                        title='Average Food Waste by Day of Week')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def display_forecasting(self):
        """Display simple forecasting based on historical patterns"""
        st.markdown('<div class="section-header"> Demand Forecasting</div>', 
                   unsafe_allow_html=True)
        
        # Simple moving average forecast
        daily_totals = self.sample_data.groupby('date')['quantity_sold'].sum().reset_index()
        daily_totals['7_day_avg'] = daily_totals['quantity_sold'].rolling(window=7).mean()
        
        # Forecast next 7 days
        last_7_days_avg = daily_totals['quantity_sold'].tail(7).mean()
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            fig = px.line(daily_totals, x='date', y=['quantity_sold', '7_day_avg'],
                         title='Sales Trend with 7-Day Moving Average')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="7-Day Average Sales",
                value=f"{last_7_days_avg:.0f}",
                delta="items/day"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Recommendation based on patterns
            st.info("**Recommendation:** Use this average for daily meal planning")
        
        with col3:
            # Quick forecast for next week
            forecast_days = 7
            forecast = [last_7_days_avg] * forecast_days
            
            st.markdown("**Next Week Forecast:**")
            for i, day_forecast in enumerate(forecast):
                st.write(f"Day {i+1}: {day_forecast:.0f} items")
    
    def display_waste_analysis(self):
        """Display detailed food waste analysis"""
        st.markdown('<div class="section-header"> Food Waste Analysis</div>', 
                   unsafe_allow_html=True)
        
        total_waste_cost = self.sample_data['waste_cost'].sum()
        total_revenue = self.sample_data['revenue'].sum()
        waste_percentage = (total_waste_cost / total_revenue) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Waste cost over time
            weekly_waste = self.sample_data.groupby(pd.Grouper(key='date', freq='W'))['waste_cost'].sum().reset_index()
            fig = px.area(weekly_waste, x='date', y='waste_cost',
                         title='Weekly Food Waste Cost Trend')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Waste metrics and recommendations
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Total Waste Cost",
                value=f"KSh {total_waste_cost:,.0f}",
                delta=f"{waste_percentage:.1f}% of revenue"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.warning("**Cost Saving Opportunity:**")
            if waste_percentage > 15:
                st.error("High waste levels detected! Consider:")
                st.write("- Reduce portions of low-selling items")
                st.write("- Implement pre-ordering system")
                st.write("- Donate excess food to reduce losses")
            elif waste_percentage > 10:
                st.warning("Moderate waste levels. Suggestions:")
                st.write("- Adjust inventory based on sales patterns")
                st.write("- Monitor popular items more closely")
            else:
                st.success("Good waste management! Maintain current practices")
    
    def display_data_export(self):
        """Display data export functionality"""
        st.markdown('<div class="section-header"> Data Export & Reports</div>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Summary report
            st.subheader("Summary Report")
            
            summary_data = {
                'Metric': ['Total Revenue', 'Total Items Sold', 'Total Waste Cost', 
                          'Waste Percentage', 'Analysis Period'],
                'Value': [
                    f"KSh {self.sample_data['revenue'].sum():,.0f}",
                    f"{self.sample_data['quantity_sold'].sum():,}",
                    f"KSh {self.sample_data['waste_cost'].sum():,.0f}",
                    f"{(self.sample_data['waste_cost'].sum() / self.sample_data['revenue'].sum()) * 100:.1f}%",
                    f"{self.sample_data['date'].nunique()} days"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
            
            # Export summary as CSV
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="Download Summary Report",
                data=csv,
                file_name="canteen_summary_report.csv",
                mime="text/csv"
            )
        
        with col2:
            # Raw data export
            st.subheader("Raw Data Export")
            st.info("Export the complete dataset for further analysis in Excel")
            
            # Convert to CSV
            csv_data = self.sample_data.to_csv(index=False)
            
            st.download_button(
                label="Download Complete Dataset",
                data=csv_data,
                file_name="canteen_sales_data.csv",
                mime="text/csv"
            )
            
            st.info("""
            **Excel Integration Tips:**
            - Use PivotTables for custom analysis
            - Create charts for specific time periods
            - Filter by menu items or days of week
            - Calculate custom metrics as needed
            """)
    
    def run_dashboard(self):
        """Run the complete dashboard"""
        self.display_header()
        
        # Sidebar for navigation
        st.sidebar.title("Navigation")
        sections = [
            "Key Metrics", "Sales Trends", "Menu Analysis", 
            "Daily Patterns", "Demand Forecasting", "Waste Analysis", "Data Export"
        ]
        
        selected_section = st.sidebar.radio("Go to:", sections)
        
        # Display selected section
        if selected_section == "Key Metrics":
            self.display_key_metrics()
        elif selected_section == "Sales Trends":
            self.display_sales_trends()
        elif selected_section == "Menu Analysis":
            self.display_menu_analysis()
        elif selected_section == "Daily Patterns":
            self.display_daily_patterns()
        elif selected_section == "Demand Forecasting":
            self.display_forecasting()
        elif selected_section == "Waste Analysis":
            self.display_waste_analysis()
        elif selected_section == "Data Export":
            self.display_data_export()
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.info("""
        **Project Objectives Achieved:**
        - Sales pattern analysis
        - Food waste monitoring
        - Demand forecasting
        - Menu performance tracking
        - Data export functionality
        """)

# Run the dashboard
if __name__ == "__main__":
    dashboard = CanteenDashboard()
    dashboard.run_dashboard()