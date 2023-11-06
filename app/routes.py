from flask import render_template, request, redirect, session, url_for, flash
from app import app
import app.helpers as h
import app.constants as c




# Define Routes ------------------------------------------------------------------------------------
#
#
# Home page and login screen for returning users

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # Grab the players to populate the rankings list
        page = request.args.get('page')
        if page == None:
            page = 1
        players, pages = h.get_players(int(page))
        if "USER" in session:
            try:
                user = h.get_user()
            except KeyError:
                print("Exception caught! KeyError")
                h.remove_session()
                user = None
        else:
            user = None
        messages = h.get_broadcast_messages()
        return render_template("index.html", players=players, pages=pages, user=user, spread=c.CHALLENGE_SPREAD, messages=messages)
    elif request.method == "POST":
        # Get the login information from the POST request
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        # Check username and password against database and if valid log user in
        if not h.validate_credentials(username, password):
            return redirect("/")
        else:
            h.create_session(username)
            return redirect("/")
        
# Registration form for new users
@app.route("/register")
def register():
    return render_template("register.html", page="register")

# Profile page
@app.route("/profile")
def profile():
        # Get the id of the profile to pull up
        id = request.args.get('id')
        profile = h.get_profile(id)
        if "USER" in session:
            try:
                user = h.get_user()
                messages = h.get_private_messages(profile.id, user.id)
                return render_template("profile.html", profile=profile, messages=messages, user=user)
            except KeyError:
                print("Exception caught! KeyError")
                user = h.No_user()
                return render_template("profile.html", profile=profile, user=user)
        else:
            user = h.No_user()
            return render_template("profile.html", profile=profile, user=user)

# Logout button 
@app.route("/logout")
def logout():
    h.remove_session()
    return redirect("/")

# Route to create a new user and then redirect them to the main page and log them in
@app.route("/create", methods=["POST"])
def create():
    # Collect data submitted in POST request
    first = request.form.get("first").strip()
    last = request.form.get("last").strip()
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    confirm = request.form.get("confirm").strip()
    email = request.form.get("email").strip()
    phone = h.format_phone(request.form.get("phone").strip())

    if h.validate_registration(first, last, username, password, email, confirm, phone):
        h.create_user(first, last, username, password, email, phone)
        h.create_session(username)
        return redirect("/info")
    else:
        return render_template("register.html", first=first, last=last, username=username, password=password, confirm=confirm, email=email, phone=phone, page="register")

 # Route to collect match data from a user and store it in a temporary databease to await confirmation   
@app.route("/input", methods=["GET", "POST"])
def input():
    if request.method == "GET":
        try:
            # Find the opponents within 3 ranks of user
            user = h.get_user()
            opponent = h.get_opponent()
            friendlies = h.get_friendly_opponents()
            # Send username and opponents to input page
            return render_template("input.html", opponent=opponent, friendlies=friendlies, user=user)
        except KeyError:
            print("Exception caught! KeyError")
            return redirect("/")
    elif request.method == "POST":
        # Get the data from the form
        first_winner = request.form.get("1st-winner")
        first_loser = request.form.get("1st-loser")
        first_tie_winner = request.form.get("1st-tie-winner")
        first_tie_loser = request.form.get("1st-tie-loser")
        second_winner = request.form.get("2nd-winner")
        second_loser = request.form.get("2nd-loser")
        second_tie_winner = request.form.get("2nd-tie-winner")
        second_tie_loser = request.form.get("2nd-tie-loser")
        third_winner = request.form.get("3rd-winner")
        third_loser = request.form.get("3rd-loser")
        third_tie_winner = request.form.get("3rd-tie-winner")
        third_tie_loser = request.form.get("3rd-tie-loser")
        score = h.format_score(first_winner, first_loser, first_tie_winner, first_tie_loser, second_winner, second_loser, second_tie_winner, second_tie_loser, third_winner, third_loser, third_tie_winner, third_tie_loser)
        opponent_id = request.form.get("opponent")
        is_win = request.form.get("is_win")
        date_played = request.form.get("date_played")
        match_type = request.form.get("type")
        if not match_type:
            match_type = c.CHALLENGE
        # Make sure no data is missing
        if not score or not opponent_id or not is_win or not date_played:
            flash("Please fill out all fields.")
            return redirect("/input")
        # Make sure data has not been tampered with client-side
        elif not h.validate_match_data(score, opponent_id, is_win, date_played, match_type):
            flash("Problem recording match. Please try again")
            return redirect("/input")
        else:
            # If all looks good, record the match to Temp_match database to await confirmation
            h.record_match(score, opponent_id, is_win, date_played, match_type, session["USER"])
            h.create_notification(opponent_id, session["USER"], c.MATCH_REPORTED)
            return redirect("/redirect_profile")

