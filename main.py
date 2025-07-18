from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, jsonify
import csv
import os
import pandas as pd
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATA_FILE = 'data/donations.csv'
STATS_FILE = 'data/stats.csv'

# Clothing categories
CATEGORIES = ['Shirts', 'Pants', 'Dresses', 'Shoes', 'Jackets', 'Accessories', 'Undergarments', 'Other']
STATUSES = ['Received', 'Processing', 'Distributed', 'Pending']

os.makedirs('data', exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Name', 'Contact', 'Email', 'Address', 'Category', 'Clothes Description', 'Quantity', 'Status', 'Date', 'Notes'])

if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Total_Donations', 'Items_Distributed'])

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[\+]?[1-9][\d]{0,15}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def get_next_id():
    try:
        with open(DATA_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            rows = list(reader)
            if rows:
                return str(int(rows[-1][0]) + 1)
            return "1"
    except:
        return "1"

def send_confirmation_email(name, email, donation_id):
    try:
        # This is a placeholder - you'd need to configure SMTP settings
        msg = MIMEMultipart()
        msg['From'] = "donations@yourorg.com"
        msg['To'] = email
        msg['Subject'] = f"Donation Confirmation - ID: {donation_id}"
        
        body = f"""
        Dear {name},
        
        Thank you for your generous donation! Your donation has been recorded with ID: {donation_id}.
        
        We will process your donation and contact you for pickup arrangements.
        
        Best regards,
        Clothes Donation Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        return True
    except:
        return False

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        category = request.form.get('category', '')
        clothes = request.form.get('clothes', '').strip()
        quantity = request.form.get('quantity', '1')
        
        # Validation
        errors = []
        if not name:
            errors.append("Name is required")
        if not contact or not validate_phone(contact):
            errors.append("Valid contact number is required")
        if not email or not validate_email(email):
            errors.append("Valid email is required")
        if not address:
            errors.append("Address is required")
        if not quantity.isdigit() or int(quantity) < 1:
            errors.append("Valid quantity is required")
            
        if errors:
            return render_template('index.html', errors=errors, categories=CATEGORIES, 
                                 form_data=request.form)
        
        donation_id = get_next_id()
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(DATA_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([donation_id, name, contact, email, address, category, 
                           clothes, quantity, 'Received', current_date, ''])
        
        # Send confirmation email
        send_confirmation_email(name, email, donation_id)
        
        return render_template('success.html', name=name, donation_id=donation_id)

    return render_template('index.html', categories=CATEGORIES)

@app.route('/admin')
def admin():
    # Check if user is authenticated with session
    if not session.get('authenticated'):
        return render_template('login.html')
    
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    
    donations = []
    with open(DATA_FILE, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if len(row) >= 11:  # Ensure row has all columns
                # Apply filters
                if search_query and search_query.lower() not in ' '.join(row).lower():
                    continue
                if status_filter and row[8] != status_filter:
                    continue
                if category_filter and row[5] != category_filter:
                    continue
                donations.append(row)
    
    # Calculate statistics
    total_donations = len(donations)
    distributed_count = sum(1 for d in donations if d[8] == 'Distributed')
    pending_count = sum(1 for d in donations if d[8] in ['Received', 'Processing'])
    
    stats = {
        'total_donations': total_donations,
        'distributed': distributed_count,
        'pending': pending_count,
        'categories': {}
    }
    
    for donation in donations:
        category = donation[5]
        stats['categories'][category] = stats['categories'].get(category, 0) + 1
    
    return render_template('admin.html', donations=donations, stats=stats,
                         categories=CATEGORIES, statuses=STATUSES,
                         search_query=search_query, status_filter=status_filter,
                         category_filter=category_filter)

@app.route('/update_status', methods=['POST'])
def update_status():
    donation_id = request.form.get('donation_id')
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    # Read all donations
    donations = []
    with open(DATA_FILE, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        donations = [header] + list(reader)
    
    # Update the specific donation
    for i, row in enumerate(donations[1:], 1):
        if row[0] == donation_id:
            donations[i][8] = new_status  # Status column
            donations[i][10] = notes  # Notes column
            break
    
    # Write back to file
    with open(DATA_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(donations)
    
    return redirect(url_for('admin'))

@app.route('/delete_donation', methods=['POST'])
def delete_donation():
    donation_id = request.form.get('donation_id')
    
    # Read all donations except the one to delete
    donations = []
    with open(DATA_FILE, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        donations = [header]
        for row in reader:
            if row[0] != donation_id:
                donations.append(row)
    
    # Write back to file
    with open(DATA_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(donations)
    
    return redirect(url_for('admin'))

@app.route('/export')
def export_excel():
    try:
        df = pd.read_csv(DATA_FILE)
        excel_file = 'data/donations.xlsx'
        df.to_excel(excel_file, index=False)
        return send_file(excel_file, as_attachment=True)
    except Exception as e:
        return f"<h3>Error exporting to Excel: {e}</h3>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin_id = request.form.get('admin_id', '').strip()
        password = request.form.get('password', '').strip()
        
        # Simple authentication - you can change these credentials
        if admin_id == 'admin' and password == 'admin123':
            session['authenticated'] = True
            session['admin_id'] = admin_id
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    # Check if user is authenticated with session
    if not session.get('authenticated'):
        return render_template('login.html')
    
    donations = []
    with open(DATA_FILE, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            # Only include rows with sufficient columns
            if len(row) >= 11:
                donations.append(row)
    
    # Calculate detailed statistics with safe data access
    total_items = 0
    for d in donations:
        try:
            if len(d) > 7 and d[7].isdigit():
                total_items += int(d[7])
        except (IndexError, ValueError):
            continue
    
    stats = {
        'total_donations': len(donations),
        'total_items': total_items,
        'distributed': len([d for d in donations if len(d) > 8 and d[8] == 'Distributed']),
        'pending': len([d for d in donations if len(d) > 8 and d[8] in ['Received', 'Processing']]),
        'categories': {},
        'monthly_data': {},
        'status_breakdown': {
            'Received': 0,
            'Processing': 0,
            'Distributed': 0,
            'Pending': 0
        }
    }
    
    for donation in donations:
        try:
            # Category stats
            if len(donation) > 5:
                category = donation[5]
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Status breakdown
            if len(donation) > 8:
                status = donation[8]
                if status in stats['status_breakdown']:
                    stats['status_breakdown'][status] += 1
            
            # Monthly stats
            if len(donation) > 9:
                try:
                    date_str = donation[9].split()[0]
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    month_key = date.strftime("%B %Y")
                    stats['monthly_data'][month_key] = stats['monthly_data'].get(month_key, 0) + 1
                except (ValueError, IndexError):
                    pass
        except (IndexError, ValueError):
            continue
    
    # Sort monthly data by date
    sorted_monthly = dict(sorted(stats['monthly_data'].items(), 
                                key=lambda x: datetime.strptime(x[0], "%B %Y")))
    stats['monthly_data'] = sorted_monthly
    
    return render_template('dashboard.html', stats=stats)

@app.route('/api/stats')
def api_stats():
    donations = []
    with open(DATA_FILE, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        donations = list(reader)
    
    # Filter out incomplete rows
    valid_donations = [d for d in donations if len(d) >= 11]
    
    stats = {
        'total': len(valid_donations),
        'distributed': len([d for d in valid_donations if d[8] == 'Distributed']),
        'pending': len([d for d in valid_donations if d[8] in ['Received', 'Processing']])
    }
    
    return jsonify(stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

