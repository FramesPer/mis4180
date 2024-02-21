#!/usr/bin/env python3
"""
MIS 4180 Project
Professor Deng's IS Risk Course Project

Please read the README.md for more information about this project.

Helpful Resources:
- https://owasp.org/www-pdf-archive/How_to_Build_a_Secure_Login_BenBroussard_June2011.pdf
"""
from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import bcrypt
import creds
import datetime
from helpers import fetch_email, init_backend, recent_order_number

app = Flask(__name__)
app.secret_key = creds.session_key

@app.route('/thank-you', methods=['GET', 'POST'])
def confirmation():
    hologram_specs = session.pop('hologram_specs', None)

    if hologram_specs is None:
        return "<span style='color: red; font-weight: bold;'>Don't even try.</span>"

    populate_hologram_fields(hologram_specs)
    recent_order = recent_order_number(session['username'])
    ordered = datetime.datetime.now()

    return render_template('thank-you.html', order_number=recent_order, order_time=ordered)

"""
The below is pretty ugly, but it's an example of a control

This control is important because otherwise users could access the
/checkout page without creating a hologram first. This would result in
an error when writing to database and obviously when attempting to
dislpay the data.
"""
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    hologram_specs = None
    user_email = fetch_email(session['username'])[0]

    if request.method == 'POST':
        hologram_specs = request.form
        session['hologram_specs'] = hologram_specs.to_dict()

    if hologram_specs is None:
        return redirect(url_for('create_hologram'))
    else:
        return render_template('checkout.html', user_email=user_email, holo_specs=hologram_specs)

def fetch_user_id():
    con = sqlite3.connect("backend.db", timeout=10)
    cur = con.cursor()
    name = cur.execute("SELECT user_id FROM user WHERE username = ?;", (session['username'],))
    user_id = name.fetchone()[0]
    return user_id

def populate_hologram_fields(specs):
    con = sqlite3.connect("backend.db", timeout=10)
    cur = con.cursor()
    user_id = fetch_user_id()

    cur.execute("INSERT INTO hologram (building_dimensions, building_style, building_type, purpose, additional_info, user_id) VALUES (?, ?, ?, ?, ?, ?);", (specs['buildingDimensions'], specs['architecturalStyle'], specs['buildingType'], specs['purpose'], specs['additional'], user_id))
    con.commit()
    con.close()

@app.route('/create_hologram', methods=['GET', 'POST'])
def create_hologram():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        return redirect(url_for('checkout'))

    return render_template('create_hologram.html')

def order_crate(raw_details):
    ordered = []
    for order in raw_details:
        ordered.append(order)
    return ordered

@app.route('/orders')
def orders():
    if 'username' in session:
        con = sqlite3.connect("backend.db", timeout=10)
        cur = con.cursor()
        cur.execute("SELECT hologram_id, building_dimensions, building_style, building_type, purpose, additional_info FROM hologram WHERE user_id = ?", (fetch_user_id(),))
        info = order_crate(cur.fetchall())
        con.close()
        return render_template('orders.html', rows=info)

    return redirect(url_for('login_page'))

def register_account(username, password, email):
    con = sqlite3.connect("backend.db", timeout=10)
    cur = con.cursor()
    cur.execute("INSERT INTO user (username, email, password) VALUES (?, ?, ?);", (username, email, password))
    con.commit()
    con.close()

def attempt_login(stored_pass, submitted_pass):
    submitted_pass_utf8 = submitted_pass.encode('utf-8')
    stored_pass_utf8 = stored_pass.encode('utf-8')
    if bcrypt.checkpw(submitted_pass_utf8, stored_pass_utf8):
        return True
    return False

def login_checker(attempt_password, actual_password):
    error_message = "Invalid password and/or username."
    if actual_password is None:
        return error_message

    if attempt_login(actual_password[0], attempt_password):
        return None

    return error_message

def login_account(username, password):
    con = sqlite3.connect("backend.db", timeout=10)
    cur = con.cursor()
    cur.execute("SELECT password FROM user WHERE username = ?;", (username,))
    actual_password = cur.fetchone()
    con.close()

    err_msg = login_checker(password, actual_password)
    if err_msg:
        return render_template("login.html", error_message=err_msg)
    else:
        session['username'] = username
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        return login_account(username, password)
    return render_template("login.html")

def blowfish_hash(plaintext_password):
    utf8_pass = plaintext_password.encode('utf-8')
    salt = bcrypt.gensalt()
    pass_hash = bcrypt.hashpw(utf8_pass, salt)

    return pass_hash.decode('utf-8')

def validation_checks(username, password, email):
    if len(username) < 4 or len(username) > 18:
        return "Username is either too short or too long."
    if username.__contains__(" "):
        return "Spaces are not allowed your username."
    if len(password) < 6:
        return "Password is too short. Use a length of (6 < p < 128)."
    if len(password) > 128:
        return "Let's not make thing more complicated than they need to be... okay?"
    if len(email) < 4 or "@" not in email:
        return "Please enter a valid email address."

    con = sqlite3.connect("backend.db", timeout=10)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM user WHERE username= ?;", (username,))
    data = cur.fetchone()
    con.close()

    if data is not None:
        return "User already exists."

    return None

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['emailAddress'].strip()
        password = request.form['password'].strip()

        err_msg = validation_checks(username, password, email)
        if err_msg:
            return render_template("register.html", error_message=err_msg)

        hashed_pass = blowfish_hash(password)
        register_account(username, hashed_pass, email)
        return render_template("login.html", registration_status="registered")
    else:
        return render_template("register.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_backend()
    app.run()
