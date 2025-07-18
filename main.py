import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re

# Paths
DATA_FILE = "donations.csv"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Create CSV if not exists
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["ID", "Name", "Contact", "Email", "Address", "Category", "Clothes", "Quantity", "Status", "Date", "Notes"])
    df.to_csv(DATA_FILE, index=False)

# Validation helpers
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def validate_phone(phone):
    pattern = r'^[\+]?[0-9\s\-]{7,15}$'
    return re.match(pattern, phone)

def get_next_id():
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        return "1"
    return str(int(df["ID"].iloc[-1]) + 1)

# UI
st.set_page_config(page_title="Clothes Donation App")
menu = st.sidebar.radio("Navigate", ["Donate", "Admin Panel"])

# --- DONATION FORM ---
if menu == "Donate":
    st.title("👕 Donate Clothes")

    with st.form("donation_form"):
        name = st.text_input("Name")
        contact = st.text_input("Contact")
        email = st.text_input("Email")
        address = st.text_area("Address")
        category = st.selectbox("Clothing Category", ['Shirts', 'Pants', 'Dresses', 'Shoes', 'Jackets', 'Accessories', 'Undergarments', 'Other'])
        clothes = st.text_area("Clothes Description")
        quantity = st.number_input("Quantity", min_value=1, step=1)

        submit = st.form_submit_button("Submit")

        if submit:
            errors = []
            if not name: errors.append("Name is required.")
            if not contact or not validate_phone(contact): errors.append("Valid contact required.")
            if not email or not validate_email(email): errors.append("Valid email required.")
            if not address: errors.append("Address required.")
            if not clothes: errors.append("Clothes description required.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                donation_id = get_next_id()
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_entry = pd.DataFrame([[donation_id, name, contact, email, address, category, clothes, quantity, "Received", date, ""]],
                                         columns=["ID", "Name", "Contact", "Email", "Address", "Category", "Clothes", "Quantity", "Status", "Date", "Notes"])
                new_entry.to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.success(f"Thank you for your donation! Your donation ID is {donation_id}.")

# --- ADMIN PANEL ---
elif menu == "Admin Panel":
    st.title("🔐 Admin Panel")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.form("login_form"):
            username = st.text_input("Admin ID")
            password = st.text_input("Password", type="password")
            login = st.form_submit_button("Login")

            if login:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.success("Logged in successfully.")
                else:
                    st.error("Invalid credentials.")
    else:
        df = pd.read_csv(DATA_FILE)
        st.subheader("📊 All Donations")

        # Filters
        status_filter = st.selectbox("Filter by status", ["All"] + df["Status"].unique().tolist())
        if status_filter != "All":
            df = df[df["Status"] == status_filter]

        st.dataframe(df)

        # Export
        st.download_button("📥 Download Excel", data=df.to_excel(index=False), file_name="donations.xlsx")

        # Logout
        if st.button("Logout"):
            st.session_state.logged_in = False
