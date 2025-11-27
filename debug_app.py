import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
from simple_auth import SimpleAuth

# Page configuration
st.set_page_config(
    page_title="Canteen Management System - DEBUG",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def debug_main():
    st.title("🐛 Canteen Management System - DEBUG MODE")
    st.markdown("---")
    
    # Initialize system
    auth = SimpleAuth()
    
    # Debug information
    st.sidebar.header("🔧 Debug Info")
    st.sidebar.write(f"Current User: {auth.get_current_user()}")
    st.sidebar.write(f"Session State: {dict(st.session_state)}")
    
    # Simple login
    st.sidebar.header("🔐 Login")
    
    if auth.get_current_user():
        user = auth.get_current_user()
        st.sidebar.success(f"✅ Logged in as: {user['username']}")
        
        if st.sidebar.button("Logout"):
            auth.logout()
            st.rerun()
    else:
        username = st.sidebar.text_input("Username", value="admin")
        password = st.sidebar.text_input("Password", type="password", value="admin")
        
        if st.sidebar.button("Login"):
            success, message = auth.login(username, password)
            if success:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(message)
    
    # Main content based on login status
    if not auth.get_current_user():
        st.warning("Please login above")
        return
    
    # User is logged in - show simple dashboard
    st.success(f"🎉 Welcome, {auth.get_current_user()['full_name']}!")
    
    # Simple dashboard
    st.header("📊 Simple Dashboard")
    
    # Create sample data for demonstration
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    sales_data = pd.DataFrame({
        'date': dates,
        'sales': np.random.randint(50, 200, size=30)
    })
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Sales", "1,234")
    
    with col2:
        st.metric("Items Sold", "456")
    
    with col3:
        st.metric("Waste Cost", "KSh 123")
    
    # Simple chart
    fig = px.line(sales_data, x='date', y='sales', title='Sales Trend')
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("✅ If you can see this, the dashboard is working!")

if __name__ == "__main__":
    debug_main()
    