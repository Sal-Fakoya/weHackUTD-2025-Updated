import streamlit as st
# from pymongo import MongoClient
# from pymongo.server_api import ServerApi
# import bcrypt
from datetime import datetime


from home import *

# # --- MongoDB Setup ---
# uri = "mongodb+srv://Sal-Fakoya:lvrUjuFRkPLEHlhL@cluster0.56ongae.mongodb.net/?appName=Cluster0"

# # Create a new client and connect to the server
# try:
#     client = MongoClient(uri, server_api=ServerApi('1'))
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     st.error("Failed to connect to MongoDB!")
#     print(f"Failed to connect to MongoDB: {e}")

# # Connect to databases and collections
# db = client["db1"]
# users = db["users"]
# api_data = db["api_data"]

# # --- Helper Functions ---

# # User Registration
# def register_user(username, email, password):
#     if users.find_one({"email": email}):
#         return False, "User already exists!"
    
#     # Hash the password
#     hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#     user_doc = {
#         "username": username,
#         "email": email,
#         "password_hash": hashed,
#         "created_at": datetime.now(),
#         "last_login": None
#     }
#     users.insert_one(user_doc)
#     return True, "User registered successfully!"

# # User Login
# def login_user(email, password):
#     user = users.find_one({"email": email})
#     if not user:
#         return False, "User not found!"

#     if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
#         users.update_one({"email": email}, {"$set": {"last_login": datetime.utcnow()}})
#         return True, "Login successful!"
#     else:
#         return False, "Incorrect password!"

# # Fetch and Store API Data
# def fetch_and_store_api_data():
#     # Dummy data – replace this with a real API call
#     response = {
#         "location": "New York",
#         "temperature": 18,
#         "condition": "Partly Cloudy"
#     }

#     data_doc = {
#         "source": "mock_weather_api",
#         "fetched_at": datetime.utcnow(),
#         "data": response
#     }
#     api_data.insert_one(data_doc)
#     return response

# # --- Streamlit UI Components ---

   

# Menu Function
def select_menu():
    menu = ["Home"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        home()
    elif choice == "About":
        about()

# --- Main Application ---
def main():
    # st.set_page_config(page_title="FinClo", layout="centered")
    select_menu()

# Run the app
if __name__ == "__main__":
    main()