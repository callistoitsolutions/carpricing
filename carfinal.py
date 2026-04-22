# ======================================================
# GLOBAL ULTRA ACCURATE CAR PRICE PREDICTION SYSTEM
# ======================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from datetime import datetime
import io
import base64

# ========================================
# COMPREHENSIVE GLOBAL CAR DATABASE
# ========================================

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
    'Mazda': {
        'models': ['Mazda2', 'Mazda3', 'Mazda6', 'CX-3', 'CX-5', 'CX-9', 'MX-5 Miata', 'CX-30'],
        'base_prices': [2500000, 3000000, 4000000, 3200000, 3800000, 5500000, 4500000, 3500000]
    },
    'Mitsubishi': {
        'models': ['Mirage', 'Lancer', 'Outlander', 'Pajero Sport', 'Eclipse Cross', 'Montero'],
        'base_prices': [1500000, 2000000, 3500000, 3800000, 3200000, 5000000]
    },
    'Suzuki': {
        'models': ['Vitara', 'S-Cross', 'Jimny', 'Swift Sport'],
        'base_prices': [2500000, 2000000, 1800000, 1500000]
    },
    'Subaru': {
        'models': ['Impreza', 'Legacy', 'Outback', 'Forester', 'WRX', 'BRZ', 'Ascent'],
        'base_prices': [3000000, 3500000, 4000000, 3800000, 4500000, 4000000, 5000000]
    },
    'Lexus': {
        'models': ['ES', 'IS', 'GS', 'LS', 'NX', 'RX', 'LX', 'UX', 'LC'],
        'base_prices': [6000000, 6500000, 7500000, 15000000, 7000000, 8500000, 20000000, 5500000, 18000000]
    },
    'Infiniti': {
        'models': ['Q50', 'Q60', 'Q70', 'QX50', 'QX60', 'QX80'],
        'base_prices': [5500000, 6500000, 7000000, 6000000, 7500000, 9500000]
    },
    'Acura': {
        'models': ['ILX', 'TLX', 'RLX', 'RDX', 'MDX', 'NSX'],
        'base_prices': [4500000, 5500000, 7000000, 6000000, 7500000, 25000000]
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
    'Genesis': {
        'models': ['G70', 'G80', 'G90', 'GV60', 'GV70', 'GV80'],
        'base_prices': [6500000, 8000000, 12000000, 7500000, 8500000, 10000000]
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
    'Chevrolet': {
        'models': ['Spark', 'Cruze', 'Malibu', 'Camaro', 'Corvette', 'Equinox', 'Traverse', 'Tahoe', 'Suburban', 'Silverado'],
        'base_prices': [1000000, 2500000, 3500000, 6500000, 12000000, 3800000, 5500000, 7500000, 8500000, 5000000]
    },
    'Jeep': {
        'models': ['Compass', 'Meridian', 'Wrangler', 'Grand Cherokee', 'Cherokee', 'Renegade', 'Gladiator'],
        'base_prices': [2000000, 3500000, 6500000, 8500000, 4500000, 2500000, 7000000]
    },
    'Dodge': {
        'models': ['Challenger', 'Charger', 'Durango', 'Journey', 'Grand Caravan'],
        'base_prices': [6000000, 6500000, 5500000, 3500000, 4000000]
    },
    'Chrysler': {
        'models': ['300', 'Pacifica', 'Voyager'],
        'base_prices': [5500000, 5000000, 4500000]
    },
    'Cadillac': {
        'models': ['CT4', 'CT5', 'XT4', 'XT5', 'XT6', 'Escalade', 'Lyriq'],
        'base_prices': [6000000, 7500000, 6500000, 7500000, 8500000, 12000000, 10000000]
    },
    'Tesla': {
        'models': ['Model 3', 'Model S', 'Model X', 'Model Y', 'Cybertruck', 'Roadster'],
        'base_prices': [6000000, 12000000, 13000000, 7500000, 8500000, 28000000]
    },
    'GMC': {
        'models': ['Sierra', 'Canyon', 'Terrain', 'Acadia', 'Yukon', 'Hummer EV'],
        'base_prices': [5500000, 4000000, 4500000, 5500000, 8000000, 15000000]
    },
    'Lincoln': {
        'models': ['Corsair', 'Nautilus', 'Aviator', 'Navigator'],
        'base_prices': [6500000, 7500000, 8500000, 11000000]
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
    'Aston Martin': {
        'models': ['Vantage', 'DB11', 'DBS', 'DBX', 'Rapide'],
        'base_prices': [28000000, 35000000, 45000000, 38000000, 40000000]
    },
    'McLaren': {
        'models': ['GT', '570S', '720S', 'Artura', 'P1'],
        'base_prices': [32000000, 28000000, 48000000, 38000000, 150000000]
    },
    'Lotus': {
        'models': ['Elise', 'Exige', 'Evora', 'Emira'],
        'base_prices': [8000000, 10000000, 12000000, 9500000]
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
    'Maserati': {
        'models': ['Ghibli', 'Quattroporte', 'Levante', 'GranTurismo', 'MC20'],
        'base_prices': [15000000, 18000000, 16000000, 22000000, 45000000]
    },
    'Alfa Romeo': {
        'models': ['Giulia', 'Stelvio', '4C'],
        'base_prices': [6500000, 7500000, 8500000]
    },
    'Fiat': {
        'models': ['500', 'Panda', 'Tipo', '500X', '500L'],
        'base_prices': [1500000, 1200000, 1800000, 2000000, 2200000]
    },
    
    # FRENCH BRANDS
    'Renault': {
        'models': ['Kwid', 'Triber', 'Kiger', 'Duster', 'Captur', 'Koleos', 'Megane', 'Clio'],
        'base_prices': [400000, 650000, 750000, 1100000, 1500000, 3500000, 2500000, 2000000]
    },
    'Peugeot': {
        'models': ['208', '308', '508', '2008', '3008', '5008'],
        'base_prices': [2000000, 2800000, 4500000, 2500000, 3500000, 4500000]
    },
    'Citroën': {
        'models': ['C3', 'C3 Aircross', 'C5 Aircross', 'Berlingo'],
        'base_prices': [700000, 900000, 3500000, 2500000]
    },
    'Bugatti': {
        'models': ['Chiron', 'Divo', 'Centodieci'],
        'base_prices': [280000000, 500000000, 800000000]
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
    'Geely': {
        'models': ['Coolray', 'Azkarra', 'Okavango', 'Emgrand'],
        'base_prices': [2000000, 2500000, 2800000, 1500000]
    },
    'NIO': {
        'models': ['ES6', 'ES8', 'ET7', 'ET5'],
        'base_prices': [6500000, 8000000, 7500000, 5500000]
    },
    'Xpeng': {
        'models': ['P7', 'P5', 'G3', 'G9'],
        'base_prices': [5500000, 4500000, 4000000, 6500000]
    },
    
    # SWEDISH BRANDS
    'Volvo': {
        'models': ['S60', 'S90', 'V60', 'V90', 'XC40', 'XC60', 'XC90', 'C40 Recharge'],
        'base_prices': [6500000, 8500000, 7000000, 8000000, 5500000, 7500000, 10000000, 7500000]
    },
    'Polestar': {
        'models': ['Polestar 2', 'Polestar 3'],
        'base_prices': [6500000, 9500000]
    },
    'Koenigsegg': {
        'models': ['Jesko', 'Gemera', 'Regera'],
        'base_prices': [300000000, 180000000, 200000000]
    },
    
    # CZECH BRANDS
    'Skoda': {
        'models': ['Rapid', 'Slavia', 'Kushaq', 'Kodiaq', 'Octavia', 'Superb', 'Karoq'],
        'base_prices': [800000, 1100000, 1200000, 3500000, 2800000, 3500000, 2500000]
    },
}

FUEL_TYPES = ["Petrol", "Diesel", "CNG", "Electric", "Hybrid", "LPG", "Hydrogen"]
TRANSMISSIONS = ["Manual", "Automatic", "CVT", "DCT", "AMT", "Sequential", "Dual-Clutch"]
CAR_CONDITIONS = ["Excellent", "Very Good", "Good", "Fair", "Poor"]
OWNER_TYPES = ["First", "Second", "Third", "Fourth & Above"]
INSURANCE_STATUS = ["Comprehensive", "Third Party", "Expired", "No Insurance"]
COLORS = ["White", "Black", "Silver", "Grey", "Red", "Blue", "Brown", "Green", "Yellow", "Orange", "Purple", "Gold", "Other"]
CITIES = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata", "Ahmedabad", "Surat", "Jaipur", 
          "Lucknow", "Chandigarh", "London", "New York", "Tokyo", "Dubai", "Paris", "Berlin", "Los Angeles", "Shanghai"]

# ========================================
# ULTRA ACCURATE PRICE PREDICTION ENGINE
# ========================================

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
                "Hybrid": 1.35, "LPG": 0.88, "Hydrogen": 1.75
            }
            base_price *= fuel_multipliers.get(input_data['Fuel_Type'], 1.0)
            
            # Transmission adjustment
            transmission_multipliers = {
                "Manual": 1.0, "Automatic": 1.18, "CVT": 1.15, "DCT": 1.22, 
                "AMT": 1.08, "Sequential": 1.25, "Dual-Clutch": 1.23
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
                "Pune": 1.03, "Hyderabad": 1.03, "London": 1.15, "New York": 1.18,
                "Tokyo": 1.12, "Dubai": 1.20, "Paris": 1.14, "Berlin": 1.08
            }
            final_price *= city_premium.get(input_data['Registration_City'], 1.0)
            
            # Insurance adjustment
            if input_data['Insurance_Status'] == 'Comprehensive':
                final_price *= 1.03
            elif input_data['Insurance_Status'] == 'Expired':
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

    def load_csv_data(self, uploaded_file):
        """Load CSV data for training"""
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Successfully loaded {len(df)} records from CSV")
            return df
        except Exception as e:
            st.error(f"Error loading CSV: {str(e)}")
            return None

    def train_from_csv(self, df, selected_brand=None, selected_model=None):
        """Train model from CSV data with optional filtering"""
        try:
            st.info("🔄 Training advanced model from CSV data...")
            
            df_processed = df.copy()
            
            # Handle Price_INR
            if 'Price_INR' in df_processed.columns and 'Price' not in df_processed.columns:
                df_processed['Price'] = df_processed['Price_INR']
                st.success("✅ Mapped 'Price_INR' → 'Price'")
            
            # Flexible column mapping
            column_mapping = {
                'brand': 'Brand', 'car_brand': 'Brand',
                'model': 'Model', 'car_model': 'Model',
                'year': 'Year', 'manufacture_year': 'Year',
                'fuel': 'Fuel_Type', 'fuel_type': 'Fuel_Type',
                'transmission': 'Transmission',
                'mileage': 'Mileage', 'km_driven': 'Mileage',
                'condition': 'Condition', 'car_condition': 'Condition',
                'price': 'Price', 'selling_price': 'Price', 'price_inr': 'Price'
            }
            
            for old_col, new_col in column_mapping.items():
                matching_cols = [col for col in df_processed.columns if str(col).lower() == old_col.lower()]
                if matching_cols and new_col not in df_processed.columns:
                    actual_col = matching_cols[0]
                    df_processed[new_col] = df_processed[actual_col]
                    st.success(f"✅ Mapped '{actual_col}' → '{new_col}'")
            
            # Filter by brand and model if selected
            if selected_brand and selected_brand != "All":
                df_processed = df_processed[df_processed['Brand'] == selected_brand]
                st.info(f"🔍 Filtered for brand: {selected_brand}")
                
                if selected_model and selected_model != "All":
                    df_processed = df_processed[df_processed['Model'] == selected_model]
                    st.info(f"🔍 Filtered for model: {selected_model}")
            
            # Required columns
            required_columns = ['Brand', 'Model', 'Year', 'Fuel_Type', 'Transmission', 
                              'Mileage', 'Condition', 'Price']
            
            missing_columns = [col for col in required_columns if col not in df_processed.columns]
            if missing_columns:
                st.error(f"Missing columns: {missing_columns}")
                return False
            
            # Clean data
            df_clean = df_processed.dropna()
            if len(df_clean) < 5:
                st.error("Not enough data after cleaning")
                return False
            
            st.success(f"✅ Using {len(df_clean)} records for training")
            
            # Prepare features
            features = ['Brand', 'Model', 'Year', 'Fuel_Type', 'Transmission', 'Mileage', 'Condition']
            X = df_clean[features]
            y = df_clean['Price']
            
            # Show filtered data summary
            if selected_brand or selected_model:
                st.subheader("📊 Filtered Data Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Records", len(df_clean))
                with col2:
                    st.metric("Avg Price", f"₹{y.mean():,.0f}")
                with col3:
                    st.metric("Price Range", f"₹{y.min():,.0f} - ₹{y.max():,.0f}")
                
                # Show sample of filtered data
                with st.expander("View Filtered Data"):
                    st.dataframe(df_clean.head(10))
            
            # Encode categorical variables
            categorical_features = ['Brand', 'Model', 'Fuel_Type', 'Transmission', 'Condition']
            for feature in categorical_features:
                self.encoders[feature] = LabelEncoder()
                X[feature] = self.encoders[feature].fit_transform(X[feature].astype(str))
            
            # Train model
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X, y)
            self.is_trained = True
            self.training_data = df_clean
            
            # Evaluate
            y_pred = self.model.predict(X)
            r2 = r2_score(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            
            st.success(f"✅ Model trained! R²: {r2:.3f}, MAE: ₹{mae:,.0f}")
            return True
            
        except Exception as e:
            st.error(f"Training error: {str(e)}")
            return False

    def predict_price(self, input_data):
        """Main prediction function"""
        if self.is_trained:
            try:
                features = ['Brand', 'Model', 'Year', 'Fuel_Type', 'Transmission', 'Mileage', 'Condition']
                input_df = pd.DataFrame([input_data])
                
                for feature in ['Brand', 'Model', 'Fuel_Type', 'Transmission', 'Condition']:
                    if feature in self.encoders:
                        try:
                            input_df[feature] = self.encoders[feature].transform([input_data[feature]])[0]
                        except:
                            return self.calculate_accurate_price(input_data)
                
                prediction = self.model.predict(input_df[features])[0]
                return max(100000, int(prediction))
            except:
                return self.calculate_accurate_price(input_data)
        else:
            return self.calculate_accurate_price(input_data)

# ========================================
# STREAMLIT UI COMPONENTS
# ========================================

def main():
    if 'predictor' not in st.session_state:
        st.session_state.predictor = UltraAccurateCarPricePredictor()
    
    st.set_page_config(
        page_title="Global Car Price Predictor", 
        layout="wide", 
        initial_sidebar_state="expanded"
    )
    
    st.title("🚗 Global Ultra Accurate Car Price Prediction System")
    st.markdown("### **Real Market Prices with Advanced Depreciation Analysis - Worldwide Coverage**")
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", [
            "🎯 Price Prediction", 
            "📊 Market Analysis",
            "📁 CSV Training",
            "🌍 Brand Explorer"
        ])
        
        st.markdown("---")
        st.subheader("🌍 Global Database")
        total_brands = len(CAR_DATABASE)
        total_models = sum(len(CAR_DATABASE[brand]['models']) for brand in CAR_DATABASE)
        st.info(f"""
        **Coverage:**
        - 🏢 Brands: {total_brands}
        - 🚗 Models: {total_models}
        - 🌎 Worldwide
        - 💎 Luxury & Super Luxury
        """)
    
    # Page routing
    if page == "🎯 Price Prediction":
        show_prediction_interface()
    elif page == "📊 Market Analysis":
        show_market_analysis()
    elif page == "📁 CSV Training":
        show_csv_training()
    elif page == "🌍 Brand Explorer":
        show_brand_explorer()

