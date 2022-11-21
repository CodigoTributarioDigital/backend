from flask import Flask, jsonify, request
from flask_cors import CORS
from methods import list_filtered, get_aliquotas_value

app = Flask(__name__)

CORS(app)

@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'

@app.route('/list/<cnpj>/<month>/<year>', methods=['GET'])
def list_nf(cnpj, month, year): 
    return list_filtered(cnpj, month, year)

@app.route('/aliquota', methods=['POST'])
def get_aliquota():
    request_data = request.get_json()
    ncm = request_data['ncm']
    return {"ncm":get_aliquotas_value(ncm)}