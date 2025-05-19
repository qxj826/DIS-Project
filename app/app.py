from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from random import sample
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://localhost/snackster_dev")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

# Database setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    deficit_goal = db.Column(db.Integer)
    workouts = db.relationship("WorkoutSession", backref="user")

    def set_password(self, pwd: str) -> None:
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd: str) -> bool:
        return check_password_hash(self.password_hash, pwd)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    calories_burned = db.Column(db.Integer, nullable=False)
    activity_type = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recommendations = db.relationship("Recommendation", backref="session")

class Snack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    brand = db.Column(db.String(120))
    calories = db.Column(db.Integer)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    session_id = db.Column(db.Integer, db.ForeignKey("workout_session.id"))
    snack_id = db.Column(db.Integer, db.ForeignKey("snack.id"))

# Helper functions
def _current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None

def recommend_snacks(session, user, k=5):
    ceiling = session.calories_burned
    snacks = Snack.query.filter(Snack.calories <= ceiling).all()
    return sample(snacks, k) if len(snacks) >= k else snacks

# Routes
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["username"].strip().lower()
        pwd = request.form["password"]

        user = User.query.filter_by(username=uname).first()
        if user is None:
            user = User(username=uname)
            user.set_password(pwd)
            db.session.add(user)
            db.session.commit()
        elif not user.check_password(pwd):
            return render_template("login.html", error="Forkert password")

        session["user_id"] = user.id
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = _current_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        calories = int(request.form["calories"])
        session_row = WorkoutSession(date=datetime.utcnow(), calories_burned=calories, user=user)
        db.session.add(session_row)
        db.session.commit()

        snacks = recommend_snacks(session_row, user)
        for s in snacks:
            db.session.add(Recommendation(user_id=user.id, session_id=session_row.id, snack_id=s.id))
        db.session.commit()

        return render_template("dashboard.html", user=user, snacks=snacks)

    return render_template("dashboard.html", user=user)

# Run the app
if __name__ == "__main__":
    app.run()