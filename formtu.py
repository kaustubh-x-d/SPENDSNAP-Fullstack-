from flask import Flask, render_template, request
app = Flask(__name__)
# @app.route("/")
# def home():
#     return render_template("home.html")
@app.route("/",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        username=request.form["Budget"]
        print(username,type(username))
        return render_template("welcome.html",username=username)
    return render_template("budget_log.html")
if __name__ == "__main__":
    app.run(debug=True)
