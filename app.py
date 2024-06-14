import re
from datetime import date, timedelta
from flask import Flask, flash, redirect, render_template, request, session,url_for
from flask_session import Session
from cs50 import SQL
import bcrypt
import csv
from functools import wraps


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db= SQL("sqlite:///games.db")
with open("teams.csv") as file:
    teams =list (csv.DictReader(file))

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(hashed_password, input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("id"):
            message="Please insert the id"
            return redirect(url_for('fail', message=message))
        elif not request.form.get("password"):
            message="Please insert the password"
            return redirect(url_for('fail', message=message))

        rows = db.execute("SELECT * FROM users WHERE id = ?", (request.form.get("id")))
        if len(rows) != 1 or not verify_password(rows[0]["password"], request.form.get("password")):
            message="Invalid user name or password"
            return redirect(url_for('fail', message=message))

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")



@app.route("/create_acc",methods=["GET","POST"])
def create_acc():
    if request.method == "GET":
        return render_template("create_acc.html", teams=teams)
    user_name=request.form.get("username")
    id = (request.form.get("id"))
    password=request.form.get("password")
    club=request.form.get("club")

    if not (user_name and id and password and club):
        message="Please insert the data required"
        return redirect(url_for('fail', message=message))
    pattern = pattern = r"^[1-5]20(18|19|20|21|22|23)0[0-3][0-9][0-9]$"
    if not re.match(pattern, id ):
        message="Please insert a valid id"
        return redirect(url_for('fail', message=message))
    users=db.execute("SELECT * FROM users WHERE id =?",id)
    if users:
        message="already used id"
        return redirect(url_for('fail', message=message))
    hashed=hash_password(password)
    db.execute("INSERT INTO users (username,id,team,password) VALUES(?,?,?,?) ",user_name,id,club,hashed)

    return  redirect("/")



@app.route("/fail")
def fail():
    message = request.args.get('message', '')
    return render_template('fail.html', message=message)

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")

@app.route("/")
@login_required
def matches():
    today_date = date.today()-timedelta(days=500)
    other_date = today_date +timedelta(days=7)
    matches= db.execute("SELECT * FROM games WHERE Date BETWEEN ? AND ? ",str(today_date),str(other_date))
    for match in matches:
        n= db.execute("SELECT COUNT(*) FROM registers WHERE game_id = ?",match["id"])[0]["COUNT(*)"]
        match["number"]=n
    return render_template("matches.html",matches=matches,teams=teams)

@app.route("/register" ,methods=["POST", "GET"])
@login_required
def register():
    id = session["user_id"]
    team = db.execute("SELECT team FROM users WHERE id = ?", id)[0]["team"]
    today_date = date.today()- timedelta(days=500)
    other_date = today_date + timedelta(days=7)
    match= db.execute("SELECT * FROM games WHERE Date BETWEEN ? AND ? AND (HomeTeam= ? OR AwayTeam=? )",str(today_date),str(other_date),team,team)
    match = match[0]
    home=""
    away=""
    for i in teams:
        if i["club_name"]==match["HomeTeam"]:
            home=i
        if i["club_name"]==match["AwayTeam"]:
            away=i
    if request.method == "GET":
        users = db.execute("SELECT user_id FROM registers WHERE game_id = ? AND user_id =?", match["id"],session["user_id"])
        return render_template("register.html", match=match ,home=home,away=away, users = users)

    else:
        value = request.form.get("reg")
        if value == "1" :
            exist=db.execute("SELECT COUNT(*) FROM registers WHERE user_id=? AND game_id=?",session["user_id"],match["id"])
            exist = exist[0]["COUNT(*)"]

            if exist>=50:
                message="there is no seat"
                return redirect(url_for('fail', message=message))

            db.execute("INSERT INTO registers (user_id,game_id) VALUES(?,?)",session["user_id"],match["id"])
            return redirect("/success")

        elif value == "0" :
            db.execute("DELETE FROM registers WHERE user_id=? AND game_id=?",session["user_id"],match["id"])
            return redirect("/register")