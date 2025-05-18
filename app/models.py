from datetime import datetime
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    deficit_goal = db.Column(db.Integer)          # calories
    workouts = db.relationship("WorkoutSession", backref="user")

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

class Preference(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    snack_id = db.Column(db.Integer, db.ForeignKey("snack.id"), primary_key=True)
    rating = db.Column(db.Integer)  # −1 dislike, 0 neutral, 1 like

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    session_id = db.Column(db.Integer, db.ForeignKey("workout_session.id"))
    snack_id = db.Column(db.Integer, db.ForeignKey("snack.id"))
