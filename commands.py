from datetime import datetime
import mysql.connector as my
import csv

connector=my.connect(host="localhost", user="root", password="210607", database="spendsnap")
cursor=connector.cursor()

def add_data(run_login):
    cursor.execute(
    "SELECT budget_start FROM remaining_budget WHERE username = %s",
    (run_login,)
    )
    budget_start = cursor.fetchone()[0]
    amount=int(input("Enter Amount spent"))
    date=datetime.strptime(input("Enter Date of Transactions: "), "%Y-%m-%d").date()
    if date<=budget_start:
        print("Transaction Date cannot be in past")
    else:
        allowed_categories = [
        "Grocery", 
        "Entertainment", 
        "Health and Fitness", 
        "Snacks", 
        "Relatives/Friends"
        ]

        while True:
            category = input('''Enter Category: 
                                Grocery, 
                                Entertainment, 
                                Health and Fitness, 
                                Snacks, 
                                Relatives/Friends''').strip()
            if category in allowed_categories:
                break
            else:
                print("Invalid category. Choose from:", ", ".join(allowed_categories))
        cursor.execute(
        "INSERT INTO transactions (amount, date, category,username) VALUES (%s, %s, %s,%s);",
        (amount, date, category,run_login)
    )
        connector.commit()
        cursor.execute("select Sum(amount) from transactions where username=%s AND date >= %s;",
        (run_login, budget_start))
        total=cursor.fetchone()
        cursor.execute("select Initial_budget from remaining_budget where username=%s;",(run_login,))
        Initial_budget=cursor.fetchone()
        if total[0]==None:
            pass
        else:
            cursor.execute("UPDATE remaining_budget SET amt_left = %s WHERE username=%s;",(Initial_budget[0]-total[0],run_login,))
        connector.commit()

def show_T(username):
    cursor.execute("SELECT budget_start FROM remaining_budget WHERE username = %s", (username,))
    budget_start = cursor.fetchone()[0]
    cursor.execute("Select * from transactions where username=%s AND date >= %s;",(username,budget_start))
    transactions_data=cursor.fetchall()
    print("Amount \t Date \t Category")
    for i in transactions_data:
        print(f"{i[1]} \t {i[3]} \t {i[2]}") 

def categories__(username):
    cursor.execute("SELECT budget_start FROM remaining_budget WHERE username = %s", (username,))
    budget_start = cursor.fetchone()[0]
    cursor.execute("select Category, Sum(amount) from transactions where username=%s AND date >= %s group by Category;",(username, budget_start))
    category_data=cursor.fetchall()
    print("Category \t Total Amount")
    for i in category_data:
        print(f"{i[0]} \t {i[1]}")

def show_R(username):
    cursor.execute("select username, amt_left from remaining_budget where username=%s;",(username,))
    r_data=cursor.fetchone()
    print("Username \t Remaining Budget")
    print(f"{r_data[0]} \t \t {r_data[1]}")

def edit(username):
    ch=input("Edit/Delete ?: ")
    if ch.lower()== "edit":
        column=input("Which Column ?: ")
        date_=datetime.strptime(input("Enter Recorded Date of Transactions: "), "%Y-%m-%d").date()
        allowed_categories = [
        "Grocery", 
        "Entertainment", 
        "Health and Fitness", 
        "Snacks", 
        "Relatives/Friends"
        ]

        while True:
            category_ = input('''Enter Category: 
                                Grocery, 
                                Entertainment, 
                                Health and Fitness, 
                                Snacks, 
                                Relatives/Friends''').strip()
            if category_ in allowed_categories:
                break
            else:
                print("Invalid category. Choose from:", ", ".join(allowed_categories))
        
        if column.lower()=="amount":
            edited_amt=int(input("Enter Amount: "))
            cursor.execute(f"UPDATE transactions SET {column} = %s WHERE Date = %s AND Category = %s AND username = %s",(edited_amt,date_,category_,username))
        elif column.lower()=="date":
            edited_date=datetime.strptime(input("Enter Updated Date of Transactions: "), "%Y-%m-%d").date()
            cursor.execute("update transactions set Date=%s where Date=%s and Category=%s and username=%s;", (edited_date,date_,category_,username))
        elif column.lower()=="category":
                edited_category=input("Enter Updated Category")
                cursor.execute("update transactions set Category=%s where Date=%s and Category=%s and username =%s;",(edited_category, date_, category_,username))
        
    elif ch.lower()=="delete":
        date_=datetime.strptime(input("Enter Date of Transactions: "), "%Y-%m-%d").date()
        allowed_categories = [
        "Grocery", 
        "Entertainment", 
        "Health and Fitness", 
        "Snacks", 
        "Relatives/Friends"
        ]

        while True:
            category = input('''Enter Category: 
                                Grocery, 
                                Entertainment, 
                                Health and Fitness, 
                                Snacks, 
                                Relatives/Friends''').strip()
            if category in allowed_categories:
                break
            else:
                print("Invalid category. Choose from:", ", ".join(allowed_categories))
        cursor.execute("delete from transactions where Date=%s and Category=%s and username=%s;",(date_,category,username))

    connector.commit()

def export_data(user):
    cursor.execute("SELECT amount, date, category FROM transactions WHERE username = %s", (user,))
    transactions_data = cursor.fetchall()

    if not transactions_data:
        print("No transactions found to export.")
        return 

    filename = f"{user}_transactions.csv"
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Amount", "Date", "Category"])
        writer.writerows(transactions_data)

    print(f"Transactions exported successfully to {filename}")
