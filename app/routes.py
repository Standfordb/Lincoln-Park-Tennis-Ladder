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
            user = h.get_user()
        else:
            user = None
        messages = h.get_broadcast_messages()
        return render_template("index.html", players=players, pages=pages, user=user, spread=c.SPREAD, messages=messages)
    elif request.method == "POST":
        # Get the login information from the POST request
        username = request.form.get("username").strip().upper()
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
    page = "register"
    return render_template("register.html", page=page)

# Profile page
@app.route("/profile")
def profile():
    # Get the id of the profile to pull up
    id = request.args.get('id')
    profile, stats = h.get_profile(id)
    return render_template("profile.html", profile=profile, stats=stats)

# Logout button 
@app.route("/logout")
def logout():
    h.remove_session()
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
    
    if h.validate_registration(first, last, username, password, email, confirm):
        h.create_user(first, last, username, password, email, phone)
        h.create_session(username)
        return redirect("/")
    else:
        return redirect("/register")

 # Route to collect match data from a user and store it in a temporary databease to await confirmation   
@app.route("/input", methods=["GET", "POST"])
def input():
    if request.method == "GET":
        # Find the opponents within 3 ranks of user
        user = h.get_user()
        opponents = h.get_opponents(user.rank)
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
        elif not h.validate_match_data(score, opponent_id, is_win, date_played):
            flash("Problem recording match. Please try again")
            return redirect("/input")
        else:
            # If all looks good, record the match to Temp_match database to await confirmation
            h.record_match(score, opponent_id, is_win, date_played)
            profile, stats = h.get_profile(session["USER"])
            return redirect(url_for("profile", profile=profile, stats=stats, id=profile.id))

# Route to confirm and entry in the Temp_match database and commit it to the Matches database
@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    if request.method == "GET":
        temp_matches = h.get_temp_matches(session["USER"])
        return render_template("confirm.html", temp_matches=temp_matches )
    elif request.method == "POST":
        match_id = request.form.get("match_id")
        h.confirm_match(match_id)
        h.update_rankings()
        return redirect("/confirm")

# Route to delete temp match if player disputes
@app.route("/dispute", methods=["POST"])
def dispute():
    match_id = request.form.get("match_id")
    h.delete_temp_match(match_id)
    return redirect("/confirm")

@app.route("/redirect_profile")
def redirect_profile():    
    profile, stats = h.get_profile(session["USER"])
    return render_template("profile.html", profile=profile, stats=stats, id=profile.id)

# Route to edit profile information
@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "GET":
        user = h.get_user()
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

        if not h.validate_update(username, email, phone, new_password, confirm_new_password, password):
            return redirect("/edit")
        else:
            h.update_profile(first, last, username, email, phone, new_password)
            if username:
                h.create_session(username)
            return redirect("/redirect_profile")
