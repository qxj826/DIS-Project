from flask import Blueprint, render_template, request, redirect, url_for, session
from .models import db, User, WorkoutSession, Recommendation, Snack
from .recommendations import recommend_snacks
from datetime import datetime

bp = Blueprint("main", __name__)

# ---------- LOGIN ----------
@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["username"].strip().lower()
        pwd = request.form["password"]

        user = User.query.filter_by(username=uname).first()

        if user is None:
            # registrér ny bruger
            user = User(username=uname)
            user.set_password(pwd)
            db.session.add(user)
            db.session.commit()
        elif not user.check_password(pwd):
            return render_template("login.html", error="Forkert password")

        # log ind → gem id i session
        session["user_id"] = user.id
        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


# ---------- LOGOUT ----------
@bp.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("main.login"))


def _current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None


# ---------- DASHBOARD ----------
@bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = _current_user()
    if not user:
        return redirect(url_for("main.login"))

    if request.method == "POST":
        calories = int(request.form["calories"])

        # registrér workout (uden activity-type her)
        session_row = WorkoutSession(
            date=datetime.utcnow(),
            calories_burned=calories,
            user=user,
        )
        db.session.add(session_row)
        db.session.commit()

        snacks = recommend_snacks(session_row, user)

        # gem anbefalinger i DB
        for s in snacks:
            db.session.add(
                Recommendation(user_id=user.id, session_id=session_row.id, snack_id=s.id)
            )
        db.session.commit()

        return render_template("dashboard.html", user=user, snacks=snacks)

    return render_template("dashboard.html", user=user)
