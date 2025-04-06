import streamlit as st


# from pymongo import MongoClient
# from pymongo.server_api import ServerApi
from bucket import *

import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

file = "rootkey.csv"
session = createSession(file=file)

name = "John Doe"
bucket_name= "website-sample-bucket"
enable_Bucket_Versioning_Support(bucket_name=bucket_name)

path = "data.csv"
uploadFiles(bucket_name, path)

data = pd.read_csv(f"{path}")

def extractCal(data):
    # Ensure 'Date' column is parsed as datetime
    data["date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d") 
        
    # Extract year, month, week, and day from 'date'
    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    data["week"] = data["date"].dt.isocalendar().week
    data["day"] = data["date"].dt.day
    
    return data


def getBalance(data):    
    # Calculate total income, total expense, and savings
    current_balance = {
        "total_income": data["Income"].sum(),
        "total_expense": data["Expense"].sum(),
        "savings": data["Income"].sum() - data["Expense"].sum()
    }
    
    return current_balance["savings"]

# based
# def calculate_projected_expenses(df, n_months):
#     """Calculate moving average of expenses by category for the last 'n_months'."""
#     # Ensure 'date' is parsed as datetime (assuming df already has a 'date' column or using 'Date')
#     df['date'] = pd.to_datetime(df['date'])  
#     # Group by year-month
#     df['year_month'] = df['date'].dt.to_period('M')  

#     latest_month = df['year_month'].max()
#     cutoff_month = latest_month - n_months
#     last_n_months_data = df[df['year_month'] > cutoff_month]

#     projected_expenses = {}
#     for category in last_n_months_data['Category'].unique():
#         category_data = last_n_months_data[last_n_months_data['Category'] == category]
#         avg_expense = category_data['Expense'].mean()  # Simple moving average per transaction across months
#         projected_expenses[category] = avg_expense

#     total_projected = sum(projected_expenses.values())
#     return total_projected, projected_expenses

def calculate_projected_expenses(df, n_months):
    """
    Calculate projected expenses for the current month by:
    1. Summing expenses per category for each of the last 'n_months',
    2. Averaging these monthly totals per category,
    3. Summing across categories for the final projection.
    """
    # Parse dates and group by year-month
    df['date'] = pd.to_datetime(df['date'])
    df['year_month'] = df['date'].dt.to_period('M')

    # Filter last 'n_months' of data
    latest_month = df['year_month'].max()
    cutoff_month = latest_month - n_months
    last_n_months_data = df[df['year_month'] > cutoff_month]

    # Group by month and category, then sum expenses
    monthly_totals = (
        last_n_months_data
        .groupby(['year_month', 'Category'])['Expense']
        .sum()
        .reset_index()
    )

    # Average monthly totals per category
    projected_expenses = (
        monthly_totals
        .groupby('Category')['Expense']
        .mean()
        .to_dict()
    )

    total_projected = sum(projected_expenses.values())
    return total_projected, projected_expenses

# Helper function: Create a weekly savings chart.
def create_weekly_savings_chart(df, weeks_to_compare=2):
    # Ensure date is a datetime and create a savings column
    df['date'] = pd.to_datetime(df['date'])
    if 'savings' not in df.columns:
        df['savings'] = df['Income'] - df['Expense']
    today = datetime.now()
    # Define current week as from Monday to today.
    start_current_week = today - timedelta(days=today.weekday())
    current_week_df = df[(df['date'] >= start_current_week) & (df['date'] <= today)]
    # Sum savings per weekday (0=Mon, …, 6=Sun)
    current_week_daily = current_week_df.groupby(df['date'].dt.weekday)['savings'].sum()
    
    # For previous weeks: period = previous {weeks_to_compare} weeks before current week.
    start_prev_period = start_current_week - timedelta(days=weeks_to_compare*7)
    previous_weeks_df = df[(df['date'] >= start_prev_period) & (df['date'] < start_current_week)]
    # Average savings by weekday over previous weeks.
    prev_weekly = previous_weeks_df.groupby(previous_weeks_df['date'].dt.weekday)['savings'].mean()
    
    weekdays = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    data_chart = pd.DataFrame({
         "This Week": [current_week_daily.get(i, 0) for i in range(7)],
         "Previous Weeks": [prev_weekly.get(i, 0) for i in range(7)]
    }, index=weekdays)
    return data_chart

