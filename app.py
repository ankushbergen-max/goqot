from flask import Flask, render_template, request
import mysql.connector
import os
import time

app = Flask(__name__)

# Print all possible MySQL variables for debugging
print("===== DATABASE CONFIGURATION =====")
print(f"MYSQLHOST: {os.environ.get('MYSQLHOST', 'NOT SET')}")
print(f"MYSQLUSER: {os.environ.get('MYSQLUSER', 'NOT SET')}")
print(f"MYSQLPASSWORD: {'SET' if os.environ.get('MYSQLPASSWORD') else 'NOT SET'}")
print(f"MYSQLDATABASE: {os.environ.get('MYSQLDATABASE', 'NOT SET')}")
print(f"MYSQLPORT: {os.environ.get('MYSQLPORT', 'NOT SET')}")
print("===================================")

# MySQL connection with error handling
def get_db_connection():
    try:
        # Use the EXACT variable names from Railway (no underscores)
        host = os.environ.get('MYSQLHOST')
        user = os.environ.get('MYSQLUSER')
        password = os.environ.get('MYSQLPASSWORD')
        database = os.environ.get('MYSQLDATABASE')
        port = os.environ.get('MYSQLPORT')
        
        print(f"Attempting to connect to database at {host}:{port}...")
        
        if not host or not user:
            print("❌ MySQL host or user not set in environment variables")
            return None
            
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password if password else "",
            database=database if database else "railway",
            port=int(port) if port else 3306,
            connection_timeout=10
        )
        print("✅ Database connected successfully!")
        return connection
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("⚠️  App will continue but database features won't work!")
        return None

# Initialize database connection
db = get_db_connection()

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
else:
    cursor = None

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
