import os

from cs50 import SQL
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)



# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///diary.db")
#db = sqlite3.connect("diary.db")




@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return render_template("index.html")

@app.route("/contactus")
def contactus():
    return apology("contact information will be displayed here")

@app.route("/aboutus")
def aboutus():
    return apology("About us Infromatin will be displayed here")

@app.route("/home")
def home():
    return apology("home screen will be displayed here")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/profile")
def profile():
    return apology("account and profile managment page goes here")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        # validate submited data

        if len(username) > 0 and len(password) > 0:
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)

            if password != confirm:
                return apology("confirmation does not match with password")
            if len(rows) == 0:
                # insert username and password to user table /register user
                db.execute("INSERT INTO users(username, hash) VALUES (?, ?)", username, generate_password_hash(password))
                rows = db.execute("SELECT * FROM users WHERE username = ?", username)
                session["user_id"] = rows[0]["id"]

                # Redirect user to home pages

                return redirect("/")

            else:

                logout()
                return apology("user allready exists")

        else:
            return apology("check user name and password")

    else:
        return render_template("register.html")


@app.route("/viewdiary", methods=["GET", "POST"])
@login_required
def viewdiary():
    """Sell shares of stock"""
    return apology("Diary search features will be implemented here")

@app.route("/writediary", methods=["GET", "POST"])
@login_required
def writediary():
    """Buy shares of stock"""
    return apology(" page to write diary will be displayed and implemented here")

