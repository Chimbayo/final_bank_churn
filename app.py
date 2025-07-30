# Import necessary libraries
from flask import Flask, render_template, request, jsonify  # Flask web framework components
import joblib  # For loading the trained machine learning model
import numpy as np  # For numerical operations
import pandas as pd # For data manipulation and analysis
import io  # For handling CSV data in memor
from faker import Faker # For generating fake data
import psycopg2 # PostgreSQL database adapter for Python
from psycopg2.extras import RealDictCursor, execute_batch  # For returning query results as dictionaries and batch execution
import random # For generating random numbers
import os # For environment variable management
from dotenv import load_dotenv # For loading environment variables from a .env file
# Initialize Flask application
app = Flask(__name__)

# ==============================================
# DATABASE CONFIGURATION
# ==============================================
load_dotenv()
# Configure PostgreSQL connection settings

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    Customer_ID SERIAL PRIMARY KEY,
    Age INT,
    Gender INT,
    District INT,
    Region INT,
    Location_Type INT,
    Customer_Type INT,
    Employment_Status INT,
    Income_Level FLOAT,
    Education_Level INT,
    Tenure INT,
    Balance FLOAT,
    Credit_Score INT,
    Outstanding_Loans FLOAT,
    Num_Of_Products INT,
    Mobile_Banking_Usage INT,
    Number_of_Transactions_per_Month INT,
    Num_Of_Complaints INT,
    Proximity_to_NearestBranch_or_ATM_km FLOAT,
    Mobile_Network_Quality INT,
    Owns_Mobile_Phone INT,
    prediction INT,
    Churn_Probability FLOAT
);
""")

conn.commit()
cursor.close()
conn.close()

# ==============================================
# MODEL LOADING
# ==============================================

# Load the pre-trained LightGBM model from file
model = joblib.load('lgb_model.pkl')
# ==============================================
# ROUTE DEFINITIONS
# ==============================================

@app.route('/customers')
def customers_page():
    return render_template("customers.html")

# Home page route - redirects to login
@app.route('/')
def home():
    """Render the login page as the home page"""
    return render_template('index.html')
# About page route
@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')
# Contacts page route
@app.route('/contacts')
def contacts():
    """Render the contacts page"""
    return render_template('contacts.html')
# ==============================================
# At-Risk Customers Page
@app.route('/AtRiskcustomers')
def at_risk_customers():
    """
    Render the At-Risk Customers page 
    """
    return render_template('AtRiskcustomers.html')
# Login page route
@app.route('/index')
def login():
    """Render the login page"""
    return render_template('index.html')

# Main dashboard/churn analysis page
@app.route('/churn')
def dashboard():
    """
    Render the churn analysis dashboard with customer data
    and total customer count
    """
    try:
        # Create a database cursor
        conn = get_db_connection()
        cursor = conn.cursor()

        
        # Execute query to get customer data
        cursor.execute("SELECT * FROM customers LIMIT 10")  # Sample customers
        customers = cursor.fetchall()
        
        # Execute query to get total customer count
        cursor.execute("SELECT COUNT(*) as total_customers FROM customers")
        count_result = cursor.fetchone()
        total_customers = count_result['total_customers']
        
        # Close the cursor
        cursor.close()
        
        # Render template with both customer data and total count
        return render_template('churn.html', 
                            customers=customers,
                            total_customers=total_customers)
    
    except Exception as e:
        print("Database error:", str(e))
        return render_template('churn.html', 
                            customers=[], 
                            total_customers=0,
                            error=str(e))
        

# Constants for data generation
GENDER_MAP = {0: "Female", 1: "Male"}
REGION_MAP = {0: "Southern", 1: "Northern", 2: "Central"}
CUSTOMER_TYPE_MAP = {0: "Retail", 1: "SME", 2: "Corporate"}
EMPLOYMENT_STATUS_MAP = {0: "Self Employed", 1: "Not Employed", 2: "Employed"}
EDUCATION_LEVEL_MAP = {0: "Primary", 1: "Secondary", 2: "Tertiary"}
NET_QUALITY_MAP = {0: "Fair", 1: "Poor", 2: "Good"}
PHONE_MAP = {0: "Yes", 1: "No"}
MOBILE_BANK_MAP = {0: "No", 1: "Yes"}
LOCATION_TYPE_MAP = {0: "Rural", 1: "Urban", 2: "Semi Urban"}
DISTRICT_MAP = {
    0: "Zomba", 1: "Thyolo", 2: "Chikwawa", 3: "Nkhata Bay", 4: "Machinga",
    5: "Karonga", 6: "Dedza", 7: "Chiradzulu", 8: "Mchinji", 9: "Ntchisi",
    10: "Kasungu", 11: "Chitipa", 12: "Nkhotakota", 13: "Neno", 14: "Mangochi",
    15: "Mulanje", 16: "Mzimba", 17: "Blantyre", 18: "Nsanje", 19: "Phalombe",
    20: "Likoma", 21: "Salima", 22: "Lilongwe", 23: "Mwanza", 24: "Rumphi",
    25: "Balaka", 26: "Dowa", 27: "Ntcheu", 28: "Unknown", 29: "Unknown"
}

# Reverse mappings for categorical to numerical conversion
REVERSE_MAPS = {
    'Gender': {v: k for k, v in GENDER_MAP.items()},
    'Region': {v: k for k, v in REGION_MAP.items()},
    'Customer_Type': {v: k for k, v in CUSTOMER_TYPE_MAP.items()},
    'Employment_Status': {v: k for k, v in EMPLOYMENT_STATUS_MAP.items()},
    'Education_Level': {v: k for k, v in EDUCATION_LEVEL_MAP.items()},
    'Mobile_Network_Quality': {v: k for k, v in NET_QUALITY_MAP.items()},
    'Owns_Mobile_Phone': {v: k for k, v in PHONE_MAP.items()},
    'Mobile_Banking_Usage': {v: k for k, v in MOBILE_BANK_MAP.items()},
    'Location_Type': {v: k for k, v in LOCATION_TYPE_MAP.items()},
    'District': {v: k for k, v in DISTRICT_MAP.items()}
}

from flask import jsonify, request
import numpy as np
from psycopg2.extras import execute_batch

@app.route('/replace_all_customers', methods=['POST'])
def replace_all_customers():
    """Replace all customer data with 508 randomly generated records"""
    try:
        n_samples = 508

        # Generate random data with numerical values for database
        random_data = {
            'Age': np.random.randint(18, 80, n_samples).tolist(),
            'Gender': np.random.choice(list(GENDER_MAP.keys()), n_samples).tolist(),
            'District': np.random.choice(list(DISTRICT_MAP.keys()), n_samples).tolist(),
            'Region': np.random.choice(list(REGION_MAP.keys()), n_samples).tolist(),
            'Location_Type': np.random.choice(list(LOCATION_TYPE_MAP.keys()), n_samples).tolist(),
            'Customer_Type': np.random.choice(list(CUSTOMER_TYPE_MAP.keys()), n_samples).tolist(),
            'Employment_Status': np.random.choice(list(EMPLOYMENT_STATUS_MAP.keys()), n_samples).tolist(),
            'Income_Level': np.random.uniform(50000, 1000000, n_samples).tolist(),
            'Education_Level': np.random.choice(list(EDUCATION_LEVEL_MAP.keys()), n_samples).tolist(),
            'Tenure': np.random.randint(1, 15, n_samples).tolist(),
            'Balance': np.random.uniform(1000, 3800000, n_samples).tolist(),
            'Credit_Score': np.random.randint(300, 850, n_samples).tolist(),
            'Outstanding_Loans': np.random.uniform(0, 2000000, n_samples).tolist(),
            'Num_Of_Products': np.random.randint(1, 6, n_samples).tolist(),
            'Mobile_Banking_Usage': np.random.choice(list(MOBILE_BANK_MAP.keys()), n_samples).tolist(),
            'Number_of_Transactions_per_Month': np.random.randint(1, 50, n_samples).tolist(),
            'Num_Of_Complaints': np.random.randint(0, 11, n_samples).tolist(),
            'Proximity_to_NearestBranch_or_ATM_km': np.random.uniform(0.2, 50, n_samples).tolist(),
            'Mobile_Network_Quality': np.random.choice(list(NET_QUALITY_MAP.keys()), n_samples).tolist(),
            'Owns_Mobile_Phone': np.random.choice(list(PHONE_MAP.keys()), n_samples).tolist()
        }

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Start transaction
            cursor.execute("BEGIN")
            cursor.execute("TRUNCATE TABLE customers RESTART IDENTITY")

            insert_query = """
                INSERT INTO customers (
                    Age, Gender, District, Region, Location_Type, Customer_Type,
                    Employment_Status, Income_Level, Education_Level, Tenure,
                    Balance, Credit_Score, Outstanding_Loans, Num_Of_Products,
                    Mobile_Banking_Usage, Number_of_Transactions_per_Month,
                    Num_Of_Complaints, Proximity_to_NearestBranch_or_ATM_km,
                    Mobile_Network_Quality, Owns_Mobile_Phone,
                    prediction, Churn_Probability
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            batch_data = []
            for i in range(n_samples):
                features = np.array([
                    random_data['Age'][i],
                    random_data['Gender'][i],
                    random_data['District'][i],
                    random_data['Region'][i],
                    random_data['Location_Type'][i],
                    random_data['Customer_Type'][i],
                    random_data['Employment_Status'][i],
                    random_data['Income_Level'][i],
                    random_data['Education_Level'][i],
                    random_data['Tenure'][i],
                    random_data['Balance'][i],
                    random_data['Credit_Score'][i],
                    random_data['Outstanding_Loans'][i],
                    random_data['Num_Of_Products'][i],
                    random_data['Mobile_Banking_Usage'][i],
                    random_data['Number_of_Transactions_per_Month'][i],
                    random_data['Num_Of_Complaints'][i],
                    random_data['Proximity_to_NearestBranch_or_ATM_km'][i],
                    random_data['Mobile_Network_Quality'][i],
                    random_data['Owns_Mobile_Phone'][i]
                ]).reshape(1, -1)

                # Predict churn
                probabilities = model.predict_proba(features)
                prob_churn = float(probabilities[0][1])  # ✅ make sure it's a float
                prediction = int(prob_churn >= 0.5)

                if prediction == 0:
                    prob_churn = min(prob_churn + 0.40, 1.0)

                # Append row
                batch_data.append((
                    random_data['Age'][i],
                    random_data['Gender'][i],
                    random_data['District'][i],
                    random_data['Region'][i],
                    random_data['Location_Type'][i],
                    random_data['Customer_Type'][i],
                    random_data['Employment_Status'][i],
                    float(random_data['Income_Level'][i]),
                    random_data['Education_Level'][i],
                    random_data['Tenure'][i],
                    float(random_data['Balance'][i]),
                    random_data['Credit_Score'][i],
                    float(random_data['Outstanding_Loans'][i]),
                    random_data['Num_Of_Products'][i],
                    random_data['Mobile_Banking_Usage'][i],
                    random_data['Number_of_Transactions_per_Month'][i],
                    random_data['Num_Of_Complaints'][i],
                    float(random_data['Proximity_to_NearestBranch_or_ATM_km'][i]),
                    random_data['Mobile_Network_Quality'][i],
                    random_data['Owns_Mobile_Phone'][i],
                    prediction,
                    prob_churn
                ))

            # Execute and commit
            execute_batch(cursor, insert_query, batch_data)
            conn.commit()

            return jsonify({
                "message": f"Successfully updated {n_samples} predictions",
                "success": True
            })

        except Exception as db_error:
            conn.rollback()
            return jsonify({
                "error": f"Database error: {str(db_error)}",
                "success": False
            }), 500
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        return jsonify({
            "error": f"Failed to update customer data: {str(e)}",
            "success": False
        }), 500

# API endpoint to fetch customers with optional pagination
@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Handle optional pagination
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10000))
        offset = (page - 1) * size

        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM customers;")
        total_result = cursor.fetchone()
        total = total_result['total'] if total_result else 0

        # Fetch customers
        cursor.execute("""
            SELECT
                Customer_ID as customer_id,
                Age as age,
                Gender as gender,
                District as district,
                Region as region,
                Location_Type as location_type,
                Customer_Type as customer_type,
                Employment_Status as employment_status,
                Income_Level as income_level,
                Education_Level as education_level,
                Tenure as tenure,
                Balance as balance,
                Credit_Score as credit_score,
                Outstanding_Loans as outstanding_loans,
                Num_Of_Products as num_of_products,
                Mobile_Banking_Usage as mobile_banking_usage,
                Number_of_Transactions_per_Month as number_of_transactions_per_month,
                Num_Of_Complaints as num_of_complaints,
                Proximity_to_NearestBranch_or_ATM_km as proximity_to_nearestbranch_or_atm_km,
                Mobile_Network_Quality as mobile_network_quality,
                Owns_Mobile_Phone as owns_mobile_phone,
                prediction,
                Churn_Probability as churn_probability
            FROM customers
            ORDER BY Customer_ID ASC
            LIMIT %s OFFSET %s;
        """, (size, offset))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({
            "total": total,
            "customers": rows
        })

    except Exception as e:
        print("Error fetching customers:", str(e))
        return jsonify({"error": str(e)}), 500

    
