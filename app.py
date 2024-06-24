#app.py
from flask import Flask, request, session, redirect, url_for, render_template,flash
import psycopg2 #pip install psycopg2 
import psycopg2.extras
import re 
from werkzeug.security import generate_password_hash, check_password_hash
 
app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'
 
DB_HOST = "localhost"
DB_NAME = "sampledb"
DB_USER = "postgres"
DB_PASS = "rinitha"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
 
# @app.route('/')
# def home():
#     # Check if user is loggedin
#     if 'loggedin' in session:
#         home1()   
#         # User is loggedin show them the home page
#         return render_template('home.html', username=session['username'])
#     # User is not loggedin redirect to login page
#     return redirect(url_for('login'))
# @app.route('/')
# def home():
#     # Check if user is logged in
#     if 'loggedin' in session:
#         # Autocomplete data
#         languages = ["C++", "Python", "PHP", "Java", "C", "Ruby",
#                      "R", "C#", "Dart", "Fortran", "Pascal", "Javascript"]

#         # Render the home page with autocomplete data
#         return render_template('home.html', username=session['username'], languages=languages)
    
#     # User is not logged in, redirect to login page
#     return redirect(url_for('login'))

@app.route('/')
def home():
    # Check if user is logged in
    if 'loggedin' in session:
        # Autocomplete data
        countries = get_countries_from_database()

        # Render the home page with autocomplete data
        return render_template('home.html', username=session['username'],countries=countries)
    
    # User is not logged in, redirect to login page
    # return redirect(url_for('login'))
    return redirect(url_for('homee.html'))

def get_countries_from_database():
    # Assuming you have a database connection available, and the cursor is established
    # Execute the query to fetch country names
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT country_name FROM country")
    countries = [row[0] for row in cursor.fetchall()]
    print(countries)
    # Return the list of countries
    return countries


@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')
 
    return render_template('login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')
   
   
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
  
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# @app.route('/view_data')
# def view_data():
#     return redirect(url_for('redirected_page'))

@app.route('/view_data')
def view_data():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute( "SELECT * from country" )
    fetched_records = cursor.fetchall()
    print(fetched_records)
    return render_template('view.html',records=fetched_records)

@app.route('/insert_data')
def insert_data():
    print("CAME IN, 1")    
    return render_template("insertform.html")

@app.route('/inserted_data',methods=["POST","GET"])
def inserted_data():
    print("CAME IN INSERTED DATA")
    if request.method == 'POST':
        print("CAME IN POST")
        country_id = request.form['country_id']
        country_name = request.form['country_name']
        continent = request.form['continent']
        gdp = request.form['gdp']

        # Assuming 'conn' is your database connection
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Use a parameterized query to prevent SQL injection
        cursor.execute("INSERT INTO country (country_id,country_name, continent, gdp) VALUES (%s ,%s, %s, %s)",
                       (country_id,country_name, continent, gdp))
        
        # Commit the transaction to save the changes
        conn.commit()

        cursor.execute( "SELECT * from country" )
        country = cursor.fetchall()
        print(country)
        flash('Inserted Data successfully')       

        # Redirect to the 'inserted_data' route after inserting data
        return render_template('insertform.html')
       
    else:
        return render_template('insertform.html')

@app.route('/update_data')
def update_data():
    return render_template("updateform.html")

@app.route('/updated_data',methods=["POST","GET"])
def updated_data():
    print("CAME IN UPDATED DATA")
    if request.method == 'POST':
        print("CAME IN POST")
        country_id = request.form['country_id']
        country_name = request.form['country_name']
        continent = request.form['continent']
        gdp = request.form['gdp']

        # Assuming 'conn' is your database connection

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)      
        
        countries = get_countries_from_database()
        cursor.execute( "SELECT country_name from country" )
        fetched_records=cursor.fetchall()
        print(fetched_records)
        flag = 0
        for record in fetched_records:
            if record[0] == country_name:
                flag = 1
        if flag == 0:
            flash('The record does not exist','error')
            return render_template('updateform.html')
        # Use a parameterized query to prevent SQL injection
        cursor.execute("UPDATE country SET country_name = %s, continent = %s, gdp = %s WHERE country_id = %s",
               (country_name, continent, gdp, country_id))
        
        # Commit the transaction to save the changes
        conn.commit()

        cursor.execute( "SELECT * from country" )
        country = cursor.fetchall()
        print(country)
        flash('Updated Data successfully','success')       

        # Redirect to the 'inserted_data' route after inserting data
        return render_template('updateform.html',countries=countries)
       
    else:
        return render_template('updateform.html',countries=countries)