# Helper function: Create a monthly savings chart.
def create_monthly_savings_chart(df):
    df['date'] = pd.to_datetime(df['date'])
    if 'savings' not in df.columns:
        df['savings'] = df['Income'] - df['Expense']
    today = datetime.now()
    # Current month: from the 1st until today.
    start_current_month = today.replace(day=1)
    current_month_df = df[(df['date'] >= start_current_month) & (df['date'] <= today)]
    current_daily = current_month_df.groupby(current_month_df['date'].dt.day)['savings'].sum()
    
    # Last month calculation.
    if today.month == 1:
        last_month_year = today.year - 1
        last_month = 12
    else:
        last_month_year = today.year
        last_month = today.month - 1
    last_month_start = datetime(last_month_year, last_month, 1)
    last_month_days = pd.Period(f"{last_month_year}-{last_month}").days_in_month
    last_month_end = datetime(last_month_year, last_month, last_month_days)
    last_month_df = df[(df['date'] >= last_month_start) & (df['date'] <= last_month_end)]
    last_daily = last_month_df.groupby(last_month_df['date'].dt.day)['savings'].sum()
    
    # Build a DataFrame aligning day numbers.
    max_days = max(current_daily.index.max() if not current_daily.empty else 0,
                   last_daily.index.max() if not last_daily.empty else 0)
    days = list(range(1, max_days+1))
    current_list = [current_daily.get(day, 0) for day in days]
    last_list = [last_daily.get(day, 0) for day in days]
    avg_last = sum(last_list)/len(last_list) if last_list else 0
    data_chart = pd.DataFrame({
         "Current Month Savings": current_list,
         "Last Month Savings": last_list,
         "Avg Last Month": [avg_last]*len(days)
    }, index=days)
    return data_chart



def home():
    budget = st.number_input("Enter a budget for the month: ", key="budget")
    
    # Initialize session state for months selection if not already set
    if 'selected_months' not in st.session_state:
        st.session_state.selected_months = 1  # Default to 1 month

    with st.form("My Account", clear_on_submit=True):
        # Create three columns for metrics
        col1, col2, col3 = st.columns(3)
        
        # Load and process the data with your custom extractCal() function
        # (Ensure that extractCal returns a DataFrame with columns: 'date', 'Expense', 'Category')
        df = extractCal(data)  
        
        # Calculate total balance (make sure getBalance(df) is defined elsewhere)
        balance = round(getBalance(df), 2)
        col1.metric("Total Balance ($)", balance)
        
        # Dropdown to select time period for projection (1, 2, or 3 months)
        months = st.selectbox(
            "Select Time Period:", 
            [1, 2, 3], 
            index=[1, 2, 3].index(st.session_state.selected_months),
            format_func=lambda x: f"Past {x} Month(s)",
            key='months_selectbox'
        )
        
        # Update session state if selection changes
        if months != st.session_state.selected_months:
            st.session_state.selected_months = months
            try:
                st.rerun()
            except Exception:
                pass
        
        # Calculate projected expenses for next month based on past n months data
        total_projected, by_category = calculate_projected_expenses(df, st.session_state.selected_months)
        col2.metric(
            "Expected Expenses - This Month ($)", 
            round(total_projected, 2)
        )
        
        # Calculate available budget for current month:
        # Assume the user's available budget resets to $2000 at the start of each month.
        initial_budget = budget
        today = datetime.now()
        start_current_month = today.replace(day=1)
        # Filter for expenses incurred from the start of the month until today
        current_month_expenses = df[(df["date"] >= start_current_month) & (df["date"] <= today)]["Expense"].sum()
        available_budget = initial_budget - current_month_expenses
        col3.metric(
            "Available Budget This Month ($)",
            round(available_budget, 2)
        )
        
        # Dynamic category breakdown (auto-updates with dropdown)
        with st.expander(f"Category Breakdown (Past {st.session_state.selected_months} Month(s))"):
            st.subheader("Category Breakdown")
            for category, expense in by_category.items():
                st.write(f"**{category}**: ${round(expense, 2)}")
        
        st.form_submit_button("Refresh Data")
        
    # ========== EXPANDER: Detailed Savings Analysis ==========
    with st.expander("Detailed Savings Analysis", expanded=True):
        # --- Average Savings Last Month ---
        if today.month == 1:
            last_month_year = today.year - 1
            last_month = 12
        else:
            last_month_year = today.year
            last_month = today.month - 1
            
        last_month_start = datetime(last_month_year, last_month, 1)
        last_month_days = pd.Period(f"{last_month_year}-{last_month}").days_in_month
        last_month_end = datetime(last_month_year, last_month, last_month_days)
        
        # Ensure a savings column is available.
        df['savings'] = df['Income'] - df['Expense']
        last_month_data = df[(df['date'] >= last_month_start) & (df['date'] <= last_month_end)]
        daily_savings_last = last_month_data.groupby(last_month_data['date'].dt.day)['savings'].sum()
        avg_savings_last = daily_savings_last.mean() if not daily_savings_last.empty else 0
        st.write(f"**Average Daily Savings Last Month:** ${round(avg_savings_last, 2)}")
        
        # --- Savings: This Week vs. Previous Weeks (Line Chart) ---
        st.subheader("Savings: This Week vs. Previous Weeks")
        weekly_chart_data = create_weekly_savings_chart(df)
        st.line_chart(weekly_chart_data)
        
        # --- Current Month vs. Last Month (Line Chart) ---
        st.subheader("Savings: Current Month vs. Last Month")
        monthly_chart_data = create_monthly_savings_chart(df)
        st.line_chart(monthly_chart_data)

