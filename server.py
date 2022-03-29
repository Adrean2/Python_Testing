import json
from multiprocessing.sharedctypes import Value
from tkinter.tix import INTEGER
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()
POINTS_COST_PER_PLACE = 3

@app.route('/')
def index():
    return render_template('index.html',clubs=clubs)

@app.route('/showSummary',methods=['POST'])
def showSummary():
    try:
        if not request.form["email"]:
            raise ValueError("Vous devez inscrire une adresse email.")
        club = [club for club in clubs if club['email'] == request.form['email']]
        if club == []:
            raise ValueError("Vous devez utiliser une adresse email valide.")
    except ValueError as error:
        return render_template('index.html',error=error,clubs=clubs)

    return render_template('welcome.html',club=club[0],competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    try:
        Club = [c for c in clubs if c['name'] == club]
        Competition = [c for c in competitions if c['name'] == competition]
        if Club:
            foundClub = Club[0]
        elif not Club:
            raise IndexError("Renseignez un club valide")

        if Competition:
            foundCompetition = Competition[0]
        elif not Competition:
            raise IndexError("Renseignez une competition valide")

        if foundClub and foundCompetition:
            return render_template('booking.html',club=foundClub,competition=foundCompetition)

    except IndexError as error:
        return render_template('booking.html',competition=competition,club=club,error=error)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    try:
        if not request.form["places"]:
            raise ValueError("Ecrivez une valeur")
        else:
            placesRequired = int(request.form['places'])
    except ValueError as error:
        return render_template("booking.html",club=club,competition=competition,error=error)
    try:
        if placesRequired >= 12:
            raise ValueError("Vous ne pouvez pas reserver + de 12 places")
        elif int(club["points"]) < placesRequired*POINTS_COST_PER_PLACE:
            raise ValueError("Il vous faut plus de points pour reserver")
        elif placesRequired < 1:
            raise ValueError("Utilisez un chiffre positif !")
        elif type(placesRequired) is not int:
            raise ValueError("Utilisez une valeur valide")
        else:
            competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-int(placesRequired)
            club["points"]= int(club["points"]) - placesRequired*POINTS_COST_PER_PLACE
            flash('Great-booking complete!')
            return render_template('welcome.html', club=club, competitions=competitions)
    except ValueError as error:
        return render_template("booking.html",club=club,competition=competition,error=error)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))