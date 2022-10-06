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

    #query = "SELECT * FROM stocks WHERE id = (SELECT sid FROM userstocks WHERE uid = (SELECT id FROM users WHERE id = ?))"
    #query = "SELECT * FROM stocks WHERE id = ?"
    #id = (1)

    #rows = db.execute(query, id)

    query1 = "SELECT username FROM users WHERE id = ?"
    id = (int(session["user_id"]))

    user= db.execute(query1, (1))

    id = (int(session["user_id"]))
    rows= db.execute("SELECT * FROM stocks WHERE id = (SELECT sid FROM userstocks WHERE uid = (SELECT id FROM users WHERE id = ?))", id)
    #query = "SELECT * FROM stocks WHERE id = (SELECT sid FROM userstocks WHERE uid = (SELECT id FROM users WHERE id =  ?))"
    #id = (int(session["user_id"]))
    #rows = db.execute(query, id)
    
    return render_template("index.html", rows=rows, user=user)
    #return apology("TODO")




@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

         #initialize it for later use
        uid = int(session["user_id"])
        user = db.execute("SELECT * FROM users WHERE id = ?", (uid)) 

        cash = db.execute("SELECT cash FROM users WHERE id = ?", (int(session["user_id"])) )


        symbol= request.form.get("symbol")
        shares = request.form.get("shares")

        buy_symbol = lookup(str(symbol))

        if buy_symbol:
            total_price = int(shares) * int(buy_symbol["price"])
            print(buy_symbol)
            if cash[0]["cash"] > total_price:

                # now we can acctually make the transaction
                transaction_date = str(datetime.datetime.now())
                # add stock to database
                db.execute("INSERT INTO stocks(symbol, name, shares, price) VALUES (?, ?, ?, ?)", buy_symbol["symbol"], buy_symbol["name"], shares * (-1), buy_symbol["price"])
                #get sid of inserted stock
                sid = db.execute("SELECT *  FROM stocks WHERE id=(SELECT MAX(id) FROM stocks)")
                
                #sid = db.execute("SELECT id FROM stocks ORDER BY id ASC LIMIT 1")
                   
                #the new cash owned by user
                new_cash = cash[0]["cash"] - total_price

                #update cash field of users to new cash value after buying stock

                #query_update = "UPDATE users SET cash = (?) WHERE id = (?)"
                #db.execute(query_update, (new_cash, uid))

                #db.execute("UPDATE users SET cash = ?, WHERE id = ?", (new_cash, uid))
                
                
                
                
                #update user stock table to show transaction date and transaction type
                db.execute("INSERT INTO userstocks(uid, sid, transactions, transaction_type) VALUES (?, ?, ?, ?)", uid, sid[0]["id"], transaction_date, "buy")
                
                
                
                
                return render_template("bought.html", rows=sid,  user=user)
            else:
                return apology("Insufficent fund")

        else:
            return apology ("Symbol not Correct")

    else:
        return render_template("buy.html")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
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
                display[0] = "registered"
                return redirect("/")

            else:
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
    return render_template("sell.html")



# TEST PRINT
#rows= db.execute("select * from users")
#print(rows)


#------------
symbol = 'AAPL'
buy_symbol = lookup(symbol)

if buy_symbol:

    print(buy_symbol)

cash = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])

print("hellllllllllllllllllllllllllllllllllllllllllll")
print(cash)


