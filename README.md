# Snackster database - Get your favorite snack!

# running dis-snackster-project:

This assumes a working Python 3 installation (with python=python3 and pip=pip3).

(1)
Install all dependencies by running
$ pip install -r requirements.txt

(2)
Asuming you have a running postgreSQL:
Such as $ createdb snackster_dev
(3)
run the sql 
$ psql -d snackster_dev -f app/sql/schema.sql
$ psql -d snackster_dev -f app/sql/seed_data.sql


(4)
run the app
python -m flask --app app.app run





