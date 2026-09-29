from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app =Flask(__name__)
app.secret_key = "supersecretkey"

#file types that are alowed when uploading dinosaur images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif'}

#displays homepage
@app.route("/")
def root():
    return render_template("home.html", page_title="Home", greeting="Database connected")

#displays all dinosaurs and allows the user to search by dinosaur name
@app.route("/dinosaurs")
def dinosaurs_page():

# get the search text entered by the user
    search = request.args.get('search', '')

#connect to the sql database
    conn = sqlite3.connect("dinosaurs.db")
    cur = conn.cursor()

#only show matching dinosaurs if the user uses search
    if search:
        cur.execute('''
             SELECT
                 Dinosaurs.dinosaur_id,
                 Dinosaurs.name,
                 Dinosaurs.diet,
                 Dinosaurs.habitat,
                 Dinosaurs.location,
                 Dinosaurs.description,
                 Dinosaurs.image,
                 Dinosaurs.license_info,
                 GROUP_CONCAT(Era.era_name, ', ') AS eras
             FROM Dinosaurs
             LEFT JOIN Dino_Era
                 ON Dinosaurs.dinosaur_id = Dino_Era.dinosaur_id
             LEFT JOIN Era
                 ON Dino_Era.era_id = Era.era_id
             WHERE Dinosaurs.name LIKE ?
             GROUP BY Dinosaurs.dinosaur_id
             ORDER BY Dinosaurs.name ASC
         ''', ('%' + search + '%',))

#display all dinosaurs if there is no search
    else:
        cur.execute('''
            SELECT
                Dinosaurs.dinosaur_id,
                Dinosaurs.name,
                Dinosaurs.diet,
                Dinosaurs.habitat,
                Dinosaurs.location,
                Dinosaurs.description,
                Dinosaurs.image,
                Dinosaurs.license_info,
                GROUP_CONCAT(Era.era_name, ', ') AS eras
            FROM Dinosaurs
            LEFT JOIN Dino_Era
                ON Dinosaurs.dinosaur_id = Dino_Era.dinosaur_id
            LEFT JOIN Era
                ON Dino_Era.era_id = Era.era_id
            GROUP BY Dinosaurs.dinosaur_id
            ORDER BY Dinosaurs.name ASC
        ''')

#get all matching rows from the database
    dinosaurs = cur.fetchall()
    print(dinosaurs)
    conn.close()

#send the dinosaur data to the jinja template
    return render_template(
        'dinosaurs.html', 
        page_title='DINOSAURS',
        dinosaurs=dinosaurs
    )

#displays detailed info about one selected dinosaur
@app.route("/dinosaur/<int:id>")
def dinosaur_details(id):

    conn = sqlite3.connect('dinosaurs.db')
    cur = conn.cursor()

#find the dinosaur using its unique id
    cur.execute('''
        SELECT
            Dinosaurs.dinosaur_id,
            Dinosaurs.name,
            Dinosaurs.diet,
            Dinosaurs.habitat,
            Dinosaurs.location,
            Dinosaurs.description,
            Dinosaurs.image,
            Dinosaurs.license_info,
            GROUP_CONCAT(Era.era_name, ', ') AS eras
        FROM Dinosaurs
        LEFT JOIN Dino_Era
            ON Dinosaurs.dinosaur_id = Dino_Era.dinosaur_id
        LEFT JOIN Era
            ON Dino_Era.era_id = Era.era_id
        WHERE Dinosaurs.dinosaur_id = ?
        GROUP BY Dinosaurs.dinosaur_id
    ''', (id,))

    #get the selected dinosaur from query
    dinosaur = cur.fetchone()
    #close connection
    conn.close()

#send the dinosaur data to the details page
    return render_template("dinosaur_details.html", dinosaur=dinosaur)

#gets all the eras from the database and displays them
@app.route("/eras")
def eras_page():
    conn = sqlite3.connect('dinosaurs.db')
    cur = conn.cursor()

