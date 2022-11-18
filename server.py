
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import re
import psycopg2, psycopg2.extras
from urllib.parse import urlparse
from datetime import date
import random

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'cairocoders-ednalan'

DATABASEURI = "postgresql://rvg2119:Reset123@34.75.94.195/proj1part2"

result = urlparse(DATABASEURI)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port
conn = psycopg2.connect( database = database, user = username, password = password, host = hostname, port = port )

# This line creates a database engine that knows how to connect to the URI above.
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def home():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print(engine.table_names())
    
    cursor.execute("SELECT Tournament_Name, Category, Player1.First_Name || ' ' || Player1.Last_Name AS Player_1_Name, Player2.First_Name || ' ' || Player2.Last_Name AS Player_2_Name, Round FROM Fixtures, Tournaments, Players AS Player1, Players AS Player2 WHERE Tournaments.Tournament_ID=Fixtures.Tournament_ID AND Player1.Player_ID=Player_1 AND Player2.Player_ID=Player_2 AND Player_1 IS NOT NULL AND Player_2 IS NOT NULL AND Winner IS NULL ORDER BY Fixtures.Tournament_ID ASC, Fixture_ID ASC")
    fixtures = cursor.fetchall()

    cursor.execute("SELECT Tournaments.Tournament_ID, Tournament_Name, Tournament_Type, Category, Status, Location, Start_Date, End_Date, Court_Surface, Sponsor, Admin_Name, Date_of_Announcement FROM Tournaments, Tournament_Points, Register, Admins WHERE Tournaments.Tournament_ID=Register.Tournament_ID AND Tournaments.Tournament_Type_ID=Tournament_Points.Tournament_Type_ID AND Admin_Incharge=Admin_ID")
    tournaments = cursor.fetchall()

    cursor.execute("SELECT RANK () OVER (ORDER BY Points DESC) Rank, Player_ID, First_Name || ' ' || Last_Name AS Player_Name, Country, Points FROM Players WHERE Sex='M' ORDER BY Points DESC")
    men_rankings = cursor.fetchall()

    cursor.execute("SELECT RANK () OVER (ORDER BY Points DESC) Rank, Player_ID, First_Name || ' ' || Last_Name AS Player_Name, Country, Points FROM Players WHERE Sex='F' ORDER BY Points DESC")
    women_rankings = cursor.fetchall()
    cursor.close()

    fixture_heading = ('Tournament', 'Category', 'Player 1', 'Player 2', 'Round')
    tournament_heading = ('ID', 'Tournament', 'Type', 'Category', 'Registration Status', 'Location','Start Date', 'End Date', 'Surface', 'Sponsor', 'Admin Incharge', 'Announcement Date')
    ranking_heading = ('Rank', 'ID', 'Player', 'Country', 'Points')

    dict = {'fixture_heading': fixture_heading, 'tournament_heading': tournament_heading, 'men_ranking_heading': ranking_heading, 'women_ranking_heading': ranking_heading, 'fixtures': fixtures, 'tournaments': tournaments, 'men_rankings': men_rankings, 'women_rankings': women_rankings}
    return render_template('home.html', **dict) 

    # # Check if user is loggedin
    # if 'loggedin' in session:
    
    #     # User is loggedin show them the home page
    #     return render_template('home.html', username=session['username'])
    # # User is not loggedin redirect to login page
    # return redirect(url_for('login'))

'''
  Admin registration and login
'''
@app.route('/loginAdmin/', methods=['GET', 'POST'])
def loginAdmin():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "admin_id" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'admin_id' in request.form and 'password' in request.form:
        admin_id = request.form['admin_id']
        password = request.form['password']
        print(password)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM admins WHERE admin_id = %s', (admin_id,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if password_rs == password:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['admin_id']
                session['admin_id'] = account['admin_id']
                # Redirect to home page
                return redirect(url_for('admin'))
            else:
                # Account doesnt exist or admin_id/password incorrect
                flash('Incorrect admin_id/password')
        else:
            # Account doesnt exist or admin_id/password incorrect
            flash('Incorrect admin_id/password')
 
    return render_template('loginAdmin.html')

# localhost:8111/register
@app.route('/registerAdmin', methods=["GET", "POST"])
def registerAdmin():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Check if "admin_name", "password" and "admin_id" POST requests exist (user submitted form)
    if request.method == 'POST' and 'admin_name' in request.form and 'password' in request.form and 'admin_id' in request.form:
        # Create variables for easy access
        admin_name = request.form['admin_name']
        password = request.form['password']
        admin_id = request.form['admin_id']
    
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM admins WHERE admin_id = %s', (admin_id,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[A-Za-z0-9]+', admin_id):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z]+', admin_name):
            flash('Admin Name must contain only characters and numbers!')
        elif not admin_name or not password or not admin_id:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO admins (admin_name, password, admin_id) VALUES (%s,%s,%s)", (admin_name, password, admin_id))
            conn.commit()
            flash('You have successfully registered!')
            return render_template('loginAdmin.html')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('registerAdmin.html')

