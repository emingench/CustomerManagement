from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import names,functools,random

app = Flask(__name__)
app.secret_key = "Secret Key"

# SqlAlchemy Database Configuration With sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Dell/PycharmProjects/CustomerManagement/database.db' #edit your path acording to urself
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Creating model table
class Data(db.Model):
    __searchable__ = ['name', 'tcno', 'phone']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    tcno = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def __init__(self, name, tcno, phone):
        self.name = name
        self.tcno = tcno
        self.phone = phone


# This is the index route where we are going to
@app.route('/search', methods=['GET'])
def search():
    posts = Data.query.filter(Data.name.like(f'%{request.args.get("query")}%')).all()
    count = str(Data.query.filter(Data.name.like(f'%{request.args.get("query")}%')).count())
    flash(count+" result")
    return render_template("index.html", customers=posts)


@app.route('/')
def Index():
    all_data = Data.query.all()

    return render_template("index.html", customers=all_data)


# this route is for inserting data to  database via html forms
@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        tcno = request.form['tcno']
        phone = request.form['phone']

        my_data = Data(f"{fname} {lname}", tcno, phone)
        db.session.add(my_data)
        db.session.commit()

        flash("Customer Inserted Successfully")

        return redirect(url_for('Index'))


# this is our update route where we are going to update our dats
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        my_data = Data.query.get(request.form.get('id'))
        fname = request.form['fname']
        lname = request.form['lname']
        my_data.name = " ".join([fname , lname])
        my_data.tcno = request.form['tcno']
        my_data.phone = request.form['phone']

        db.session.commit()
        flash("Customer Updated Successfully")

        return redirect(url_for('Index'))


# This route is for deleting our data
@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    my_data = Data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Customer Deleted Successfully")

    return redirect(url_for('Index'))

# last to functions are just for test
@app.route('/random1000')
def randomuser():
    for i in range(1000) :
        a = functools.partial(random.randint, 0, 9)
        gsm = lambda: "{}{}{}{}{}{}{}{}{}{}".format( a(), a(), a(), a(), a(), a(), a(), a(), a(), a())
        tcno = lambda: "{}{}{}{}{}{}{}{}{}{}{}".format(a(), a(), a(), a(), a(), a(), a(), a(), a(), a(), a())

        my_data = Data(names.get_full_name(), tcno(), gsm())
        db.session.add(my_data)
        db.session.commit()

    flash("1000 Customer Inserted Successfully")

    return redirect(url_for('Index'))

@app.route('/delete_all')
def delete_all():
    db.drop_all()
    db.create_all()
    return redirect(url_for('Index'))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=8000)
