import os
import datetime
import math

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

transaction_date = datetime.datetime.now()
display = ["empty"]

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
    user = db.execute("SELECT * FROM users WHERE id = ?", session_id)

    if user:
        user_avilable = True

    if index_display[0] == "registered":

        rows = db.execute("SELECT * FROM stocks WHERE id = (SELECT sid FROM userstocks WHERE uid = ?)", session_id)
        total[0] = 0
        index_display[0] = "registered"
        return render_template("index.html", rows=rows, user=user, user_avilable=user_avilable, index_display=index_display[0], total=total)

    elif index_display[0] == "bought":
        rows = db.execute("SELECT * FROM stocks WHERE id = ?", index_stock_id[0])
        total[0] = rows[0]["price"]
        return render_template("index.html", rows=rows, user=user, cash_remaining=index_cash_remaining, index_display=index_display[0], total=total)

    elif index_display[0] == "sold":
        rows = db.execute("SELECT * FROM stocks WHERE id = ?", index_stock_id[0])
        total[0] = rows[0]["price"]
        return render_template("index.html", rows=rows, user=user, cash_remaining=index_cash_remaining, index_display=index_display[0], total=total)

    elif index_display[0] == "history":

        index_display[0] = "history"
        rows = db.execute(
            "select stocks.id, stocks.symbol, stocks.shares, stocks.price, userstocks.transactions, userstocks.transaction_type from stocks join userstocks on stocks.id = userstocks.sid join users on users.id = userstocks.uid where users.id = ?", session["user_id"])

        return render_template("index.html", rows=rows, index_display=index_display[0])
        # return apology("history will be displayed here")

    elif index_display[0] == "stock_info":

        session_id = session["user_id"]
        index_display[0] = "stock_info"

        rows = db.execute(
            "select stocks.symbol, stocks.name, sum(cast(stocks.shares as int)) as total_shares from stocks join userstocks on stocks.id = userstocks.sid join users on users.id = userstocks.uid where users.id = ? group by symbol", session["user_id"])

        return render_template("index.html", rows=rows, user=user, index_display=index_display[0], total=total)

        # return render_template("index.html", rows=rows, user=user, index_display= "stock_info", total= 1001)
    else:
        return render_template("index.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        valid_share = False  # to check if weather user input share is number on not true if number
        requested_symbol = request.form.get("symbol")
        requested_shares = request.form.get("shares")
        submited_symbole_valid = False
        submited_share_valid = True
        xx = str(requested_symbol)
        yy = requested_shares
        # check submited input (symbol) validity
        for i in range(len(str(requested_symbol))):
            if ord(requested_symbol[i]) < 65 or ord(requested_symbol[i]) > 97:
                return apology("symbol not correct")
            if i == len(requested_symbol) - 1:
                submited_symbole_valid = True

        # check submited input (share) validity
        for i in range(len(yy)):
            if (ord(yy[i]) < 48 or ord(yy[i]) > 57):
                return apology("submited data not valid")
                break
            if i == len(yy) - 1:
                submited_share_valid = True
        yy = math.floor(int(request.form.get("shares")))

        # Validate submited stock symbol
        for i in range(len(xx)):

            if (ord(xx[i]) < 65 or ord(xx[i]) > 90):
                return apology("submited stock symbol is not valid")
                break

            if i == len(xx) - 1:
                submited_symbole_valid = True

        checked_symbol = lookup(str(requested_symbol))
        if checked_symbol and requested_symbol and requested_shares:
            session_id = int(session["user_id"])
            # check if user has sufficent fund
            users_ld = db.execute("SELECT * FROM users WHERE id = ?", session_id)
            user_cash = users_ld[0]['cash']
            cash_needed = int(requested_shares) * checked_symbol["price"]
            cash_remaining = usd(user_cash - cash_needed)
            if cash_remaining >= 0:
                # 1 add symbol information to stocks table in the database
                stock_ld = db.execute("INSERT INTO stocks(symbol, name, shares, price) VALUES (?, ?, ?, ?)",
                                      checked_symbol["symbol"], checked_symbol["name"], int(requested_shares), checked_symbol["price"])
                # find id of inserted stock
                inserted_stock_ld = db.execute("SELECT * FROM stocks ORDER BY id DESC LIMIT 1")
                inserted_stock_id = inserted_stock_ld[0]["id"]  # id integer datatype

                # 2 update cash in user  cash_avilable
                db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_remaining, session_id)

                # 3 insert transaction infromation to userstocks
                db.execute("INSERT INTO userstocks (uid, sid, transactions, transaction_type) VALUES (?, ?, ?, ?)",
                           session_id, inserted_stock_id, datetime.datetime.now(), "bought")

                # return redirect("/")
                index_display[0] = "bought"
                index_rows[0] = inserted_stock_ld
                index_stock_id[0] = inserted_stock_id
                index_cash_remaining[0] = cash_remaining
                # return render_template("index.html", rows=inserted_stock_ld, user=users_ld, cash_remaining=cash_remaining, index_display= str(index_display[0]))
                return redirect("/")
                return apology("THOMAS KITABA TEST")
            else:
                return apology("Insuficent CASH in ACCOUNT")

        else:

            return apology("Symbol not found")
    else:
        return render_template("buy.html")
        # return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    index_display[0] = "history"
    # select stocks.id, stocks.symbol, stocks.shares, stocks.price, userstocks.transactions, userstocks.transaction_type from stocks join userstocks on stocks.id = userstocks.sid join users on users.id = userstocks.uid where users.id = 4;
    return redirect("/")


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
def quote():
    """Get stock quote."""
    #display[0] = request.form.get("display")
    xx = request.form.get("symbol")
    ticker_valid = False
    row = lookup(str(xx))

    if request.method == "POST":

        if xx:
            for i in range(len(xx)):

                if ord(xx[i]) >= 65 and ord(xx[i]) <= 97:
                    ticker_valid = True
                else:

                    ticker_valid = False

                    return apology("ticker symbol is invalid")

        else:
            return apology("ticker symbol not provided")

        if ticker_valid:
            row = lookup(str(xx))
            if row:
                return render_template("quote.html", row=row)
            else:
                return apology("ticker symbol not found")
    else:
        return render_template("quote.html")


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

    # return apology("TODO")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    session_id = session["user_id"]
    index_display[0] = "sold"
    users_ld = db.execute("SELECT * FROM users WHERE id = ?", session_id)
    list_sum = []
    user_stocks_list = db.execute(
        "SELECT id, symbol, sum(shares) as sum_of_shares from stocks where id in (select sid from userstocks where uid = ? ) group by symbol", session["user_id"])
    # conver dictionary to list or two dimensional array
    # validate user submited input

    list_sum = []
    for row in user_stocks_list:
        list_sum.append([row["symbol"], math.floor(row["sum_of_shares"])])

    if request.method == "POST":
        share_valid_for_sale = False  # to check if weather user input share is number on not true if number
        submited_share_valid = False
        submited_symbole_valid = False
        requested_symbol = str(request.form.get("symbol"))
        xx = str(request.form.get("symbol"))

        requested_shares = request.form.get("shares")
        yy = str(request.form.get("shares"))
        # ADD input validation here TODO
        for i in range(len(yy)):
            if (ord(yy[i]) < 48 or ord(yy[i]) > 57):
                return apology("submited data not valid")
                break
            if i == len(yy) - 1:
                submited_share_valid = True
        yy = math.floor(int(request.form.get("shares")))

        # Validate submited stock symbol
        for i in range(len(xx)):

            if (ord(xx[i]) >= 65 or ord(xx[i]) <= 90):
                submited_symbole_valid = True
            else:
                return apology("submited stock symbol is not valid")

        # user_stocks_list= db.execute("SELECT id, symbol, sum(shares) as sum_of_shares from stocks where id in (select sid from userstocks where uid = ? ) group by symbol", session["user_id"])

        checked_symbol = lookup(str(xx))

        # check if user is selling what he has

        for i in range(len(list_sum)):
            # return apology("checking users share list")
            if str(list_sum[i][0]) == xx:
                if list_sum[i][1] >= yy:
                    share_valid_for_sale = True
                    # return apology("share avilable for thomas kitaba sale")

                else:
                    return apology("Insufficent share for sale")

        if share_valid_for_sale == True and submited_share_valid == True and submited_symbole_valid == True:

            users_ld = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
            user_cash = users_ld[0]['cash']

            cash_remaining = (user_cash + yy)

            yy = yy * (-1)

            # 1 add symbol information to stocks table in the database
            stock_ld = db.execute("INSERT INTO stocks(symbol, name, shares, price) VALUES (?, ?, ?, ?)", xx, checked_symbol["name"],
                                  yy, checked_symbol["price"])
            # find id of inserted stock
            inserted_stock_ld = db.execute("SELECT * FROM stocks ORDER BY id DESC LIMIT 1")

            inserted_stock_id = inserted_stock_ld[0]["id"]  # id integer datatype

            # 2 update cash in user  cash_avilable
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_remaining, session["user_id"])

            # 3 insert transaction infromation to userstocks
            db.execute("INSERT INTO userstocks (uid, sid, transactions, transaction_type) VALUES (?, ?, ?, ?)",
                       session_id, inserted_stock_id, datetime.datetime.now(), "sold")

            # return redirect("/")
            index_display[0] = "sold"  # --------------------
            index_rows[0] = inserted_stock_ld  # ----------------
            index_stock_id[0] = inserted_stock_id  # ---------------------
            index_cash_remaining[0] = cash_remaining

            return redirect("/")
            # return apology("processing stock sale finished succesfully")
        else:
            return apology("Insuficent Amount of shares for sale")

        # to be checked

        # to be checked ----------------------------------------------------------------
    else:

        rows = db.execute(
            "SELECT id, symbol, sum(shares) as sum_of_shares from stocks where id in (select sid from userstocks where uid = ?) group by symbol", session["user_id"])

        return render_template("sell.html", rows=rows)


