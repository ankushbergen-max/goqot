from flask import Flask, render_template, request
import mysql.connector
import os

app = Flask(__name__)

# MySQL connection (Railway + local compatible)
db = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST", "localhost"),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASSWORD", ""),  # Don't hardcode password!
    database=os.environ.get("MYSQL_DATABASE", "railway"),
    port=int(os.environ.get("MYSQL_PORT", 3306))
)
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
    name = request.form["name"]
    company = request.form["company"]
    email = request.form["email"]
    phone = request.form["phone"]
    message = request.form["message"]

    sql = """
    INSERT INTO contacts (name, company, email, phone, message)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (name, company, email, phone, message)
    cursor.execute(sql, values)
    db.commit()

    return render_template("contact.html", success=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
