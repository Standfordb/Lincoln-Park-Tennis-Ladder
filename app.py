from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import re
import constants as c


# Create and configure application
app = Flask(__name__)
app.secret_key = "Sb39MDCIyj1kWgEKVzpmkQ"
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Wj7gWQuu849VNDMYSY3j@containers-us-west-191.railway.app:7456/railway"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()
db = SQLAlchemy(app)







# Define Routes ------------------------------------------------------------------------------------
#
#
# Home page and login screen for returning users
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # Grab the players to populate the rankings list
        players = get_players()
        return render_template("index.html", players=players)
    elif request.method == "POST":
        # Get the login information from the POST request
        username = request.form.get("username").strip().upper()
        password = request.form.get("password").strip()
        # Check username and password against database and if valid log user in
        if not validate_credentials(username, password):
            return redirect("/")
        else:
            create_session(username)
            return redirect("/")
        
# Registration form for new users
@app.route("/register")
def register():
    return render_template("register.html")

# Profile page
@app.route("/profile")
def profile():
    # Get the id of the profile to pull up
    id = request.args.get('id')
    profile, stats = get_profile(id)
    return render_template("profile.html", profile=profile, stats=stats)

# Logout button 
@app.route("/logout")
def logout():
    remove_session()
    return redirect("/")

# Route to create a new user and then redirect them to the main page and log them in
@app.route("/create", methods=["POST"])
def create():
    # Collect data submitted in POST request
    first = request.form.get("first").strip().capitalize()
    last = request.form.get("last").strip().capitalize()
    username = request.form.get("username").strip().upper()
    password = request.form.get("password").strip()
    confirm = request.form.get("confirm").strip()
    email = request.form.get("email").strip().upper()
    phone = request.form.get("phone").strip()
    
    if validate_registration(first, last, username, password, email, confirm):
        create_user(first, last, username, password, email, phone)
        create_session(username)
        return redirect("/")
    else:
        return redirect("/register")

 # Route to collect match data from a user and store it in a temporary databease to await confirmation   
@app.route("/input", methods=["GET", "POST"])
def input():
    if request.method == "GET":
        # Find the opponents within 3 ranks of user
        user = get_user()
        opponents = get_opponents(user.rank)
        # Send username and opponents to input page
        return render_template("input.html", opponents=opponents)
    elif request.method == "POST":
        # Get the data from the form
        score = request.form.get("score").strip()
        opponent_id = request.form.get("opponent")
        is_win = request.form.get("is_win")
        date_played = request.form.get("date_played")
        # Make sure no data is missing
        if not score or not opponent_id or not is_win or not date_played:
            flash("Please fill out all fields.")
            return redirect("/input")
        # Make sure data has not been tampered with client-side
        elif not validate_match_data(score, opponent_id, is_win, date_played):
            flash("Problem recording match. Please try again")
            return redirect("/input")
        else:
            # If all looks good, record the match to Temp_match database to await confirmation
            record_match(score, opponent_id, is_win, date_played)
            profile, stats = get_profile(session["USER"])
            return redirect(url_for("profile", profile=profile, stats=stats, id=profile.id))

# Route to confirm and entry in the Temp_match database and commit it to the Matches database
@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    if request.method == "GET":
        temp_matches = get_temp_matches(session["USER"])
        return render_template("confirm.html", temp_matches=temp_matches )
    elif request.method == "POST":
        match_id = request.form.get("match_id")
        confirm_match(match_id)
        update_rankings()
        return redirect("/confirm")

# Route to delete temp match if player disputes
@app.route("/dispute", methods=["POST"])
def dispute():
    match_id = request.form.get("match_id")
    delete_temp_match(match_id)
    return redirect("/confirm")

@app.route("/redirect_profile")
def redirect_profile():    
    profile, stats = get_profile(session["USER"])
    return render_template("profile.html", profile=profile, stats=stats, id=profile.id)

