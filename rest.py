import pymongo
import json
import functools
import ConfigParser
import os
from flask import request, Flask, abort, Response

import tmdbsimple as tmdb

app = Flask(__name__)
app.debug = True

config = ConfigParser.ConfigParser()
config.read(os.path.dirname(os.path.realpath(__file__)) + '\\properties.ini')
rest_username = config.get('rest', 'username')
rest_password = config.get('rest', 'password')
tmdb.API_KEY = config.get('tmdb', 'api_key')

client = pymongo.MongoClient()
db = client.test
collection = db.testData


def authenticate():
    # Sends a 401 response that enables basic auth
    return Response(
        'Authentication failed', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def authenticated(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == rest_username and auth.password == rest_password):
            return authenticate()
        return f(*args, **kwargs)
    return wrapper


@app.route('/credentials', methods=['POST'])
@authenticated
def check_auth():
    data = json.loads(request.data)
    exists = collection.find_one({'_id': data['username'], 'password': data['password']})
    if not exists:
        abort(404)
    return 'true'

@app.route('/result/<title>', methods=['GET'])
def get_by_title(title):
    results = tmdb.Search().movie(query=title, include_adult=False)
    return json.dumps(results, indent=1)

@app.route('/info/<id>', methods=['GET'])
def get_info_by_id(id):
    movie = tmdb.Movies(id)
    results = movie.info()
    return json.dumps(results)

@app.route('/add', methods=['POST'])
def add_new():
    data = json.loads(request.data)
    existing = collection.find_one({'_id': data['username']})
    if existing:
        abort(400)
    new_record = {
        '_id': data['username'],
        'password': data['password']
    }
    collection.insert(new_record)
    return 'true'

if __name__ == '__main__':
    app.run()
