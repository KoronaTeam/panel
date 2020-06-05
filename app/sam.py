# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 18:15:33 2019

@author: Maciej
"""
from flask import Flask, render_template, url_for, request, redirect, abort, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config.update(
    DEBUG=True,
    SECRET_KEY='bardzotajnyklucz')
db = SQLAlchemy(app)

# ustawienie flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# przeladowanie użytkownika
@login_manager.user_loader
def load_user(userid):
    return User(userid)


global userData


# modelużytkownika
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "User" + str(id)
        self.password = self.name + "_haslo"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# generowanie użytkowników
users = [User(id) for id in range(1, 10)]


@app.route("/login", methods=['GET', 'POST'])
def login():
    title = 'Log in'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == username + "_haslo":
            id = username.split('User')[1]
            user = User(id)
            login_user(user)
            return redirect(url_for("index"))
        else:
            return abort(401)
    else:
        return render_template('login.html', tytul=title)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    tytul = "Logout"
    return render_template('logout.html', tytul=tytul)


class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    subtitle = db.Column(db.String(100))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)


@app.route('/')
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/userView')
def userView():
    res = requests.get('http://51.83.131.71:8080/users')
    data = res.json()
    #print(data)

    return render_template('userView.html', data=data)


@app.route('/about')
def about():
    title = "About our project"
    return render_template('about.html', tytul=title)


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)


@app.route('/add')
@login_required
def add():
    return render_template('add.html')


@app.route('/adduser', methods=['POST'])
@login_required
def adduser():
    import json
    newUser = {
        "username": request.form['phone'],
        "password": request.form['pass'],
        "email": request.form['email'],
        "firstName": request.form['fName'],
        "lastName": request.form['lName']
    }
    newuserjson = json.dumps(newUser)
    print(newuserjson)
    headers = {'Content-Type': 'application/json'}
    url = "http://51.83.131.71:8080/users"
    response = requests.request("POST", url, headers=headers, data=newuserjson)
    print(response.text.encode('utf8'))
    # post = Blogpost(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())

    return redirect(url_for('userView'))

@app.route('/addq')
@login_required
def addq():
    return render_template('addQuar.html')

@app.route('/addquar', methods=['POST'])
@login_required
def addquar():
    import json
    a = request.form['startDate']
    b = request.form['endDate']
    a1 = a.replace("T", " ")+":00"
    b1 = b.replace("T", " ")+":00"
    newQuar = {
        "userId": request.form['userId'],
        "startDate": a1,
        "endDate": b1
    }
    newQuarJson = json.dumps(newQuar)
    headers = {'Content-Type': 'application/json'}
    url = "http://51.83.131.71:8080/quarantines"
    response = requests.request("POST", url, headers=headers, data=newQuarJson)
    print(newQuarJson)

    return redirect(url_for('userView'))

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    return render_template('edit.html', post=post)


@app.route('/editpost/<int:post_id>', methods=['GET', 'POST'])
@login_required
def editpost(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    post.title = request.form['title']
    post.subtitle = request.form['subtitle']
    post.author = request.form['author']
    post.content = request.form['content']

    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))


@app.route("/json", methods=["POST"])
def json():
    if request.is_json:
        # req = request.get_json()
        # response = {
        #     "UserID": req.get("username"),
        #     "Hasło": req.get("password"),
        #     "Adres e-mail": req.get("email"),
        #     "Imię": req.get("firstName"),
        #     "Nazwisko": req.get("lastName")
        # }
        # print(response)
        # post = Blogpost(title=response.get("UserID"), subtitle=response.get("Nazwisko"), author=response.get("Imię"),
        #                 content=response.get("Hasło"), date_posted=datetime.now())
        #
        # db.session.add(post)
        # db.session.commit()
        #
        # res = make_response(jsonify(response), 200)

        return render_template('index.html')
    else:
        res = make_response(jsonify({"message": "No JSON received!"}), 400)
        return res


if __name__ == "__main__":
    app.run(debug=True)
