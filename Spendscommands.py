import mysql.connector as my
from datetime import datetime

connector=my.connect(host="localhost", user="root", password="210607", database="demo")
cursor=connector.cursor()

today=datetime.today().date()
user_name=""
passwordd=""

def add_expense(amount,category,datee,user):
    cursor.execute(
        "SELECT budget_start FROM remaining_budget WHERE username = %s",
        (user,)
        )
    budget_start = cursor.fetchone()[0]
    date=datetime.strptime(str(datee), "%Y-%m-%d").date()
    if date<=budget_start:
        print("Transaction Date cannot be in past")
    else:
        cursor.execute(
        "INSERT INTO transactions (amount, date, category,username) VALUES (%s, %s, %s,%s);",
        (amount, date, category,user))
        connector.commit()
        cursor.execute("select Sum(amount) from transactions where username=%s AND date >= %s;",
        (user, budget_start))
        total=cursor.fetchone()
        cursor.execute("select Initial_budget from remaining_budget where username=%s;",(user,))
        Initial_budget=cursor.fetchone()
        if total[0]==None:
            pass
        else:
            cursor.execute("UPDATE remaining_budget SET amt_left = %s WHERE username=%s;",(Initial_budget[0]-total[0],user,))
        connector.commit()

def show_T(username):
    cursor.execute("SELECT budget_start FROM remaining_budget WHERE username = %s", (username,))
    budget_start = cursor.fetchone()[0]
    print(budget_start,type(budget_start))
    cursor.execute("Select amount, Date, Category from transactions where username=%s AND date >= %s ;",(username,budget_start))
    transactions_data=cursor.fetchall()
    return transactions_data

def categories(username):
    cursor.execute("SELECT budget_start FROM remaining_budget WHERE username = %s", (username,))
    budget_start = cursor.fetchone()[0]
    cursor.execute("select Category, Sum(amount) from transactions where username=%s AND date >= %s group by Category;",(username, budget_start))
    category_data=cursor.fetchall()
    return category_data

def show_R(username):
    cursor.execute("select username, amt_left from remaining_budget where username=%s;",(username,))
    r_data=cursor.fetchone()
    return r_data

def show_d(username):
    cursor.execute("SELECT budget_start FROM remaining_budget WHERE username = %s", (username,))
    budget_start = cursor.fetchone()[0]
    cursor.execute("select Date, Sum(amount) from transactions where username=%s AND date >= %s group by Date;",(username, budget_start))
    category_data=cursor.fetchall()
    return category_data

def Edit(column,category,date,edited_amt,edited_date,edited_category,username):
    allowed_categories = [
        "Grocery", 
        "Entertainment", 
        "Health and Fitness", 
        "Snacks", 
        "Relatives/Friends"
        ]
    if category not in allowed_categories:
        print("Invalid category. Choose from:", ", ".join(allowed_categories))
        return  # exit early instead of infinite loop
    
    if column.lower() == "amount":
        cursor.execute(
            "UPDATE transactions SET amount = %s WHERE Date = %s AND Category = %s AND username = %s;",
            (edited_amt, date, category, username)
        )
    elif column.lower()=="date":
        edited__date=datetime.strptime(edited_date, "%Y-%m-%d").date()
        cursor.execute("update transactions set Date=%s where Date=%s and Category=%s and username=%s;", (edited__date,date,category,username))
    elif column.lower()=="category":
        cursor.execute("update transactions set Category=%s where Date=%s and Category=%s and username =%s;",(edited_category, date, category,username))
    connector.commit()

def delete(date,category,username):
    date_=datetime.strptime(date, "%Y-%m-%d").date()
    allowed_categories = [
        "Grocery", 
        "Entertainment", 
        "Health and Fitness", 
        "Snacks", 
        "Relatives/Friends"
        ]

    if category not in allowed_categories:
        print("Invalid category. Choose from:", ", ".join(allowed_categories))
        return  # exit early instead of infinite loop
    
    cursor.execute("delete from transactions where Date=%s and Category=%s and username=%s;",(date_,category,username))
    connector.commit()