# Route to edit profile information
@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "GET":
        user = get_user()
        return render_template("edit.html", user=user)
    elif request.method == "POST":
        first = request.form.get("first").strip().capitalize()
        last = request.form.get("last").strip().capitalize()
        username = request.form.get("username").strip().upper()
        email = request.form.get("email").strip().upper()
        phone = request.form.get("phone").strip()
        new_password = request.form.get("new-password")
        confirm_new_password = request.form.get("confirm-new-password")
        password = request.form.get("password")

        if not validate_update(username, email, phone, new_password, confirm_new_password, password):
            return redirect("/edit")
        else:
            update_profile(first, last, username, email, phone, new_password)
            if username:
                create_session(username)
            return redirect("/redirect_profile")









#Define helper functions ---------------------------------------------------------------------------
#
#
# Check if username is already taken
def username_taken(username):
    taken = User.query.filter_by(username=username).first()
    if taken:
        return True
    else:
        return False
    
# Check if email is already taken
def email_taken(email):
    taken = User.query.filter_by(email=email).first()
    if taken:
        return True
    else:
        return False
    
# Create new user in database
def create_user(first, last, username, password, email, phone):
    # Place their starting rank at the bottom of the ladder
    rank = starting_rank()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf8'), salt)
    # Add the user to the database
    user = User(first=first, last=last, username=username, password=hashed_password, salt=salt, email=email, phone=phone, rank=rank)
    db.session.add(user)
    db.session.commit()
    return

# Calculate a persons starting rank (1 greater than total users)
def starting_rank():
    rank = User.query.count() + 1
    return rank
    
# Update ranks after any changes in the database
def update_ranks():
    return

