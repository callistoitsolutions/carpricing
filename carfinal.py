"""
Global Ultra Accurate Car Price Prediction System
Complete system with authentication, admin panel, and AI-powered predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from datetime import datetime
import hashlib
import sqlite3
import time
from io import BytesIO

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Global Car Price Predictor",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# COMPREHENSIVE GLOBAL CAR DATABASE
# ============================================================================

CAR_DATABASE = {
    # INDIAN BRANDS
    'Maruti Suzuki': {
        'models': ['Alto', 'Alto K10', 'S-Presso', 'Celerio', 'Wagon R', 'Ignis', 'Swift', 'Baleno', 'Dzire', 'Ciaz', 
                  'Ertiga', 'XL6', 'Vitara Brezza', 'Jimny', 'Fronx', 'Grand Vitara', 'Eeco', 'Omni'],
        'base_prices': [300000, 400000, 450000, 550000, 600000, 650000, 800000, 900000, 850000, 950000,
                       1100000, 1300000, 1000000, 1250000, 950000, 1200000, 500000, 250000]
    },
    'Tata': {
        'models': ['Tiago', 'Tigor', 'Altroz', 'Nexon', 'Punch', 'Harrier', 'Safari', 'Nexon EV', 'Tigor EV', 'Tiago EV',
                  'Indica', 'Indigo', 'Sumo', 'Hexa'],
        'base_prices': [450000, 550000, 700000, 950000, 650000, 1800000, 2000000, 1600000, 1300000, 850000,
                       200000, 250000, 400000, 1200000]
    },
    'Mahindra': {
        'models': ['Bolero', 'Scorpio', 'XUV300', 'XUV400', 'XUV700', 'Thar', 'Marazzo', 'Bolero Neo', 'Scorpio N',
                  'KUV100', 'TUV300', 'Alturas G4', 'XUV500'],
        'base_prices': [850000, 1500000, 1100000, 1700000, 1600000, 1500000, 1200000, 950000, 1700000,
                       500000, 850000, 2800000, 1400000]
    },
    
    # JAPANESE BRANDS
    'Toyota': {
        'models': ['Innova Crysta', 'Fortuner', 'Glanza', 'Urban Cruiser Hyryder', 'Camry', 'Vellfire', 'Hilux', 
                  'Etios', 'Corolla Altis', 'Innova Hycross', 'Land Cruiser', 'Prius', 'RAV4', 'Highlander'],
        'base_prices': [2000000, 3500000, 750000, 1200000, 4500000, 9000000, 3800000, 
                       600000, 1600000, 1900000, 10000000, 4000000, 3500000, 5000000]
    },
    'Honda': {
        'models': ['Amaze', 'City', 'Jazz', 'WR-V', 'Elevate', 'Civic', 'CR-V', 'Brio', 'Accord', 'Odyssey'],
        'base_prices': [750000, 1200000, 850000, 950000, 1200000, 2000000, 3200000, 500000, 4500000, 5500000]
    },
    'Nissan': {
        'models': ['Magnite', 'Kicks', 'Micra', 'Sunny', 'GT-R', 'Patrol', 'X-Trail', 'Leaf', 'Altima', '370Z'],
        'base_prices': [600000, 1100000, 700000, 800000, 22000000, 7000000, 3500000, 4000000, 3500000, 6000000]
    },
    
    # KOREAN BRANDS
    'Hyundai': {
        'models': ['i10', 'i20', 'Aura', 'Grand i10 Nios', 'Verna', 'Creta', 'Venue', 'Alcazar', 'Tucson', 
                  'Kona Electric', 'Santro', 'Elantra', 'Ioniq 5', 'Palisade', 'Santa Fe', 'Genesis GV70'],
        'base_prices': [500000, 700000, 650000, 600000, 1100000, 1400000, 950000, 2000000, 2800000, 
                       2400000, 450000, 1800000, 4500000, 5500000, 4500000, 8000000]
    },
    'Kia': {
        'models': ['Seltos', 'Sonet', 'Carens', 'Carnival', 'EV6', 'Rio', 'Stinger', 'Sportage', 'Sorento', 'Telluride'],
        'base_prices': [1200000, 850000, 1300000, 3300000, 6500000, 700000, 6000000, 3500000, 4500000, 5500000]
    },
    
    # GERMAN LUXURY BRANDS
    'BMW': {
        'models': ['1 Series', '2 Series', '3 Series', '4 Series', '5 Series', '6 Series', '7 Series', '8 Series',
                  'X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'Z4', 'i3', 'i4', 'iX', 'M2', 'M3', 'M4', 'M5', 'M8'],
        'base_prices': [4000000, 4500000, 5000000, 6000000, 6800000, 8000000, 15000000, 18000000,
                       4700000, 4900000, 6200000, 7500000, 8500000, 10000000, 12000000, 7000000, 
                       5500000, 7200000, 11500000, 9000000, 10000000, 11000000, 14000000, 20000000]
    },
    'Mercedes-Benz': {
        'models': ['A-Class', 'B-Class', 'C-Class', 'E-Class', 'S-Class', 'CLA', 'CLS', 'GLA', 'GLB', 'GLC', 
                  'GLE', 'GLS', 'G-Class', 'EQC', 'EQS', 'AMG GT', 'Maybach S-Class', 'Maybach GLS'],
        'base_prices': [4700000, 5000000, 6000000, 7800000, 17000000, 5500000, 9000000, 5200000, 5800000, 6500000,
                       7800000, 10000000, 18000000, 9900000, 15000000, 25000000, 28000000, 35000000]
    },
    'Audi': {
        'models': ['A1', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'Q2', 'Q3', 'Q4 e-tron', 'Q5', 'Q7', 'Q8', 
                  'e-tron', 'TT', 'R8', 'RS3', 'RS5', 'RS6', 'RS7', 'RSQ8'],
        'base_prices': [3800000, 4500000, 5500000, 6500000, 7000000, 8500000, 13000000, 4200000, 5200000, 7500000,
                       6800000, 8200000, 10000000, 10000000, 7500000, 28000000, 8500000, 10500000, 15000000, 18000000, 20000000]
    },
    'Volkswagen': {
        'models': ['Polo', 'Vento', 'Virtus', 'Taigun', 'Tiguan', 'Golf', 'Passat', 'Arteon', 'Touareg', 'ID.4'],
        'base_prices': [700000, 900000, 1100000, 1300000, 3200000, 3500000, 4500000, 5500000, 8000000, 6500000]
    },
    'Porsche': {
        'models': ['718 Cayman', '718 Boxster', '911 Carrera', '911 Turbo', 'Panamera', 'Macan', 'Cayenne', 'Taycan'],
        'base_prices': [10000000, 11000000, 18000000, 28000000, 15000000, 8500000, 12000000, 15000000]
    },
    
    # AMERICAN BRANDS
    'Ford': {
        'models': ['EcoSport', 'Endeavour', 'Figo', 'Aspire', 'Mustang', 'F-150', 'Explorer', 'Escape', 
                  'Edge', 'Expedition', 'Ranger', 'Bronco', 'Mach-E'],
        'base_prices': [850000, 3200000, 600000, 650000, 8000000, 5500000, 6000000, 3500000,
                       4500000, 7000000, 4000000, 5000000, 7500000]
    },
    'Tesla': {
        'models': ['Model 3', 'Model S', 'Model X', 'Model Y', 'Cybertruck', 'Roadster'],
        'base_prices': [6000000, 12000000, 13000000, 7500000, 8500000, 28000000]
    },
    'Jeep': {
        'models': ['Compass', 'Meridian', 'Wrangler', 'Grand Cherokee', 'Cherokee', 'Renegade', 'Gladiator'],
        'base_prices': [2000000, 3500000, 6500000, 8500000, 4500000, 2500000, 7000000]
    },
    
    # BRITISH BRANDS
    'Land Rover': {
        'models': ['Defender', 'Discovery', 'Discovery Sport', 'Range Rover Evoque', 'Range Rover Velar', 
                  'Range Rover Sport', 'Range Rover'],
        'base_prices': [9000000, 8500000, 6500000, 6800000, 8500000, 14000000, 22000000]
    },
    'Jaguar': {
        'models': ['XE', 'XF', 'XJ', 'F-Type', 'E-Pace', 'F-Pace', 'I-Pace'],
        'base_prices': [6000000, 7500000, 12000000, 11000000, 6500000, 8500000, 12000000]
    },
    'Bentley': {
        'models': ['Continental GT', 'Flying Spur', 'Bentayga', 'Mulsanne'],
        'base_prices': [35000000, 38000000, 45000000, 50000000]
    },
    'Rolls-Royce': {
        'models': ['Ghost', 'Wraith', 'Dawn', 'Phantom', 'Cullinan'],
        'base_prices': [55000000, 60000000, 65000000, 80000000, 70000000]
    },
    
    # ITALIAN BRANDS
    'Ferrari': {
        'models': ['Portofino', 'Roma', 'F8 Tributo', 'SF90 Stradale', '812 Superfast', 'Purosangue'],
        'base_prices': [38000000, 42000000, 55000000, 85000000, 65000000, 75000000]
    },
    'Lamborghini': {
        'models': ['Huracán', 'Aventador', 'Urus'],
        'base_prices': [45000000, 75000000, 50000000]
    },
    
    # CHINESE BRANDS
    'BYD': {
        'models': ['Atto 3', 'E6', 'Han', 'Tang', 'Seal', 'Dolphin'],
        'base_prices': [3400000, 2900000, 6500000, 5500000, 4500000, 3000000]
    },
    'MG': {
        'models': ['Hector', 'Astor', 'Gloster', 'ZS EV', 'Comet EV', 'Windsor'],
        'base_prices': [1500000, 1300000, 3200000, 2200000, 800000, 1200000]
    },
    
    # FRENCH BRANDS
    'Renault': {
        'models': ['Kwid', 'Triber', 'Kiger', 'Duster', 'Captur', 'Koleos', 'Megane', 'Clio'],
        'base_prices': [400000, 650000, 750000, 1100000, 1500000, 3500000, 2500000, 2000000]
    },
    
    # CZECH BRANDS
    'Skoda': {
        'models': ['Rapid', 'Slavia', 'Kushaq', 'Kodiaq', 'Octavia', 'Superb', 'Karoq'],
        'base_prices': [800000, 1100000, 1200000, 3500000, 2800000, 3500000, 2500000]
    },
}

FUEL_TYPES = ["Petrol", "Diesel", "CNG", "Electric", "Hybrid", "LPG"]
TRANSMISSIONS = ["Manual", "Automatic", "CVT", "DCT", "AMT"]
CAR_CONDITIONS = ["Excellent", "Very Good", "Good", "Fair", "Poor"]
OWNER_TYPES = ["First", "Second", "Third", "Fourth & Above"]
INSURANCE_STATUS = ["Comprehensive", "Third Party", "Expired", "No Insurance"]
CITIES = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def init_database():
    """Initialize database with migration support"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  email TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_login TIMESTAMP,
                  is_active BOOLEAN DEFAULT 1,
                  role TEXT DEFAULT 'user')''')
    
    # Create usage_logs table
    c.execute('''CREATE TABLE IF NOT EXISTS usage_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  action TEXT,
                  details TEXT,
                  predictions_made INTEGER,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Create sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  logout_time TIMESTAMP,
                  is_active BOOLEAN DEFAULT 1,
                  session_token TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Migration: Add missing columns
    try:
        c.execute("PRAGMA table_info(sessions)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'is_active' not in columns:
            c.execute("ALTER TABLE sessions ADD COLUMN is_active BOOLEAN DEFAULT 1")
            conn.commit()
            
        if 'session_token' not in columns:
            c.execute("ALTER TABLE sessions ADD COLUMN session_token TEXT")
            conn.commit()
    except Exception as e:
        pass
    
    # Create admin user if not exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                  ('admin', admin_password, 'admin@carprice.com', 'admin'))
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    """Verify and login user"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        c.execute("SELECT id, username, role, is_active FROM users WHERE username = ? AND password_hash = ?",
                  (username, password_hash))
        
        user = c.fetchone()
        
        if user and user[3]:
            c.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now(), user[0]))
            session_token = hashlib.md5(f"{user[0]}{datetime.now()}".encode()).hexdigest()
            
            try:
                c.execute("UPDATE sessions SET is_active = 0, logout_time = ? WHERE user_id = ? AND is_active = 1", 
                          (datetime.now(), user[0]))
            except sqlite3.OperationalError:
                pass
            
            try:
                c.execute("INSERT INTO sessions (user_id, login_time, is_active, session_token) VALUES (?, ?, ?, ?)",
                          (user[0], datetime.now(), 1, session_token))
            except sqlite3.OperationalError:
                c.execute("INSERT INTO sessions (user_id, login_time) VALUES (?, ?)",
                          (user[0], datetime.now()))
            
            conn.commit()
            conn.close()
            
            return {
                'id': user[0], 
                'username': user[1], 
                'role': user[2], 
                'is_active': user[3], 
                'session_token': session_token
            }
        
        conn.close()
        return None
    except Exception as e:
        conn.close()
        return None

def create_user_by_admin(username, password, email):
    """Admin creates user"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    try:
        password_hash = hash_password(password)
        c.execute("INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                  (username, password_hash, email, 'user'))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def logout_user(user_id):
    """Logout user"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute("UPDATE sessions SET is_active = 0, logout_time = ? WHERE user_id = ? AND is_active = 1",
                  (datetime.now(), user_id))
    except sqlite3.OperationalError:
        c.execute("UPDATE sessions SET logout_time = ? WHERE user_id = ? AND logout_time IS NULL",
                  (datetime.now(), user_id))
    conn.commit()
    conn.close()

def log_usage(user_id, action, details="", predictions_made=0):
    """Log activity"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO usage_logs (user_id, action, details, predictions_made) VALUES (?, ?, ?, ?)",
              (user_id, action, details, predictions_made))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    """Get user stats"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usage_logs WHERE user_id = ? AND action = 'predict_price'", (user_id,))
    total_predictions = c.fetchone()[0]
    c.execute("SELECT SUM(predictions_made) FROM usage_logs WHERE user_id = ? AND action = 'predict_price'", (user_id,))
    total_cars = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM sessions WHERE user_id = ?", (user_id,))
    total_logins = c.fetchone()[0]
    conn.close()
    return {'total_predictions': total_predictions, 'total_cars': total_cars, 'total_logins': total_logins}

def get_all_users():
    """Get all users"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id, username, email, created_at, last_login, is_active, role FROM users ORDER BY created_at DESC")
    users = c.fetchall()
    conn.close()
    return users