@app.route('/api/customers/churn_count', methods=['GET'])
def churn_count():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        
        cursor.execute("""
            SELECT COUNT(*) as churn_count
            FROM customers
            WHERE prediction = 1
        """)
        
        result = cursor.fetchone()
        churn_count = result['churn_count'] if result else 0
        # Close the cursor
        cursor.close()
        
        return jsonify({'churn_count': churn_count})
    
    except Exception as e:
        print("Error fetching churn count:", str(e))
        return jsonify({'error': str(e)}), 500
#
@app.route('/api/customers/churn_summary', methods=['GET'])
def churn_summary():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Mappings
        gender_map = {1: 'Male', 0: 'Female'}
        region_map = {0: 'Southern', 1: 'Northern', 2: 'Central'}
        location_type_map = {0: 'Rural', 1: 'Urban', 2: 'Semi Urban'}
        customer_type_map = {0: 'Retail', 1: 'SME', 2: 'Corporate'}
        employment_status_map = {0: 'Self Employed', 1: 'Not Employed', 2: 'Employed'}
        education_level_map = {0: 'Primary', 1: 'Secondary', 2: 'Tertiary'}
        mobile_banking_map = {0: 'No', 1: 'Yes'}
        net_quality_map = {0: 'Fair', 1: 'Poor', 2: 'Good'}
        owns_phone_map = {0: 'Yes', 1: 'No'}
        district_map = {
            6: 'Dedza', 26: 'Dowa', 10: 'Kasungu', 22: 'Lilongwe', 8: 'Mchinji',
            12: 'Nkhotakota', 27: 'Ntcheu', 9: 'Ntchisi', 21: 'Salima',
            11: 'Chitipa', 5: 'Karonga', 20: 'Likoma', 16: 'Mzimba',
            3: 'Nkhata Bay', 24: 'Rumphi', 25: 'Balaka', 17: 'Blantyre',
            2: 'Chikwawa', 7: 'Chiradzulu', 4: 'Machinga', 14: 'Mangochi',
            15: 'Mulanje', 23: 'Mwanza', 18: 'Nsanje', 1: 'Thyolo',
            19: 'Phalombe', 0: 'Zomba', 13: 'Neno'
        }

        mappings = {
            'Gender': gender_map,
            'Region': region_map,
            'Location_Type': location_type_map,
            'Customer_Type': customer_type_map,
            'Employment_Status': employment_status_map,
            'Education_Level': education_level_map,
            'Mobile_Banking_Usage': mobile_banking_map,
            'Mobile_Network_Quality': net_quality_map,
            'Owns_Mobile_Phone': owns_phone_map,
            'District': district_map
        }

        cursor.execute("""
            SELECT COUNT(*) as total_churners
            FROM customers
            WHERE prediction = 1
        """)
        total_churners = cursor.fetchone()['total_churners'] or 0

        if total_churners == 0:
            return jsonify({})  # No churners

        attributes = [
            'Mobile_Banking_Usage',
            'Mobile_Network_Quality',
            'Num_Of_Complaints',
            'Proximity_to_NearestBranch_or_ATM_km',
            'Education_Level',
            'District',
            'Location_Type',
            'Region',
            'Employment_Status',
            'Num_Of_Products'
        ]

        summary = {}

        for attr in attributes:
            if attr == 'Proximity_to_NearestBranch_or_ATM_km':
                query = """
                    SELECT
                        CASE
                            WHEN Proximity_to_NearestBranch_or_ATM_km BETWEEN 0.2 AND 16.999 THEN '0.2 - 16 km'
                            WHEN Proximity_to_NearestBranch_or_ATM_km BETWEEN 17.999 AND 32.999 THEN '17 - 32 km'
                            WHEN Proximity_to_NearestBranch_or_ATM_km BETWEEN 33.999 AND 50 THEN '33 - 50 km'
                            ELSE 'Unknown'
                        END AS value,
                        COUNT(*) as churners
                    FROM customers
                    WHERE prediction = 1
                    GROUP BY value
                    ORDER BY churners DESC
                """
            else:
                query = f"""
                    SELECT {attr} AS value, COUNT(*) AS churners
                    FROM customers
                    WHERE prediction = 1
                    GROUP BY {attr}
                    ORDER BY churners DESC
                """

            cursor.execute(query)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                percentage = (row['churners'] / total_churners) * 100

                if attr in mappings:
                    mapping = mappings[attr]
                    mapped_value = mapping.get(row['value'], row['value'])
                else:
                    mapped_value = row['value']

                result.append({
                    "value": mapped_value,
                    "churners": row['churners'],
                    "percentage": round(percentage, 2)
                })

            summary[attr] = result

        cursor.close()
        return jsonify(summary)

    except Exception as e:
        print("Error generating churn summary:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/api/customers/all")