@app.route('/admin')
def admin():
    if 'loggedin' in session:      
        return render_template('admin.html', username = session['admin_id'])

    else: return redirect(url_for('loginAdmin'))

@app.route('/ban', methods = ["GET", "POST"])
def ban():
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        if request.method == "POST" and 'player' in request.form:
            player_id = request.form.get('player') #playerid
            
            cursor.execute("DELETE FROM players WHERE player_id = %s", (player_id,))
            conn.commit()
            flash('Player {} has been banned from the tournament'.format(player_id))
            return redirect(url_for('ban'))
        else:
            cursor.execute('SELECT * FROM players')

            players = []
            for player in cursor:
                players.append(player['player_id'])

            data_dict = dict(data = players)

            return render_template('adminPrivileges/ban.html', **data_dict)
    else: return redirect(url_for('loginAdmin'))
    
    
@app.route('/authorize', methods=["GET", "POST"])
def authorize():
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        if request.method == "POST" and 'player' in request.form:
            authorizer = session['admin_id'] #None
            today = date.today() #None

            player_id = request.form.get('player') #playerid
            
            cursor.execute("UPDATE players SET authorizer = %s, authorization_date = %s WHERE player_id = %s", (authorizer, today, player_id ))
            flash('Player {} has been authorized'.format(player_id))
            return redirect(url_for('authorize'))
        else:
            # Check if account exists using MySQL
            cursor.execute('SELECT * FROM players')
            # Fetch one record and return result
            unauth_players = []
            for player in cursor:
                if player['authorizer'] == None: unauth_players.append(player['player_id'])

            data_dict = dict(data = unauth_players)

            return render_template('adminPrivileges/auth.html', **data_dict)
    else: return redirect(url_for('loginAdmin'))

@app.route('/createTour', methods=["GET", "POST"])
def createTour():
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        today = date.today()
        
        if request.method == "POST" and 'tournament_name' in request.form and 'tournament_id' in request.form:
                # Create variables for easy access
                tournament_id = request.form['tournament_id']
                tournament_name = request.form['tournament_name']
                tournament_type = request.form['tournament_type']
                category = request.form['category']
                tournament_location = request.form['location']
                tournament_start = request.form['start_date']
                tournament_end = request.form['end_date']
                tournament_surface = request.form['court_surface']
                tournament_sponsor = request.form['sponsor']
                tournament_admin = request.form['admin_incharge']
                tournament_announcement = request.form['date_of_announcement']

                cursor.execute('SELECT * FROM tournaments WHERE tournament_id = %s', (tournament_id,))
                tournament = cursor.fetchone()
                print(tournament)
                # If account exists show error and validation checks
                if tournament:
                    flash('Tournament already exists!')
                elif not re.match(r'[A-Za-z]+', tournament_name):
                    flash('Tournament name must contain only characters!')
                elif not re.match(r'[A-Za-z]+', tournament_location):
                    flash('Tournament location must contain only characters')
                elif tournament_admin != session['admin_id']:
                    flash('You cant assign other admin as in charge for this tournament')
                elif not tournament_id or not tournament_location or not tournament_name:
                    flash('Please fill out the form!')
                else:
                    cursor.execute("INSERT INTO tournaments (tournament_id, tournament_name, tournament_type_id, location, start_date, end_date, court_surface, sponsor, admin_incharge, date_of_announcement) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)", (tournament_id, tournament_name, tournament_type, tournament_location, tournament_start, tournament_end, tournament_surface, tournament_sponsor, tournament_admin, tournament_announcement))
                    if category == "Men's":
                        cursor.execute("INSERT INTO Register (Tournament_ID, Category) VALUES (%s, %s)", (tournament_id, "Men's"))
                    elif category == "Women's":
                        cursor.execute("INSERT INTO Register (Tournament_ID, Category) VALUES (%s, %s)", (tournament_id, "Women's"))
                    else:
                        cursor.execute("INSERT INTO Register (Tournament_ID, Category) VALUES (%s, %s)",
                                       (tournament_id, "Men's"))
                        cursor.execute("INSERT INTO Register (Tournament_ID, Category) VALUES (%s, %s)",
                                       (tournament_id, "Women's"))
                    conn.commit()
                    flash('Tounament successfully created!')
                    return redirect(url_for('createTour'))
                    
                return redirect(url_for('createTour'))                    
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            flash('Please fill out the form!')
        else:
            cursor.execute('SELECT * from tournament_points')
            exist = cursor.fetchall()
            exist_id = []
            for item in exist: exist_id.append(item[0])

            data_dict = {'admin_id': session['admin_id'], 'date': today, 'surfaces': ['Clay', 'Grass', 'Hard'], 'type_id': exist_id}
            return render_template('adminPrivileges/createTour.html', data=data_dict)
        
    else: return redirect(url_for('loginAdmin'))