# Ensure that extractCal, getBalance, and data are defined or imported before calling home().







   
# def calculate_projected_expenses(df, n_months):
#     # Ensure 'date' is datetime and extract year-month
#     df['date'] = pd.to_datetime(df['date'])
#     df['year_month'] = df['date'].dt.to_period('M')  # Group by month
    
#     # Filter last 'n_months' of data
#     latest_month = df['year_month'].max()
#     cutoff_month = latest_month - n_months
#     last_n_months_data = df[df['year_month'] > cutoff_month]
    
#     # Group by Category and compute moving average
#     projected_expenses = {}
#     for category in last_n_months_data['Category'].unique():
#         category_data = last_n_months_data[last_n_months_data['Category'] == category]
#         avg_expense = category_data['Expense'].mean()  # Simple moving average
#         projected_expenses[category] = avg_expense
    
#     total_projected = sum(projected_expenses.values())
#     return total_projected, projected_expenses


# def home():
#     with st.form("My Account", clear_on_submit=True):
#         col1, col2 = st.columns(2)
        
#         df = extractCal(data)  # Your existing data loading function
#         balance = round(getBalance(df), 2)
        
#         col1.metric("Total Balance ($)", balance)
        
#         # Dropdown to select time period (1, 2, or 3 months)
#         months = st.selectbox(
#             "Select Time Period:", 
#             [1, 2, 3], 
#             format_func=lambda x: f"Past {x} Month(s)"
#         )
        
#         # Calculate projections
#         total_projected, by_category = calculate_projected_expenses(df, months)
        
        
#         if months:       
#             # Display total projected expenses in col2
#             col2.metric(
#                 "Expected Expenses for Next Month ($)", 
#                 round(total_projected, 2)
#             )
            
#             with st.expander("Category Breakdown of Projected Expenses"):
#                 # Display category breakdown
#                 st.subheader("Category Breakdown")
#                 for category, expense in by_category.items():
#                     st.write(f"**{category}**: ${round(expense, 2)}")
            
#             st.form_submit_button("submit")
        
        
        
    




# # MongoDB Setup with proper Server API
# uri = "mongodb+srv://Sal-Fakoya:lvrUjuFRkPLEHlhL@cluster0.56ongae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# try:
#     client = MongoClient(uri, server_api=ServerApi('1'))
#     # Verify connection works
#     client.admin.command('ping')
#     st.success("Connected to MongoDB!")
# except Exception as e:
#     st.error(f"Could not connect to MongoDB: {e}")
#     st.stop()

# # Database and collections
# db = client["user_financial_data"]
# users_collection = db["users"]

# def validate_user(first_name, last_name, plain_password):
#     try:
#         # Case-insensitive search
#         user = users_collection.find_one({
#             "first_name": {"$regex": f'^{first_name}$', "$options": "i"},
#             "last_name": {"$regex": f'^{last_name}$', "$options": "i"}
#         })
        
#         if not user:
#             st.error("User not found")
#             return None
            
#         if "password_hash" not in user:
#             st.error("Invalid user record - missing password hash")
#             return None
            
#         # Verify password
#         if bcrypt.checkpw(plain_password.encode('utf-8'), user["password_hash"].encode('utf-8')):
#             return user
#         else:
#             st.error("Incorrect password")
#             return None
            
#     except Exception as e:
#         st.error(f"Authentication error: {str(e)}")
#         return None

# def sign_in_page():
#     st.title("User Sign-In")
    
#     with st.form(key="sign_in_form"):
#         first_name = st.text_input("First Name").strip()
#         last_name = st.text_input("Last Name").strip()
#         password = st.text_input("Password", type="password").strip()
#         submit_button = st.form_submit_button("Sign In")
    
#     if submit_button:
#         if not all([first_name, last_name, password]):
#             st.error("Please fill all fields!")
#             return
            
#         with st.spinner("Authenticating..."):
#             user = validate_user(first_name, last_name, password)
            
#         if user:
#             st.success(f"Welcome {user['first_name']} {user['last_name']}!")
#             st.session_state.user = user
#             st.json({
#                 "User ID": user.get("unique_id"),
#                 "Name": f"{user.get('first_name')} {user.get('last_name')}",
#                 "Account Created": user.get("created_at", "Unknown date")
#             })

# def home():
#     if 'user' not in st.session_state:
#         sign_in_page()
#     else:
#         st.write(f"Welcome back, {st.session_state.user['first_name']}!")

