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
> run the sql 
> $ psql -d snackster_dev -f app/sql/schema.sql
> $ psql -d snackster_dev -f app/sql/seed_data.sql


(4)
> run the app
> python -m flask --app app.app run



--------------------------------------------------
# How to use the application:

(1) Log in. The first time you log in, it will create your user account, and you will be logged in to your unique user profile.

(2) On the front page, you can input values for calories, protein, or carbs. You can enter any one of these, and if you want, for example, 200 calories, simply input 200 in both the minimum and maximum fields.

(3) After submitting your criteria, you will be presented with snack choices based on your personal input. You can browse through the options using the page slider at the bottom or the search bar.

(4) If you find a snack you like, you can add it to your favorites, which will be visible in the favorites section.

(5) You can also remove a snack from your favorites if you decide it is not for you.

(6) You can update your name, username, or even add your email if you wish (though the email functionality is not implemented yet).

(7) The items you add are stored in the database, allowing other users to see these items as well.

