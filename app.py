from flask import Flask, render_template, request
import mysql.connector
import os
import time
from urllib.parse import urlparse

app = Flask(__name__)

# === ONLY THESE 2 LINES ADDED FOR CSS FIX ===
app.static_folder = 'static'
app.static_url_path = '/static'
# ============================================

# Print all possible MySQL variables for debugging
print("===== DATABASE CONFIGURATION =====")
print(f"MYSQLHOST: {os.environ.get('MYSQLHOST', 'NOT SET')}")
print(f"MYSQLUSER: {os.environ.get('MYSQLUSER', 'NOT SET')}")
print(f"MYSQLPASSWORD: {'SET' if os.environ.get('MYSQLPASSWORD') else 'NOT SET'}")
print(f"MYSQLDATABASE: {os.environ.get('MYSQLDATABASE', 'NOT SET')}")
print(f"MYSQLPORT: {os.environ.get('MYSQLPORT', 'NOT SET')}")
print(f"MYSQL_URL: {'SET' if os.environ.get('MYSQL_URL') else 'NOT SET'}")
print("===================================")

# MySQL connection with error handling
def get_db_connection():
    connection = None
    
    # Method 1: Try using MYSQL_URL first (easiest)
    mysql_url = os.environ.get('MYSQL_URL')
    if mysql_url:
        try:
            print(f"Attempting to connect using MYSQL_URL...")
            parsed = urlparse(mysql_url)
            
            connection = mysql.connector.connect(
                host=parsed.hostname,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:],  # Remove leading '/'
                port=parsed.port or 3306,
                connection_timeout=10
            )
            print("✅ Database connected successfully using MYSQL_URL!")
            return connection
        except Exception as e:
            print(f"❌ MYSQL_URL connection failed: {e}")
    
    # Method 2: Try individual variables (no underscores)
    try:
        host = os.environ.get('MYSQLHOST')
        user = os.environ.get('MYSQLUSER')
        password = os.environ.get('MYSQLPASSWORD')
        database = os.environ.get('MYSQLDATABASE')
        port = os.environ.get('MYSQLPORT')
        
        if host and user:
            print(f"Attempting to connect to database at {host}:{port}...")
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password if password else "",
                database=database if database else "railway",
                port=int(port) if port else 3306,
                connection_timeout=10
            )
            print("✅ Database connected successfully using individual variables!")
            return connection
    except Exception as e:
        print(f"❌ Individual variables connection failed: {e}")
    
    # Method 3: Try variables with underscores
    try:
        host = os.environ.get('MYSQL_HOST')
        user = os.environ.get('MYSQL_USER')
        password = os.environ.get('MYSQL_PASSWORD')
        database = os.environ.get('MYSQL_DATABASE')
        port = os.environ.get('MYSQL_PORT')
        
        if host and user:
            print(f"Attempting to connect to database at {host}:{port}...")
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password if password else "",
                database=database if database else "railway",
                port=int(port) if port else 3306,
                connection_timeout=10
            )
            print("✅ Database connected successfully using underscored variables!")
            return connection
    except Exception as e:
        print(f"❌ Underscored variables connection failed: {e}")
    
    print("⚠️ All connection methods failed. App will continue without database.")
    return None

# Initialize database connection
db = get_db_connection()
cursor = None

# Create cursor and table if database connected
if db:
    try:
        cursor = db.cursor()
        # Create table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            company VARCHAR(255),
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(255),
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        db.commit()
        print("✅ Table checked/created successfully!")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        cursor = None

# Debug route to see all environment variables
@app.route('/debug-vars')
def debug_vars():
    import os
    result = "<h1>Environment Variables</h1><table border='1' style='border-collapse: collapse;'>"
    result += "<tr><th>Variable Name</th><th>Value</th></tr>"
    
    # Show all MySQL related variables
    mysql_vars = {}
    for key, value in os.environ.items():
        if 'mysql' in key.lower() or 'MYSQL' in key:
            if 'password' in key.lower() or 'PASSWORD' in key:
                mysql_vars[key] = '********'  # Hide passwords
            else:
                mysql_vars[key] = value
    
    # Sort and display
    for key in sorted(mysql_vars.keys()):
        result += f"<tr><td>{key}</td><td>{mysql_vars[key]}</td></tr>"
    
    result += "</table>"
    
    # Add database status
    if db and cursor:
        result += "<p style='color: green;'>✅ Database is connected!</p>"
    else:
        result += "<p style='color: red;'>❌ Database is not connected</p>"
    
    return result

# Test database connection
@app.route('/test-db')
def test_db():
    if db and cursor:
        try:
            cursor.execute("SELECT 1")
            return "✅ Database is connected and working!"
        except Exception as e:
            return f"❌ Database connection exists but query failed: {e}"
    else:
        return "❌ Database not connected"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/products')
def products():
    return render_template("products.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/ecommerce")
def ecommerce():
    return render_template("ecommerce.html")
    
@app.route("/goqc")
def goqc():
    return render_template("goqc.html")

@app.route("/qai")
def qai():
    return render_template("qai.html")    
    
@app.route("/submit", methods=["POST"])
def submit():
    try:
        name = request.form["name"]
        company = request.form["company"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]
        
        print(f"Form submission received - Name: {name}, Email: {email}")
        
        if cursor is not None and db is not None:
            try:
                sql = """
                INSERT INTO contacts (name, company, email, phone, message)
                VALUES (%s, %s, %s, %s, %s)
                """
                values = (name, company, email, phone, message)
                cursor.execute(sql, values)
                db.commit()
                print("✅ Form data saved to database successfully!")
                return render_template("contact.html", success=True)
            except Exception as e:
                print(f"❌ Error saving to database: {e}")
                return render_template("contact.html", success=False, error="Database error")
        else:
            print("⚠️ Database not available - form data not saved")
            return render_template("contact.html", success=False, error="Database not connected")
            
    except Exception as e:
        print(f"❌ Error in form submission: {e}")
        return render_template("contact.html", success=False, error="Form submission error")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting app on port {port}...")
    app.run(host="0.0.0.0", port=port)
