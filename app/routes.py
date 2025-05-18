from flask import Blueprint, jsonify, request
from .models import db, User, WorkoutSession, Recommendation
from .recommendations import recommend_snacks

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return {"msg": "Snackster API online 🚀"}

@bp.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    user = User.query.get_or_404(data["user_id"])

    session = WorkoutSession(
        calories_burned=data["calories_burned"],
        activity_type=data.get("activity_type"),
        user=user,
    )
    db.session.add(session)
    db.session.commit()

    snacks = recommend_snacks(session, user)
    for snack in snacks:
        db.session.add(
            Recommendation(user_id=user.id, session_id=session.id, snack_id=snack.id)
        )
    db.session.commit()

    return jsonify([{"name": s.name, "calories": s.calories} for s in snacks])
