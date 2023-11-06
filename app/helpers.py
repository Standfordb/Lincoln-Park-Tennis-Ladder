from flask import flash, session
from app import db
from app import routes as r
from datetime import datetime
import pytz
import bcrypt
import re
import app.constants as c
import math




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
    id = db.Column(db.Integer, primary_key=True)
    first= db.Column(db.String(255), nullable=False)
    last = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    salt = db.Column(db.LargeBinary, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(255))
    rank = db.Column(db.Integer(), default=0)
    challenge = db.Column(db.Integer)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    matches = db.relationship("Match", secondary=user_match, backref="players")
    notifications = db.relationship("Notification", backref="user", foreign_keys=("Notification.user_id"))
    temp_matches = db.relationship("Temp_match", secondary=user_temp, backref="players")
    matches_won = db.relationship("Match", backref="winner", foreign_keys="Match.winner_id", lazy=True)
    matches_lost = db.relationship("Match", backref="loser", foreign_keys="Match.loser_id", lazy=True)
    temp_matches_won = db.relationship("Temp_match", backref="winner", foreign_keys="Temp_match.winner_id", lazy=True)
    temp_matches_lost = db.relationship("Temp_match", backref="loser", foreign_keys="Temp_match.loser_id", lazy=True)
    msg_sent = db.relationship("Chat", backref="sender", foreign_keys="Chat.sender_id", lazy=True)
    msg_received = db.relationship("Chat", backref="recipient", foreign_keys="Chat.recipient_id", lazy=True)

    # Create a representation for the User class that is the users username
    def __repr__(self):
        return f"<User: {self.username}>"
    
    def win_rate(self):
        if self.matches:
            matches = len(self.matches)
            wins = len(self.matches_won)
            win_rate = int((wins/matches)*100)
            win_rate = str(win_rate) + "%"
        else:
            matches = "N/A"
        return win_rate
    
    def chall_win_rate(self):
        challs = 0
        wins = 0
        if self.matches:
            for match in self.matches:
                if match.match_type == c.CHALLENGE:
                    challs += 1
                    if match.winner_id == self.id:
                        wins += 1
            if challs >0 :
                chall_win_rate = int((wins/challs)*100)
                chall_win_rate = str(chall_win_rate) + "%"
            else:
                chall_win_rate = "N/A"
        else:
            chall_win_rate = "N/A"
        return chall_win_rate
    
    def open_challenge(self):
        if self.challenge:
            opp = User.query.filter_by(id=self.challenge).first()
            opp = f"{opp.first} {opp.last}"
        else:
            opp = "N/A"
        return opp
    
    def total_matches(self):
        if self.matches:
            total = len(self.matches)
        else:
            total = "No matches played yet"
        return total
    
    def h2h(self, id):
        losses = 0
        wins = 0
        for match in self.matches:
            if match.winner_id != id and match.loser_id != id:
                pass
            else:
                if match.winner_id == self.id:
                    losses += 1
                else:
                    wins += 1
        h2h = f"{wins} wins | {losses} losses"
        return h2h
    
    def chall_h2h(self, id):
        losses = 0
        wins = 0
        for match in self.matches:
            if match.winner_id != id and match.loser_id != id:
                    pass
            else:
                if match.match_type == c.CHALLENGE:
                    if match.winner_id == self.id:
                        losses += 1
                    else:
                        wins +=1
        h2h = f"{wins} wins | {losses} losses"
        return h2h
                    


# Create database class for "Match" table    
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.String(50))
    winner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    loser_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date_played = db.Column(db.DateTime, default=datetime.utcnow)
    match_type = db.Column(db.String(50))

    def date(self):
        date = remove_timestamp(self.date_played)
        return date

# Create a temporary match table to hold matches while they wait for confirmation
class Temp_match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.String(50))
    winner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    loser_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date_played = db.Column(db.DateTime, default=datetime.utcnow)
    match_type = db.Column(db.String(50))
    submit_by = db.Column(db.Integer)

    def date(self):
        date = remove_timestamp(self.date_played)
        return date