#get the name and description sorted alphabetically
    cur.execute('''
    SELECT
        era_id,
        era_name,
        description
    FROM Era
    ORDER BY era_name ASC
    ''')

#get all eras returned by the query
    eras = cur.fetchall()
    conn.close()

#send the era data to the jinja template
    return render_template(
        "eras.html",
        page_title="ERAS",
        eras=eras
    )

#alows the admin to add a new dinosaur to the database
@app.route('/add_dinosaur', methods=["GET", "POST"])
def add_dinosaur():

#check if the user is logged in as an admin
    if not session.get('admin'):
        return render_template('login_required.html',
            previous_page=request.referrer or url_for('root')
        )
    
    conn = sqlite3.connect('dinosaurs.db')
    cur = conn.cursor()

#get all available eras for the add dinosaur form
    cur.execute('SELECT era_id, era_name FROM Era ORDER BY era_name ASC')
    all_eras = cur.fetchall()

    #if the form has been submitted get the users input
    if request.method == 'POST':
        name        = request.form['name']
        diet        = request.form['diet']
        habitat     = request.form['habitat']
        location    = request.form['location']
        description = request.form['description']
        eras        = request.form.getlist('eras')
        license_info= request.form['license_info']

    #Handle the uploaded image file
        image_file = request.files['image']

        #check weather an image was uploaded
        if image_file and image_file.filename != '' :
            ext = image_file.filename.rsplit('.', 1) [1].lower()
            #check weather the uploaded file has an alowed extension
            if ext not in ALLOWED_EXTENSIONS:
                return '''
                    <script>
                        alert("Invalid image type. Please select a PNG, JPG, or GIF image.");
                        window.history.back();
                    </script>
                '''
            #make the filename secure and save the img
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join('static', 'images', filename))

        else:
            filename = None #No image uploaded

        #insert the new dinosaur's info to the database
        cur.execute(
            '''
            INSERT INTO Dinosaurs
            (name, diet, habitat, location, description, image, license_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (name, diet, habitat, location, description, filename, license_info)
        )

        #Get the new dinosaur's auto assigned id
        dinosaur_id = cur.lastrowid

        #connect the dinosaur to its selected eras 
        for era_id in eras:
            cur.execute(
                'INSERT INTO Dino_Era (era_id, dinosaur_id) VALUES (?, ?) ',
                 (era_id, dinosaur_id)
                )

        conn.commit()
        conn.close()

        return redirect(url_for('dinosaurs_page'))
    
    conn.close()

#display the add dinosaur form
    return render_template(
        'add_dinosaur.html',
        page_title='ADD DINOSAUR',
        all_eras=all_eras
    )

#logs an admin into the website
@app.route('/login', methods=['GET', 'POST'])
def login():
    #check weather the login has been submitted
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #check the entered login credentials
        if username == 'admin' and password == 'dinosaur123' :
            #store the admin login status in the session
            session['admin'] = True
            #send admin to the dinosaur page
            return redirect(url_for('dinosaurs_page'))
        else: 
            #show an error if login details are incorrect
            return render_template('login.html', error="Invalid Login")

    #display login form
    return render_template('login.html')

#logs the admin out and removes their login session
@app.route('/logout')
def logout():
    #removes admin status from session
    session.pop('admin', None)
    #display logout page
    return render_template('logout.html')

#deletes a dinosaur from the database if the admin is logged in
@app.route('/delete/<int:id>', methods=['POST'])
def delete_dinosaur(id):
    #check that the user is logged in as an admin
    if not session.get('admin'):
        return "Not authorised", 403
    
    conn = sqlite3.connect('dinosaurs.db')
    cur = conn.cursor()
    #delete the dinosaur with the matching id
    cur.execute('DELETE FROM Dinosaurs WHERE dinosaur_id = ?', (id,))
    conn.commit()
    conn.close()
    #return to the dinosaur list
    return redirect(url_for('dinosaurs_page'))

#start the flask development server
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