@app.route('/openCloseRegistrations', methods=["GET", "POST"])
def openCloseRegistrations():
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        if request.method == "POST" and 'tournament_id' in request.form and 'status' in request.form:
            tournament_id = request.form['tournament_id']
            status = request.form['status']

            if status not in ['Open', 'Closed']:
                flash('Enter a valid status')
            else:
                if status == 'Open': status = 'Open  '
                else: status = 'Closed'

            cursor.execute('UPDATE register SET status = %s WHERE tournament_id = %s', (status, tournament_id))
            conn.commit()
            flash('Registration status successfully updated!')
            return redirect(url_for('openCloseRegistrations'))

        elif request.method == "POST":
            flash('Please fill all details!')
            
        else:
            cursor.execute('SELECT * FROM tournaments WHERE admin_incharge = %s', (session['admin_id'],))
            tournaments = cursor.fetchall()

            cursor.execute('SELECT register.tournament_id, tournament_name, category, status, player_count FROM register, tournaments WHERE register.tournament_id=tournaments.tournament_id')
            registrations = cursor.fetchall()

            print(tournaments)
            print(registrations)

            final = []
            for registration in registrations:
                for tournament in tournaments:
                    if registration[0] == tournament[0]: final.append(registration)

            headings = ('ID', 'Tournament', 'Category', 'Status', 'Player Count')
            data_dict = {'final': final, 'headings': headings}
            return render_template('adminPrivileges/openCloseRegistrations.html', data=data_dict)

    else: return redirect(url_for('loginAdmin'))

@app.route('/logoutAdmin')
def logoutAdmin():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('admin_id', None)
   # Redirect to login page
   return redirect(url_for('home'))

'''
  Player registration and login
'''
@app.route('/loginPlayer/', methods=['GET', 'POST'])
def loginPlayer():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "player_id" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'player_id' in request.form and 'password' in request.form:
        player_id = request.form['player_id']
        password = request.form['password']
        print(password)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM players WHERE player_id = %s', (player_id,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if password_rs == password:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['player_id']
                session['player_id'] = account['player_id']
                # Redirect to home page
                return redirect(url_for('player'))
            else:
                # Account doesnt exist or player_id/password incorrect
                flash('Incorrect player_id/password')
        else:
            # Account doesnt exist or player_id/password incorrect
            flash('Incorrect player_id/password')
 
    return render_template('loginPlayer.html')

