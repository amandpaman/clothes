import streamlit as st
import pandas as pd
import os
from datetime import datetime
import uuid

# ---------- Config ----------
st.set_page_config(page_title="Clothes Donation", layout="centered")
DATA_FILE = "data/donations.csv"

# ---------- Ensure CSV Exists ----------
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        f.write("ID,Name,Contact,Email,Address,Category,Clothes Description,Quantity,Status,Date,Notes\n")

# ---------- Functions ----------
def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(new_entry):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def get_stats(df):
    return {
        "total": len(df),
        "distributed": len(df[df["Status"] == "Distributed"]),
        "pending": len(df[df["Status"].isin(["Received", "Processing"])])
    }

# ---------- CSS Styling ----------
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #667eea, #764ba2);
}
section.main > div {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}
h1, h2, h3, label {
    color: #333;
}
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #667eea, #764ba2);
    color: white;
}
.stButton button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border-radius: 8px;
}
.stTextInput, .stSelectbox, .stNumberInput, .stTextArea {
    background-color: #f0f0f5;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.title("👕 Clothes Donation")
nav = st.sidebar.radio("Go to", ["Submit Donation", "Admin Panel", "Download Data"])

# ---------- Page 1: Submit Donation ----------
if nav == "Submit Donation":
    st.title("🤝 Donate Clothes")

    df = load_data()
    stats = get_stats(df)
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.2); padding:15px; border-radius:10px; color:white; text-align:center;'>
        <h3>📊 Live Stats</h3>
        <p>Total Donations: <b>{stats['total']}</b> | Distributed: <b>{stats['distributed']}</b> | Pending: <b>{stats['pending']}</b></p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    with st.form("donation_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
        with col2:
            contact = st.text_input("Phone Number *")

        email = st.text_input("Email *")
        address = st.text_area("Pickup Address *")
        col3, col4 = st.columns(2)
        with col3:
            category = st.selectbox("Clothing Category", ["Shirts", "Pants", "Dresses", "Shoes", "Jackets", "Accessories", "Undergarments", "Other"])
        with col4:
            quantity = st.number_input("Estimated Quantity", min_value=1, step=1, value=1)

        clothes = st.text_area("Clothes Description")
        submitted = st.form_submit_button("🎁 Submit Donation")

        if submitted:
            if not name or not contact or not email or not address:
                st.error("Please fill all required fields.")
            else:
                donation_id = str(uuid.uuid4())[:8]
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_entry = {
                    "ID": donation_id,
                    "Name": name,
                    "Contact": contact,
                    "Email": email,
                    "Address": address,
                    "Category": category,
                    "Clothes Description": clothes,
                    "Quantity": quantity,
                    "Status": "Received",
                    "Date": now,
                    "Notes": ""
                }
                save_data(new_entry)
                st.success(f"Thank you, {name}! Your donation has been recorded with ID: {donation_id}.")

# ---------- Page 2: Admin Panel ----------
elif nav == "Admin Panel":
    st.title("👨‍💼 Admin Panel")

    password = st.text_input("Admin Password", type="password")
    if password == "admin123":
        df = load_data()

        st.subheader("Filter Donations")
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["", "Received", "Processing", "Distributed", "Pending"])
        with col2:
            category_filter = st.selectbox("Filter by Category", [""] + df["Category"].unique().tolist())

        filtered = df.copy()
        if status_filter:
            filtered = filtered[filtered["Status"] == status_filter]
        if category_filter:
            filtered = filtered[filtered["Category"] == category_filter]

        st.dataframe(filtered, use_container_width=True)

        st.info(f"Showing {len(filtered)} records.")
    else:
        if password:
            st.error("Incorrect password.")

# ---------- Page 3: Export ----------
elif nav == "Download Data":
    df = load_data()
    st.title("📥 Export Donation Data")
    st.download_button("Download as Excel", df.to_csv(index=False).encode('utf-8'), "donations.csv", "text/csv")
