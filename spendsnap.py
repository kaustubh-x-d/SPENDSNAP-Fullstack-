import mysql.connector as my
from datetime import datetime
import Spendscommands as C
from flask import Flask, render_template, request, redirect, url_for
connector=my.connect(host="localhost", user="root", password="210607", database="demo")
cursor=connector.cursor()

app = Flask(__name__)

today=datetime.today().date()
user_name=""
passwordd=""

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup.html",methods=["GET","POST"])
def sign_up():
    if request.method=="POST":
        global user_name
        global passwordd
        user_name=request.form["Username"]
        passwordd=request.form["Password"]
        cursor.execute("SELECT * FROM user WHERE username = %s", (user_name,))
        if cursor.fetchone():
            return render_template("signup.html", error="Username already exist",username=user_name)
        
        today = datetime.today().date()

        cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (user_name, passwordd))
        cursor.execute(
        "INSERT INTO remaining_budget (username, amt_left) VALUES (%s, 0)",
        (user_name,)
        )
        connector.commit()

        #     (user_name, initial_budget, today, today, initial_budget))
        connector.commit()
        return render_template("home.html")
    return render_template("signup.html")

@app.route("/login.html", methods= ["GET", "POST"])
def login():
    if request.method=="POST":
        global user_name
        global passwordd
        user_name=request.form["Username"]
        passwordd=request.form["Password"]
        cursor.execute("Select * from user where username=%s and password=%s", (user_name,passwordd))
        result=cursor.fetchone()
        if result:
            cursor.execute("SELECT last_updated FROM remaining_budget WHERE username = %s", (user_name,))
            data = cursor.fetchone()
            last_updated=data[0]
            if last_updated==None:
                return redirect(url_for("budget_log"))
            elif (today-last_updated).days<=30:
                return redirect(url_for("spendsnap"))
            else:
                return redirect(url_for("budget_log"))
        else:
            return render_template("login.html", error="Incorrect Username or password")
    return render_template("login.html")

@app.route("/budget_log.html", methods= ["GET","POST"])
def budget_log():
    if request.method=="POST":    
        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (user_name, passwordd))
        result = cursor.fetchone()
        if result:
            cursor.execute("SELECT amt_left FROM remaining_budget WHERE username = %s", (user_name,))
            amt_left=cursor.fetchone()
            cursor.execute("SELECT last_updated FROM remaining_budget WHERE username = %s", (user_name,))
            data = cursor.fetchone()
            if data[0]==None:
                initial__budget=int(request.form["Budget"])
                message="Please set up you Budget"
                cursor.execute("UPDATE remaining_budget SET amt_left = %s, last_updated = %s, budget_start=%s,  Initial_budget=%s WHERE username = %s",(initial__budget, today, today,initial__budget,user_name))
                connector.commit()
            else:
                last_updated=data[0]
                print(data) 
                if (today-last_updated).days>=30:
                    initial___budget = int(request.form["Budget"])
                    cursor.execute("UPDATE remaining_budget SET amt_left = %s, last_updated = %s, budget_start=%s,  Initial_budget=%s WHERE username = %s",(initial___budget, today, today, user_name,initial___budget))
                    connector.commit()
                    message="It's been 30+ days. Enter new budget: "
                else:
                    initial__budget = amt_left
            return redirect(url_for("spendsnap",message=message))
    return render_template("budget_log.html")

@app.route("/spendsnap.html",methods=["GET","POST"])
def spendsnap():
    return render_template("spendsnap.html",username=user_name)

@app.route("/add.html",methods=["GET","POST"])
def add():
    if request.method=="POST":
        amount=request.form["AMOUNT"]
        date=request.form["DATE"]
        category=request.form["CATEGORY"]
        C.add_expense(amount,category,date,user_name)
        return redirect(url_for("spendsnap"))
    return render_template("add.html")

@app.route("/transactions.html", methods=["GET","POST"])
def show():
    if request.method=="POST":
        

if __name__ == "__main__":
    app.run(debug=True)