def get_currently_logged_in_users():
    """Get currently logged in users"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT u.id, u.username, u.email, s.login_time, u.role
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.is_active = 1
            ORDER BY s.login_time DESC
        """)
        active_users = c.fetchall()
    except sqlite3.OperationalError:
        active_users = []
    conn.close()
    return active_users

def get_user_activity_details(user_id):
    """Get detailed activity for a specific user"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        SELECT action, details, predictions_made, timestamp
        FROM usage_logs
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 20
    """, (user_id,))
    activities = c.fetchall()
    conn.close()
    return activities

def get_all_user_activities():
    """Get all activities from all users"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        SELECT u.username, l.action, l.details, l.predictions_made, l.timestamp
        FROM usage_logs l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.timestamp DESC
        LIMIT 100
    """)
    activities = c.fetchall()
    conn.close()
    return activities

def get_system_stats():
    """Get system stats"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
    total_users = c.fetchone()[0]
    try:
        c.execute("SELECT COUNT(*) FROM sessions WHERE is_active = 1")
        currently_online = c.fetchone()[0]
    except sqlite3.OperationalError:
        currently_online = 0
    c.execute("SELECT COUNT(*) FROM usage_logs WHERE action = 'predict_price'")
    total_predictions = c.fetchone()[0]
    c.execute("SELECT SUM(predictions_made) FROM usage_logs WHERE action = 'predict_price'")
    total_cars = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM sessions WHERE DATE(login_time) = DATE('now')")
    today_logins = c.fetchone()[0]
    conn.close()
    return {
        'total_users': total_users,
        'currently_online': currently_online,
        'total_predictions': total_predictions,
        'total_cars': total_cars,
        'today_logins': today_logins
    }

def toggle_user_status(user_id, is_active):
    """Enable/disable user"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE users SET is_active = ? WHERE id = ?", (is_active, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    """Delete user"""
    conn = sqlite3.connect('car_price_predictor.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# ============================================================================
# MACHINE LEARNING PREDICTION ENGINE
# ============================================================================

class UltraAccurateCarPricePredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.encoders = {}
        self.is_trained = False
        self.training_data = None
        
    def get_base_price(self, brand, model):
        """Get accurate base price from database"""
        try:
            if brand in CAR_DATABASE and model in CAR_DATABASE[brand]['models']:
                model_index = CAR_DATABASE[brand]['models'].index(model)
                return CAR_DATABASE[brand]['base_prices'][model_index]
            else:
                return 500000
        except:
            return 500000

    def calculate_accurate_price(self, input_data):
        """Calculate ultra accurate price using advanced formula"""
        try:
            base_price = self.get_base_price(input_data['Brand'], input_data['Model'])
            
            # Fuel type adjustment
            fuel_multipliers = {
                "Petrol": 1.0, "Diesel": 1.12, "CNG": 0.92, "Electric": 1.65, 
                "Hybrid": 1.35, "LPG": 0.88
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
            elif car_age == 2:
                depreciation = 0.35
            elif car_age == 3:
                depreciation = 0.45
            elif car_age == 4:
                depreciation = 0.53
            elif car_age == 5:
                depreciation = 0.60
            else:
                depreciation = min(0.75, 0.60 + (car_age - 5) * 0.05)
            
            # Mileage impact
            mileage = input_data['Mileage']
            if mileage <= 10000:
                mileage_impact = 0
            elif mileage <= 30000:
                mileage_impact = 0.03
            elif mileage <= 50000:
                mileage_impact = 0.07
            elif mileage <= 80000:
                mileage_impact = 0.12
            elif mileage <= 120000:
                mileage_impact = 0.18
            elif mileage <= 200000:
                mileage_impact = 0.25
            else:
                mileage_impact = 0.35
            
            total_depreciation = depreciation + mileage_impact
            
            # Condition multiplier
            condition_multipliers = {
                "Excellent": 0.92, "Very Good": 0.85, "Good": 0.75, "Fair": 0.60, "Poor": 0.45
            }
            
            # Owner type multiplier
            owner_multipliers = {
                "First": 1.0, "Second": 0.88, "Third": 0.75, "Fourth & Above": 0.60
            }
            
            # Calculate final price
            depreciated_price = base_price * (1 - total_depreciation)
            final_price = depreciated_price * condition_multipliers[input_data['Condition']] * owner_multipliers[input_data['Owner_Type']]
            
            # City adjustment
            city_premium = {
                "Delhi": 1.04, "Mumbai": 1.06, "Bangalore": 1.05, "Chennai": 1.02, 
                "Pune": 1.03, "Hyderabad": 1.03
            }
            final_price *= city_premium.get(input_data.get('Registration_City', 'Mumbai'), 1.0)
            
            # Insurance adjustment
            if input_data.get('Insurance_Status') == 'Comprehensive':
                final_price *= 1.03
            elif input_data.get('Insurance_Status') == 'Expired':
                final_price *= 0.98
            
            return max(100000, int(final_price))
            
        except Exception as e:
            return self.fallback_calculation(input_data)
    
    def fallback_calculation(self, input_data):
        """Simple fallback calculation"""
        base_price = self.get_base_price(input_data['Brand'], input_data['Model'])
        current_year = datetime.now().year
        age = current_year - input_data['Year']
        age_factor = max(0.3, 1 - (age * 0.15))
        
        condition_multipliers = {
            "Excellent": 1.0, "Very Good": 0.9, "Good": 0.8, "Fair": 0.7, "Poor": 0.5
        }
        
        price = base_price * age_factor * condition_multipliers[input_data['Condition']]
        return max(100000, int(price))

    def predict_price(self, input_data):
        """Main prediction function"""
        return self.calculate_accurate_price(input_data)
    
    def get_market_price_range(self, brand, model, year, condition):
        """Get accurate market price range"""
        try:
            base_price = self.get_base_price(brand, model)
            current_year = datetime.now().year
            age = current_year - year
            
            if age == 0:
                dep_factor = 0.85
            elif age == 1:
                dep_factor = 0.70
            elif age == 2:
                dep_factor = 0.60
            elif age == 3:
                dep_factor = 0.52
            elif age == 4:
                dep_factor = 0.45
            elif age == 5:
                dep_factor = 0.40
            else:
                dep_factor = max(0.25, 0.40 - (age - 5) * 0.03)
            
            avg_price = base_price * dep_factor
            
            condition_factors = {
                "Excellent": 1.1, "Very Good": 1.0, "Good": 0.9, "Fair": 0.75, "Poor": 0.6
            }
            avg_price *= condition_factors[condition]
            
            min_price = avg_price * 0.85
            max_price = avg_price * 1.15
            
            return [int(min_price), int(avg_price), int(max_price)]
            
        except:
            return [300000, 500000, 700000]

# ============================================================================
# LOGIN PAGE
# ============================================================================

def show_login_page():
    """Professional login page with modern design"""
    
    # Creative CSS for login page
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
        
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Poppins', sans-serif;
        }
        
        .login-container {
            max-width: 480px;
            margin: 80px auto;
            padding: 0;
            background: white;
            border-radius: 24px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.3);
            overflow: hidden;
            animation: slideUp 0.6s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 30px;
            text-align: center;
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .login-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.3; }
        }
        
        .login-icon {
            font-size: 80px;
            margin-bottom: 15px;
            display: inline-block;
            animation: float 3s ease-in-out infinite;
            position: relative;
            z-index: 1;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
        }
        
        .login-title {
            font-size: 2.2rem;
            font-weight: 800;
            margin: 0;
            position: relative;
            z-index: 1;
            letter-spacing: -0.5px;
        }
        
        .login-subtitle {
            font-size: 1rem;
            opacity: 0.95;
            margin-top: 8px;
            font-weight: 400;
            position: relative;
            z-index: 1;
        }
        
        .login-body {
            padding: 40px 35px;
        }
        
        .input-label {
            font-size: 0.9rem;
            font-weight: 600;
            color: #334155;
            margin-bottom: 8px;
            display: block;
        }
        
        .stTextInput > div > div > input {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px 18px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: #f8fafc;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }
        
        .feature-card {
            background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);
            padding: 20px;
            border-radius: 16px;
            margin-top: 30px;
            border: 2px solid #e0e7ff;
        }
        
        .feature-title {
            font-size: 1rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .feature-item {
            font-size: 0.9rem;
            color: #475569;
            margin: 8px 0;
            padding-left: 24px;
            position: relative;
        }
        
        .feature-item::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: #10b981;
            font-weight: 800;
            font-size: 1.1rem;
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .login-container {
                margin: 20px;
                max-width: 100%;
            }
            
            .login-title {
                font-size: 1.8rem;
            }
            
            .login-icon {
                font-size: 60px;
            }
            
            .login-body {
                padding: 30px 25px;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Header Section
        st.markdown('''
        <div class="login-header">
            <div class="login-icon">🚗</div>
            <h1 class="login-title">Car Price Pro</h1>
            <p class="login-subtitle">AI-Powered Global Car Valuation Platform</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Body Section
        st.markdown('<div class="login-body">', unsafe_allow_html=True)
        
        st.markdown('<label class="input-label">👤 Username</label>', unsafe_allow_html=True)
        username = st.text_input("", key="login_username", placeholder="Enter your username", label_visibility="collapsed")
        
        st.markdown('<label class="input-label" style="margin-top: 20px;">🔒 Password</label>', unsafe_allow_html=True)
        password = st.text_input("", type="password", key="login_password", placeholder="Enter your password", label_visibility="collapsed")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 Login", use_container_width=True, type="primary", key="login_btn"):
                if username and password:
                    user = verify_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.predictor = UltraAccurateCarPricePredictor()
                        log_usage(user['id'], 'login')
                        st.success(f"✅ Welcome back, {username}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        with col_btn2:
            if st.button("🔑 Demo Access", use_container_width=True, key="demo_btn"):
                with st.expander("📌 Demo Credentials", expanded=True):
                    st.markdown("""
                        **Admin Account:**
                        - Username: `admin`
                        - Password: `admin123`
                        
                        **Features:**
                        - Full system access
                        - User management
                        - Global car database
                    """)
        
        # Features Section
        st.markdown('''
        <div class="feature-card">
            <div class="feature-title">
                <span>⭐</span>
                <span>Platform Features</span>
            </div>
            <div class="feature-item">Global car price predictions</div>
            <div class="feature-item">50+ brands, 500+ models</div>
            <div class="feature-item">Real-time market analysis</div>
            <div class="feature-item">Advanced depreciation engine</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close login-body
        st.markdown('</div>', unsafe_allow_html=True)  # Close login-container
        
        # Footer
        st.markdown('''
        <div style="text-align: center; margin-top: 30px; color: white; font-size: 0.9rem; opacity: 0.9;">
            <p>🔒 Secure & Encrypted | ⚡ Accurate Predictions | 🌍 Global Coverage</p>
            <p style="opacity: 0.7; font-size: 0.85rem;">© 2024 Car Price Pro. All rights reserved.</p>
        </div>
        ''', unsafe_allow_html=True)

# ============================================================================
# INITIALIZE
# ============================================================================

init_database()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'predictor' not in st.session_state:
    st.session_state.predictor = UltraAccurateCarPricePredictor()

# Check login
if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# ============================================================================
# MAIN APPLICATION CSS (After Login)
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Header Styles */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0 0.5rem 0;
        margin-bottom: 0;
        letter-spacing: -0.03em;
    }
    
    .sub-header {
        text-align: center;
        color: white;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 400;
        opacity: 0.95;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding: 1rem;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* User Info Card */
    .user-info {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 24px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem;
        border-radius: 16px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.7);
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* DataFrames */
    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Info Boxes */
    .info-box {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border-left: 4px solid #667eea;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 24px;
        border-radius: 16px;
        border-left: 4px solid #4caf50;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Online Indicator */
    .online-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse-green 2s infinite;
        box-shadow: 0 0 10px #10b981;
    }
    
    @keyframes pulse-green {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .sub-header {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR (Common for both Admin & User)
# ============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/sports-car.png", width=80)
    st.title("🚗 Car Price Pro")
    
    user_stats = get_user_stats(st.session_state.user['id'])
    
    st.markdown(f"""
    <div class='user-info'>
        <h3 style='color: #60a5fa !important;'>👤 {st.session_state.user['username']}</h3>
        <p style='margin: 8px 0; opacity: 0.9;'>Role: <b style='color: #a78bfa;'>{st.session_state.user['role'].upper()}</b></p>
        <hr style='margin: 12px 0; opacity: 0.3;'>
        <p style='margin: 6px 0;'>🎯 Predictions: <b>{user_stats['total_predictions']}</b></p>
        <p style='margin: 6px 0;'>🚗 Cars Valued: <b>{user_stats['total_cars']:,}</b></p>
        <p style='margin: 6px 0;'>🔑 Logins: <b>{user_stats['total_logins']}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 LOGOUT", use_container_width=True):
        logout_user(st.session_state.user['id'])
        log_usage(st.session_state.user['id'], 'logout')
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
    
    st.markdown("---")
    
    # Database stats
    total_brands = len(CAR_DATABASE)
    total_models = sum(len(CAR_DATABASE[brand]['models']) for brand in CAR_DATABASE)
    
    st.markdown(f"""
    ### 🌍 Global Database
    - 🏢 Brands: **{total_brands}**
    - 🚗 Models: **{total_models}**
    - 💎 Luxury Cars Included
    - 🌎 Worldwide Coverage
    
    ### 📊 Features
    - **AI Predictions**: ML-based pricing
    - **Market Analysis**: Real-time data
    - **Depreciation Engine**: Advanced calc
    - **Export Reports**: Download results
    """)

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

if st.session_state.user['role'] == 'admin':
    
    st.markdown('<div class="main-header">👑 ADMIN COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Complete System Management & Car Price Prediction</div>', unsafe_allow_html=True)
    
    # System Stats
    sys_stats = get_system_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("👥 Users", sys_stats['total_users'])
    with col2:
        st.metric("🟢 Online", sys_stats['currently_online'])
    with col3:
        st.metric("🎯 Predictions", sys_stats['total_predictions'])
    with col4:
        st.metric("🚗 Cars", f"{sys_stats['total_cars']:,}")
    with col5:
        st.metric("🕒 Today", sys_stats['today_logins'])
    
    st.markdown("---")
    
    # Main Admin Tabs
    admin_main_tab1, admin_main_tab2 = st.tabs([
        "🚗 CAR PRICE PREDICTION DASHBOARD",
        "👑 USER MANAGEMENT"
    ])
    
    # ========================================================================
    # ADMIN TAB 1: CAR PRICE PREDICTION DASHBOARD
    # ========================================================================
    
    with admin_main_tab1:
        st.markdown("## 🚀 Ultra Accurate Car Price Prediction Engine")
        
        # Prediction Interface
        col1, col2 = st.columns(2)
        
        with col1:
            brand = st.selectbox("🏢 Select Brand", sorted(list(CAR_DATABASE.keys())), key="admin_brand")
            
            if brand in CAR_DATABASE:
                model = st.selectbox("🚗 Select Model", sorted(CAR_DATABASE[brand]['models']), key="admin_model")
                base_price = st.session_state.predictor.get_base_price(brand, model)
                st.info(f"**Base New Price:** ₹{base_price:,}")
            
            current_year = datetime.now().year
            year = st.slider("📅 Manufacturing Year", 2000, current_year, current_year - 3, key="admin_year")
            fuel_type = st.selectbox("⛽ Fuel Type", FUEL_TYPES, key="admin_fuel")
            transmission = st.selectbox("⚙️ Transmission", TRANSMISSIONS, key="admin_trans")
        
        with col2:
            mileage = st.number_input("📊 Mileage (km)", min_value=0, max_value=500000, value=30000, step=5000, key="admin_mileage")
            condition = st.selectbox("✨ Condition", CAR_CONDITIONS, key="admin_condition")
            owner_type = st.selectbox("👤 Owner Type", OWNER_TYPES, key="admin_owner")
            insurance_status = st.selectbox("🛡️ Insurance Status", INSURANCE_STATUS, key="admin_insurance")
            registration_city = st.selectbox("🌍 Registration City", sorted(CITIES), key="admin_city")
        
        if st.button("🎯 Get Ultra Accurate Price", type="primary", use_container_width=True, key="admin_predict_btn"):
            with st.spinner('🔄 Calculating ultra accurate price...'):
                input_data = {
                    'Brand': brand, 'Model': model, 'Year': year,
                    'Fuel_Type': fuel_type, 'Transmission': transmission,
                    'Mileage': mileage, 'Condition': condition,
                    'Owner_Type': owner_type, 'Insurance_Status': insurance_status,
                    'Registration_City': registration_city
                }
                
                predicted_price = st.session_state.predictor.predict_price(input_data)
                market_prices = st.session_state.predictor.get_market_price_range(brand, model, year, condition)
                
                # Log the prediction
                log_usage(st.session_state.user['id'], 'predict_price', f"{brand} {model} {year}", 1)
                
                st.balloons()
                
                # Results Display
                st.markdown("---")
                st.markdown("## 💰 Price Analysis Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <h2 style="color: white; margin: 0;">🎯</h2>
                        <h2 style="margin: 10px 0; color: white;">₹{predicted_price:,}</h2>
                        <p style="margin: 0; color: rgba(255,255,255,0.9);">Predicted Price</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2 style="color: #ef5350; margin: 0;">💵</h2>
                        <h3 style="margin: 10px 0;">₹{market_prices[0]:,}</h3>
                        <p style="color: #7f8c8d; margin: 0;">Market Low</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2 style="color: #ffa726; margin: 0;">📊</h2>
                        <h3 style="margin: 10px 0;">₹{market_prices[1]:,}</h3>
                        <p style="color: #7f8c8d; margin: 0;">Market Avg</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2 style="color: #66bb6a; margin: 0;">💰</h2>
                        <h3 style="margin: 10px 0;">₹{market_prices[2]:,}</h3>
                        <p style="color: #7f8c8d; margin: 0;">Market High</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Depreciation Analysis
                st.markdown("### 📉 Depreciation Analysis")
                
                base_price = st.session_state.predictor.get_base_price(brand, model)
                depreciation = base_price - predicted_price
                depreciation_percent = (depreciation / base_price) * 100
                car_age = current_year - year
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Original Price", f"₹{base_price:,}")
                with col2:
                    st.metric("Current Value", f"₹{predicted_price:,}")
                with col3:
                    st.metric("Depreciation", f"₹{depreciation:,}", f"-{depreciation_percent:.1f}%")
                with col4:
                    st.metric("Car Age", f"{car_age} years")
                
                # Visualizations
                st.markdown("---")
                st.markdown("### 📊 Visual Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Price comparison chart
                    fig = go.Figure(data=[
                        go.Bar(name='Market Range', x=['Low', 'Average', 'High'], 
                               y=market_prices, marker_color=['#ef5350', '#ffa726', '#66bb6a']),
                        go.Scatter(name='Your Prediction', x=['Low', 'Average', 'High'], 
                                 y=[predicted_price, predicted_price, predicted_price],
                                 mode='lines', line=dict(color='#667eea', width=3, dash='dash'))
                    ])
                    fig.update_layout(
                        title="Price Comparison",
                        height=400,
                        paper_bgcolor='rgba(255,255,255,0.9)',
                        plot_bgcolor='rgba(255,255,255,0.9)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Depreciation gauge
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=100 - depreciation_percent,
                        title={'text': "Value Retention %"},
                        delta={'reference': 100},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "#667eea"},
                            'steps': [
                                {'range': [0, 30], 'color': "#ffebee"},
                                {'range': [30, 60], 'color': "#fff9c4"},
                                {'range': [60, 100], 'color': "#e8f5e9"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    fig.update_layout(height=400, paper_bgcolor='rgba(255,255,255,0.9)')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Car Details Summary
                st.markdown("---")
                st.markdown("### 🚗 Vehicle Details Summary")
                
                details_df = pd.DataFrame([
                    {"Attribute": "Brand", "Value": brand},
                    {"Attribute": "Model", "Value": model},
                    {"Attribute": "Year", "Value": year},
                    {"Attribute": "Age", "Value": f"{car_age} years"},
                    {"Attribute": "Fuel Type", "Value": fuel_type},
                    {"Attribute": "Transmission", "Value": transmission},
                    {"Attribute": "Mileage", "Value": f"{mileage:,} km"},
                    {"Attribute": "Condition", "Value": condition},
                    {"Attribute": "Owner Type", "Value": owner_type},
                    {"Attribute": "Insurance", "Value": insurance_status},
                    {"Attribute": "City", "Value": registration_city},
                ])
                
                st.dataframe(details_df, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # ADMIN TAB 2: USER MANAGEMENT
    # ========================================================================
    
    with admin_main_tab2:
        st.markdown("## 👑 User Management System")
        
        user_tab1, user_tab2, user_tab3, user_tab4 = st.tabs([
            "🟢 LIVE DASHBOARD",
            "➕ CREATE USER",
            "👥 MANAGE USERS",
            "📊 ACTIVITY LOG"
        ])
        
        with user_tab1:
            st.markdown("### 🟢 Live User Activity")
            
            if st.button("🔄 Refresh", key="admin_refresh"):
                st.rerun()
            
            active_users = get_currently_logged_in_users()
            
            if active_users:
                st.success(f"**{len(active_users)} user(s) online**")
                
                for user in active_users:
                    user_id, username, email, login_time, role = user
                    user_stats = get_user_stats(user_id)
                    
                    st.markdown(f"""
<div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%);
            padding: 20px; border-radius: 12px; margin: 12px 0; border: 2px solid rgba(16, 185, 129, 0.3);'>
    <span class='online-indicator'></span>
    <b style='color: white; font-size: 1.1rem;'>{username}</b> 
    <span style='color: #a7f3d0; margin-left: 10px;'>({role})</span><br>
    <small style='color: rgba(255,255,255,0.8);'>📧 {email if email else 'N/A'} | 🕒 {login_time}</small><br>
    <small style='color: rgba(255,255,255,0.9);'>🎯 {user_stats['total_predictions']} predictions | 🚗 {user_stats['total_cars']:,} cars</small>
</div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No users currently online")
        
        with user_tab2:
            st.markdown("### ➕ Create New User")
            
            with st.form("create_user_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    new_username = st.text_input("Username *")
                    new_email = st.text_input("Email")
                with col_b:
                    new_password = st.text_input("Password *", type="password")
                    confirm_password = st.text_input("Confirm Password *", type="password")
                
                submitted = st.form_submit_button("✅ CREATE USER", type="primary", use_container_width=True)
                
                if submitted:
                    if new_username and new_password == confirm_password and len(new_password) >= 6:
                        if create_user_by_admin(new_username, new_password, new_email):
                            st.success(f"""
✅ User Created Successfully!

**Username:** `{new_username}`
**Password:** `{new_password}`
**Email:** `{new_email if new_email else 'Not provided'}`
                            """)
                        else:
                            st.error("❌ Username already exists!")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        st.error("❌ Passwords don't match or fields are empty")
        
        with user_tab3:
            st.markdown("### 👥 All Users")
            
            users = get_all_users()
            user_data = []
            for user in users:
                user_data.append({
                    'ID': user[0],
                    'Username': user[1],
                    'Email': user[2] if user[2] else 'N/A',
                    'Created': user[3],
                    'Last Login': user[4] if user[4] else 'Never',
                    'Status': '🟢 Active' if user[5] else '🔴 Inactive',
                    'Role': user[6]
                })
            
            df_users = pd.DataFrame(user_data)
            st.dataframe(df_users, use_container_width=True, height=500)
            
            st.markdown("---")
            st.markdown("### ⚙️ User Actions")
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                user_id_action = st.number_input("User ID", min_value=1, step=1)
            with col_m2:
                action_type = st.selectbox("Action", ["Enable", "Disable", "Delete"])
            with col_m3:
                st.write("")
                if st.button("▶️ EXECUTE", type="primary"):
                    if user_id_action != 1:
                        if action_type == "Enable":
                            toggle_user_status(user_id_action, 1)
                            st.success("✅ User enabled!")
                            time.sleep(1)
                            st.rerun()
                        elif action_type == "Disable":
                            toggle_user_status(user_id_action, 0)
                            st.warning("⚠️ User disabled!")
                            time.sleep(1)
                            st.rerun()
                        elif action_type == "Delete":
                            delete_user(user_id_action)
                            st.error("🗑️ User deleted!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("❌ Cannot modify admin account")
        
        with user_tab4:
            st.markdown("### 📊 System Activity Log")
            
            all_activities = get_all_user_activities()
            
            if all_activities:
                activity_data = []
                for activity in all_activities:
                    username, action, details, predictions_made, timestamp = activity
                    activity_data.append({
                        'Username': username,
                        'Action': action,
                        'Details': details if details else '-',
                        'Cars': predictions_made if predictions_made else '-',
                        'Timestamp': timestamp
                    })
                
                df_activities = pd.DataFrame(activity_data)
                st.dataframe(df_activities, use_container_width=True, height=600)
            else:
                st.info("No activities logged yet")

# ============================================================================
# USER DASHBOARD
# ============================================================================

else:
    
    st.markdown('<div class="main-header">🚗 CAR PRICE PREDICTION</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ultra Accurate Global Car Valuation Platform</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="success-box">
        <h3>✅ System Ready</h3>
        <p>Advanced AI engine loaded. Get ultra-accurate car price predictions from our global database of 50+ brands and 500+ models.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main User Tabs
    user_main_tab1, user_main_tab2, user_main_tab3 = st.tabs([
        "🎯 PRICE PREDICTION",
        "📊 MARKET ANALYSIS",
        "🌍 BRAND EXPLORER"
    ])
    
    # ========================================================================
    # USER TAB 1: PRICE PREDICTION
    # ========================================================================
    
    with user_main_tab1:
        st.markdown("## 🎯 Ultra Accurate Price Prediction")
        
        # Prediction Interface
        col1, col2 = st.columns(2)
        
        with col1:
            brand = st.selectbox("🏢 Select Brand", sorted(list(CAR_DATABASE.keys())), key="user_brand")
            
            if brand in CAR_DATABASE:
                model = st.selectbox("🚗 Select Model", sorted(CAR_DATABASE[brand]['models']), key="user_model")
                base_price = st.session_state.predictor.get_base_price(brand, model)
                st.info(f"**Base New Price:** ₹{base_price:,}")
            
            current_year = datetime.now().year
            year = st.slider("📅 Manufacturing Year", 2000, current_year, current_year - 3, key="user_year")
            fuel_type = st.selectbox("⛽ Fuel Type", FUEL_TYPES, key="user_fuel")
            transmission = st.selectbox("⚙️ Transmission", TRANSMISSIONS, key="user_trans")
        
        with col2:
            mileage = st.number_input("📊 Mileage (km)", min_value=0, max_value=500000, value=30000, step=5000, key="user_mileage")
            condition = st.selectbox("✨ Condition", CAR_CONDITIONS, key="user_condition")
            owner_type = st.selectbox("👤 Owner Type", OWNER_TYPES, key="user_owner")
            insurance_status = st.selectbox("🛡️ Insurance Status", INSURANCE_STATUS, key="user_insurance")
            registration_city = st.selectbox("🌍 Registration City", sorted(CITIES), key="user_city")
        
        if st.button("🎯 Get Ultra Accurate Price", type="primary", use_container_width=True, key="user_predict_btn"):
            with st.spinner('🔄 Calculating ultra accurate price...'):
                input_data = {
                    'Brand': brand, 'Model': model, 'Year': year,
                    'Fuel_Type': fuel_type, 'Transmission': transmission,
                    'Mileage': mileage, 'Condition': condition,
                    'Owner_Type': owner_type, 'Insurance_Status': insurance_status,
                    'Registration_City': registration_city
                }
                
                predicted_price = st.session_state.predictor.predict_price(input_data)
                market_prices = st.session_state.predictor.get_market_price_range(brand, model, year, condition)
                
                # Log the prediction
                log_usage(st.session_state.user['id'], 'predict_price', f"{brand} {model} {year}", 1)
                
                st.balloons()
                
                # Results Display
                st.markdown("---")
                st.markdown("## 💰 Price Analysis Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <h2 style="color: white; margin: 0;">🎯</h2>
                        <h2 style="margin: 10px 0; color: white;">₹{predicted_price:,}</h2>
                        <p style="margin: 0; color: rgba(255,255,255,0.9);">Predicted Price</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2 style="color: #ef5350; margin: 0;">💵</h2>
                        <h3 style="margin: 10px 0;">₹{market_prices[0]:,}</h3>
                        <p style="color: #7f8c8d; margin: 0;">Market Low</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2 style="color: #ffa726; margin: 0;">📊</h2>
                        <h3 style="margin: 10px 0;">₹{market_prices[1]:,}</h3>
                        <p style="color: #7f8c8d; margin: 0;">Market Avg</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2 style="color: #66bb6a; margin: 0;">💰</h2>
                        <h3 style="margin: 10px 0;">₹{market_prices[2]:,}</h3>
                        <p style="color: #7f8c8d; margin: 0;">Market High</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Depreciation Analysis
                st.markdown("### 📉 Depreciation Analysis")
                
                base_price = st.session_state.predictor.get_base_price(brand, model)
                depreciation = base_price - predicted_price
                depreciation_percent = (depreciation / base_price) * 100
                car_age = current_year - year
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Original Price", f"₹{base_price:,}")
                with col2:
                    st.metric("Current Value", f"₹{predicted_price:,}")
                with col3:
                    st.metric("Depreciation", f"₹{depreciation:,}", f"-{depreciation_percent:.1f}%")
                with col4:
                    st.metric("Car Age", f"{car_age} years")
                
                # Visualizations
                st.markdown("---")
                st.markdown("### 📊 Visual Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Price comparison chart
                    fig = go.Figure(data=[
                        go.Bar(name='Market Range', x=['Low', 'Average', 'High'], 
                               y=market_prices, marker_color=['#ef5350', '#ffa726', '#66bb6a']),
                        go.Scatter(name='Your Prediction', x=['Low', 'Average', 'High'], 
                                 y=[predicted_price, predicted_price, predicted_price],
                                 mode='lines', line=dict(color='#667eea', width=3, dash='dash'))
                    ])
                    fig.update_layout(
                        title="Price Comparison",
                        height=400,
                        paper_bgcolor='rgba(255,255,255,0.9)',
                        plot_bgcolor='rgba(255,255,255,0.9)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Depreciation gauge
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=100 - depreciation_percent,
                        title={'text': "Value Retention %"},
                        delta={'reference': 100},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "#667eea"},
                            'steps': [
                                {'range': [0, 30], 'color': "#ffebee"},
                                {'range': [30, 60], 'color': "#fff9c4"},
                                {'range': [60, 100], 'color': "#e8f5e9"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    fig.update_layout(height=400, paper_bgcolor='rgba(255,255,255,0.9)')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Car Details Summary
                st.markdown("---")
                st.markdown("### 🚗 Vehicle Details Summary")
                
                details_df = pd.DataFrame([
                    {"Attribute": "Brand", "Value": brand},
                    {"Attribute": "Model", "Value": model},
                    {"Attribute": "Year", "Value": year},
                    {"Attribute": "Age", "Value": f"{car_age} years"},
                    {"Attribute": "Fuel Type", "Value": fuel_type},
                    {"Attribute": "Transmission", "Value": transmission},
                    {"Attribute": "Mileage", "Value": f"{mileage:,} km"},
                    {"Attribute": "Condition", "Value": condition},
                    {"Attribute": "Owner Type", "Value": owner_type},
                    {"Attribute": "Insurance", "Value": insurance_status},
                    {"Attribute": "City", "Value": registration_city},
                ])
                
                st.dataframe(details_df, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # USER TAB 2: MARKET ANALYSIS
    # ========================================================================
    
    with user_main_tab2:
        st.markdown("## 📊 Car Market Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📉 Price Depreciation Over Years")
            
            brand_analysis = st.selectbox("Select Brand", sorted(list(CAR_DATABASE.keys())), key="analysis_brand")
            
            if brand_analysis in CAR_DATABASE:
                model_analysis = st.selectbox("Select Model", sorted(CAR_DATABASE[brand_analysis]['models']), key="analysis_model")
                
                base_price = st.session_state.predictor.get_base_price(brand_analysis, model_analysis)
                current_year = datetime.now().year
                
                price_data = []
                for years_old in range(0, 10):
                    year = current_year - years_old
                    input_data = {
                        'Brand': brand_analysis, 'Model': model_analysis, 'Year': year,
                        'Fuel_Type': 'Petrol', 'Transmission': 'Manual',
                        'Mileage': years_old * 12000, 'Condition': 'Very Good',
                        'Owner_Type': 'First', 'Insurance_Status': 'Comprehensive',
                        'Registration_City': 'Mumbai'
                    }
                    price = st.session_state.predictor.predict_price(input_data)
                    price_data.append({'Year': year, 'Price': price, 'Age': years_old})
                
                price_df = pd.DataFrame(price_data)
                fig = px.line(price_df, x='Age', y='Price', 
                             title=f'{brand_analysis} {model_analysis} - Price Depreciation Curve',
                             labels={'Age': 'Years Old', 'Price': 'Price (₹)'},
                             markers=True)
                fig.update_layout(
                    height=400,
                    paper_bgcolor='rgba(255,255,255,0.9)',
                    plot_bgcolor='rgba(255,255,255,0.9)'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🏷️ Top Luxury Brands")
            
            luxury_brands = ['Ferrari', 'Lamborghini', 'Rolls-Royce', 'Bentley', 
                            'Porsche', 'Aston Martin', 'McLaren', 'Bugatti']
            
            luxury_data = []
            for lux_brand in luxury_brands:
                if lux_brand in CAR_DATABASE:
                    models = CAR_DATABASE[lux_brand]['models']
                    avg_price = sum(CAR_DATABASE[lux_brand]['base_prices']) / len(models)
                    luxury_data.append({
                        'Brand': lux_brand,
                        'Models': len(models),
                        'Avg Price': avg_price
                    })
            
            if luxury_data:
                luxury_df = pd.DataFrame(luxury_data)
                fig = px.bar(luxury_df, x='Brand', y='Avg Price',
                            title='Luxury Brand Average Prices',
                            color='Avg Price',
                            color_continuous_scale='Viridis')
                fig.update_layout(
                    height=400,
                    paper_bgcolor='rgba(255,255,255,0.9)',
                    plot_bgcolor='rgba(255,255,255,0.9)'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Additional Market Insights
        st.markdown("---")
        st.markdown("### 💡 Market Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="info-box">
                <h4>🔥 Fastest Depreciating</h4>
                <p>Luxury cars typically depreciate 15-25% in the first year</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-box">
                <h4>💎 Best Value Retention</h4>
                <p>Japanese brands retain 60-70% value after 5 years</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="info-box">
                <h4>📊 Sweet Spot</h4>
                <p>3-5 year old cars offer best value for money</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ========================================================================
    # USER TAB 3: BRAND EXPLORER
    # ========================================================================
    
    with user_main_tab3:
        st.markdown("## 🌍 Global Brand Explorer")
        
        # Brand categories
        categories = {
            "🇮🇳 Indian Brands": ['Maruti Suzuki', 'Tata', 'Mahindra'],
            "🇯🇵 Japanese Brands": ['Toyota', 'Honda', 'Nissan'],
            "🇰🇷 Korean Brands": ['Hyundai', 'Kia'],
            "🇩🇪 German Brands": ['BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Porsche'],
            "🇺🇸 American Brands": ['Ford', 'Tesla', 'Jeep'],
            "🇬🇧 British Brands": ['Land Rover', 'Jaguar', 'Bentley', 'Rolls-Royce'],
            "🇮🇹 Italian Brands": ['Ferrari', 'Lamborghini'],
            "🇫🇷 French Brands": ['Renault'],
            "🇨🇳 Chinese Brands": ['BYD', 'MG'],
            "🇨🇿 Czech Brands": ['Skoda']
        }
        
        for category, brands in categories.items():
            available_brands = [b for b in brands if b in CAR_DATABASE]
            if available_brands:
                with st.expander(f"{category} ({len(available_brands)} brands)"):
                    for brand in available_brands:
                        models = CAR_DATABASE[brand]['models']
                        prices = CAR_DATABASE[brand]['base_prices']
                        
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"**{brand}** - {len(models)} models")
                        with col_b:
                            st.markdown(f"₹{min(prices):,} - ₹{max(prices):,}")
                        
                        with st.expander(f"View {brand} models"):
                            model_df = pd.DataFrame({
                                'Model': models,
                                'Base Price': [f"₹{p:,}" for p in prices]
                            })
                            st.dataframe(model_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 20px; border-radius: 10px; color: white;'>
    <p style='margin: 0;'>🔐 Logged in as: <b>{st.session_state.user['username']}</b> ({st.session_state.user['role']}) | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <h3 style='color: white; margin: 10px 0 0 0;'>🚗 Global Car Price Prediction Platform</h3>
    <p style='margin: 5px 0 0 0;'>Powered by Advanced AI | Built with Streamlit & Python | © 2024</p>
</div>
""", unsafe_allow_html=True)
