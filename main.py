import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ------------------- Setup -------------------
st.set_page_config(page_title="Clothes Donation Portal", layout="centered")

DATA_FILE = 'data/donations.csv'
os.makedirs('data', exist_ok=True)

if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        'ID', 'Name', 'Contact', 'Email', 'Address',
        'Category', 'Clothes Description', 'Quantity',
        'Status', 'Date', 'Notes'
    ])
    df_init.to_csv(DATA_FILE, index=False)

# ------------------- Utility Functions -------------------
def get_next_id():
    df = pd.read_csv(DATA_FILE)
    return str(df['ID'].astype(int).max() + 1) if not df.empty else '1'

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(new_row):
    df = load_data()
    df.loc[len(df)] = new_row
    df.to_csv(DATA_FILE, index=False)

def apply_background():
    st.markdown("""
        <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .stTextInput > div > input,
        .stTextArea > div > textarea,
        .stSelectbox > div > div {
            background-color: white !important;
            color: black !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px 16px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_background()

# ------------------- Pages -------------------
st.title("🤝 Clothes Donation Portal")
st.subheader("Help those in need by donating your unused clothes")

menu = st.sidebar.radio("Navigate", ["Home", "Admin Panel", "Dashboard"])

# ------------------- Home Form -------------------
if menu == "Home":
    st.header("🎁 Submit Your Donation")

    with st.form("donation_form"):
        name = st.text_input("Full Name *")
        contact = st.text_input("Phone Number *")
        email = st.text_input("Email *")
        address = st.text_area("Pickup Address *")
        category = st.selectbox("Clothing Category *", 
                                ["Shirts", "Pants", "Dresses", "Shoes", "Jackets", "Accessories", "Undergarments", "Other"])
        quantity = st.number_input("Quantity *", min_value=1, value=1)
        clothes = st.text_area("Description")
        submitted = st.form_submit_button("Submit Donation")

        if submitted:
            if not name or not contact or not email or not address:
                st.error("Please fill all required fields marked with *")
            else:
                donation_id = get_next_id()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_data([
                    donation_id, name, contact, email, address,
                    category, clothes, quantity, 'Received', timestamp, ''
                ])
                st.success(f"✅ Thank you {name}! Your donation ID is {donation_id}")

# ------------------- Admin Panel -------------------
elif menu == "Admin Panel":
    st.header("👨‍💼 Admin Panel")

    password = st.text_input("Enter Admin Password", type='password')
    if password != 'admin123':
        st.warning("🔐 Enter correct password to access admin panel.")
        st.stop()

    df = load_data()
    st.success("🔓 Access granted!")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + df['Status'].unique().tolist())
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All"] + df['Category'].unique().tolist())

    if status_filter != "All":
        df = df[df['Status'] == status_filter]
    if category_filter != "All":
        df = df[df['Category'] == category_filter]

    st.dataframe(df, use_container_width=True)

    st.download_button("📥 Download Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="donations.csv")

# ------------------- Dashboard -------------------
elif menu == "Dashboard":
    st.header("📊 Donation Statistics")

    df = load_data()
    st.info(f"📦 Total Donations: {len(df)}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Distributed", len(df[df['Status'] == 'Distributed']))
    col2.metric("Received", len(df[df['Status'] == 'Received']))
    col3.metric("Processing", len(df[df['Status'] == 'Processing']))

    st.bar_chart(df['Category'].value_counts())
