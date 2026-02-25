from flask import Flask, render_template, request
import mysql.connector
import os

app = Flask(__name__)

# MySQL connection (Railway + local compatible)
db = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST", "localhost"),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASSWORD", "ulanHawpqqntrrNjrCOFeHhGXmFHMbFB"),
    database=os.environ.get("MYSQL_DATABASE", "railway"),  # ← change "test" to "railway"
    port=int(os.environ.get("MYSQL_PORT", 3306))
)
cursor = db.cursor()

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
