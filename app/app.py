from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from random import sample
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://localhost/snackster_dev")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    deficit_goal  = db.Column(db.Integer)

    def set_password(self, pwd):  self.password_hash = generate_password_hash(pwd)
    def check_password(self, pwd): return check_password_hash(self.password_hash, pwd)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    calories_burned = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Snack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    calories = db.Column(db.Numeric)
    grams    = db.Column(db.Numeric)
    protein  = db.Column(db.Numeric)
    carbs    = db.Column(db.Numeric)

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer)
    session_id = db.Column(db.Integer)
    snack_id   = db.Column(db.Integer)

def _current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None

def recommend_snacks(ws, user, k=9999):
    ceiling = ws.calories_burned
    snacks  = Snack.query.filter(Snack.calories > 0,
                                 Snack.calories <= ceiling).all()
    results = []
    for s in snacks:
        servings = int(ceiling // float(s.calories))
        if servings:
            results.append({
                "id":        s.id,
                "name":      s.name,
                "servings":  servings,
                "grams":     (s.grams or 0)   * servings,
                "calories":  s.calories       * servings,
                "protein":  (s.protein or 0) * servings,
                "carbs":    (s.carbs   or 0) * servings,
            })
    return results[:k]

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["username"].strip().lower()
        pwd   = request.form["password"]
        user  = User.query.filter_by(username=uname).first()
        if not user:
            user = User(username=uname); user.set_password(pwd); db.session.add(user); db.session.commit()
        elif not user.check_password(pwd):
            return render_template("login.html", error="Forkert password")
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = _current_user()
    if not user:
        return redirect(url_for("login"))

    # ------------------------------------------------ POST: user submits kcal
    if request.method == "POST":
        session["cal_limit"] = int(request.form["calories"])
        return redirect(url_for("dashboard"))        # PRG pattern

    # ------------------------------------------------ GET
    cal_limit = session.get("cal_limit")
    q         = request.args.get("q", "").strip()
    snacks    = []

    if cal_limit:
        fake_ws = type("WS", (), {"calories_burned": cal_limit})

        if q:                         # --- SEARCH mode -----------
            # all snacks ≤ kcal whose name matches q
            rows = Snack.query.filter(
                Snack.calories <= cal_limit,
                Snack.name.ilike(f"%{q}%")
            ).all()
            # convert to dicts (no random sampling)
            snacks = [dict(id=r.id,
                           name=r.name,
                           servings=int(cal_limit // float(r.calories)),
                           grams=(r.grams or 0) * int(cal_limit // float(r.calories)),
                           calories=r.calories * int(cal_limit // float(r.calories)),
                           protein=(r.protein or 0) * int(cal_limit // float(r.calories)),
                           carbs  =(r.carbs   or 0) * int(cal_limit // float(r.calories)))
                      for r in rows if cal_limit // float(r.calories) >= 1]

        else:                        # --- INITIAL recommend 5 ----
            snacks = recommend_snacks(fake_ws, user, k=5)

    return render_template(
        "dashboard.html",
        user=user,
        snacks=snacks,
        search=q,
        cal_limit=cal_limit
    )


@app.route("/add_snack", methods=["GET", "POST"])
def add_snack():
    if not _current_user(): return redirect(url_for("login"))

    if request.method == "POST":
        p = request.form                      
        sql = open("app/insert_snack.sql").read()
        db.session.execute(db.text(sql), {
            "name": p["name"],
            "cal" : p["calories"] or None,
            "g"   : p["grams"]    or None,
            "p"   : p["protein"]  or None,
            "c"   : p["carbs"]    or None,
        })
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("add_snack.html")

if __name__ == "__main__":
    db.create_all()          
    app.run()
