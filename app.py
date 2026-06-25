from flask import Flask, render_template
import _sqlite3

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
