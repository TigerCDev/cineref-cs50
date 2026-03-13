import os
from cs50 import SQL

from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db=SQL("sqlite:///cineref.db")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        career_status = request.form.get("career_status")
        country = request.form.get("country")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not all([username, career_status, country, password, confirmation]):
            flash("Please provide all the information")
            return redirect("/register")
        
        if password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")
        
        try:
            user_id = db.execute("INSERT INTO users (username, career_status, country, hash) VALUES (?, ?, ?, ?)",
                                 username, career_status, country, generate_password_hash(password))
        except ValueError:
            flash("Username already taken")
            return redirect("/register")
        
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")
    
    else:
        return render_template("register.html")
    

# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not all([username, password]):
            flash("Must provide Username and Password")
            return redirect("/login")
        
        rows = db.execute("SELECT * FROM users WHERE username=?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username or password")
            return redirect("/login")
        
        session.clear()
        session["user_id"] = rows[0]["id"]

        return redirect("/")
    
    else:
        return render_template("login.html")


# Logout
@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")
        
    

    
    
    