# Route to confirm and entry in the Temp_match database and commit it to the Matches database
@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    if request.method == "GET":
        try:
            user = h.get_user()
            temp_matches = h.get_temp_matches(session["USER"])
            return render_template("confirm.html", temp_matches=temp_matches, user=user)
        except KeyError:
            print("Exception caught! KeyError")
            return redirect("/")
    elif request.method == "POST":
        match_id = request.form.get("match_id")
        try:
            match = h.confirm_match(match_id)
        except:
            flash("There was a problem confirming your match results")
            return redirect("/confirm")
        if match.match_type == c.CHALLENGE:
            h.update_ranks(match.winner_id, match.loser_id)
            h.reset_challenge(match.winner.id, match.loser.id)
        return redirect("/confirm")

# Route to delete temp match if player disputes
@app.route("/dispute", methods=["POST"])
def dispute():
    match_id = request.form.get("match_id")
    try:
        match = h.Temp_match.query.filter_by(id=match_id).first()
        user = h.get_user()
        h.create_notification(match.submit_by, user.id, c.DISPUTE)
        h.delete_temp_match(match_id)
        return redirect("/confirm")
    except:
        flash("There was a problem disputing your match")
        return redirect("/confirm")
    
# Route to delete temp match if player disputes
@app.route("/delete_match", methods=["POST"])
def delete_match():
    match_id = request.form.get("match_id")
    try:
        h.delete_temp_match(match_id)
        return redirect("/confirm")
    except:
        flash("There was a problem deleting your match")
        return redirect("/confirm")

@app.route("/redirect_profile")
def redirect_profile():    
    if "USER" in session:
        try:
            user = h.get_user()
            profile = h.get_profile(user.id)
            return render_template("profile.html", profile=profile, id=profile.id, user=user)
        except KeyError:
            print("Exception caught! KeyError")
            return redirect("/")
    else:
        return redirect("/")

# Route to edit profile information
@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "GET":
        try:
            user = h.get_user()
            return render_template("edit.html", user=user)
        except KeyError:
            print("Exception caught! KeyError")
            return redirect("/")
    elif request.method == "POST":
        first = request.form.get("first").strip()
        last = request.form.get("last").strip()
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        phone = h.format_phone(request.form.get("phone").strip())
        new_password = request.form.get("new-password")
        confirm_new_password = request.form.get("confirm-new-password")
        password = request.form.get("password")

        if not h.validate_update(username, email, phone, new_password, confirm_new_password, password):
            return redirect("/edit")
        else:
            h.update_profile(first, last, username, email, phone, new_password)
            if username:
                h.create_session(username)
            return redirect("/redirect_profile")

@app.route("/info")
def info():
    user = h.get_user()
    return render_template("info.html", user=user)

@app.route("/challenge")
def challenge():
    id = request.args.get("id")
    recipient = h.User.query.filter_by(id=id).first()
    user = h.get_user()
    if recipient.challenge != None:
        flash("Player currently has an open challenge. Please wait until it is completed to challenge this player.")
        return redirect("/")
    else:
        h.create_notification(id, user.id, c.CHALLENGE)
        user.challenge = id
        h.db.session.commit()
        return redirect("/")
        

@app.route("/cancel_challenge")
def cancel_challenge():
    user = h.get_user()
    challenge_id = request.args.get("id")
    h.cancel_challenge(user.id, challenge_id)
    return redirect("/")