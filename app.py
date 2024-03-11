#!/usr/bin/env python3

from flask import Flask,request,render_template
from json import loads,dumps,load

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def hello():
    if 'use_template' in request.args:
        return render_template('hello.html')
    else:
        return 'Hello World!'

@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)

@app.route('/recommend/', methods=['GET'])
def get_user():
    '''
        get data from frontend then sent free text into llm for generate recommended places.
    '''
    try:
        return make_response(jsonify({'message': 'succeed'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': e}), 500)