def get_countries_from_database():
    # Assuming you have a database connection available, and the cursor is established
    # Execute the query to fetch country names
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT country_name FROM country")
    countries = [row[0] for row in cursor.fetchall()]
    print(countries)
    # Return the list of countries
    return countries


@app.route('/delete_data')
def delete_data():
    return render_template("deleteform.html")

@app.route('/deleted_data',methods=["POST","GET"])
def deleted_data():
    print("CAME IN DELETED DATA")
    if request.method == 'POST':
        print("CAME IN POST")
        country_name = request.form['country_name']
        # Assuming 'conn' is your database connection
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        countries=get_countries_from_database()
        cursor.execute( "SELECT * from country" )
        fetched_records=cursor.fetchall()
        print(fetched_records)
        flag = 0
        for record in fetched_records:
            if record[1] == country_name:
                flag = 1
        if flag == 0:
            flash('The record does not exist','error')
            return render_template('deleteform.html')

        # Use a parameterized query to prevent SQL injection
        cursor.execute("DELETE FROM country WHERE country_name = %s", (country_name,))
        # Commit the transaction to save the changes
        conn.commit()

        cursor.execute( "SELECT * from country" )
        country = cursor.fetchall()
        print(country)
        flash('Deleted Data successfully','success')       

        # Redirect to the 'inserted_data' route after inserting data
        return render_template('deleteform.html',countries=countries)
       
    else:
        return render_template('deleteform.html',countries=countries)      

@app.route('/query_data')
def query_data():
    return render_template("queryform.html")

@app.route('/queried_data',methods=["POST","GET"])
def queried_data():
    print("CAME IN QUERIED DATA")
    if request.method == 'POST':
        print("CAME IN POST")
        query = request.form['query']  
               
        # Assuming 'conn' is your database connection
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Use a parameterized query to prevent SQL injection
        final_query = "%s"%(query)
        cursor.execute(final_query)
       
        # Commit the transaction to save the changes
        conn.commit()

        fetched_records = cursor.fetchall()
        print(fetched_records)
        flash('Fetched Data successfully')       

        # Redirect to the 'inserted_data' route after inserting data
        return render_template('queriedview.html',records=fetched_records)
         
    else:
        return render_template('queryform.html',records=None)          

    
@app.route('/filter_data')
def filter_data():
    return render_template("filterform.html")

@app.route('/filtered_data',methods=["POST","GET"])
def filtered_data():
    print("CAME IN FILTERED DATA")
    if request.method == 'POST':
        print("CAME IN POST")
        lower = request.form['lower']  
        upper = request.form['upper']
        final_query=''

        if not lower and not upper:
            flash('Please enter either lower or upper limit for filtering!')
            return render_template('filterform.html',records=None)
        elif lower and upper:
            flash('Enter any one fields to render the data')
            return render_template('filterform.html',records=None)
        elif lower:
            final_query = "SELECT * FROM country WHERE gdp< %s"%(lower)
        else: 
              final_query= "SELECT * FROM country WHERE gdp> %s"%(upper)

               
        # Assuming 'conn' is your database connection
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Use a parameterized query to prevent SQL injection
        
        cursor.execute(final_query)
       
        # Commit the transaction to save the changes
        conn.commit()

        fetched_records = cursor.fetchall()
        print(fetched_records)
        flash('Fetched Data successfully')       

        # Redirect to the 'inserted_data' route after inserting data
        return render_template('queriedview.html',records=fetched_records)
         
    else:
        return render_template('filterform.html',records=None) 
 
if __name__ == "__main__":
    app.run(debug=True)