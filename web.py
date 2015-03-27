import functools
import json
import requests
import ConfigParser
import os
from requests.auth import HTTPBasicAuth
from flask import request, Flask, render_template, Response

app = Flask(__name__)
app.debug = True

config = ConfigParser.ConfigParser()
config.read(os.path.dirname(os.path.realpath(__file__)) + '\\properties.ini')
rest_username = config.get('rest', 'username')
rest_password = config.get('rest', 'password')


def check_auth(username, password):
    return requests.post('http://localhost:5000/credentials',
                         data=json.dumps({'username': username, 'password': password}),
                         headers={'content-type': 'application/json'},
                         auth=HTTPBasicAuth(rest_username, rest_password))


def authenticate():
    # Sends a 401 response that enables basic auth
    return Response(
        'Authentication failed', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def authenticated(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return wrapper


@app.route('/', methods=['GET'])
@authenticated
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
@authenticated
def show_search():
    return render_template('search.html')

@app.route('/result', methods=['POST'])
@authenticated
def get_by_title():
    r = requests.get('http://localhost:5000/result/%s' % request.form['search'])
    return render_template('result.html', output=r.json())

@app.route('/info/<id>', methods=['GET'])
@authenticated
def get_info_by_id(id):
    r = requests.get('http://localhost:5000/info/%s' % id)
    return render_template('info.html', output=r.json())

@app.route('/signup', methods=['GET'])
def show_signup_form():
    return render_template('signup.html')

@app.route('/add', methods=['POST'])
def add_new():
    new_record = {
        'username': request.form['username'],
        'password': request.form['password']
    }
    response = requests.post('http://localhost:5000/add',
                             data=json.dumps(new_record),
                             headers={'content-type': 'application/json'})
    if response.status_code == requests.codes.ok:
        return "Yay!"
    return 'username already exists'


if __name__ == '__main__':
    app.run(
        port=80
    )
