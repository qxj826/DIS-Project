from flask import (
    Flask, render_template, request, redirect, url_for,
    session, abort
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pathlib, os, re
from sqlalchemy import text

# ---------- regexes ------------------------------------------------
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,20}$")
EMAIL_RE    = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

# ---------- Flask & DB ---------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "postgresql://localhost/snackster_dev"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ---------- models -------------------------------------------------
class User(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80), unique=True, nullable=False)
    password_hash= db.Column(db.String(256),               nullable=False)
    email        = db.Column(db.String(120))
    fullname     = db.Column(db.String(120))

    def set_password(self, pwd):   self.password_hash = generate_password_hash(pwd)
    def check_password(self, pwd): return check_password_hash(self.password_hash, pwd)

class WorkoutSession(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    date            = db.Column(db.DateTime, default=datetime.utcnow)
    calories_burned = db.Column(db.Integer, nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey("user.id"))

class Snack(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(120))
    calories = db.Column(db.Numeric)
    grams    = db.Column(db.Numeric)
    protein  = db.Column(db.Numeric)
    carbs    = db.Column(db.Numeric)

# ---------- helpers ------------------------------------------------
def _current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None

def _paginate(seq, page, per_page=5):
    page  = max(page, 1)
    pages = max((len(seq) - 1) // per_page + 1, 1)
    start = (page - 1) * per_page
    return seq[start : start + per_page], pages

def _fav_ids(uid):
    rows = db.session.execute(
        text("SELECT snack_id FROM favourite WHERE user_id=:u"), {"u": uid}
    )
    return {r[0] for r in rows}

def _row(snack, servings):
    """Return one table-ready dictionary for Jinja."""
    return dict(
        id        = snack.id,
        name      = snack.name,
        servings  = servings,
        grams     = (snack.grams    or 0) * servings,
        calories  = (snack.calories or 0) * servings,
        protein   = (snack.protein  or 0) * servings,
        carbs     = (snack.carbs    or 0) * servings,
    )

# ---------- routes -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    """Sign-in / sign-up page."""
    if request.method == "POST":
        uname = request.form["username"].strip().lower()
        pwd   = request.form["password"]

        user = User.query.filter_by(username=uname).first()
        if not user:
            user = User(username=uname)
            user.set_password(pwd)
            db.session.add(user)
            db.session.commit()
        elif not user.check_password(pwd):
            return render_template("login.html", error="Forkert password")

        session.clear()
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))

    # GET -----------------------------------------------------------
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ------------------------------------------------------------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = _current_user()
    if not user:
        return redirect(url_for("login"))
    # Reset limits if "reset" query parameter is present
    if request.args.get("reset"):
        session.pop("limits", None)
        return redirect(url_for("dashboard"))

    # ------------------------------------------------------------------
    # 1) helpers we always need
    q     = request.args.get("q", "").strip()
    page  = int(request.args.get("page", 1))

    # ------------------------------------------------------------------
    # 2) read / update limits (they live in the session)
    limits = session.get("limits")        # may be None

    if request.method == "POST":
        # Get raw input values
        cal_min_raw = request.form.get("calories_min") or None
        cal_max_raw = request.form.get("calories_max") or None
        pro_min_raw = request.form.get("protein_min") or None
        pro_max_raw = request.form.get("protein_max") or None
        car_min_raw = request.form.get("carbs_min") or None
        car_max_raw = request.form.get("carbs_max") or None

        # Convert to integers or None
        limits = dict(
            cal_min=int(cal_min_raw) if cal_min_raw else None,
            cal_max=int(cal_max_raw) if cal_max_raw else None,
            pro_min=int(pro_min_raw) if pro_min_raw else None,
            pro_max=int(pro_max_raw) if pro_max_raw else None,
            car_min=int(car_min_raw) if car_min_raw else None,
            car_max=int(car_max_raw) if car_max_raw else None,
        )
        session["limits"] = limits
        return redirect(url_for("dashboard"))


    # “Reset” back to the form
    if request.args.get("reset"):
        session.pop("limits", None)
        limits = None

    # ------------------------------------------------------------------
    # 3) build snack list
    favs   = _fav_ids(user.id)
    snacks = []

    if limits:
        qry = Snack.query
        if limits["cal_min"] is not None:
            qry = qry.filter(Snack.calories >= limits["cal_min"])
        if limits["cal_max"] is not None:
            qry = qry.filter(Snack.calories <= limits["cal_max"])
        if limits["pro_min"] is not None:
            qry = qry.filter(Snack.protein >= limits["pro_min"])
        if limits["pro_max"] is not None:
            qry = qry.filter(Snack.protein <= limits["pro_max"])
        if limits["car_min"] is not None:
            qry = qry.filter(Snack.carbs >= limits["car_min"])
        if limits["car_max"] is not None:
            qry = qry.filter(Snack.carbs <= limits["car_max"])
        if q:
            qry = qry.filter(Snack.name.ilike(f"%{q}%"))

        rows = qry.all()

        # ----- deduplicate BY NAME (case-insensitive) -----------------
        seen_names = set()
        for r in rows:
            key = r.name.lower()
            if key in seen_names:
                continue
            seen_names.add(key)

            if not r.calories or float(r.calories) == 0:
                snacks.append(_row(r, 1))  # 1 serving
            else:
                servings = int(limits["cal_min"] // float(r.calories)) if limits["cal_min"] else 1
                if servings:
                    snacks.append(_row(r, servings))

    # ------------------------------------------------------------------
    # 4) paginate (5 per page)
    snacks, pages = _paginate(snacks, page)
    prev_url = url_for("dashboard", q=q, page=page-1) if page > 1 else None
    next_url = url_for("dashboard", q=q, page=page+1) if page < pages else None

    # ------------------------------------------------------------------
    return render_template(
        "dashboard.html",
        user=user,
        limits=limits,
        snacks=snacks,
        fav_ids=favs,
        search=q,
        page=page,
        pages=pages,
        prev_url=prev_url,
        next_url=next_url,
    )


# ---------- favourites toggle --------------------------------------
@app.post("/fav/<int:snack_id>")
def fav_toggle(snack_id):
    user = _current_user()
    if not user:
        abort(401)

    sql = """
    WITH ins AS (
      INSERT INTO favourite(user_id, snack_id)
      VALUES (:u, :s) ON CONFLICT DO NOTHING RETURNING 1
    )
    DELETE FROM favourite
          WHERE user_id = :u
            AND snack_id = :s
            AND NOT EXISTS (SELECT 1 FROM ins);
    """
    db.session.execute(text(sql), {"u": user.id, "s": snack_id})
    db.session.commit()
    return redirect(request.referrer or url_for("dashboard"))

# ---------- favourites list ----------------------------------------
@app.route("/favorites")
def favorites():
    user = _current_user()
    if not user:
        return redirect(url_for("login"))

    page = int(request.args.get("page", 1))
    rows = db.session.execute(text("""
        SELECT s.* FROM favourite f
        JOIN snack s ON s.id = f.snack_id
        WHERE f.user_id = :u
    """), {"u": user.id}).mappings().all()

    snacks = [_row(r, 1) for r in rows]
    snacks, pages = _paginate(snacks, page)

    prev_url = next_url = None
    if page > 1:
        prev_url = url_for("favorites", page=page - 1)
    if page < pages:
        next_url = url_for("favorites", page=page + 1)

    return render_template(
        "favorites.html",
        user=user,
        snacks=snacks,
        fav_ids={s["id"] for s in snacks},
        page=page,
        pages=pages,
        prev_url=prev_url,
        next_url=next_url,
    )

# ---------- add-snack (pure SQL INSERT) ----------------------------
# ----- ADD SNACK ---------------------------------------------------
@app.route("/add_snack", methods=["GET", "POST"])
def add_snack():
    if not _current_user():
        return redirect(url_for("login"))

    if request.method == "POST":
        p = request.form            # short-hand

        # inline SQL – no external file needed
        sql = text("""
            INSERT INTO snack (name, calories, grams, protein, carbs)
            VALUES (:name, :cal, :g, :p, :c)
        """)

        db.session.execute(sql, {
            "name": p["name"].strip(),
            "cal" : p["calories"] or None,
            "g"   : p["grams"]    or None,
            "p"   : p["protein"]  or None,
            "c"   : p["carbs"]    or None
        })
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("add_snack.html")


# ---------- profile -------------------------------------------------
@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = _current_user()
    if not user:
        return redirect(url_for("login"))

    err = None
    if request.method == "POST":
        un = request.form["username"].strip().lower()
        em = request.form["email"].strip()
        fn = request.form["fullname"].strip()

        if not USERNAME_RE.fullmatch(un):
            err = "Ugyldigt brugernavn"
        elif em and not EMAIL_RE.fullmatch(em):
            err = "Ugyldig e-mail"
        else:
            db.session.execute(text("""
                UPDATE "user"
                   SET username=:u, email=:e, fullname=:f
                 WHERE id=:id
            """), {"u": un, "e": em or None, "f": fn or None, "id": user.id})
            db.session.commit()
            return redirect(url_for("dashboard"))

    return render_template("profile.html", user=user, error=err)

# -------------------------------------------------------------------
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
