# Snackster database - Get your favorite snack!

# running dis-snackster-project:

This assumes a working Python 3 installation (with python=python3 and pip=pip3).

(1) Install all dependencies by running
$ pip install -r requirements.txt

(2)
run the sql 
$ psql snackster_dev -f app/seed_food.sql

(3)
run the app
$ python3 -m flask run






Til os ___________________________________________________________________________

How to start the project
1 Start PostgreSQL
Action	
Launch Postgres.app	Menu-bar icon turns green = local PostgreSQL running on port 5432
(first run only) createdev DB	
    createdb snackster_dev


To load the data
psql snackster_dev -f db/seed_food.sql      # copies data/nutrition_facts.csv



3 Run the backend

# open terminal in repo root
source .venv/bin/activate          # fish → .venv/bin/activate.fish

# env vars (auto-loaded if you have .flaskenv)
export FLASK_APP=manage.py
export FLASK_DEBUG=1               # auto-reloader

# keep schema in sync
python -m flask db upgrade

# launch dev server
python -m flask run

You should see:

* Running on http://127.0.0.1:5000

Open that URL in the browser → login page appears.
4 (optional) Seed demo snacks

psql snackster_dev <<'SQL'
INSERT INTO snack (name, brand, calories, protein, carbs, fat)
VALUES ('Proteinbar Choco', 'RXBar', 210, 12, 23, 8)
ON CONFLICT DO NOTHING;
SQL

5 Shutdown procedure
Component	Command / action
Flask server	CTRL-C in its terminal
Virtual-env	deactivate
Postgres.app	Menu-bar ▸ Stop
VS Code / pgAdmin	Quit apps



6 Daily quick-start (copy-paste)
open -a Postgres        # 1. start PostgreSQL
cd path/to/snackster
source .venv/bin/activate
python -m flask db upgrade
python -m flask run

Snackster is now live at http://127.0.0.1:5000 🚀