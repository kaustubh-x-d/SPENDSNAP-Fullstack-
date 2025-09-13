import mysql.connector as my
from datetime import datetime
import Spendscommands as C
from flask import Flask, render_template, request, redirect, url_for

# ----------------- DATABASE CONNECTION -----------------
try:
    connector = my.connect(
        host="localhost",
        user="root",
        password="210607",   # ⚠️ Better move to config in production
        database="demo"
    )
    cursor = connector.cursor()
except Exception as e:
    print("❌ Database connection failed:", e)
    raise

# ----------------- FLASK APP CONFIG -----------------
app = Flask(__name__)

today = datetime.today().date()
user_name = ""
passwordd = ""


# ----------------- ROUTES -----------------
@app.route("/")
def home():
    return render_template("home.html")


# -------- SIGN UP --------
@app.route("/signup.html", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        global user_name, passwordd
        user_name = request.form["Username"].strip()
        passwordd = request.form["Password"]

        try:
            # Check if user already exists
            cursor.execute("SELECT * FROM user WHERE username = %s", (user_name,))
            if cursor.fetchone():
                return render_template("signup.html", error="Username already exists", username=user_name)

            # Insert into tables
            cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (user_name, passwordd))
            cursor.execute("INSERT INTO remaining_budget (username, amt_left) VALUES (%s, 0)", (user_name,))
            connector.commit()

            return render_template("home.html")

        except Exception as e:
            connector.rollback()
            return render_template("signup.html", error=f"Error: {e}")

    return render_template("signup.html")


# -------- LOGIN --------
@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        global user_name, passwordd
        user_name = request.form["Username"].strip()
        passwordd = request.form["Password"]

        try:
            cursor.execute("SELECT * FROM user WHERE username=%s AND password=%s", (user_name, passwordd))
            result = cursor.fetchone()

            if result:
                cursor.execute("SELECT last_updated FROM remaining_budget WHERE username = %s", (user_name,))
                data = cursor.fetchone()
                last_updated = data[0] if data else None

                # ✅ Handle None safely
                if last_updated is None:
                    return redirect(url_for("budget_log"))
                elif (today - last_updated).days <= 30:
                    return redirect(url_for("spendsnap"))
                else:
                    return redirect(url_for("budget_log"))
            else:
                return render_template("login.html", error="Incorrect Username or Password")

        except Exception as e:
            return render_template("login.html", error=f"Error: {e}")

    return render_template("login.html")


# -------- BUDGET LOG --------
@app.route("/budget_log.html", methods=["GET", "POST"])
def budget_log():
    if request.method == "POST":
        try:
            cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (user_name, passwordd))
            result = cursor.fetchone()

            if result:
                cursor.execute("SELECT amt_left, last_updated FROM remaining_budget WHERE username = %s", (user_name,))
                data = cursor.fetchone()
                amt_left, last_updated = data if data else (0, None)

                if last_updated is None:
                    # First-time budget setup
                    initial_budget = int(request.form["Budget"])
                    cursor.execute(
                        "UPDATE remaining_budget SET amt_left=%s, last_updated=%s, budget_start=%s, Initial_budget=%s WHERE username=%s",
                        (initial_budget, today, today, initial_budget, user_name)
                    )
                    connector.commit()
                elif (today - last_updated).days >= 30:
                    # New budget after 30 days
                    new_budget = int(request.form["Budget"])
                    cursor.execute(
                        "UPDATE remaining_budget SET amt_left=%s, last_updated=%s, budget_start=%s, Initial_budget=%s WHERE username=%s",
                        (new_budget, today, today, new_budget, user_name)
                    )
                    connector.commit()

                return redirect(url_for("spendsnap"))

        except Exception as e:
            connector.rollback()
            return render_template("budget_log.html", error=f"Error: {e}")

    return render_template("budget_log.html")


# -------- DASHBOARD --------
@app.route("/spendsnap.html", methods=["GET", "POST"])
def spendsnap():
    return render_template("spendsnap.html", username=user_name)


# -------- ADD TRANSACTION --------
@app.route("/add.html", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        try:
            amount = request.form["AMOUNT"]
            date = request.form["DATE"]
            category = request.form["CATEGORY"]
            C.add_expense(amount, category, date, user_name)
            return redirect(url_for("spendsnap"))
        except Exception as e:
            return render_template("add.html", error=f"Error: {e}")

    return render_template("add.html")


# -------- TRANSACTIONS --------
@app.route("/transactions.html", methods=["GET", "POST"])
def show():
    columns, data = [], []
    if request.method == "POST":
        try:
            choice = request.form.get("Choice", "")
            if choice.lower() == "category":
                columns = ["Category", "Amount"]
                data = C.categories(user_name)
            elif choice.lower() == "date":
                columns = ["Date", "Amount"]
                data = C.show_d(user_name)
            elif choice.lower() == "no filters":
                columns = ["Amount", "Date", "Category"]
                data = C.show_T(user_name)
            elif choice.lower() == "exit":
                return redirect(url_for("spendsnap"))
        except Exception as e:
            return render_template("transactions.html", error=f"Error: {e}")

    return render_template("transactions.html", columns=columns, row_data=data)


# -------- EDIT TRANSACTION ----------
@app.route("/edit.html", methods=["GET", "POST"])
def edit_D():
    if request.method == "POST":
        try:
            columns = request.form["Column"]
            category = request.form["Category"]
            date = request.form["Date"]
            edited_amt = request.form["Amt"]   # ✅ fixed case consistency
            edited_date = request.form["Edit_date"]
            edited_category = request.form["Edit_categ"]
            C.Edit(columns, category, date, edited_amt, edited_date, edited_category, user_name)
            return redirect(url_for("spendsnap"))
        except Exception as e:
            return render_template("edit.html", error=f"Error: {e}")

    return render_template("edit.html")


# -------- DELETE TRANSACTION --------
@app.route("/delete.html", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        try:
            date = request.form["Date"]
            category = request.form["Category"]
            C.delete(date, category, user_name)
            return redirect(url_for("spendsnap"))
        except Exception as e:
            return render_template("delete.html", error=f"Error: {e}")

    return render_template("delete.html")


# ----------------- MAIN ENTRY -----------------
if __name__ == "__main__":
    app.run(debug=True)
