from flask import Flask, jsonify, request
from flask_cors import CORS
from compliance import verify_efd
from methods import list_filtered

app = Flask(__name__)

CORS(app)

@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'

@app.route('/verify_efd', methods=['POST'])
def verify():
    return verify_efd()

@app.route('/list/<cnpj>/<month>/<year>', methods=['POST'])
def list_nf(cnpj, month, year): 
    return list_filtered(cnpj, month, year)