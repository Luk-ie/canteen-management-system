import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

class AnalyticsEngine:
    def __init__(self, data_manager):
        self.dm = data_manager
    
    def get_sales_trends(self, period_days=30):
        """Analyze sales trends"""
        data = self.dm.load_sales_data()
        recent_data = data[data['date'] >= (datetime.now() - timedelta(days=period_days))]
        
        daily_sales = recent_data.groupby('date').agg({
            'quantity_sold': 'sum',
            'revenue': 'sum',
            'waste_quantity': 'sum'
        }).reset_index()
        
        return daily_sales
    
    def get_menu_performance(self):
        """Analyze menu item performance"""
        data = self.dm.load_sales_data()
        
        performance = data.groupby('menu_item').agg({
            'quantity_sold': ['sum', 'mean'],
            'revenue': 'sum',
            'waste_quantity': 'sum',
            'waste_cost': 'sum'
        }).round(2)
        
        performance.columns = ['total_sold', 'avg_daily_sold', 'total_revenue', 
                             'total_waste', 'total_waste_cost']
        performance = performance.reset_index()
        
        performance['waste_percentage'] = (performance['total_waste'] / performance['total_sold']) * 100
        performance['profitability'] = performance['total_revenue'] - performance['total_waste_cost']
        
        return performance.sort_values('profitability', ascending=False)
    
    def get_daily_patterns(self):
        """Analyze daily and weekly patterns"""
        data = self.dm.load_sales_data()
        
        # Day of week analysis
        daily_patterns = data.groupby('day_of_week').agg({
            'quantity_sold': 'mean',
            'revenue': 'mean',
            'waste_quantity': 'mean'
        }).reset_index()
        
        # Order days properly
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_patterns['day_of_week'] = pd.Categorical(daily_patterns['day_of_week'], 
                                                     categories=days_order, ordered=True)
        daily_patterns = daily_patterns.sort_values('day_of_week')
        
        return daily_patterns
    
    def forecast_demand(self, days=7):
        """Simple demand forecasting"""
        data = self.dm.load_sales_data()
        recent_sales = data[data['date'] >= (datetime.now() - timedelta(days=30))]
        
        daily_totals = recent_sales.groupby('date')['quantity_sold'].sum()
        
        # Simple moving average
        forecast_value = daily_totals.tail(7).mean()
        
        forecast = []
        for i in range(days):
            forecast_date = datetime.now() + timedelta(days=i+1)
            forecast.append({
                'date': forecast_date,
                'forecasted_demand': int(forecast_value),
                'day_of_week': forecast_date.strftime('%A')
            })
        
        return pd.DataFrame(forecast)
    
    def get_waste_analysis(self):
        """Comprehensive waste analysis"""
        data = self.dm.load_sales_data()
        
        waste_summary = data.groupby('menu_item').agg({
            'waste_quantity': 'sum',
            'waste_cost': 'sum',
            'quantity_sold': 'sum'
        }).reset_index()
        
        waste_summary['waste_percentage'] = (waste_summary['waste_quantity'] / waste_summary['quantity_sold']) * 100
        waste_summary = waste_summary.sort_values('waste_cost', ascending=False)
        
        return waste_summary
    
    def generate_recommendations(self):
        """Generate actionable recommendations"""
        data = self.dm.load_sales_data()
        menu_perf = self.get_menu_performance()
        waste_analysis = self.get_waste_analysis()
        
        recommendations = []
        
        # High waste items
        high_waste = waste_analysis[waste_analysis['waste_percentage'] > 15]
        if not high_waste.empty:
            for _, item in high_waste.iterrows():
                recommendations.append({
                    'type': 'warning',
                    'message': f"High waste detected for {item['menu_item']}: {item['waste_percentage']:.1f}%",
                    'action': f"Consider reducing portions or improving demand forecasting for {item['menu_item']}"
                })
        
        # Low performing items
        low_performers = menu_perf[menu_perf['profitability'] < menu_perf['profitability'].quantile(0.25)]
        if not low_performers.empty:
            for _, item in low_performers.head(2).iterrows():
                recommendations.append({
                    'type': 'info',
                    'message': f"Low profitability for {item['menu_item']}",
                    'action': f"Review pricing or consider replacing {item['menu_item']} on menu"
                })
        
        # General recommendations
        total_waste_percent = (data['waste_cost'].sum() / data['revenue'].sum()) * 100
        if total_waste_percent > 15:
            recommendations.append({
                'type': 'critical',
                'message': f"High overall waste: {total_waste_percent:.1f}% of revenue",
                'action': "Implement pre-ordering system and improve inventory management"
            })
        
        return recommendations