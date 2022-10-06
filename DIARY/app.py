import os
import datetime
import math

from cs50 import SQL
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
# Configure application
app = Flask(__name__)

#sqlconnection = sqlite3.connect("diary.db")
#db = sqlconnection.cursor()

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

transaction_date = datetime.datetime.now()


#global variables
#index_display = "history"
#index_display = "bought"
#index_display = "sold"
index_display = ["stock_info"]  # default
total = [0]
index_rows = [0]
index_stock_id = [0]
index_cash_remaining = [0]


# Make sure API key is set
#if not os.environ.get("API_KEY"):
    #raise RuntimeError("API_KEY not set")

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
    user_avilable = False
    session_id = int(session["user_id"])
    user = db.execute("SELECT * FROM users WHERE id = ?", session_id)

    if user:
        user_avilable = True

    if index_display[0] == "registered":
        pass
        return apology("after registering this page will be displayed")

    elif index_display[0] == "bought":
        pass
        return apology("after registering this page will be displayed")

    elif index_display[0] == "edit_profile":
        pass
        return apology ("manage user account goes here")

    elif index_display[0] == "history":
        
        pass
        return apology ("diary history goes here")

        # TODO
    elif index_display[0] == "search_diary":

        pass
        return apology ("manage user account goes here")
        # return render_template("index.html", rows=rows, user=user, index_display= "stock_info", total= 1001)
    else:
        return render_template("index.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    pass

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    
    return apology ("code to show diary history")



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
        total[0] = 0

        index_display[0] = "stock_info"

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

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote(): # to be converted to search diary
    """Get stock quote."""
    pass

    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        return apology("registered")
    else:
        return render_template("register.html")
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    pass

