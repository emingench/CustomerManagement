from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from flask_sqlalchemy import SQLAlchemy
import names, functools, random, time,json

app = Flask(__name__)
app.secret_key = "Secret Key"

# SqlAlchemy Database Configuration With sqlite
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/emingenc/PycharmProjects/CustomerManagement/database.db'  # edit your path acording to urself
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


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


users = []
users.append(User(id=1, username='Emin', password='q1w2e3r4t5y6'))



@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        try:
            user = [x for x in users if x.username == username][0]
            if user and user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('Index'))
            flash("user name or password is wrong", "error")
            return redirect(url_for('login'))
        except: flash("user name or password is wrong","error")

    return render_template('login.html')


# This is the index route where we are going to
@app.route('/search', methods=['GET'])
def search():
    if not g.user:
        return redirect(url_for('login'))
    posts = Data.query.filter(Data.name.like(f'%{request.args.get("query")}%')).all()
    count = str(Data.query.filter(Data.name.like(f'%{request.args.get("query")}%')).count())
    flash(count + " result")
    return render_template("index.html", customers=posts)


@app.route('/')
def Index():
    if not g.user:
        return redirect(url_for('login'))
    all_data = Data.query.all()

    return render_template("index.html", customers=all_data)


# this route is for inserting data to  database via html forms
@app.route('/insert', methods=['POST'])
def insert():
    if not g.user:
        return redirect(url_for('login'))
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
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        my_data = Data.query.get(request.form.get('id'))
        fname = request.form['fname']
        lname = request.form['lname']
        my_data.name = " ".join([fname, lname])
        my_data.tcno = request.form['tcno']
        my_data.phone = request.form['phone']

        db.session.commit()
        flash("Customer Updated Successfully")

        return redirect(url_for('Index'))


# This route is for deleting our data
@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    if not g.user:
        return redirect(url_for('login'))
    my_data = Data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Customer Deleted Successfully")

    return redirect(url_for('Index'))

@app.route('/json_export')
def json_export():
    dct= {}
    if not g.user:
        return redirect(url_for('login'))
    all_data = Data.query.all()
    for i in all_data:
        dct[i.id]={'name':i.name,'tcno':i.tcno,'phone':i.phone}
    with open("customers.json", "w") as outfile:
        json.dump(dct, outfile)
    return redirect(url_for('Index'))


# last to functions are just for test
@app.route('/randomuseradd')
def randomuser():
    if not g.user:
        return redirect(url_for('login'))
    time1 = time.time()
    n = 1000
    for i in range(n):
        a = functools.partial(random.randint, 0, 9)
        gsm = lambda: "{}{}{}{}{}{}{}{}{}{}".format(a(), a(), a(), a(), a(), a(), a(), a(), a(), a())
        tcno = lambda: "{}{}{}{}{}{}{}{}{}{}{}".format(a(), a(), a(), a(), a(), a(), a(), a(), a(), a(), a())

        my_data = Data(names.get_full_name(), tcno(), gsm())
        db.session.add(my_data)
        db.session.commit()
    time2 = time.time()

    flash(f"{str(n)} Customer Inserted Successfully.({str(round(time2 - time1, 2))} seconds took) ")

    return redirect(url_for('Index'))


@app.route('/delete_all')
def delete_all():
    if not g.user:
        return redirect(url_for('login'))
    db.drop_all()
    db.create_all()
    return redirect(url_for('Index'))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=8000)
