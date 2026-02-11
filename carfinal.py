"""
=================================================================
GLOBAL CAR PRICE PREDICTION SYSTEM WITH LOGIN & USER MANAGEMENT
Login System + Admin Panel (Create/Edit/Delete Users) + Full Dashboard
=================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from datetime import datetime
import io
import hashlib
import sqlite3
import time

# ============================================================================
# DATABASE INITIALIZATION & USER MANAGEMENT
# ============================================================================

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  email TEXT,
                  full_name TEXT,
                  phone TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_login TIMESTAMP,
                  is_active BOOLEAN DEFAULT 1,
                  role TEXT DEFAULT 'user')''')
    
    # Predictions history table
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  brand TEXT,
                  model TEXT,
                  year INTEGER,
                  predicted_price INTEGER,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  logout_time TIMESTAMP,
                  is_active BOOLEAN DEFAULT 1,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Create default admin
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("""INSERT INTO users (username, password_hash, email, full_name, role) 
                     VALUES (?, ?, ?, ?, ?)""",
                  ('admin', admin_password, 'admin@carprice.com', 'System Administrator', 'admin'))
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    """Verify and login user"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        c.execute("""SELECT id, username, role, is_active, email, full_name 
                     FROM users WHERE username = ? AND password_hash = ?""",
                  (username, password_hash))
        
        user = c.fetchone()
        
        if user and user[3]:
            user_id = user[0]
            c.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now(), user_id))
            c.execute("UPDATE sessions SET is_active = 0 WHERE user_id = ? AND is_active = 1", (user_id,))
            c.execute("INSERT INTO sessions (user_id, login_time, is_active) VALUES (?, ?, ?)",
                      (user_id, datetime.now(), 1))
            conn.commit()
            conn.close()
            
            return {
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'is_active': user[3],
                'email': user[4] or '',
                'full_name': user[5] or username
            }
        
        conn.close()
        return None
    except:
        conn.close()
        return None

def create_user(username, password, email, full_name, phone, role='user'):
    """Create new user"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    try:
        password_hash = hash_password(password)
        c.execute("""INSERT INTO users (username, password_hash, email, full_name, phone, role) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (username, password_hash, email, full_name, phone, role))
        conn.commit()
        conn.close()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists"
    except Exception as e:
        conn.close()
        return False, str(e)

def update_user(user_id, username, email, full_name, phone, is_active, password=None):
    """Update user"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    try:
        if password:
            password_hash = hash_password(password)
            c.execute("""UPDATE users 
                         SET username = ?, email = ?, full_name = ?, phone = ?, 
                             is_active = ?, password_hash = ?
                         WHERE id = ?""",
                      (username, email, full_name, phone, is_active, password_hash, user_id))
        else:
            c.execute("""UPDATE users 
                         SET username = ?, email = ?, full_name = ?, phone = ?, is_active = ?
                         WHERE id = ?""",
                      (username, email, full_name, phone, is_active, user_id))
        conn.commit()
        conn.close()
        return True, "User updated successfully"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists"
    except Exception as e:
        conn.close()
        return False, str(e)

def delete_user(user_id):
    """Delete user"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True, "User deleted successfully"
    except Exception as e:
        conn.close()
        return False, str(e)

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("""SELECT id, username, email, full_name, phone, is_active, role, created_at, last_login
                 FROM users WHERE id = ?""", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    """Get all users"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("""SELECT id, username, email, full_name, phone, created_at, last_login, is_active, role 
                 FROM users ORDER BY created_at DESC""")
    users = c.fetchall()
    conn.close()
    return users

def get_currently_logged_in_users():
    """Get active users"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.username, u.email, u.full_name, s.login_time, u.role
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.is_active = 1
        ORDER BY s.login_time DESC
    """)
    users = c.fetchall()
    conn.close()
    return users

def logout_user(user_id):
    """Logout user"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE sessions SET is_active = 0, logout_time = ? WHERE user_id = ? AND is_active = 1",
              (datetime.now(), user_id))
    conn.commit()
    conn.close()

