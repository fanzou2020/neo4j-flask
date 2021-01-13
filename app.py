from flask import Flask, jsonify, abort
from flask import g
from flask import render_template
from flask import session, redirect, request, url_for
from neo4j_db import *
from urllib.parse import unquote

app = Flask(__name__)

# Set the secret key to some random bytes.
app.secret_key = b'_5#y2L"F4Q8z]/gafqehyth'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = Neo4jDriver("neo4j://localhost:7687", "neo4j", "neo4j_team")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', user_id=session['user_id'], user_name=session['user_name'])
    return render_template('index.html', user_id=None, user_name=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        db = get_db()
        user = db.find_user(user_id)
        if user is not None:
            session['user_id'] = request.form['user_id']
            session['user_name'] = user["name"]
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    # remove the user_id from the session if it's there
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))


# homepage of user_id
@app.route('/home/<user_id>')
def home(user_id):
    # get user info from database
    db = get_db()
    user = db.find_user(user_id)
    print(user)

    # get friends recommendation
    recommend_friends = db.friend_recommendation(user_id)
    if len(recommend_friends) > 20:
        r = recommend_friends[:20]
    else:
        r = recommend_friends
    return render_template('home.html', user_id=user_id, user=user, recommend_friends=r)


# map page
@app.route('/map')
def google_map():
    # get all states
    db = get_db()
    states = db.get_states()
    return render_template('map.html', states=states)


# return a json object that contains the cities of a state,
@app.route('/cities/<state>')
def cities_in_state(state):
    # get all cities of a state
    db = get_db()
    cities = db.get_cities_by_state(state)
    return jsonify(cities)


@app.route('/categories/<city>')
def categories_in_city(city):
    # get all categories of a city
    db = get_db()
    categories = db.get_categories_by_city(city)
    return jsonify(categories)


# return data of businesses, given parameters state, city, category
@app.route('/business')
def business_data():
    state = unquote(request.args['state'])
    city = unquote(request.args['city'])
    category = unquote(request.args['category'])
    print(category)
    if state == 'undefined' or city == 'undefined' or category == 'undefined':
        abort(404, "Resource not found")
    else:
        db = get_db()
        result = db.get_business(state, city, category)
        print(result)
        business = []
        for record in result:
            d = dict()
            for key in record.keys():
                d[key] = record.get(key)
            business.append(d)
        return jsonify(business)


# get all friends of a user
@app.route('/friends/<user_id>')
def get_friends(user_id):
    db = get_db()
    friends = db.get_friends(user_id)
    return jsonify(friends)


# add friend
@app.route('/addfriend/<user_id>/<friend_id>')
def add_friend(user_id, friend_id):
    db = get_db()
    try:
        tuple_of_two_user = db.add_friend(user_id, friend_id)
        return jsonify(True)
    except Exception as e:
        return jsonify(False)

"""
@app.route('/')
def hello_world():
    db = get_db()
    user_id = 'O6RoUsBLWKe7Jzcu66ybUw'
    user = db.find_user(user_id)

    html = ""
    for u in user:
        html += u["name"]

    return html


@app.route('/users')
def get_users():
    db = get_db()
    users = db.find_users()

    html = ""
    for u in users:
        html += u["name"] + "<br>"

    return html
"""

if __name__ == '__main__':
    app.run()