# localhost:8111/register
@app.route('/registerPlayer', methods=["GET", "POST"])
def registerPlayer():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    print(request.form)
    # Check if "player_id", "password" and "firstname" POST requests exist (user submitted form)
    if request.method == 'POST' and 'first_name' in request.form and 'password' in request.form and 'player_id' in request.form:
        # Create variables for easy access
        firstname = request.form['first_name']
        middlename = request.form['middle_initial']
        lastname = request.form['last_name']
        player_id = request.form['player_id']
        password = request.form['password']
        gender = request.form['gender']
        dob = request.form['dob']
        country = request.form['country']

        cursor.execute("SELECT Country_Name FROM countries")
        res = cursor.fetchall()
        countries = []
        for item in res: countries.append(item[0])

        cursor.execute('SELECT * FROM players WHERE player_id = %s', (player_id,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[A-Za-z]+', firstname):
            flash('Firstname must contain only characters!')
        elif not re.match(r'[A-Za-z]+', middlename):
            flash('Middlename must contain only characters')
        elif not re.match(r'[A-Za-z]+', lastname):
            flash('Lastname must contain only characters')
        elif not re.match(r'[A-Za-z0-9]+', player_id):
            flash('PlayerID must contain only characters and numbers!')
        elif not player_id or not password or not firstname:
            flash('Please fill out the form!')
        elif country not in countries:
            flash("Enter a valid country name")
        else:
            con = ''
            sub_cur = g.conn.execute("SELECT country_id FROM countries WHERE Country_Name = %s", (country))
            for item in sub_cur: con = item['country_id']
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO players (first_name, middle_initial, last_name, player_id, password, sex, date_of_birth, country) VALUES (%s,%s, %s, %s, %s, %s,%s,%s)", (firstname, middlename, lastname, player_id, password, gender, dob, con))
            conn.commit()
            flash('You have successfully registered!')
            return render_template('loginPlayer.html')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('registerPlayer.html')


@app.route('/logoutPlayer')
def logoutPlayer():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('player_id', None)
   # Redirect to login page
   return redirect(url_for('home'))

@app.route('/player', methods=["GET"])
def player():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if 'loggedin' in session:   
        cursor.execute('SELECT register.tournament_id, tournament_name, category, status, player_count FROM register, tournaments WHERE register.tournament_id=tournaments.tournament_id')
        tournaments = cursor.fetchall()

        cursor.execute('SELECT * FROM players WHERE player_id = %s', (session['player_id'], ))
        player = cursor.fetchone()

        cursor.execute(
            "SELECT RANK () OVER (ORDER BY Points DESC) Rank, Player_ID, First_Name || ' ' || Last_Name AS Player_Name, Country, Points FROM Players WHERE Sex=%s ORDER BY Points DESC", (player['sex']))
        rankings = cursor.fetchall()

        ts = []
        for tournament in tournaments: 
            cat = ''
            if tournament['category'] == "Men's  ": cat = "M"
            else: cat = "F"
            if tournament['status'] == 'Open  ' and cat == player['sex'] : ts.append(tournament)

        headings = ('ID', 'Tournament', 'Category', 'Status', 'Player Count')
        ranking_heading = ('Rank', 'ID', 'Player', 'Country', 'Points')

        data_dict = {'player': player, 'ts': ts, 'headings': headings, 'ranking_heading': ranking_heading, 'rankings': rankings}

        if player['authorizer'] == None:
            return render_template('unauth_player.html', player = player) 
        else:           
            return render_template('player.html', player = data_dict)

    else: return redirect(url_for('loginPlayer'))

@app.route('/tourReg', methods=["GET", "POST"])
def tourReg():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:
        if request.method =="POST":
            tournament_id = request.form['tournament_id']
            player_id = request.form['player_id']
            category = request.form['category']
            today = date.today()
            seed = random.randint(1, 10)


            if not tournament_id or not player_id or not category:
                flash('Please fill out all the details!!')
            elif player_id != session['player_id']:
                flash('You cant register for other players')
            else:
                if category == "M": category = "Men's  "
                else: category = "Women's"

                cursor.execute('SELECT * FROM register WHERE tournament_id = %s', (tournament_id, ))
                t = cursor.fetchone()
                count = t['player_count']

                cursor.execute('INSERT INTO registrations (tournament_id, player_id, category, seed, registration_date) VALUES (%s, %s, %s, %s, %s)', (tournament_id, player_id, category, seed, today))
                cursor.execute('UPDATE register SET player_count = %s WHERE tournament_id = %s', (count+1, tournament_id))
                conn.commit()
                flash("Successfully registered for the tournament {}".format(tournament_id))
                return redirect(url_for('tourReg'))

            return redirect(url_for('tourReg'))
        else:             
            cursor.execute('SELECT * FROM register')
            tournaments = cursor.fetchall()

            cursor.execute('SELECT * FROM players WHERE player_id = %s', (session['player_id'],))
            player = cursor.fetchone()

            ids = []
            for tournament in tournaments: 
                cat = ''
                if tournament['category'] == "Men's  ": cat = "M"
                else: cat = "F"
                if tournament['status'] == 'Open  ' and cat == player['sex'] : ids.append(tournament['tournament_id'])
                
            data_dict = {'player_id': session['player_id'], 'ids': ids}
            return render_template('playerPrivileges/tourReg.html', dict = data_dict)

    else: return redirect(url_for('loginPlayer'))

@app.route('/updateBio', methods=["GET", "POST"])
def updateBio():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:  
        if request.method == "POST":
            firstname = request.form['first_name']
            middlename = request.form['middle_initial']
            lastname = request.form['last_name']
            password = request.form['password']
            gender = request.form['gender']
            dob = request.form['dob']

            if not re.match(r'[A-Za-z]+', firstname):
                flash('Firstname must contain only characters!')
            elif not re.match(r'[A-Za-z]+', middlename):
                flash('Middlename must contain only characters')
            elif not re.match(r'[A-Za-z]+', lastname):
                flash('Lastname must contain only characters')
            elif not password or not firstname:
                flash('Please fill out the form!')
            else:
                cursor.execute('SELECT * FROM players WHERE player_id = %s', (session['player_id'],))
                account = cursor.fetchone()
                # print(account)

                cursor.execute("UPDATE players SET first_name = %s, middle_initial = %s, last_name = %s, password = %s, sex = %s, date_of_birth = %s WHERE player_id = %s", (firstname, middlename, lastname, password, gender, dob, session['player_id']))
                conn.commit()

                cursor.execute('SELECT * FROM players WHERE player_id = %s', (session['player_id'],))
                account = cursor.fetchone()
                # print(account)

                flash('You have successfully updated your info!')
                return redirect(url_for('updateBio'))
                        
            return redirect('updateBio')

        else: 
            cursor.execute('SELECT * FROM players WHERE player_id = %s', (session['player_id'],))
            player = cursor.fetchone()
            return render_template('playerPrivileges/updateBio.html', player = player)

    else: return redirect(url_for('loginPlayer'))

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