# TEST PRINT
#rows= db.execute("select * from users")
# print(rows)
#query1 = "SELECT username FROM users WHERE id = ?"
#id = (int(1))


#user= db.execute(query1, id)
# print(user)
# ------------------------------------
#rows = db.execute("SELECT symbol, sum(shares) as sum_of_shares from stocks where id in (select sid from userstocks where uid = ?) group by symbol", 16)

# for row in rows:
    # print(row['symbol'])
    # print(row['sum_of_shares'])
    # print(row)
# ------------------------------------
#rows = db.execute("select * from stocks join userstocks on stocks.id = userstocks.sid where userstocks.uid = ?", 4)

# for row in rows:
    # print(row)
# --------------------------

user_stocks_list = db.execute(
    "SELECT id, symbol, sum(shares) as sum_of_shares from stocks where id in (select sid from userstocks where uid = ? ) group by symbol", 4)
for row in user_stocks_list:
    if row["symbol"] == "AAPL":
        print("found")


list_sum = []
for row in user_stocks_list:
    list_sum.append([row["symbol"], math.floor(row["sum_of_shares"])])

for i in range(len(list_sum)):
    print(list_sum[i])
    if list_sum[i][0] == 'PEP':
        if list_sum[i][1] > 1:
            print(list_sum[i][1], end='')
            print(" share avilable for sale")
        else:
            print("insufficent share")
# ------------------

input = "335555f55"

for i in range(len(input)):
    if (ord(input[i]) < 48 or ord(input[i]) > 57):
        print("invalid input ")
        break
    if i == len(input) - 1:
        print("valid input your are good to go")


row = lookup('BA')
print(row)


#rows= db.execute("SELECT id, symbol, sum(shares) as sum_of_shares from stocks where id in (select sid from userstocks where uid = ?) group by symbol", session["user_id"])
usd(100)
print(usd(233))