def all_customers():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = "SELECT * FROM customers ORDER BY churn_probability DESC"
    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(rows)

@app.route("/api/customers/predicted")
def predicted_customers():
    min_threshold = request.args.get("min", default=0, type=float) / 100.0
    max_threshold = request.args.get("max", default=100, type=float) / 100.0

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = """
        SELECT * FROM customers
        WHERE prediction = 1
        AND churn_probability >= %s
        AND churn_probability <= %s
        ORDER BY churn_probability DESC
    """
    cursor.execute(query, (min_threshold, max_threshold))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(rows)
# API endpoint to get alerts summary    
@app.route('/api/alerts/summary', methods=['GET'])
def alerts_summary():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        alert_data = []

        # Helper function to fetch avg safely
        def fetch_avg(query):
            cursor.execute(query)
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] is not None else 0.0

        avg_balance = fetch_avg("SELECT AVG(balance) FROM customers;")
        cursor.execute("SELECT COUNT(*) FROM customers WHERE balance < %s;", (avg_balance,))
        count_low_balance = cursor.fetchone()[0]
        alert_data.append({
            "code": "low_balance",
            "name": "Customers with Low Balance",
            "description": f"{count_low_balance} customers have balance below the average of {avg_balance:.2f}.",
            "count": count_low_balance
        })

        avg_complaints = fetch_avg("SELECT AVG(num_of_complaints) FROM customers;")
        cursor.execute("SELECT COUNT(*) FROM customers WHERE num_of_complaints > %s;", (avg_complaints,))
        count_high_complaints = cursor.fetchone()[0]
        alert_data.append({
            "code": "high_complaints",
            "name": "Customers with High Complaints",
            "description": f"{count_high_complaints} customers have complaints above the average of {avg_complaints:.2f}.",
            "count": count_high_complaints
        })

        avg_transactions = fetch_avg("SELECT AVG(number_of_transactions_per_month) FROM customers;")
        cursor.execute("SELECT COUNT(*) FROM customers WHERE number_of_transactions_per_month < %s;", (avg_transactions,))
        count_low_tx = cursor.fetchone()[0]
        alert_data.append({
            "code": "low_transactions",
            "name": "Customers with Low Transactions",
            "description": f"{count_low_tx} customers have transactions below the average of {avg_transactions:.2f}.",
            "count": count_low_tx
        })

        avg_income = fetch_avg("SELECT AVG(income_level) FROM customers;")
        cursor.execute("SELECT COUNT(*) FROM customers WHERE income_level < %s;", (avg_income,))
        count_low_income = cursor.fetchone()[0]
        alert_data.append({
            "code": "low_income",
            "name": "Customers with Low Income",
            "description": f"{count_low_income} customers have income below the average of {avg_income:.2f}.",
            "count": count_low_income
        })

        cursor.close()
        conn.close()

        return jsonify(alert_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/churn_summary')
def churn_summary_page():
    """
    Render the churn summary page with data visualizations.
    """
    try:
        # Create a database cursor
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute query to get total churn count
        cursor.execute("SELECT COUNT(*) as churn_count FROM customers WHERE prediction ='will leave'")
        churn_count_result = cursor.fetchone()
        churn_count = churn_count_result['churn_count'] if churn_count_result else 0

        # Close the cursor
        cursor.close()

        # Render template with churn count
        return render_template('churn_summary.html', churn_count=churn_count)

    except Exception as e:
        print("Database error:", str(e))
        return render_template('churn_summary.html', churn_count=0, error=str(e)) 
@app.route("/api/customers/churn_rate", methods=["GET"])
def churn_rate():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM customers")
    total = cursor.fetchone()["total"] or 0

    cursor.execute("SELECT COUNT(*) AS churners FROM customers WHERE prediction = 1")
    churners = cursor.fetchone()["churners"] or 0

    churn_rate = (churners / total * 100) if total > 0 else 0

    return jsonify({"churn_rate": round(churn_rate, 2)})

@app.route('/clear_predictions', methods=['POST'])
def clear_predictions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers 
        SET prediction = NULL, 
            churn_probability = NULL
    """)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

# ==============================================
# Mappings for categorical variables
# ==============================================
# Mappings based on your frontend lookup tables
GENDER_MAP = {0: "Female", 1: "Male"}
REGION_MAP = {0: "Southern", 1: "Northern", 2: "Central"}
CUSTOMER_TYPE_MAP = {0: "Retail", 1: "SME", 2: "Corporate"}
EMPLOYMENT_STATUS_MAP = {0: "Self Employed", 1: "Not Employed", 2: "Employed"}
EDUCATION_LEVEL_MAP = {0: "Primary", 1: "Secondary", 2: "Tertiary"}
NET_QUALITY_MAP = {0: "Fair", 1: "Poor", 2: "Good"}
PHONE_MAP = {0: "Yes", 1: "No"}
MOBILE_BANK_MAP = {0: "No", 1: "Yes"}
LOCATION_TYPE_MAP = {0: "Rural", 1: "Urban", 2: "Semi Urban"}

DISTRICT_MAP = {
    0: "Zomba", 1: "Thyolo", 2: "Chikwawa", 3: "Nkhata Bay", 4: "Machinga",
    5: "Karonga", 6: "Dedza", 7: "Chiradzulu", 8: "Mchinji", 9: "Ntchisi",
    10: "Kasungu", 11: "Chitipa", 12: "Nkhotakota", 13: "Neno", 14: "Mangochi",
    15: "Mulanje", 16: "Mzimba", 17: "Blantyre", 18: "Nsanje", 19: "Phalombe",
    20: "Likoma", 21: "Salima", 22: "Lilongwe", 23: "Mwanza", 24: "Rumphi",
    25: "Balaka", 26: "Dowa", 27: "Ntcheu"
}

# Reverse mappings for categorical to numerical conversion
REVERSE_MAPS = {
    'Gender': {v: k for k, v in GENDER_MAP.items()},
    'Region': {v: k for k, v in REGION_MAP.items()},
    'Customer_Type': {v: k for k, v in CUSTOMER_TYPE_MAP.items()},
    'Employment_Status': {v: k for k, v in EMPLOYMENT_STATUS_MAP.items()},
    'Education_Level': {v: k for k, v in EDUCATION_LEVEL_MAP.items()},
    'Mobile_Network_Quality': {v: k for k, v in NET_QUALITY_MAP.items()},
    'Owns_Mobile_Phone': {v: k for k, v in PHONE_MAP.items()},
    'Mobile_Banking_Usage': {v: k for k, v in MOBILE_BANK_MAP.items()},
    'Location_Type': {v: k for k, v in LOCATION_TYPE_MAP.items()},
    'District': {v: k for k, v in DISTRICT_MAP.items()}
}

@app.route('/update_customers', methods=['POST'])
def update_customers():
    """Replace all customer data with randomly generated records (storing human-readable data)"""
    try:
        n_samples = request.json.get('n_samples', 100)
        
        # Generate random data with human-readable values
        random_data = {
            'Age': np.random.randint(18, 80, n_samples),
            'Gender': np.random.choice(list(GENDER_MAP.values()), n_samples),
            'District': np.random.choice(list(DISTRICT_MAP.values()), n_samples),
            'Region': np.random.choice(list(REGION_MAP.values()), n_samples),
            'Location_Type': np.random.choice(list(LOCATION_TYPE_MAP.values()), n_samples),
            'Customer_Type': np.random.choice(list(CUSTOMER_TYPE_MAP.values()), n_samples),
            'Employment_Status': np.random.choice(list(EMPLOYMENT_STATUS_MAP.values()), n_samples),
            'Income_Level': np.random.uniform(50000, 1000000, n_samples),
            'Education_Level': np.random.choice(list(EDUCATION_LEVEL_MAP.values()), n_samples),
            'Tenure': np.random.randint(1, 15, n_samples),
            'Balance': np.random.uniform(1000, 3800000, n_samples),
            'Credit_Score': np.random.randint(300, 850, n_samples),
            'Outstanding_Loans': np.random.uniform(0, 100000, n_samples),
            'Num_Of_Products': np.random.randint(1, 6, n_samples),
            'Mobile_Banking_Usage': np.random.choice(list(MOBILE_BANK_MAP.values()), n_samples),
            'Number_of_Transactions_per_Month': np.random.randint(0, 50, n_samples),
            'Num_Of_Complaints': np.random.randint(0, 10, n_samples),
            'Proximity_to_NearestBranch_or_ATM_km': np.random.uniform(0.5, 50, n_samples),
            'Mobile_Network_Quality': np.random.choice(list(NET_QUALITY_MAP.values()), n_samples),
            'Owns_Mobile_Phone': np.random.choice(list(PHONE_MAP.values()), n_samples)
        }

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Start transaction
            cursor.execute("BEGIN")
            
            # Clear existing data
            cursor.execute("TRUNCATE TABLE customers RESTART IDENTITY")
            
            # Prepare insert query (now storing human-readable values)
            insert_query = """
                INSERT INTO customers (
                    Age, Gender, District, Region, Location_Type, Customer_Type,
                    Employment_Status, Income_Level, Education_Level, Tenure,
                    Balance, Credit_Score, Outstanding_Loans, Num_Of_Products,
                    Mobile_Banking_Usage, Number_of_Transactions_per_Month,
                    Num_Of_Complaints, Proximity_to_NearestBranch_or_ATM_km,
                    Mobile_Network_Quality, Owns_Mobile_Phone,
                    prediction, Churn_Probability,
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                          %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Insert records with predictions
            for i in range(n_samples):
                # Convert human-readable to numerical for prediction
                features = np.array([
                    random_data['Age'][i],
                    REVERSE_MAPS['Gender'][random_data['Gender'][i]],
                    REVERSE_MAPS['District'][random_data['District'][i]],
                    REVERSE_MAPS['Region'][random_data['Region'][i]],
                    REVERSE_MAPS['Location_Type'][random_data['Location_Type'][i]],
                    REVERSE_MAPS['Customer_Type'][random_data['Customer_Type'][i]],
                    REVERSE_MAPS['Employment_Status'][random_data['Employment_Status'][i]],
                    random_data['Income_Level'][i],
                    REVERSE_MAPS['Education_Level'][random_data['Education_Level'][i]],
                    random_data['Tenure'][i],
                    random_data['Balance'][i],
                    random_data['Credit_Score'][i],
                    random_data['Outstanding_Loans'][i],
                    random_data['Num_Of_Products'][i],
                    REVERSE_MAPS['Mobile_Banking_Usage'][random_data['Mobile_Banking_Usage'][i]],
                    random_data['Number_of_Transactions_per_Month'][i],
                    random_data['Num_Of_Complaints'][i],
                    random_data['Proximity_to_NearestBranch_or_ATM_km'][i],
                    REVERSE_MAPS['Mobile_Network_Quality'][random_data['Mobile_Network_Quality'][i]],
                    REVERSE_MAPS['Owns_Mobile_Phone'][random_data['Owns_Mobile_Phone'][i]]
                ]).reshape(1, -1)

                # Make prediction
                probabilities = model.predict_proba(features)
                prob_churn = float(probabilities[0][1])
                prediction = 1 if prob_churn >= 0.5 else 0

                # Insert record (storing human-readable values and codes)
                cursor.execute(insert_query, (
                    # Human-readable values
                    random_data['Age'][i],
                    random_data['Gender'][i],
                    random_data['District'][i],
                    random_data['Region'][i],
                    random_data['Location_Type'][i],
                    random_data['Customer_Type'][i],
                    random_data['Employment_Status'][i],
                    float(random_data['Income_Level'][i]),
                    random_data['Education_Level'][i],
                    int(random_data['Tenure'][i]),
                    float(random_data['Balance'][i]),
                    int(random_data['Credit_Score'][i]),
                    float(random_data['Outstanding_Loans'][i]),
                    int(random_data['Num_Of_Products'][i]),
                    random_data['Mobile_Banking_Usage'][i],
                    int(random_data['Number_of_Transactions_per_Month'][i]),
                    int(random_data['Num_Of_Complaints'][i]),
                    float(random_data['Proximity_to_NearestBranch_or_ATM_km'][i]),
                    random_data['Mobile_Network_Quality'][i],
                    random_data['Owns_Mobile_Phone'][i],
                    prediction,
                    prob_churn,
                    # Numerical codes (for reference/analysis)
                    REVERSE_MAPS['Gender'][random_data['Gender'][i]],
                    REVERSE_MAPS['District'][random_data['District'][i]],
                    REVERSE_MAPS['Region'][random_data['Region'][i]],
                    REVERSE_MAPS['Location_Type'][random_data['Location_Type'][i]],
                    REVERSE_MAPS['Customer_Type'][random_data['Customer_Type'][i]],
                    REVERSE_MAPS['Employment_Status'][random_data['Employment_Status'][i]],
                    REVERSE_MAPS['Education_Level'][random_data['Education_Level'][i]],
                    REVERSE_MAPS['Mobile_Banking_Usage'][random_data['Mobile_Banking_Usage'][i]],
                    REVERSE_MAPS['Mobile_Network_Quality'][random_data['Mobile_Network_Quality'][i]],
                    REVERSE_MAPS['Owns_Mobile_Phone'][random_data['Owns_Mobile_Phone'][i]]
                ))

            conn.commit()
            
            return jsonify({
                "message": f"Successfully replaced all customer data with {n_samples} new records",
                "success": True
            })

        except Exception as db_error:
            conn.rollback()
            raise db_error
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Error in update_customers: {str(e)}")
        return jsonify({
            "error": f"Failed to update customer data: {str(e)}",
            "success": False
        }), 500
#API endpoint to get customers whose prediction is 'will leave'
@app.route('/api/customers/will_leave', methods=['GET'])
def get_will_leave_customers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Fetch customers with prediction 'will leave'
        cursor.execute("""
            SELECT * FROM customers
            WHERE prediction = 1
            ORDER BY churn_probability DESC
        """)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(rows)

    except Exception as e:
        print("Error fetching will leave customers:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')
    
