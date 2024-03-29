from flask import Flask, jsonify, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from methods import list_filtered, get_some_value, verify_efd, pgda_calculator
import os

app = Flask(__name__)

CORS(app)

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
    path = f"./data/upload/{f.filename}"
    f.save(path) 
    return {"path": path}

@app.route('/pgda/<cnpj>', methods=['POST'])
def calculate(cnpj):
    request_data = request.get_json()
    year_income = request_data["year_income"]
    return pgda_calculator(cnpj,year_income)

if __name__ == '__main__':
    app.run()