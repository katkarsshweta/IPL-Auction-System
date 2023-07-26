from flask import Flask, redirect,render_template, session, flash
from sqlalchemy import create_engine
from flask.globals import request
from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin
from flask_login import login_required, logout_user, login_user, login_manager, LoginManager, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
import mysql
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
import json
import matplotlib.pyplot as plt
import io
import base64


# my database connection
local_server = True
app = Flask(__name__)
app.secret_key = "iplAuction"

#this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view="login"

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/databasename'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sanu5jan@localhost/dbms'
db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return owner.query.get(int(user_id))

class Test(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

#creating database tables class models

class owner(db.Model):                                      #OWNER TABLE
    ownerID = db.Column(db.Integer, primary_key = True)
    ownerName = db.Column(db.String(100))
    ownerEmail = db.Column(db.String(100), unique=True)
    teamName = db.Column(db.String(100), unique=True)
    ownerPass = db.Column(db.String(50))

class teams(db.Model):                                      #TEAMS TABLE
    teamID = db.Column(db.Integer, primary_key = True)
    teamName = db.Column(db.String(100), unique = True)
    ownerID = db.Column(db.Integer, unique = True)
    totBudget = db.Column(db.Integer, default = 40)
    remBudget = db.Column(db.Integer, default = 40)

class players(db.Model):                                    #PLAYERS TABLE
    playerID = db.Column(db.Integer, primary_key = True)
    playerName = db.Column(db.String(100))
    playerType = db.Column(db.String(50))
    playerNation = db.Column(db.String(20))
    basePrice = db.Column(db.Integer)
    playerAvail = db.Column(db.String(3), default = "YES")
    playerImage = db.Column(db.LargeBinary)

class skills(db.Model):                                     #SKILLS TABLE
    playerID =  db.Column(db.Integer, primary_key = True)
    avgRuns = db.Column(db.Integer)
    avgWickets = db.Column(db.Integer)
    matches = db.Column(db.Integer)

class sold_players(db.Model):                               #SOLD_PLAYERS TABLE
    playerID = db.Column(db.Integer, primary_key = True)
    teamID = db.Column(db.Integer)
    basePrice = db.Column(db.Integer)
    sellingP = db.Column(db.Integer)



@app.route("/")      #HOME PAGE
def home():
    return render_template("index.html")

@app.route("/viewFranchise")      #VIEW FRANCHISES PAGE
def viewFranchise():
    #Joining teams table and owner table to show all franchises 
    query = db.session.query(owner.ownerID, teams.teamName, owner.ownerName, teams.totBudget).join(teams, owner.ownerID==teams.ownerID).all()
    return render_template("viewFranchise.html", franchises = query)

@app.route("/updateFranchise",methods=["POST","GET"])      #UPDATE FRANCHISE PAGE
def updateFranchise():
    franName=request.form['teamName']
    query = db.session.query(owner.ownerID, teams.teamName, owner.ownerName, teams.totBudget, owner.ownerEmail).join(teams, owner.ownerID==teams.ownerID)
    query = query.filter_by(teamName=franName).first()
    return render_template("updateFranchise.html", record = query)

@app.route("/updateFranchise2/<string:teamName>",methods=["POST","GET"])   #Update Franchise method 
def updateFranchise2(teamName):
    ownerName=request.form['ownerName']
    ownerEmail = request.form['ownerEmail']
    getTeamName = teamName
    query = db.session.query(owner).filter_by(teamName=getTeamName).update({"ownerName": ownerName, "ownerEmail": ownerEmail})
    db.session.commit()
    flash("Changes Saved!", "success")
    return redirect("/")

@app.route("/removeFranchise")         #Remove Franchise Page
def removeFranchise():
    query = db.session.query(owner.ownerID, teams.teamName, owner.ownerName, teams.totBudget).join(teams, owner.ownerID==teams.ownerID).all()
    return render_template("removeFranchise.html", franchises = query)
   
@app.route("/viewPlayers")            #View Players Page
def viewPlayers():
    conditions = ['All Players', 'Base Price', 'Average Runs', 'Average Wickets', 'Matches Played', 'Type: Baller', 'Type: Batter', 'Type: Wicket-Keeper','Type: All-Rounder', 'Nationality: Indian', 'Nationality: Foreign']
    selected_condition = request.args.get('condition')
    query = db.session.query(players.playerID, players.playerName, players.playerNation, players.playerType, skills.avgRuns, skills.avgWickets, skills.matches, players.basePrice).join(players, players.playerID==skills.playerID)

    if selected_condition == 'Base Price':                    #Applying different order by clauses for filter
        query = query.order_by(players.basePrice.desc())

    elif selected_condition == 'Average Runs':
        query = query.order_by(skills.avgRuns.desc())

    elif selected_condition == 'Average Wickets':
        query = query.order_by(skills.avgWickets.desc())

    elif selected_condition == 'Matches Played':
        query = query.order_by(skills.matches.desc())

    # Filter players by nationality                          #Applying different where clauses for filter
    elif selected_condition == 'Nationality: Indian':
        query = query.filter_by(playerNation='Indian')

    elif selected_condition == 'Nationality: Foreign':
        query = query.filter_by(playerNation='Foreign')

    # Filter players by player type
    elif selected_condition == 'Type: Baller':
        query = query.filter_by(playerType='Baller')

    elif selected_condition == 'Type: Batter':
        query = query.filter_by(playerType='Batter')

    elif selected_condition == 'Type: All-Rounder':
        query = query.filter_by(playerType='All-Rounder')

    elif selected_condition == 'Type: Wicket-Keeper':
        query = query.filter_by(playerType='Wicket-Keeper')
    
    return render_template("viewPlayers.html", plrInfo = query, conditions=conditions)

@app.route("/removePlayer")           #Delete Player Page
def removePlayer():
    plr = players.query.filter_by(playerAvail='YES')
    return render_template("removePlayer.html", plrInfo = plr)

@app.route("/deletePlayer",methods=["GET", "POST"])          #Delete Player Method
def deletePlayer():
    playerID = request.form['playerID']

    # Get the row to be deleted from the database
    plr = players.query.filter_by(playerID=playerID).first()
    id = skills.query.filter_by(playerID=playerID).first()

    if id:
        db.session.delete(id)
        db.session.commit()

    if plr:
        # Delete the row from the database
        db.session.delete(plr)
        db.session.commit()
        flash("Player deleted successfully!", "success")     #Display message
    else:
        flash("Player not found!", "warning")

    return redirect("viewPlayers")

@app.route("/releasePlayer", methods=['POST','GET'])        #Release Player Method
def releasePlayer():
    plrID = request.form['playerID']
    print(plrID)
    getTeamID = players.query.filter_by(playerID = plrID)
    stmt = text("CALL releasePlayer(:plrID)")
    db.session.execute(stmt, {"plrID":int(plrID)})
    db.session.commit()
    flash("Player released successfully!!")
    return redirect("/")

@app.route("/addPlayer", methods=['POST','GET'])         #Add Player Page
def addPlayer():
    return render_template("addPlayer.html")

@app.route("/updatePlayer", methods = ['POST', 'GET'])   #Update Player Page
def updatePlayer():
    query = db.session.query(players.playerID, players.playerName, players.playerNation, players.playerType, skills.avgRuns, skills.avgWickets, skills.matches, players.basePrice, players.playerAvail).join(players, players.playerID==skills.playerID)
    plr = query.filter_by(playerAvail='YES')
    return render_template("updatePlayer.html", plrInfo=plr)

@app.route("/updatePlayerForm", methods = ['POST', 'GET'])       #Update Player Form
def updatePlayerForm():
    plrID=request.form['playerID']
    query = db.session.query(players.playerID, players.playerName, players.playerNation, players.playerType, skills.avgRuns, skills.avgWickets, skills.matches, players.basePrice, players.playerAvail, players.playerImage).join(players, players.playerID==skills.playerID)
    print(query)
    plr = query.filter_by(playerID=plrID).first()
    return render_template("updatePlayerForm.html", plrInfo=plr)

@app.route("/updatePlayer2/<int:playerID>", methods = ['POST', 'GET'])     #Update Player Method
def updatePlayer2(playerID):
    plrName=request.form['playerName']
    plrNation=request.form['playerNation']
    plrType=request.form['playerType']
    plrAvgRuns=request.form['avgRuns']
    plrAvgWick=request.form['avgWickets']
    plrMatches=request.form['matches']
    plrBP=request.form['basePrice']
    plrImage = request.files['playerImage'].read()
    getPlrID=playerID
    query1 = db.session.query(players).filter_by(playerID=getPlrID).update({"playerName": plrName, "playerNation": plrNation, "playerType":plrType, "basePrice": plrBP, "playerImage": plrImage})
    query2 = db.session.query(skills).filter_by(playerID = getPlrID).update({"avgRuns": plrAvgRuns, "avgWickets":plrAvgWick, "matches":plrMatches})
    db.session.commit()
    flash("Changes Saved!", "success")
    return redirect("/")


@app.route("/addPlayerForm", methods=['POST','GET'])        #Add Player
def addPlayerForm():
    plrName=request.form['playerName']
    plrNation=request.form['playerNation']
    plrType=request.form['playerType']
    plrAvgRuns=request.form['avgRuns']
    plrAvgWick=request.form['avgWickets']
    plrMatches=request.form['matches']
    plrBP=request.form['basePrice']
    playerImage = request.files['playerImage'].read()
    # if image_file:
    #     image_data = image_file.read()
    #     new_data1 = players(playerName = plrName, playerNation = plrNation, playerType = plrType, basePrice=plrBP, playerImage = image_data)
    # else:
    #     new_data1 = players(playerName = plrName, playerNation = plrNation, playerType = plrType, basePrice=plrBP)

    new_data1 = players(playerName = plrName, playerNation = plrNation, playerType = plrType, basePrice=plrBP,playerImage=playerImage)
    new_data2 = skills(avgRuns = plrAvgRuns, avgWickets = plrAvgWick, matches = plrMatches)
    db.session.add(new_data1)
    db.session.add(new_data2)
    db.session.commit()
    flash("Player Added Successfully!", "success")
    return render_template("addPlayer.html")

@app.route("/viewTeams")           #View Teams Page
def viewTeams():
    # ownerlist = owner.query.all()
    # teamlist = teams.query.all()
    query = db.session.query(teams.teamID, teams.teamName, owner.ownerName, teams.totBudget, teams.remBudget).join(teams, owner.ownerID==teams.ownerID).all()
    return render_template("viewTeams.html", teamlist = query)

@app.route("/playersByTeam", methods = ['POST','GET'])          #Players by Team
def getTeamPlayers():
    teamName = request.args.get('teamName')
    teamName = request.form['teamName']
    getTeamID = teams.query.filter_by(teamName = teamName).with_entities(teams.teamID)
    getTeamBudget= teams.query.filter_by(teamName = teamName).with_entities(teams.remBudget).all()
    list_of_players = db.session.query(players.playerID, players.playerName, players.playerType, players.playerNation, players.basePrice, sold_players.sellingP, sold_players.teamID).join(sold_players,players.playerID==sold_players.playerID)
    playerList = list_of_players.filter_by(teamID = getTeamID).all()
    
    numBatter = len([player for player in playerList if player.playerType == 'Batter'])
    numBaller = len([player for player in playerList if player.playerType == 'Baller'])
    numWick = len([player for player in playerList if player.playerType == 'Wicket-Keeper'])
    numAll = len([player for player in playerList if player.playerType == 'All-Rounder'])
    data = json.dumps([numBaller, numBatter, numWick, numAll])
    return render_template("playersByTeam.html", playerlist = playerList, teamName = teamName, data=data, budget=getTeamBudget)

@app.route("/aboutPlayer", methods=['POST','GET'])                #About Player
def aboutPlayer():
    global plrID
    plrID=request.form['playerID']  #getting player name from drop down
    plrID = players.query.filter_by(playerID = plrID).first()  #getting player id
    #print(plrID.playerImage)
    plr_image = bytes(plrID.playerImage)
    image_base64 = base64.b64encode(plr_image)
    # print(image_base64)
    image_bytes = base64.b64decode(image_base64)
    data_url = f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
    stats = skills.query.filter_by(playerID = plrID.playerID)   #getting skills of that player
    p=plrID
    query = db.session.query(teams.teamName).all() #drop down options (teams)
    
    return render_template("aboutPlayer.html", stats = stats, plrName = plrID.playerName, plrNation = plrID.playerNation,bp=plrID.basePrice, plrType=plrID.playerType, franTeams=query, plrImage=data_url)

@app.route("/actualBidding", methods = ["POST", "GET"])  #Bidding Process
def actualBidding():

    try:
        tmName = request.form['teamName']   #getting winning team
        bid = request.form['bidAmtInput']   #getting bid amt
        stmt = text("CALL makeBid(:p, :tmName, :bid)")
        db.session.execute(stmt, {"p":plrID.playerID, "tmName": tmName, "bid":bid })
        db.session.commit()
        flash("Player sold successfully!", "success")
    except OperationalError as e:
        db.session.rollback()
        error_message = str(e.orig)   # extract the error message
        if "Invalid Bid Amount!!" in error_message:
            flash("Invalid Bid Amount!!")
        elif "Not Enough Budget!" in error_message:
            flash("Not Enough Budget!")
        elif "Players limit reached!" in error_message:
            flash("Player limit reached!")
        elif "Column 'teamID' cannot be null" in error_message:
            flash("Please select a Franchise!")
        elif "Incorrect integer value:" in error_message:
            flash("Please enter details!")
        else:
            flash(str(e), "error")
        
    return redirect("bidding")

@app.route("/bidding", methods = ['POST', "GET"])     #Bidding Page
def bidding():
    conditions = ['All Players', 'Base Price', 'Baller', 'Batter', 'Wicket-Keeper','All-Rounder', 'Indian', 'Foreign']
    selected_condition = request.args.get('condition')
    plr = players.query.filter_by(playerAvail='YES')

   # Filter players by base price
    if selected_condition == 'Base Price':
        plr = plr.order_by(players.basePrice.desc())

    # Filter players by nationality
    elif selected_condition == 'Indian':
        plr = plr.filter_by(playerNation='Indian')

    elif selected_condition == 'Foreign':
        plr = plr.filter_by(playerNation='Foreign')

    # Filter players by player type
    elif selected_condition == 'Baller':
        plr = plr.filter_by(playerType='Baller')

    elif selected_condition == 'Batter':
        plr = plr.filter_by(playerType='Batter')

    elif selected_condition == 'All-Rounder':
        plr = plr.filter_by(playerType='All-Rounder')

    elif selected_condition == 'Wicket-Keeper':
        plr = plr.filter_by(playerType='Wicket-Keeper')

    # Render the template with the dropdown box and table
    return render_template('bidding.html', conditions=conditions, plr = plr)


@app.route('/signin', methods=['POST', 'GET'])           #Register Franchise
def signin():
    if request.method == "POST":
        ownerName=request.form['ownerName']
        ownerEmail=request.form['ownerEmail']
        teamName=request.form['teamName']
        ownerPass=request.form['ownerPass']
        print(ownerName, ownerEmail, teamName, ownerPass)
        userTeam = owner.query.filter_by(teamName=teamName).first()
        userEmail = owner.query.filter_by(ownerEmail=ownerEmail).first()

        if userTeam or userEmail:
            flash("Email ID or Franchise Name is already taken.", 'warning')
            return render_template("ownerSignIn.html")


        new_data = owner(ownerName = ownerName, ownerEmail = ownerEmail, teamName=teamName,ownerPass=ownerPass)
        db.session.add(new_data)
        db.session.commit()
        
        flash("New Franchise created successfully!", "success")
        return render_template("index.html")

    return render_template("ownerSignIn.html")


# @app.route('/login', methods=['POST', 'GET'])  
# def login():
#     if request.method == "POST":
#         teamName=request.form['teamName']
#         ownerPass=request.form['ownerPass']
#         user = owner.query.filter_by(teamName = teamName, ownerPass=ownerPass).first()

#         if user:
#             session['user'] = teamName
#             #return 'login success'  
#             flash('Login Successful', 'info')
#             return render_template("index.html") #add url to whichever page u wanna take to
#             #return redirect(url_for('dashboard'))    
#         else:
#             #return 'login fail'
#             flash('Invalid Credentials', 'error')
#             return render_template("ownerLogin.html")

        

#     return render_template("ownerLogin.html")

@app.route('/deleteFranchise', methods=['POST'])         #Delete Franchise
def delete_franchise():
    teamName = request.form['teamName']

    # Get the row to be deleted from the database
    franchise = teams.query.filter_by(teamName=teamName).first()

    if franchise:
        # Delete the row from the database
        db.session.delete(franchise)
        db.session.commit()
        flash("Franchise deleted successfully!", "success")
    else:
        flash("Franchise not found!", "warning")

    return redirect("viewFranchise")


@app.route("/aboutUs")         #About Us Page
def aboutUs():
    return render_template("aboutUs.html")

@app.route("/statsGraph")           #Bar Graph
def statsGraph():
    teams_data = teams.query.all()
    x_labels = [team.teamName for team in teams_data]
    y_values = [team.totBudget - team.remBudget for team in teams_data]
    # Create the bar graph
    plt.figure(figsize=(10, 30))
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.bar(x_labels, y_values, width = 0.8)
    ax.set_xlabel('Team Name')
    ax.set_ylabel('Budget Spent')
    ax.set_title('Franchise Expenditures')
    plt.xticks(rotation=15)

    # Save the bar graph to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the buffer to base64 and render the template
    image = base64.b64encode(buffer.getvalue()).decode()
    return render_template("statsGraph.html", image=image)

@app.template_filter('b64encode')
def b64encode_filter(s):
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')

# testing whether db is connected or not
@app.route("/test")
def test():
    try:
        a = Test.query.all()
        print(a)
        return 'My database is connected'
    except Exception as e:
        print(e)
        return f'My database is not connected {e}'

app.run(debug = True)