import os
from cs50 import SQL

from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required

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
                                 username, career_status, country, generate_password_hash(password, method="pbkdf2:sha256"))
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

# Upload
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():

    if request.method == "POST":
        image = request.files.get("image")
        project_name = request.form.get("project_name")
        director = request.form.get("director")
        cinematographer = request.form.get("cinematographer")
        year = request.form.get("year")
        work_type = request.form.get("work_type")
        shot_type = request.form.get("shot_type")
        shot_size = request.form.get("shot_size")
        int_or_ext = request.form.get("int_or_ext")
        time_of_day = request.form.get("time_of_day")
        aspect_ratio = request.form.get("aspect_ratio")
        description = request.form.get("description")
        user_id = session["user_id"]

        if not all([image, project_name, director, cinematographer, year]):
            flash("Please provided all the details of the shot")
            return redirect("/upload")
        
        # Clean image name and store it
        filename = secure_filename(image.filename)
        image.save(os.path.join("static/uploads", filename))
        image_path = os.path.join("static/uploads", filename)

        # Insert to database
        db.execute("INSERT INTO shots (user_id, image_path, work_type, shot_type, shot_size, int_or_ext, time_of_day, aspect_ratio, "
        "project_name, director, cinematographer, year, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        user_id, image_path, work_type, shot_type, shot_size, int_or_ext, time_of_day, aspect_ratio,
        project_name, director, cinematographer, year, description);

        return redirect("/")

    else:
        return render_template("upload.html")
    


# Browse
@app.route("/browse")
def browse():

    shots = db.execute("SELECT * FROM shots ORDER BY RANDOM()")
    return render_template("browse.html", shots=shots)


# Show metadata of shot
@app.route("/shot/<int:id>")
def shot(id):

    try:
        shot = db.execute("SELECT * FROM shots WHERE id = ?", id)[0]
    except IndexError:
        flash("Shot not found")
        return redirect("/browse")
    
    return render_template("shot.html", shot=shot)


# Profile
@app.route("/profile/<username>")
def profile(username):

    user = db.execute("SELECT * FROM users WHERE username = ?", username)
    if len(user) != 1:
        flash("Username not found")
        return redirect("/browse")
    user = user[0]

    shots = db.execute("SELECT * FROM shots WHERE user_id = ?", user["id"])

    return render_template("profile.html", user=user, shots=shots)


# Collections
@app.route("/collections")
@login_required
def collections():

    collections = db.execute("SELECT * FROM collections WHERE user_id = ?", session["user_id"])

    return render_template("collections.html", collections=collections)


# Collection <id>
@app.route("/collection/<id>")
@login_required
def collection(id):

    collection = db.execute("""
                            SELECT shots.* FROM shots
                            JOIN collections_shots ON shots.id = collections_shots.shot_id
                            WHERE collections_shots.collection_id = ?
                            """, id)

    return render_template("collection.html", collection=collection)

# Homepage
@app.route("/")
def index():
    return redirect("/browse")