def save_prediction(user_id, brand, model, year, predicted_price):
    """Save prediction to history"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("""INSERT INTO predictions (user_id, brand, model, year, predicted_price) 
                 VALUES (?, ?, ?, ?, ?)""",
              (user_id, brand, model, year, predicted_price))
    conn.commit()
    conn.close()

def get_user_predictions(user_id):
    """Get user's prediction history"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("""SELECT brand, model, year, predicted_price, timestamp 
                 FROM predictions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20""",
              (user_id,))
    predictions = c.fetchall()
    conn.close()
    return predictions

def get_user_stats(user_id):
    """Get user statistics"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (user_id,))
    total_predictions = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM sessions WHERE user_id = ?", (user_id,))
    total_logins = c.fetchone()[0]
    conn.close()
    return {'total_predictions': total_predictions, 'total_logins': total_logins}

def get_system_stats():
    """Get system stats"""
    conn = sqlite3.connect('car_price_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM sessions WHERE is_active = 1")
    currently_online = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM sessions WHERE DATE(login_time) = DATE('now')")
    today_logins = c.fetchone()[0]
    conn.close()
    return {
        'total_users': total_users,
        'currently_online': currently_online,
        'total_predictions': total_predictions,
        'today_logins': today_logins
    }

# ============================================================================
# CAR DATABASE - COMPREHENSIVE GLOBAL DATABASE
# ============================================================================

CAR_DATABASE = {
    'Maruti Suzuki': {
        'models': ['Alto', 'Swift', 'Baleno', 'Dzire', 'Ertiga', 'Vitara Brezza', 'Wagon R', 'Celerio'],
        'base_prices': [300000, 800000, 900000, 850000, 1100000, 1000000, 600000, 550000]
    },
    'Tata': {
        'models': ['Tiago', 'Tigor', 'Altroz', 'Nexon', 'Punch', 'Harrier', 'Safari', 'Nexon EV'],
        'base_prices': [450000, 550000, 700000, 950000, 650000, 1800000, 2000000, 1600000]
    },
    'Mahindra': {
        'models': ['Bolero', 'Scorpio', 'XUV300', 'XUV700', 'Thar', 'Marazzo', 'Scorpio N'],
        'base_prices': [850000, 1500000, 1100000, 1600000, 1500000, 1200000, 1700000]
    },
    'Toyota': {
        'models': ['Innova Crysta', 'Fortuner', 'Glanza', 'Urban Cruiser', 'Camry', 'Vellfire'],
        'base_prices': [2000000, 3500000, 750000, 1200000, 4500000, 9000000]
    },
    'Honda': {
        'models': ['Amaze', 'City', 'Jazz', 'WR-V', 'Elevate', 'Civic', 'CR-V'],
        'base_prices': [750000, 1200000, 850000, 950000, 1200000, 2000000, 3200000]
    },
    'Hyundai': {
        'models': ['i10', 'i20', 'Verna', 'Creta', 'Venue', 'Alcazar', 'Tucson'],
        'base_prices': [500000, 700000, 1100000, 1400000, 950000, 2000000, 2800000]
    },
    'Kia': {
        'models': ['Seltos', 'Sonet', 'Carens', 'Carnival', 'EV6'],
        'base_prices': [1200000, 850000, 1300000, 3300000, 6500000]
    },
    'BMW': {
        'models': ['3 Series', '5 Series', '7 Series', 'X1', 'X3', 'X5', 'X7'],
        'base_prices': [5000000, 6800000, 15000000, 4700000, 6200000, 8500000, 12000000]
    },
    'Mercedes-Benz': {
        'models': ['A-Class', 'C-Class', 'E-Class', 'S-Class', 'GLA', 'GLC', 'GLE', 'GLS'],
        'base_prices': [4700000, 6000000, 7800000, 17000000, 5200000, 6500000, 7800000, 10000000]
    },
    'Audi': {
        'models': ['A3', 'A4', 'A6', 'Q3', 'Q5', 'Q7', 'Q8'],
        'base_prices': [4500000, 5500000, 7000000, 5200000, 6800000, 8200000, 10000000]
    },
    'Tesla': {
        'models': ['Model 3', 'Model S', 'Model X', 'Model Y'],
        'base_prices': [6000000, 12000000, 13000000, 7500000]
    }
}

FUEL_TYPES = ["Petrol", "Diesel", "CNG", "Electric", "Hybrid"]
TRANSMISSIONS = ["Manual", "Automatic", "CVT", "DCT", "AMT"]
CAR_CONDITIONS = ["Excellent", "Very Good", "Good", "Fair", "Poor"]
OWNER_TYPES = ["First", "Second", "Third", "Fourth & Above"]
INSURANCE_STATUS = ["Comprehensive", "Third Party", "Expired", "No Insurance"]
CITIES = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata"]

# ============================================================================
# CAR PRICE PREDICTION ENGINE
# ============================================================================

class CarPricePredictor:
    def __init__(self):
        self.model = None
        self.encoders = {}
        self.is_trained = False
    
    def get_base_price(self, brand, model):
        """Get base price from database"""
        try:
            if brand in CAR_DATABASE and model in CAR_DATABASE[brand]['models']:
                model_index = CAR_DATABASE[brand]['models'].index(model)
                return CAR_DATABASE[brand]['base_prices'][model_index]
            return 500000
        except:
            return 500000
    
    def calculate_accurate_price(self, input_data):
        """Calculate price using advanced formula"""
        try:
            base_price = self.get_base_price(input_data['Brand'], input_data['Model'])
            
            # Fuel type adjustment
            fuel_multipliers = {
                "Petrol": 1.0, "Diesel": 1.12, "CNG": 0.92, "Electric": 1.65, "Hybrid": 1.35
            }
            base_price *= fuel_multipliers.get(input_data['Fuel_Type'], 1.0)
            
            # Transmission adjustment
            transmission_multipliers = {
                "Manual": 1.0, "Automatic": 1.18, "CVT": 1.15, "DCT": 1.22, "AMT": 1.08
            }
            base_price *= transmission_multipliers.get(input_data['Transmission'], 1.0)
            
            # Age depreciation
            current_year = datetime.now().year
            car_age = current_year - input_data['Year']
            
            if car_age == 0:
                depreciation = 0.10
            elif car_age == 1:
                depreciation = 0.25
            elif car_age <= 3:
                depreciation = 0.45
            elif car_age <= 5:
                depreciation = 0.60
            else:
                depreciation = min(0.75, 0.60 + (car_age - 5) * 0.05)
            
            # Mileage impact
            mileage = input_data['Mileage']
            if mileage <= 30000:
                mileage_impact = 0.03
            elif mileage <= 80000:
                mileage_impact = 0.12
            else:
                mileage_impact = 0.25
            
            # Condition multiplier
            condition_multipliers = {
                "Excellent": 0.92, "Very Good": 0.85, "Good": 0.75, "Fair": 0.60, "Poor": 0.45
            }
            
            # Owner type multiplier
            owner_multipliers = {
                "First": 1.0, "Second": 0.88, "Third": 0.75, "Fourth & Above": 0.60
            }
            
            # Calculate final price
            total_depreciation = depreciation + mileage_impact
            depreciated_price = base_price * (1 - total_depreciation)
            final_price = depreciated_price * condition_multipliers[input_data['Condition']] * owner_multipliers[input_data['Owner_Type']]
            
            # City adjustment
            city_premium = {"Delhi": 1.04, "Mumbai": 1.06, "Bangalore": 1.05, "Chennai": 1.02}
            final_price *= city_premium.get(input_data['Registration_City'], 1.0)
            
            return max(100000, int(final_price))
        except:
            return 500000
    
    def predict_price(self, input_data):
        """Main prediction function"""
        return self.calculate_accurate_price(input_data)
    
    def get_market_price_range(self, brand, model, year, condition):
        """Get market price range"""
        base_price = self.get_base_price(brand, model)
        current_year = datetime.now().year
        age = current_year - year
        
        dep_factor = max(0.25, 0.85 - (age * 0.12))
        avg_price = base_price * dep_factor
        
        condition_factors = {"Excellent": 1.1, "Very Good": 1.0, "Good": 0.9, "Fair": 0.75, "Poor": 0.6}
        avg_price *= condition_factors[condition]
        
        return [int(avg_price * 0.85), int(avg_price), int(avg_price * 1.15)]

# ============================================================================
# LOGIN PAGE
# ============================================================================

def show_login_page():
    """Display login page"""
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 80px auto;
            padding: 40px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 70px; text-align: center;">🚗</div>', unsafe_allow_html=True)
        st.markdown('<h1 style="text-align: center; color: #1f77b4;">Car Price Predictor</h1>', unsafe_allow_html=True)
        
        st.markdown("### 🔐 Sign In")
        
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔓 Login", use_container_width=True, type="primary"):
                if username and password:
                    user = verify_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success(f"✅ Welcome, {user['full_name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                else:
                    st.warning("⚠️ Enter username & password")
        
        with col_btn2:
            if st.button("🔑 Demo", use_container_width=True):
                st.info("**Admin:**\nUsername: `admin`\nPassword: `admin123`")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Car Price Predictor Pro",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize
init_database()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'predictor' not in st.session_state:
    st.session_state.predictor = CarPricePredictor()

# Check login
if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# ============================================================================
# CSS STYLING
# ============================================================================

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .user-info {
        background: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    user_stats = get_user_stats(st.session_state.user['id'])
    st.markdown(f"""
    <div class='user-info'>
        <h3>👤 {st.session_state.user['full_name']}</h3>
        <p><b>@{st.session_state.user['username']}</b></p>
        <p>Role: <b>{st.session_state.user['role'].upper()}</b></p>
        <hr>
        <p>📊 Predictions: <b>{user_stats['total_predictions']}</b></p>
        <p>🔑 Logins: <b>{user_stats['total_logins']}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout_user(st.session_state.user['id'])
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

if st.session_state.user['role'] == 'admin':
    
    st.title("👑 Admin Dashboard - Car Price Prediction System")
    
    # System Stats
    sys_stats = get_system_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Users", sys_stats['total_users'])
    with col2:
        st.metric("🟢 Online", sys_stats['currently_online'])
    with col3:
        st.metric("📊 Predictions", sys_stats['total_predictions'])
    with col4:
        st.metric("🕒 Today Logins", sys_stats['today_logins'])
    
    st.markdown("---")
    
    # Main Tabs
    main_tab = st.radio("", ["🚗 Car Price Predictor", "👥 User Management"], horizontal=True)
    
    # CAR PRICE PREDICTOR TAB
    if main_tab == "🚗 Car Price Predictor":
        st.markdown("## 🎯 Predict Car Price")
        
        col1, col2 = st.columns(2)
        
        with col1:
            brand = st.selectbox("Brand", sorted(list(CAR_DATABASE.keys())))
            if brand in CAR_DATABASE:
                model = st.selectbox("Model", sorted(CAR_DATABASE[brand]['models']))
                base_price = st.session_state.predictor.get_base_price(brand, model)
                st.info(f"**Base Price:** ₹{base_price:,}")
            
            year = st.slider("Year", 2000, datetime.now().year, datetime.now().year - 3)
            fuel_type = st.selectbox("Fuel Type", FUEL_TYPES)
            transmission = st.selectbox("Transmission", TRANSMISSIONS)
        
        with col2:
            mileage = st.number_input("Mileage (km)", 0, 500000, 30000, 5000)
            condition = st.selectbox("Condition", CAR_CONDITIONS)
            owner_type = st.selectbox("Owner", OWNER_TYPES)
            insurance = st.selectbox("Insurance", INSURANCE_STATUS)
            city = st.selectbox("City", sorted(CITIES))
        
        if st.button("🎯 Predict Price", type="primary", use_container_width=True):
            input_data = {
                'Brand': brand, 'Model': model, 'Year': year,
                'Fuel_Type': fuel_type, 'Transmission': transmission,
                'Mileage': mileage, 'Condition': condition,
                'Owner_Type': owner_type, 'Insurance_Status': insurance,
                'Registration_City': city
            }
            
            predicted_price = st.session_state.predictor.predict_price(input_data)
            market_prices = st.session_state.predictor.get_market_price_range(brand, model, year, condition)
            
            save_prediction(st.session_state.user['id'], brand, model, year, predicted_price)
            
            st.success(f"## 🎯 Predicted Price: ₹{predicted_price:,}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Market Low", f"₹{market_prices[0]:,}")
            with col2:
                st.metric("Market Avg", f"₹{market_prices[1]:,}")
            with col3:
                st.metric("Market High", f"₹{market_prices[2]:,}")
    
    # USER MANAGEMENT TAB
    else:
        st.markdown("## 👥 User Management")
        
        user_tabs = st.tabs(["🟢 Active Users", "➕ Create", "📋 All Users", "✏️ Edit", "🗑️ Delete"])
        
        # ACTIVE USERS
        with user_tabs[0]:
            st.subheader("🟢 Currently Online")
            if st.button("🔄 Refresh"):
                st.rerun()
            
            active_users = get_currently_logged_in_users()
            if active_users:
                for user in active_users:
                    st.markdown(f"""
<div style='background:#e8f5e9;padding:15px;border-radius:10px;margin:10px 0;'>
    <b>{user[3]}</b> (@{user[1]}) - {user[5]}<br>
    <small>📧 {user[2] or 'N/A'} | 🕒 {user[4]}</small>
</div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No users online")
        
        # CREATE USER
        with user_tabs[1]:
            st.subheader("➕ Create New User")
            with st.form("create_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    new_user = st.text_input("Username *")
                    new_name = st.text_input("Full Name *")
                    new_email = st.text_input("Email")
                with col_b:
                    new_phone = st.text_input("Phone")
                    new_pass = st.text_input("Password *", type="password")
                    confirm_pass = st.text_input("Confirm *", type="password")
                
                if st.form_submit_button("✅ Create User", type="primary"):
                    if new_user and new_pass and new_name and new_pass == confirm_pass and len(new_pass) >= 6:
                        success, msg = create_user(new_user, new_pass, new_email, new_name, new_phone)
                        if success:
                            st.success(f"✅ User created!\n\nUsername: `{new_user}`\nPassword: `{new_pass}`")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
        
        # ALL USERS
        with user_tabs[2]:
            st.subheader("📋 All Users")
            users = get_all_users()
            df = pd.DataFrame(users, columns=['ID', 'Username', 'Email', 'Name', 'Phone', 'Created', 'Last Login', 'Active', 'Role'])
            st.dataframe(df, use_container_width=True)
        
        # EDIT USER
        with user_tabs[3]:
            st.subheader("✏️ Edit User")
            all_users = get_all_users()
            user_options = {f"{u[0]} - {u[1]} ({u[3]})": u[0] for u in all_users}
            selected = st.selectbox("Select User", list(user_options.keys()))
            
            if selected:
                uid = user_options[selected]
                if uid != 1:
                    user_det = get_user_by_id(uid)
                    if user_det:
                        with st.form("edit_form"):
                            col1, col2 = st.columns(2)
                            with col1:
                                ed_user = st.text_input("Username", value=user_det[1])
                                ed_name = st.text_input("Name", value=user_det[3] or "")
                                ed_email = st.text_input("Email", value=user_det[2] or "")
                            with col2:
                                ed_phone = st.text_input("Phone", value=user_det[4] or "")
                                ed_active = st.selectbox("Status", [1, 0], format_func=lambda x: "Active" if x == 1 else "Inactive", index=0 if user_det[5] else 1)
                                ed_pass = st.text_input("New Password (optional)", type="password")
                            
                            if st.form_submit_button("💾 Update", type="primary"):
                                success, msg = update_user(uid, ed_user, ed_email, ed_name, ed_phone, ed_active, ed_pass if ed_pass else None)
                                if success:
                                    st.success(f"✅ {msg}")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ {msg}")
                else:
                    st.warning("Cannot edit admin account")
        
        # DELETE USER
        with user_tabs[4]:
            st.subheader("🗑️ Delete User")
            st.warning("⚠️ Permanent action!")
            all_del = get_all_users()
            del_options = {f"{u[0]} - {u[1]} ({u[3]})": u[0] for u in all_del}
            selected_del = st.selectbox("Select User to Delete", list(del_options.keys()))
            
            if selected_del:
                del_id = del_options[selected_del]
                if del_id != 1:
                    user_del = get_user_by_id(del_id)
                    if user_del:
                        st.markdown(f"**Username:** {user_del[1]}\n**Name:** {user_del[3]}")
                        confirm = st.checkbox("I confirm deletion")
                        if confirm and st.button("🗑️ DELETE", type="primary"):
                            success, msg = delete_user(del_id)
                            if success:
                                st.success(f"✅ {msg}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                else:
                    st.error("Cannot delete admin")

# ============================================================================
# USER DASHBOARD
# ============================================================================

else:
    st.title("🚗 Car Price Prediction System")
    
    tab1, tab2 = st.tabs(["🎯 Predict Price", "📜 My History"])
    
    # PREDICT TAB
    with tab1:
        st.subheader("🎯 Predict Car Price")
        
        col1, col2 = st.columns(2)
        
        with col1:
            brand = st.selectbox("Brand", sorted(list(CAR_DATABASE.keys())))
            if brand in CAR_DATABASE:
                model = st.selectbox("Model", sorted(CAR_DATABASE[brand]['models']))
                base_price = st.session_state.predictor.get_base_price(brand, model)
                st.info(f"**Base Price:** ₹{base_price:,}")
            
            year = st.slider("Year", 2000, datetime.now().year, datetime.now().year - 3)
            fuel_type = st.selectbox("Fuel", FUEL_TYPES)
            transmission = st.selectbox("Transmission", TRANSMISSIONS)
        
        with col2:
            mileage = st.number_input("Mileage (km)", 0, 500000, 30000, 5000)
            condition = st.selectbox("Condition", CAR_CONDITIONS)
            owner_type = st.selectbox("Owner", OWNER_TYPES)
            insurance = st.selectbox("Insurance", INSURANCE_STATUS)
            city = st.selectbox("City", sorted(CITIES))
        
        if st.button("🎯 Predict Price", type="primary", use_container_width=True):
            input_data = {
                'Brand': brand, 'Model': model, 'Year': year,
                'Fuel_Type': fuel_type, 'Transmission': transmission,
                'Mileage': mileage, 'Condition': condition,
                'Owner_Type': owner_type, 'Insurance_Status': insurance,
                'Registration_City': city
            }
            
            predicted_price = st.session_state.predictor.predict_price(input_data)
            market_prices = st.session_state.predictor.get_market_price_range(brand, model, year, condition)
            
            save_prediction(st.session_state.user['id'], brand, model, year, predicted_price)
            
            st.success(f"## 🎯 Predicted Price: ₹{predicted_price:,}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Market Low", f"₹{market_prices[0]:,}")
            with col2:
                st.metric("Market Avg", f"₹{market_prices[1]:,}")
            with col3:
                st.metric("Market High", f"₹{market_prices[2]:,}")
    
    # HISTORY TAB
    with tab2:
        st.subheader("📜 My Prediction History")
        predictions = get_user_predictions(st.session_state.user['id'])
        if predictions:
            for pred in predictions:
                st.markdown(f"""
<div style='background:#f5f5f5;padding:12px;border-radius:6px;margin:8px 0;'>
    <b>{pred[0]} {pred[1]} ({pred[2]})</b><br>
    <small>Predicted: ₹{pred[3]:,} | {pred[4]}</small>
</div>
                """, unsafe_allow_html=True)
        else:
            st.info("No predictions yet")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <p>🔐 {st.session_state.user['full_name']} (@{st.session_state.user['username']}) | Role: {st.session_state.user['role'].upper()}</p>
    <p>🚗 Car Price Prediction System Pro | © 2025</p>
</div>
""", unsafe_allow_html=True)
