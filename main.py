import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

# Constants
DATA_FILE = "donations.csv"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
STATUS_OPTIONS = ["Received", "Processing", "Distributed"]

# Ensure CSV exists
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["ID", "Name", "Contact", "Email", "Address", "Category", "Clothes", "Quantity", "Status", "Date", "Notes"]).to_csv(DATA_FILE, index=False)

# Utility
def get_next_id():
    try:
        df = pd.read_csv(DATA_FILE)
        return str(int(df["ID"].iloc[-1]) + 1) if not df.empty else "1"
    except:
        return "1"

# Set Page Theme
st.set_page_config(page_title="Clothes Donation", page_icon="🧥", layout="centered")

# Custom Style (colors, font)
st.markdown("""
    <style>
    .main {background-color: #f9f9f9;}
    h1, h2, h3 {color: #205375;}
    .stButton>button {
        background-color: #205375;
        color: white;
        border-radius: 5px;
        font-weight: bold;
    }
    .stDownloadButton>button {
        background-color: #28a745;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("☁️ Clothes Donation")
menu = st.sidebar.radio("📂 Navigate", ["👕 Donate Clothes", "🔐 Admin Panel"])

# --------------------------------------------
# 👕 Donation Form
# --------------------------------------------
if menu == "👕 Donate Clothes":
    st.title("👕 Donate Your Clothes")
    st.markdown("#### Help those in need by donating gently used clothes.")

    with st.form("donation_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("👤 Full Name")
        contact = col2.text_input("📞 Phone Number")
        email = col1.text_input("📧 Email")
        address = col2.text_area("🏠 Pickup Address")

        category = st.selectbox("🧷 Category", ["Shirts", "Pants", "Dresses", "Shoes", "Jackets", "Accessories", "Undergarments", "Other"])
        clothes = st.text_input("📦 Clothes Description")
        quantity = st.slider("🎁 Quantity", min_value=1, max_value=20, value=1)

        submitted = st.form_submit_button("✅ Submit Donation")

        if submitted:
            if name and contact and email and address and clothes:
                donation_id = get_next_id()
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_data = pd.DataFrame([[donation_id, name, contact, email, address, category, clothes, quantity, "Received", date, ""]],
                                        columns=["ID", "Name", "Contact", "Email", "Address", "Category", "Clothes", "Quantity", "Status", "Date", "Notes"])
                new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.success(f"🎉 Thank you, **{name}**! Your donation (ID: `{donation_id}`) has been recorded.")
            else:
                st.error("❌ Please fill in **all fields**.")

# --------------------------------------------
# 🔐 Admin Panel
# --------------------------------------------
elif menu == "🔐 Admin Panel":
    st.title("🔐 Admin Panel")
    st.markdown("Manage donations submitted by users.")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.form("login_form"):
            username = st.text_input("🆔 Admin Username")
            password = st.text_input("🔒 Password", type="password")
            login = st.form_submit_button("🚪 Login")

            if login:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.success("✅ Logged in successfully.")
                else:
                    st.error("❌ Invalid credentials.")
    else:
        try:
            df = pd.read_csv(DATA_FILE)

            st.markdown("### 📋 All Submissions")

            # Filter section
            with st.expander("🔍 Filter Options"):
                status_filter = st.selectbox("Filter by status", ["All"] + df["Status"].unique().tolist())
                if status_filter != "All":
                    df = df[df["Status"] == status_filter]

            st.dataframe(df, use_container_width=True)

            # 📥 Excel export
            with io.BytesIO() as buffer:
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                buffer.seek(0)
                st.download_button("📥 Download Excel", data=buffer, file_name="donations.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            if st.button("🔓 Logout"):
                st.session_state.logged_in = False
                st.success("You have been logged out.")

        except Exception as e:
            st.error(f"⚠️ Error loading data: {e}")
