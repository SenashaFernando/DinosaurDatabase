from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app =Flask(__name__)
app.secret_key = "supersecretkey"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif'}


@app.route("/")
def root():
    return render_template("home.html", page_title="Home", greeting="Database connected")

#List all dinosaurs in alphabetical order
#eventually link each one to a details page
@app.route("/dinosaurs")
def dinosaurs_page():

    conn = sqlite3.connect("dinosaurs.db")
    cur = conn.cursor()

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
            GROUP_CONCAT(Era.era_name) AS eras
        FROM Dinosaurs
        LEFT JOIN Dino_Era
            ON Dinosaurs.dinosaur_id = Dino_Era.dinosaur_id
        LEFT JOIN Era
            ON Dino_Era.era_id = Era.era_id
        GROUP BY Dinosaurs.dinosaur_id
        ORDER BY Dinosaurs.name ASC
    ''')

    dinosaurs = cur.fetchall()
    print(dinosaurs)
    conn.close()

    return render_template(
        'dinosaurs.html', 
        page_title='ALL DINOSAURS',
        dinosaurs=dinosaurs
    )


@app.route('/add_dinosaur', methods=["GET", "POST"])
def add_dinosaur():
    #POST = form submitted
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

        if image_file and image_file.filename != '' :
            ext = image_file.filename.rsplit('.', 1) [1].lower()

            if ext not in ALLOWED_EXTENSIONS:
                return "Invalid image type"

            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join('static', 'images', filename))

        else:
            filename = None #No image uploaded

        #Connect to database
        conn = sqlite3.connect('dinosaurs.db')
        cur = conn.cursor()

        #insert new dinosaur
        cur.execute(
            '''
            INSERT INTO Dinosaurs
            (name, diet, habitat, location, description, image, license_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (name, diet, habitat, location, description, filename, license_info)
        )

        #Get the new dinosaur's id
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
       

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #simple hardcoded login
        if username == 'admin' and password == 'dinosaur123' :
            session['admin'] = True
            return redirect(url_for('dinosaurs_page'))
        else: 
            return render_template('login.html', error="Invalid Login")
    return render_template('login.html')
        
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('dinosaurs_page'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_dinosaur(id):
    if not session.get('admin'):
        return "Not authorised", 403
    
    conn = sqlite3.connect('dinosaurs.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM Dinosaurs WHERE dinosaur_id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dinosaurs_page'))

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)