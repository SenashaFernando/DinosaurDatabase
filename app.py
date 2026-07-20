from flask import Flask, render_template, request, redirect, url_for, session
import _sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route("/")
def root():
    return render_template("home.html", page_title="Home", greeting="Database connected")

#List all dinosaurs in alphabetical order
#eventually link each one to a details page
@app.route("/dinosaurs")
def dinosaurs_page():
    conn = _sqlite3.connect(dinosaurs.db)
    cur = conn.cursor()
    cur.execute('SELECT dinosaur_id, name, diet, habitat, location, description, image, license info FROM Dinosaurs ORDER BY name ASC;')
    dinosaurs = cur.fetchall
    print(dinosaurs)
    conn.close()
    return render_template('dinosaurs.html', page_title='ALL DINOSAURS', dinosaurs=dinosaurs)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.01", port=5000)

@app.route('add_dinosaur', methods=['GET', 'POST'])
def add_dinosaur():
    #POST = form submitted
    if request.method == 'POST':
        name        = request.form['name']
        diet        = request.form['diet']
        habitat     = request.form['habitat']
        location    = request.form['location']
        description = request.form['description']
        era_name    = request.form['era_name']

#Handle the uploaded image file
image_file = request.files['image']
if image_file and image_file.filename != '':
    filename = secure_filename(image_file.filename)
    image_file.save(os.path.join('static', 'images', filename))
else:
    filename = None #No image uploaded

#Connect to database
conn = sqlite3.connect('dinosaurs.db')
cur = conn.cursor()

#insert new dinosaur
cur.execute(
    
)

@app.route('/delete/<int:id>' , methods=['POST'])
def delete_dinosaur(id):
    conn = sqlite3.connect('dinosaurs.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM Dinosaurs WHERE id = ?', (id))
    conn.comit()
    conn.close()
    return redirect(url_for('dinosaurs_page'))

