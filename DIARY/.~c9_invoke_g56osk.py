import os
import datetime

transaction_date = datetime.datetime.now()
display = ["empty"]


from cs50 import SQL
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
db = SQL("sqlite:///finance.db")

#global variables
#index_display = "history"
#index_display = "bought"
#index_display = "sold"
index_display = ["stock_info"] #default
total = [0]
index_rows = [0]
index_stock_id = [0]
  

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    user = db.execute("SELECT * FROM users WHERE id = ?", session_id )

    if user:
        user_avilable = True


    if index_display[0] == "registered":

        rows = db.execute("SELECT * FROM stocks WHERE id = (SELECT sid FROM userstocks WHERE uid = ?)", session_id)
        total[0] = 0
        index_display[0] == "registered"
        return render_template("index.html", rows=rows, user=user, user_avilable= user_avilable,index_display=index_display[0],total=total)
    elif index_display[0] == "bought":
        pass


    elif index_display[0] == "sold":
        pass
        #for row in rows:
            #total[0] += row["shares"] * row["price"]

    elif index_display[0] == "history":
        pass
    else:
        index_display[0] == "stock_info"

        rows = db.execute("SELECT * FROM stocks WHERE id = (SELECT sid FROM userstocks WHERE uid = ?)", session_id)
        for row in rows:
            total[0] += row["shares"] * row["price"]

        return render_template("index.html", rows=rows, user=user, user_avilable= user_avilable,index_display=index_display[0], total=total)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        valid_share= False #to check if weather user input share is number on not true if number
        requested_symbol = request.form.get("symbol")
        requested_shares = request.form.get("shares")


        checked_symbol = lookup(str(requested_symbol))
        if checked_symbol and requested_symbol and requested_shares:
            session_id = int(session["user_id"])
            #check if user has sufficent fund
            users_ld = db.execute("SELECT * FROM users WHERE id = ?", session_id)
            user_cash = users_ld[0]['cash']
            cash_needed = int(requested_shares) * checked_symbol["price"]
            cash_remaining = (user_cash - cash_needed)
            if cash_remaining>= 0:
                #1 add symbol information to stocks table in the database
                stock_ld= db.execute("INSERT INTO stocks(symbol, name, shares, price) VALUES (?, ?, ?, ?)", checked_symbol["symbol"], checked_symbol["name"], int(requested_shares), checked_symbol["price"])
                #find id of inserted stock
                inserted_stock_ld= db.execute("SELECT * FROM stocks ORDER BY id DESC LIMIT 1")
                inserted_stock_id= inserted_stock_ld[0]["id"] # id integer datatype

                #2 update cash in user  cash_avilable
                db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_remaining, session_id)

                #3 insert transaction infromation to userstocks
                db.execute("INSERT INTO userstocks (uid, sid, transactions, transaction_type) VALUES (?, ?, ?, ?)", session_id, inserted_stock_id, datetime.datetime.now(), "bought")

                #return redirect("/")
                index_display[0] = "bought" #--------------------
                index_rows[0] = inserted_stock_ld # ----------------
                index_stock_id[0] = inserted_stock_id #---------------------    
                index_cashremaining[0] = cashremainin
                #return render_template("index.html", rows=inserted_stock_ld, user=users_ld, cash_remaining=cash_remaining, index_display= str(index_display[0]))
                return apology("THOMAS KITABA TEST")
            else:
                return apology("Insuficent CASH in ACCOUNT")

        else:

            return apology("Symbol not found")
    else:
        return render_template("buy.html")
        #return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    session_id = int(session["user_id"])
    user= db.execute("SELECT * FROM users WHERE id = ?", session_id)
    if request.method == "GET":
        rows = db.execute("SELECT * FROM stocks WHERE id = (SELECT sid FROM userstocks WHERE uid = ? ORDER BY transactions ASC)", session_id)
        return render_template("index.html",rows=rows, user=user)
        return render_template("history.html")


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
        index_display = "stock_info"
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
def quote():
    """Get stock quote."""
    #display[0] = request.form.get("display")
    xx = str(request.form.get("symbol"))
    #xx= 'BA'

    row = lookup(xx)

    return render_template("quote.html",row=row)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if len(username) > 0  and len(password) > 0:
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)

            if password != confirm:
                return apology("confirmation does not match with password")
            if len(rows) == 0:
                #insert username and password to user table /register user
                db.execute("INSERT INTO users(username, hash) VALUES (?, ?)", username, generate_password_hash(password))
                rows = db.execute("SELECT * FROM users WHERE username = ?", username)
                session["user_id"] = rows[0]["id"]

                # Redirect user to home pages
                #display[0] = "registered"
                index_display[0] = "registered"
                return redirect("/")

            else:

                logout()
                return apology("user allready exists")

        else:
            return apology("check user name and password")

    else:
        return render_template("register.html")

    #return apology("TODO")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        valid_share= False #to check if weather user input share is number on not true if number
        requested_symbol = request.form.get("symbol")
        requested_shares = request.form.get("shares")


        checked_symbol = lookup(str(requested_symbol))
        if checked_symbol and requested_symbol and requested_shares:
            session_id = int(session["user_id"])
            #check if user has sufficent fund
            users_ld = db.execute("SELECT * FROM users WHERE id = ?", session_id)
            user_cash = users_ld[0]['cash']
            cash_needed = int(requested_shares) * checked_symbol["price"]
            cash_remaining = user_cash + cash_needed
            if cash_remaining>= 0:
                #1 add symbol information to stocks table in the database
                stock_ld= db.execute("INSERT INTO stocks(symbol, name, shares, price) VALUES (?, ?, ?, ?)", checked_symbol["symbol"], checked_symbol["name"], int(requested_shares * -1) , checked_symbol["price"])
                #find id of inserted stock
                inserted_stock_ld= db.execute("SELECT * FROM stocks ORDER BY id DESC LIMIT 1")
                inserted_stock_id= inserted_stock_ld[0]["id"] # id integer datatype

                #2 update cash in user  cash_avilable
                db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_remaining, session_id)

                #3 insert transaction infromation to userstocks
                db.execute("INSERT INTO userstocks (uid, sid, transactions, transaction_type) VALUES (?, ?, ?, ?)", session_id, inserted_stock_id, datetime.datetime.now(), "bought")

                #return redirect("/")
                index_display[0] = "bought"
                return render_template("index.html", rows=inserted_stock_ld, user=users_ld, cash_remaining=cash_remaining, index_display= str(index_display[0]))
                return apology("THOMAS KITABA TEST")
            else:
                return apology("Insuficent CASH in ACCOUNT")

        else:

            return apology("Symbol not found")
    else:
        return render_template("buy.html")



# TEST PRINT
#rows= db.execute("select * from users")
#print(rows)
#query1 = "SELECT username FROM users WHERE id = ?"
#id = (int(1))

#user= db.execute(query1, id)
#print(user)