def show_prediction_interface():
    st.subheader("🎯 Ultra Accurate Price Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brand = st.selectbox("Select Brand", sorted(list(CAR_DATABASE.keys())))
        
        if brand in CAR_DATABASE:
            model = st.selectbox("Select Model", sorted(CAR_DATABASE[brand]['models']))
            base_price = st.session_state.predictor.get_base_price(brand, model)
            st.info(f"**Base New Price:** ₹{base_price:,}")
        
        current_year = datetime.now().year
        year = st.slider("Manufacturing Year", 2000, current_year, current_year - 3)
        fuel_type = st.selectbox("Fuel Type", FUEL_TYPES)
        transmission = st.selectbox("Transmission", TRANSMISSIONS)
    
    with col2:
        mileage = st.number_input("Mileage (km)", min_value=0, max_value=500000, value=30000, step=5000)
        condition = st.selectbox("Condition", CAR_CONDITIONS)
        owner_type = st.selectbox("Owner Type", OWNER_TYPES)
        insurance_status = st.selectbox("Insurance Status", INSURANCE_STATUS)
        registration_city = st.selectbox("Registration City", sorted(CITIES))
    
    if st.button("🎯 Get Ultra Accurate Price", type="primary", use_container_width=True):
        with st.spinner('Calculating ultra accurate price...'):
            input_data = {
                'Brand': brand, 'Model': model, 'Year': year,
                'Fuel_Type': fuel_type, 'Transmission': transmission,
                'Mileage': mileage, 'Condition': condition,
                'Owner_Type': owner_type, 'Insurance_Status': insurance_status,
                'Registration_City': registration_city
            }
            
            predicted_price = st.session_state.predictor.predict_price(input_data)
            market_prices = st.session_state.predictor.get_market_price_range(brand, model, year, condition)
            
            st.success(f"## 🎯 Predicted Price: ₹{predicted_price:,}")
            
            st.subheader("📊 Market Comparison")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Market Low", f"₹{market_prices[0]:,}")
            with col2:
                st.metric("Market Average", f"₹{market_prices[1]:,}")
            with col3:
                st.metric("Market High", f"₹{market_prices[2]:,}")
            
            st.subheader("📈 Price Analysis")
            base_price = st.session_state.predictor.get_base_price(brand, model)
            depreciation = base_price - predicted_price
            depreciation_percent = (depreciation / base_price) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Original Price", f"₹{base_price:,}")
            with col2:
                st.metric("Total Depreciation", f"₹{depreciation:,}", f"-{depreciation_percent:.1f}%")

def show_market_analysis():
    st.subheader("📊 Car Market Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brand = st.selectbox("Select Brand", sorted(list(CAR_DATABASE.keys())))
        
        if brand in CAR_DATABASE:
            model = st.selectbox("Select Model", sorted(CAR_DATABASE[brand]['models']))
            
            st.subheader("💰 Price Depreciation Over Years")
            
            base_price = st.session_state.predictor.get_base_price(brand, model)
            current_year = datetime.now().year
            
            price_data = []
            for years_old in range(0, 10):
                year = current_year - years_old
                input_data = {
                    'Brand': brand, 'Model': model, 'Year': year,
                    'Fuel_Type': 'Petrol', 'Transmission': 'Manual',
                    'Mileage': years_old * 12000, 'Condition': 'Very Good',
                    'Owner_Type': 'First', 'Insurance_Status': 'Comprehensive',
                    'Registration_City': 'Mumbai'
                }
                price = st.session_state.predictor.predict_price(input_data)
                price_data.append({'Year': year, 'Price': price, 'Age': years_old})
            
            price_df = pd.DataFrame(price_data)
            fig = px.line(price_df, x='Age', y='Price', 
                         title=f'{brand} {model} - Price Depreciation Curve',
                         labels={'Age': 'Years Old', 'Price': 'Price (₹)'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Top Luxury Brands")
        luxury_brands = ['Ferrari', 'Lamborghini', 'Rolls-Royce', 'Bentley', 
                        'Bugatti', 'McLaren', 'Porsche', 'Aston Martin']
        
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
                        color='Avg Price')
            st.plotly_chart(fig, use_container_width=True)

def show_csv_training():
    st.subheader("📁 CSV Data Training with Brand/Model Filter")
    
    st.info("""
    **Upload CSV and optionally filter by specific Brand/Model for targeted training.**
    The system will automatically recognize different column names.
    """)
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
    
    if uploaded_file is not None:
        df = st.session_state.predictor.load_csv_data(uploaded_file)
        
        if df is not None:
            st.write("### Dataset Preview")
            st.dataframe(df.head())
            
            # Brand and Model filter options
            st.subheader("🔍 Filter Training Data (Optional)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Get unique brands from CSV
                if 'Brand' in df.columns:
                    available_brands = ["All"] + sorted(df['Brand'].unique().tolist())
                    selected_brand = st.selectbox("Filter by Brand", available_brands)
                else:
                    selected_brand = "All"
                    st.warning("No 'Brand' column found in CSV")
            
            with col2:
                # Get unique models for selected brand
                if 'Model' in df.columns and selected_brand != "All":
                    brand_df = df[df['Brand'] == selected_brand]
                    available_models = ["All"] + sorted(brand_df['Model'].unique().tolist())
                    selected_model = st.selectbox("Filter by Model", available_models)
                else:
                    selected_model = "All"
            
            # Show filtered count
            if selected_brand != "All":
                filtered_df = df[df['Brand'] == selected_brand]
                if selected_model != "All":
                    filtered_df = filtered_df[filtered_df['Model'] == selected_model]
                st.info(f"📊 Will train on {len(filtered_df)} records after filtering")
            
            if st.button("🚀 Train Model from CSV", type="primary"):
                success = st.session_state.predictor.train_from_csv(
                    df, 
                    selected_brand if selected_brand != "All" else None,
                    selected_model if selected_model != "All" else None
                )
                if success:
                    st.balloons()
                    st.success("Model trained successfully! Now using AI for predictions.")

def show_brand_explorer():
    st.subheader("🌍 Global Brand Explorer")
    
    # Brand categories
    categories = {
        "🇮🇳 Indian Brands": ['Maruti Suzuki', 'Tata', 'Mahindra'],
        "🇯🇵 Japanese Brands": ['Toyota', 'Honda', 'Nissan', 'Mazda', 'Mitsubishi', 'Suzuki', 'Subaru', 'Lexus', 'Infiniti', 'Acura'],
        "🇰🇷 Korean Brands": ['Hyundai', 'Kia', 'Genesis'],
        "🇩🇪 German Brands": ['BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Porsche'],
        "🇺🇸 American Brands": ['Ford', 'Chevrolet', 'Jeep', 'Dodge', 'Chrysler', 'Cadillac', 'Tesla', 'GMC', 'Lincoln'],
        "🇬🇧 British Brands": ['Land Rover', 'Jaguar', 'Bentley', 'Rolls-Royce', 'Aston Martin', 'McLaren', 'Lotus'],
        "🇮🇹 Italian Brands": ['Ferrari', 'Lamborghini', 'Maserati', 'Alfa Romeo', 'Fiat'],
        "🇫🇷 French Brands": ['Renault', 'Peugeot', 'Citroën', 'Bugatti'],
        "🇨🇳 Chinese Brands": ['BYD', 'MG', 'Geely', 'NIO', 'Xpeng'],
        "🇸🇪 Swedish Brands": ['Volvo', 'Polestar', 'Koenigsegg'],
        "🇨🇿 Czech Brands": ['Skoda']
    }
    
    for category, brands in categories.items():
        with st.expander(f"{category} ({len(brands)} brands)"):
            for brand in brands:
                if brand in CAR_DATABASE:
                    models = CAR_DATABASE[brand]['models']
                    prices = CAR_DATABASE[brand]['base_prices']
                    st.write(f"**{brand}** - {len(models)} models")
                    st.write(f"Price Range: ₹{min(prices):,} - ₹{max(prices):,}")
                    with st.expander(f"View {brand} models"):
                        for i, model in enumerate(models):
                            st.write(f"• {model} - ₹{prices[i]:,}")

if __name__ == "__main__":
    main()
