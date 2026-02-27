from flask import Flask, render_template, request
import mysql.connector
import os
from urllib.parse import urlparse
from mysql.connector import Error

app = Flask(__name__)

# === CSS Fix ===
app.static_folder = 'static'
app.static_url_path = '/static'

# =================== DATABASE CONNECTION ===================

def get_db_connection():
    """
    Connect to MySQL using Railway variables.
    Priority: MYSQL_URL -> individual MYSQL_HOST vars.
    Returns: connection object or None
    """
    mysql_url = os.environ.get("MYSQL_URL")
    if mysql_url:
        try:
            parsed = urlparse(mysql_url)
            conn = mysql.connector.connect(
                host=parsed.hostname,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path.lstrip("/"),
                port=parsed.port or 3306,
                connection_timeout=10,
                ssl_disabled=True
            )
            print("✅ Connected to DB using MYSQL_URL!")
            return conn
        except Error as e:
            print(f"❌ Connection via MYSQL_URL failed: {e}")

    # Fallback to individual variables
    host = os.environ.get("MYSQL_HOST")
    user = os.environ.get("MYSQL_USER")
    password = os.environ.get("MYSQL_PASSWORD")
    database = os.environ.get("MYSQL_DATABASE")
    port = os.environ.get("MYSQL_PORT", 3306)

    if host and user and database:
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=int(port),
                connection_timeout=10,
                ssl_disabled=True
            )
            print("✅ Connected to DB using individual variables!")
            return conn
        except Error as e:
            print(f"❌ Connection via individual variables failed: {e}")

    print("⚠️ Database connection failed. App will continue without DB.")
    return None

# Global DB connection and cursor
db = get_db_connection()
cursor = db.cursor() if db else None

# =================== HELPER: AUTO-RECONNECT ===================

def ensure_connection():
    """
    Checks if the connection is alive. Reconnects if necessary.
    Returns a valid cursor or None
    """
    global db, cursor
    try:
        if db is None or not db.is_connected():
            print("⚠️ Database disconnected. Reconnecting...")
            db = get_db_connection()
            cursor = db.cursor() if db else None
        return cursor
    except Exception as e:
        print(f"❌ Error ensuring DB connection: {e}")
        db = get_db_connection()
        cursor = db.cursor() if db else None
        return cursor

# Create table if DB is available
c = ensure_connection()
if c:
    try:
        c.execute("""
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

# =================== ROUTES ===================

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
        company = request.form.get("company", "")
        email = request.form["email"]
        phone = request.form.get("phone", "")
        message = request.form.get("message", "")

        print(f"Form submission received - Name: {name}, Email: {email}")

        c = ensure_connection()
        if c and db:
            try:
                sql = """
                INSERT INTO contacts (name, company, email, phone, message)
                VALUES (%s, %s, %s, %s, %s)
                """
                c.execute(sql, (name, company, email, phone, message))
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

# =================== DEBUG / TEST ROUTES ===================

@app.route('/debug-vars')
def debug_vars():
    result = "<h1>Environment Variables</h1><table border='1' style='border-collapse: collapse;'>"
    result += "<tr><th>Variable Name</th><th>Value</th></tr>"

    for key, value in os.environ.items():
        if "mysql" in key.lower() or "MYSQL" in key:
            if "password" in key.lower():
                value = "********"
            result += f"<tr><td>{key}</td><td>{value}</td></tr>"

    result += "</table>"

    result += "<p style='color: green;'>✅ Database is connected!</p>" if db and cursor else "<p style='color: red;'>❌ Database is not connected</p>"
    return result

@app.route('/test-db')
def test_db():
    c = ensure_connection()
    if c and db:
        try:
            c.execute("SELECT 1")
            return "✅ Database is connected and working!"
        except Exception as e:
            return f"❌ Database connection exists but query failed: {e}"
    return "❌ Database not connected"

# =================== RUN APP ===================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting app on port {port}...")
    app.run(host="0.0.0.0", port=port)
