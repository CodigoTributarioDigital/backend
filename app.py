from flask import Flask
# Return json as response
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'