import mysql.connector as my
from datetime import datetime
import commands as C
connector=my.connect(host="localhost", user="root", password="210607", database="spendsnap")
cursor=connector.cursor()

today=datetime.today().date()

def sign_up():
    new_user = input("Create your user name").strip().lower()
    passwordd = input("Enter Password: ").strip()

    cursor.execute("SELECT * FROM user WHERE username = %s", (new_user,))
    if cursor.fetchone():
        return "Existing User..... Try Again"

    initial_budget = int(input("Enter Your Budget"))
    today = datetime.today().date()

    cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (new_user, passwordd))
    cursor.execute(
        "INSERT INTO remaining_budget (username, amt_left, last_updated, budget_start, Initial_budget) VALUES (%s, %s, %s, %s,%s)",
        (new_user, initial_budget, today, today, initial_budget)
    )
    connector.commit()
    return new_user


def login():
    user_name = input("Enter Username: ")
    passwordd = input("Enter Password: ")
    cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (user_name, passwordd))
    result = cursor.fetchone()
    if result:
        cursor.execute("SELECT amt_left,last_updated FROM remaining_budget WHERE username = %s", (user_name,))
        data = cursor.fetchone()
        amt_left,last_updated=data
        if last_updated==None:
            initial__budget=int(input("Enter your Initial budget: "))  
        else: 
            if (today-last_updated).days>=30:
                initial__budget = int(input("It's been 30+ days. Enter new budget: "))
                cursor.execute("UPDATE remaining_budget SET amt_left = %s, last_updated = %s, budget_start=%s,  Initial_budget=%s WHERE username = %s",(initial__budget, today, today, user_name,initial__budget))
                connector.commit()
            else:
                initial__budget = amt_left
        return user_name  
    else:
        return "User Not Found or Incorrect Password..... Try Again"

print("Welcome to the SpendSnap")
authentication=input("Would you like to login or Sign up?: ")
# initial_budget=0
# remaining_amt=initial_budget
run=None
run_sign="Existing User..... Try Again"
try:
    if authentication.lower()=="login":
        while True:
            user = login()
            if user == "User Not Found..... Try Again":
                print(user)
            else:
                break

        while True:
            print('''What would you like to do:\n1. 
                Add expense \n
                2. Show categories where expenses spent and how much\n
                3. Show all Transactions
                4. Show Remaining Budget\n
                5. Edit or Delete a Transaction\n
                6. Export Data to Spreadsheet
                7. Logout''')
            try:
                while True:    
                    choice=int(input("Enter Choice as Option No.: "))    
                    if choice== 1:
                        C.add_data(user)
                    elif choice==2:
                        C.categories__(user)
                    elif choice==3:
                        C.show_T(user)
                    elif choice==4:
                        C.show_R(user)
                    elif choice==5:
                        C.edit(user)
                    elif choice==6:
                        C.export_data(user)
                    elif choice==7:
                        print("Logged Out succesfully")
                        break
            except ValueError:
                print("Please Enter Valid Option Number")
            break
    elif authentication.lower()=="sign up":
        while run==None or run=="Existing User..... Try Again":
            run=sign_up()
            user=run
            if run=="Existing User..... Try Again":
                print("Existing User..... Try Again")
                pass
            else:
                continue
        else:
            print(run)
            print('''What would you like to do:\n1. 
                Add expense \n
                2. Show categories where expenses spent and how much in last budget\n
                3. Show all Transactions in last 
                4. Show Remaining Budget\n
                5. Edit or Delete a Transaction\n
                6. Export Transaction Data to Spreadsheet\n
                7. Logout & Exit''')
            try:
                while True:    
                    choice=int(input("Enter Choice as Option No.: "))    
                    if choice== 1:
                        C.add_data(user)
                    elif choice==2:
                        C.categories__(user)
                    elif choice==3:
                        C.show_T(user)
                    elif choice==4:
                        C.show_R(user)
                    elif choice==5:
                        C.edit(user)
                    elif choice==6:
                        C.export_data(user)
                    elif choice==7:
                        print("Logged Out succesfully")
                        break
            except ValueError:
                print("Enter Valid option number")
    else:
        raise ValueError
except ValueError:
    print("Invalid Input...Please enter valid input with correct spelling")
                