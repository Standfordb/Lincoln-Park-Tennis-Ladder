from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from tkinter import messagebox
from datetime import datetime
import re

# Create and configure application
app = Flask(__name__)
app.secret_key = "Sb39MDCIyj1kWgEKVzpmkQ"
# Need to fix path to sqlite database. Should not be hardcoded. Need to import os and update path
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///E:\\VS Code\\Applications\\Python\\LP Tennis Ladder\\static\\ladder.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()
db = SQLAlchemy(app)


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
                            
# Define Routes
#
#
# Home page and login screen for returning users
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # Grab the players to populate the rankings list
        players = User.query.filter(User.rank < 26).all()
        return render_template("index.html", players=players)
    elif request.method == "POST":
        # Get the login information from the POST request
        username = request.form.get("username").strip().upper()
        password = request.form.get("password").strip()
        # Check username and password against database and if valid log user in
        if validate_credentials(username, password):
            create_session(username)
            # Send the players and users username to the index page
            players = get_players()
            return redirect(url_for("index", players=players))
        else:
            # If username and password dont match database give an error message
            messagebox.showerror("Error", "Username or password incorrect. Please try again")
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
    phone = request.form.get("phone")
    
    # Confirm form was submitted with all required data
    if not first or not last or not username or not password or not email:
        messagebox.showerror("Error", "Missing required data. Please make sure form is complete.")
        return redirect("/register")
    # Check email and password formatting
    elif not email_regex(email):
        messagebox.showerror("Error", "Please enter a valid email address")
        return redirect("/register")
    # Check password formatting
    elif not password_regex(password):
        messagebox.showerror("Error", "Invalid character in password. Valid characters: A-Z, 0-9, !, @, #, $, %, *, _, =, +, ^, &")
    # Check if username is taken
    elif username_taken(username):
        messagebox.showerror("Error", "Username already taken. Please select a new username.")
        return redirect("/register")
    # Check if email is taken 
    elif email_taken(email):
        messagebox.showerror("Error", "Email already in use. Please use a different email.")
        return redirect("/register")
    elif phone:
        if not phone_regex(phone):
            messagebox.showerror("Error", "Phone number in wrong format. Correct format: (###)###-####")
            return redirect("/register")
    elif password_not_match(password, confirm):
        messagebox.showerror("Error", "Passwords do not match. Please re-enter.")
        return redirect("/register")
    # If everything looks good create the new user in the database
    else:
        create_user(first, last, username, password, email, phone)
        create_session(username)
        players = get_players()
        return redirect(url_for("index", password=password, players=players))

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
        date = request.form.get("date")
        # Make sure no data is missing
        if not score or not opponent_id or not is_win or not date:
            messagebox.showerror("Error", "Please fill out all fields.")
            return redirect("/input")
        # Make sure data has not been tampered with client-side
        elif not validate_match_data(score, opponent_id, is_win, date):
            messagebox.showerror("Error", "Problem recording match. Please try again")
            return redirect("/input")
        else:
            # If all looks good, record the match to Temp_match database to await confirmation
            record_match(score, opponent_id, is_win, date)
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
        profile, stats = get_profile(session["USER"])
        return redirect(url_for("profile", profile=profile, stats=stats, id=profile.id))

# Route to delete temp match if player disputes
@app.route("/dispute", methods=["POST"])
def dispute():
    match_id = request.form.get("match_id")
    delete_temp_match(match_id)
    profile, stats = get_profile(session["USER"])
    return redirect(url_for("profile", profile=profile, stats=stats, id=profile.id))

@app.route("/redirect_profile")
def redirect_profile():    
    profile, stats = get_profile(session["USER"])
    return redirect(url_for("profile", profile=profile, stats=stats, id=profile.id))

#Define independant functions
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
    # Add the user to the database
    user = User(first=first, last=last, username=username, password=password, email=email, phone=phone, rank=rank)
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
        return False
    elif password != user.password:
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
def validate_match_data(score, opponent_id, is_win, date):
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
        datetime.strptime(date, "%Y-%m-%d")
    except:
        return False
    # Check if opponent matches possible opponents by rank
    if not opponent in opponents:
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
    players = User.query.filter(User.rank < 26).all()
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
    x = 3
    ranks = []
    opponents = []
    for i in range(-x, x):
        y = i + x
        ranks.append(rank + i)
        opponents.append(User.query.filter_by(rank=ranks[y]).first())
    opponents.pop(x)
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
    regex = re.compile("\([0-9]{3}\)[0-9]{3}-[0-9]{4}")
    p = regex.match(phone)
    if p:
        return True
    else:
        return False