# Validate username and password
def validate_credentials(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("Username or password incorrect. Please try again.")
        return False
    elif bcrypt.hashpw(password.encode('utf8'), user.salt) != user.password:
        flash("Username or password incorrect. Please try again.")
        return False
    else:
        return True
    
# Confirm passwords match
def password_not_match(password, confirm):
    if password != confirm:
        return True
    else:
        return False

# create a session for the current user 
def create_session(username):
    user = User.query.filter_by(username=username).first()
    session["USER"] = user.id
    session["USERNAME"] = user.username
    return


# Remove the current user from the session
def remove_session():
    session.pop('USER', None)
    return
    
# Record match results to match table and assign to correct users
def record_match(score, opponent_id, is_win, date):
    # Check who won the match
    if is_win == "0":
        winner_id = session["USER"]
        loser_id = opponent_id
    else:
        winner_id = opponent_id
        loser_id = session["USER"]
    
    # Convert date string to a date type
    date_played = datetime.strptime(date, "%Y-%m-%d")

    # Record the results
    match = Temp_match(score=score, winner_id=winner_id, loser_id=loser_id, submit_by=session["USER"], date_played=date_played)

    # Get user and opponent and connect them to the new match
    user = get_user()
    opponent = User.query.filter_by(id=opponent_id).first()
    user.temp_matches.append(match)
    opponent.temp_matches.append(match)
    # Commit to database
    db.session.add(match)
    db.session.commit()
    return

# Confirm match results and commit to Match table
def confirm_match(id):
    temp_match = Temp_match.query.filter_by(id=id).first()
    match = Match(score=temp_match.score, winner_id=temp_match.winner_id, loser_id=temp_match.loser_id, date_played=temp_match.date_played)
    user = get_user()
    if match.winner_id == session["USER"]:
        opponent_id = match.loser_id
    else:
        opponent_id = match.winner_id
    opponent = User.query.filter_by(id=opponent_id).first()
    user.matches.append(match)
    opponent.matches.append(match)
    db.session.add(match)
    db.session.delete(temp_match)
    db.session.commit()
    return

# Validate match data
def validate_match_data(score, opponent_id, is_win, date_played):
    # Get the user who is submitting the match
    user = get_user()
    # Find the possible opponents for this user
    opponents = get_opponents(user.rank)
    # Find the opponent user claims to have played
    opponent = User.query.filter_by(id=opponent_id).first()
    # Set values to check is_win against
    win_check = ["0", "1"]
    # Make sure score format matches our regular expression
    regex = re.compile("^\d-\d(\(\d?\d-\d?\d\))?$|^\d-\d(\(\d?\d-\d?\d\))?\s\d-\d(\(\d?\d-\d?\d\))?$|^\d-\d(\(\d?\d-\d?\d\))?\s\d-\d(\(\d?\d-\d?\d\))?\s\d-\d(\(\d?\d-\d?\d\))?$")
    p = regex.match(score)
    if p == None:
        return False
    # Set the date to a date type
    try:
        match_date = datetime.strptime(date_played, "%Y-%m-%d")
    except:
        return False
    if match_date > datetime.today():
        flash("Match date can not be in the future.")
        return False
    # Check if opponent matches possible opponents by rank
    elif not opponent in opponents:
        return False
    # Check if win_against is a 0 or 1
    elif is_win not in win_check:
        return False
    else:
        return True

# Get the current users username  
def get_user():
    user = User.query.filter_by(id=session["USER"]).first()
    return user

# Get the current top 25 players
def get_players():
    players = User.query.filter(User.rank <= c.PER_PAGE).all()
    return players

# Get the profile info
def get_profile(id):
    profile = User.query.filter_by(id=id).first()
    stats = []
    if profile.matches:
        stats.append(len(profile.matches))
        stats.append(int(len(profile.matches_won) / len(profile.matches) * 100))
    else:
        stats.append("No matches played yet")
        stats.append("N/A")
    
    return profile, stats

# Get opponents within proper rank range
def get_opponents(rank):
    ranks = []
    opponents = []
    j = 0
    for i in range(-c.SPREAD, c.SPREAD + 1):
        ranks.append(rank + i)
        opponents.append(User.query.filter_by(rank=ranks[j]).first())
        j += 1
    opponents.pop(c.SPREAD)
    return opponents

# Update ranks from all match data
def update_rankings():
    matches = Match.query.order_by(Match.date_played.asc()).all()
    for match in matches:
        update_ranks(match.winner_id, match.loser_id)
    return


# Update ranks after a match
def update_ranks(winner_id, loser_id):
    winner = User.query.filter_by(id=winner_id).first()
    loser = User.query.filter_by(id=loser_id).first()
    if winner.rank > loser.rank:
        shifters = User.query.filter((User.rank >= loser.rank) & (User.rank < winner.rank)).all()
        winner.rank = loser.rank
        for shifter in shifters:
            shifter.rank += 1
        db.session.commit()
        return
    else:
        return

# Delete a user from the User table and update ranks accordingly
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    shifters = User.query.filter(User.rank > user.rank).all()
    for shifter in shifters:
        shifter.rank -= 1
    db.session.delete(user)
    db.session.commit()
    return

# Delete temp match after player dispute
def delete_temp_match(id):
    temp_match = Temp_match.query.filter_by(id=id).first()
    db.session.delete(temp_match)
    db.session.commit()
    return

# Get all temp matches for user
def get_temp_matches(id):
    user = User.query.filter_by(id=id).first()
    temp_matches = user.temp_matches
    return temp_matches

# Check inputs against appropriate regular expressions
def email_regex(email):
    regex = re.compile("[^@.]*@[^@.]*\.[^@.]*")
    p = regex.match(email)
    if p:
        return True
    else:
        return False

def password_regex(password):
    regex = re.compile("[a-zA-Z0-9!@#$%*_=+^&]{8,16}")
    p = regex.match(password)
    if p:
        return True
    else:
        return False

def phone_regex(phone):
    regex = re.compile("^\(\d{3}\)\d{3}-\d{4}$")
    p = regex.match(phone)
    if p:
        return True
    else:
        return False
    
# Validate registration form data
def validate_registration(first, last, username, password, email, confirm):
    # Confirm form was submitted with all required data
    if not first or not last or not username or not password or not email:
        flash("Missing required data. Please make sure form is complete.")
        return False
    elif not email_regex(email):
        flash("Please enter a valid email address.")
        return False
    elif not password_regex(password):
        flash("Invalid character in password. Valid characters: A-Z, 0-9, !, @, #, $, %, *, _, =, +, ^, &")
        return False
    elif username_taken(username):
        flash("Username already taken. Please select a new username.")
        return False
    elif email_taken(email):
        flash("Email already in use. Please use a different email.")
        return False
    elif password_not_match(password, confirm):
        flash("Passwords do not match. Please re-enter.")
        return False
    else:
        return True
    
# Validate update profile info
def validate_update(username, email, phone, new_password, confirm_new_password, password):
    user = get_user()
    if username:
        if username_taken(username):
            flash("Username already taken. Please select a new username.")
            return False
    elif email:
        if email_taken(email):
            flash("Email already in use. Please use a different email.")
            return False
        elif not email_regex(email):
            flash("Please enter a valid email address.")
            return False
    elif phone:
        if not phone_regex(phone):
            flash("Phone number not in valid format: (###)###-####")
            return False
    elif new_password:
        if not password_regex(new_password):
            flash("Invalid character in new password. Valid characters: A-Z, 0-9, !, @, #, $, %, *, _, =, +, ^, &")
            return False
        elif password_not_match(new_password, confirm_new_password):
            flash("Passwords do not match. Please re-enter.")
            return False
    elif bcrypt.hashpw(password.encode('utf8'), user.salt) != user.password:
        flash("Invalid password. Changes not saved.")
        return False
    return True

# Update user data in database
def update_profile(first, last, username, email, phone, new_password):
    user = get_user()
    if first:
        user.first = first
    if last:
        user.last = last
    if username:
        user.username = username
    if email:
        user.email = email
    if phone:
        user.phone = phone
    if new_password:
        user.password = bcrypt.hashpw(new_password.encode('utf8'), user.salt)
    db.session.commit()
    return










#Create tables and classes for database--------------------------------------------------------------
#
#
#

# Create a connecting table between users and matches
user_match = db.Table("user_match",
                      db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                      db.Column("match_id", db.Integer, db.ForeignKey("match.id"))
                      )

# Create a connecting table between users and temp matches
user_temp = db.Table("user_temp",
                      db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                      db.Column("match_id", db.Integer, db.ForeignKey("temp_match.id"))
                      )


# Create database class for"User" table
class User(db.Model): 
    id = db.Column(db.Integer(), primary_key=True)
    first= db.Column(db.String(255), nullable=False)
    last = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(255))
    rank = db.Column(db.Integer(), default=0)
    matches = db.relationship("Match", secondary=user_match, backref="players")
    temp_matches = db.relationship("Temp_match", secondary=user_temp, backref="players")
    matches_won = db.relationship("Match", backref="winner", foreign_keys="Match.winner_id", lazy=True)
    matches_lost = db.relationship("Match", backref="loser", foreign_keys="Match.loser_id", lazy=True)
    temp_matches_won = db.relationship("Temp_match", backref="winner", foreign_keys="Temp_match.winner_id", lazy=True)
    temp_matches_lost = db.relationship("Temp_match", backref="loser", foreign_keys="Temp_match.loser_id", lazy=True)
    date_joined = db.Column(db.Date, default=datetime.utcnow)

    # Create a representation for the User class that is the users username
    def __repr__(self):
        return f"<User: {self.username}>"

# Create database class for "Match" table    
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.String(50))
    winner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    loser_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date_played = db.Column(db.Date, default=datetime.utcnow)

# Create a temporary match table to hold matches while they wait for confirmation
class Temp_match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.String(50))
    winner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    loser_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    submit_by = db.Column(db.Integer, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    date_played = db.Column(db.Date, default=datetime.utcnow)