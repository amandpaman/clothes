import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File path
DATA_FILE = 'data/donations.csv'
ADMIN_ID = 'admin'
ADMIN_PASSWORD = 'admin123'

# Ensure data folder and CSV exists
os.makedirs('data', exist_ok=True)
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        'ID', 'Name', 'Contact', 'Email', 'Address',
        'Category', 'Clothes Description', 'Quantity',
        'Status', 'Date', 'Notes'
    ])
    df.to_csv(DATA_FILE, index=False)

# Styling
st.set_page_config(page_title="Clothes Donation Portal", layout="centered")
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #667eea, #764ba2);
        }
        .main {
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .stTextInput>div>div>input {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 10px;
        }
        .stTextArea>div>textarea {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Categories
CATEGORIES = ['Shirts', 'Pants', 'Dresses', 'Shoes', 'Jackets', 'Accessories', 'Undergarments', 'Other']
STATUSES = ['Received', 'Processing', 'Distributed', 'Pending']

# Title
st.markdown("<h1 style='text-align:center; color:white;'>🤝 Clothes Donation Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white;'>Help those in need by donating your unused clothes</p>", unsafe_allow_html=True)

# Navigation
menu = st.sidebar.selectbox("Navigate", ["🏠 Home", "👨‍💼 Admin Panel", "📊 Dashboard"])

# Home - Donation form
if menu == "🏠 Home":
    st.subheader("🎁 Submit Your Donation")

    with st.form("donation_form"):
        name = st.text_input("Full Name *")
        contact = st.text_input("Phone Number *")
        email = st.text_input("Email Address *")
        address = st.text_area("Pickup Address *")
        category = st.selectbox("Clothing Category *", ["Select"] + CATEGORIES)
        quantity = st.number_input("Estimated Quantity", min_value=1, value=1)
        clothes_desc = st.text_area("Clothes Description (brand, size, condition...)")

        submitted = st.form_submit_button("📨 Submit")

        if submitted:
            errors = []
            if not name:
                errors.append("Name is required.")
            if not contact or len(contact) < 10:
                errors.append("Valid phone number is required.")
            if not email or "@" not in email:
                errors.append("Valid email is required.")
            if not address:
                errors.append("Address is required.")
            if category == "Select":
                errors.append("Select a valid category.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    df = pd.read_csv(DATA_FILE)
                    next_id = int(df['ID'].max()) + 1 if not df.empty else 1
                except:
                    next_id = 1

                new_data = {
                    'ID': next_id,
                    'Name': name,
                    'Contact': contact,
                    'Email': email,
                    'Address': address,
                    'Category': category,
                    'Clothes Description': clothes_desc,
                    'Quantity': quantity,
                    'Status': 'Received',
                    'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Notes': ''
                }

                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)

                st.success(f"✅ Thank you {name}! Your donation ID is {next_id}.")

# Admin Panel
elif menu == "👨‍💼 Admin Panel":
    st.subheader("🔐 Admin Login")

    login_id = st.text_input("Admin ID")
    login_pass = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_id == ADMIN_ID and login_pass == ADMIN_PASSWORD:
            st.success("Logged in successfully!")

            df = pd.read_csv(DATA_FILE)

            st.markdown("### 📋 All Donations")
            status_filter = st.selectbox("Filter by status", ["All"] + STATUSES)
            category_filter = st.selectbox("Filter by category", ["All"] + CATEGORIES)

            if status_filter != "All":
                df = df[df['Status'] == status_filter]
            if category_filter != "All":
                df = df[df['Category'] == category_filter]

            st.dataframe(df, use_container_width=True)

            # Export option
            if not df.empty:
                excel_file = 'data/exported_donations.xlsx'
                df.to_excel(excel_file, index=False)
                with open(excel_file, 'rb') as f:
                    st.download_button("📥 Download Excel", f, file_name="donations.xlsx")

        else:
            st.error("Invalid admin credentials.")

# Dashboard
elif menu == "📊 Dashboard":
    st.subheader("📈 Donation Statistics")

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        st.info("No donations submitted yet.")
    else:
        total_donations = len(df)
        total_items = df['Quantity'].astype(int).sum()
        distributed = len(df[df['Status'] == 'Distributed'])
        pending = len(df[df['Status'].isin(['Received', 'Processing'])])

        st.metric("Total Donations", total_donations)
        st.metric("Total Items", total_items)
        st.metric("Distributed", distributed)
        st.metric("Pending", pending)

        st.bar_chart(df['Category'].value_counts())
