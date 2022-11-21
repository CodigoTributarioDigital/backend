from flask import Flask, jsonify, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from methods import list_filtered, get_some_value, verify_efd
import os

app = Flask(__name__)

CORS(app)

@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'

@app.route('/list/<cnpj>/<month>/<year>', methods=['GET'])
def list_nf(cnpj, month, year): 
    return list_filtered(cnpj, month, year)

@app.route('/some', methods=['POST'])
def get_some():
    request_data = request.get_json()
    req = request_data['ncm']
    some, fecoep = get_some_value(req)
    return {"some": some, "fecoep": fecoep}

@app.route('/verify_efd/<cnpj>', methods=['POST'])
def verify(cnpj):
    request_data = request.get_json()
    efd_path = request_data['efd_path']
    return verify_efd(cnpj, efd_path)

@app.route('/upload', methods=['POST'])
def fileUpload():
    f = request.files['file']  
    f.save(f"./data/upload/{f.filename}") 
    return "done"