# Create a table to hold chat messages
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    broadcast = db.Column(db.Boolean, default=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    originator_id = db.Column(db.Integer)
    type = db.Column(db.String(50))
    message = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class No_user():
    id = 0





#Define helper functions ---------------------------------------------------------------------------
#
#
# Check if username is already taken
def username_taken(username):
    taken = User.query.filter(User.username.ilike(username)).first()
    if taken:
        return True
    else:
        return False
    
# Check if email is already taken
def email_taken(email):
    taken = User.query.filter(User.email.ilike(email)).first()
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
    user = User.query.filter(User.username.ilike(username)).first()
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
    user = User.query.filter(User.username.ilike(username)).first()
    session["USER"] = user.id
    session["USERNAME"] = user.username
    print(f"User {session['USERNAME']} logged on!")
    return


# Remove the current user from the session
def remove_session():
    print(f"User {session['USERNAME']} logged out! ")
    session.pop("USER")
    session.pop("USERNAME")
    return
    
# Record match results to match table and assign to correct users
def record_match(score, opponent_id, is_win, date, type, submit_by):
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
    match = Temp_match(score=score, winner_id=winner_id, loser_id=loser_id, date_played=date_played, match_type=type, submit_by=session["USER"])

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
    match = Match(score=temp_match.score, winner_id=temp_match.winner_id, loser_id=temp_match.loser_id, date_played=temp_match.date_played, match_type=temp_match.match_type)
    user = get_user()
    if match.winner_id == user.id:
        opponent_id = match.loser_id
    else:
        opponent_id = match.winner_id
    opponent = User.query.filter_by(id=opponent_id).first()
    user.matches.append(match)
    opponent.matches.append(match)
    db.session.add(match)
    db.session.delete(temp_match)
    db.session.commit()
    return match

# Validate match data
def validate_match_data(score, opponent_id, is_win, date_played, match_type):
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
    match_date = datetime.strptime(date_played, "%Y-%m-%d")
    if match_date > datetime.today():
        flash("Match date can not be in the future.")
        return False
    # Check if opponent matches possible opponents by rank
    if match_type == "challenge":
        if not opponent in opponents:
            return False
    # Check if win_against is a 0 or 1
    if is_win not in win_check:
        return False
    
    return True

# Get the current users username  
def get_user():
    user = User.query.filter_by(id=session["USER"]).first()
    return user

# Get the current top 25 players
def get_players(page):
    results = c.RESULTS_PER_PAGE * page
    players = User.query.filter(User.rank.between(results-(c.RESULTS_PER_PAGE-1), results)).all()
    p = math.ceil(User.query.count() / c.RESULTS_PER_PAGE)
    x = 1
    pages = []
    while x <= p:
        pages.append(x)
        x += 1
    return players, pages

# Get the profile info
def get_profile(id):
    profile = User.query.filter_by(id=id).first()
    return profile

def get_friendly_opponents():
    friendlies = User.query.filter(User.id!=session["USER"]).all()
    return friendlies


# Get opponents within proper rank range
def get_opponents(rank):
    ranks = []
    opponents = []
    j = 0
    for i in range(-c.CHALLENGE_SPREAD, c.CHALLENGE_SPREAD + 1):
        ranks.append(rank + i)
        opponents.append(User.query.filter_by(rank=ranks[j]).first())
        j += 1
    opponents.pop(c.CHALLENGE_SPREAD)
    return opponents

def get_opponent():
    user = get_user()
    opponent = User.query.filter_by(challenge=user.id).first()
    return opponent

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
    regex = re.compile("^\d{3}-\d{3}-\d{4}$")
    p = regex.match(phone)
    if p:
        return True
    else:
        return False
    
def format_phone(phone):
    new_phone = ""
    for digit in phone:
        if digit.isdigit():
            new_phone += digit
    if new_phone:
        new_phone = new_phone[:3] + "-" + new_phone[3:]
        new_phone = new_phone[:7] + "-" + new_phone[7:]
    return new_phone


    
# Validate registration form data
def validate_registration(first, last, username, password, email, confirm, phone):
    # Confirm form was submitted with all required data
    if phone:
        if not phone_regex(phone):
            flash("Invalid phone number. Please re-enter")
            return False
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
            if username.upper() == user.username.upper():
                pass
            else:
                flash("Username already taken. Please select a new username.")
                return False
    if email:
        if not email_regex(email):
            flash("Please enter a valid email address.")
            return False
        if email_taken(email):
            if email.upper() == user.email.upper():
                pass
            else:
                flash("Email already in use. Please use a different email.")
                return False
    if phone:
        phone = format_phone(phone)
        if not phone_regex(phone):
            flash("Invalid phone number. Please re-enter")
            return False
    if new_password:
        if not password_regex(new_password):
            flash("Invalid character in new password. Valid characters: A-Z, 0-9, !, @, #, $, %, *, _, =, +, ^, &")
            return False
        elif password_not_match(new_password, confirm_new_password):
            flash("Passwords do not match. Please re-enter.")
            return False
    if bcrypt.hashpw(password.encode('utf8'), user.salt) != user.password:
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

# Save messages to the database
def save_broadcast_message(message):
    msg = Chat(sender_id=session["USER"], message=message, broadcast=True)
    db.session.add(msg)
    db.session.commit()
    return msg

# Save private messages to the database
def save_private_message(message, recipient):
    msg = Chat(sender_id=session["USER"], message=message, recipient_id=recipient, broadcast=False)
    db.session.add(msg)
    db.session.commit()
    return msg

# Get messages for chat box
def get_broadcast_messages():
    messages = Chat.query.filter_by(broadcast=True).all()
    for message in messages:
        message.time = format_timestamp(message.timestamp)
    return messages

# Get private messages for chat box
def get_private_messages(recipient, sender):
    messages = Chat.query.filter_by(sender_id=sender, recipient_id=recipient).all()
    messages += Chat.query.filter_by(sender_id=recipient, recipient_id=sender).all()
    for message in messages:
        message.time = format_timestamp(message.timestamp)
    return messages

# Disallow blank messages
def blank_message(message):
    check = ""
    for _ in range(500):
        if message == check:
            return True
        else:
            check += " "
    return False

# Convert timestamps to local time and format them
def format_timestamp(timestamp):
    timestamp = pytz.utc.localize(timestamp)
    timestamp = timestamp.astimezone(pytz.timezone("Us/Eastern"))
    time = timestamp.strftime(c.TIMESTAMP_FULL)
    return time

def remove_timestamp(timestamp):
    timestamp = timestamp.strftime(c.TIMESTAMP_DATE_ONLY)
    return timestamp

def create_notification(user_id, originator_id, type):
    origin = User.query.filter_by(id=originator_id).first()
    message = c.NOTIFICATIONS[type] + f" {origin.first} {origin.last}."
    timestamp = datetime.now(tz=None)
    timestamp = format_timestamp(timestamp)
    notification = Notification(user_id=user_id, originator_id=originator_id, type=type, message=message, timestamp=timestamp)
    db.session.add(notification)
    db.session.commit()
    return
    
def cancel_challenge(user_id, challenge_id):
    user = User.query.filter_by(id=user_id).first()
    chall_user = User.query.filter_by(id=challenge_id).first()
    user.challenge = None
    if chall_user.challenge == user.id:
        chall_user.challenge = None
        create_notification(chall_user.id, user.id, c.CHALL_CANCEL)
    notification = Notification.query.filter_by(user_id=challenge_id, originator_id=user.id, type=c.CHALLENGE).first()
    if notification:
        remove_notification(notification.id)
    db.session.commit()
    return

def handle_challenge(msg, challenger_id, notification_id):
    user = get_user()
    challenger = User.query.filter_by(id=challenger_id).first()
    notification = Notification.query.filter_by(id=notification_id).first()
    if notification:
        if msg == "accept":
            if user.challenge != None:
                return False
            else:
                user.challenge = challenger_id
                challenger.challenge = user.id
                create_notification(challenger.id, user.id, c.CHALL_ACCEPTED)
                db.session.delete(notification)
                db.session.commit()
                return True
        else:
            create_notification(challenger.id, user.id, c.CHALL_DECLINED)
            challenger.challenge = None
            db.session.delete(notification)
            db.session.commit()
            return True
    else:
        return

def remove_notification(id):
    notification = Notification.query.filter_by(id=id).first()
    print(notification)
    db.session.delete(notification)
    db.session.commit()
    return

def reset_challenge(user_id, chall_id):
    user = User.query.filter_by(id=user_id).first()
    chall = User.query.filter_by(id=chall_id).first()
    user.challenge = None
    chall.challenge = None
    db.session.commit()
    return

def format_score(first_winner, first_loser, first_tie_winner, first_tie_loser, second_winner, second_loser, second_tie_winner, second_tie_loser, third_winner, third_loser, third_tie_winner, third_tie_loser):
    if first_tie_winner != "None":
        first_set = f"{first_winner}-{first_loser}({first_tie_winner}-{first_tie_loser})"
    else:
        first_set = f"{first_winner}-{first_loser}"
    
    if second_tie_winner != "None":
        second_set = f"{second_winner}-{second_loser}({second_tie_winner}-{second_tie_loser})"
    elif second_winner != "None":
        second_set = f"{second_winner}-{second_loser}"
    else:
        second_set = None
    
    if third_tie_winner != "None":
        third_set = f"{third_winner}-{third_loser}({third_tie_winner}-{third_tie_loser})"
    elif third_winner != "None":
        third_set = f"{third_winner}-{third_loser}"
    else:
        third_set = None
    
    if third_set:
        score = f"{first_set} {second_set} {third_set}"
    elif second_set:
        score = f"{first_set} {second_set}"
    else:
        score = f"{first_set}"
    print("first set =", first_set)
    print("second set =", second_set)
    print("third set =", third_set)
    print("score =", score)
    return score