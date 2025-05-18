from random import sample
from .models import Snack

def recommend_snacks(session, user, k=5):
    ceiling = session.calories_burned
    snacks = Snack.query.filter(Snack.calories <= ceiling).all()
    return sample(snacks, k) if len(snacks) >= k else snacks
