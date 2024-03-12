#!/usr/bin/env python3
import weaviate
import weaviate.classes as wvc
import os
import requests
import json

from flask import Flask,request,render_template
from flask import make_response, jsonify
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
    
@app.route('/v1/nodes/Question2', methods=['GET'])
def get_result():
    client = weaviate.connect_to_wcs(
        cluster_url="xxx",
        auth_credentials=weaviate.auth.AuthApiKey("xxx"),
        headers={
            "xxx"  # Replace with your inference API key
        }
    )

    try:
        pass # Replace with your code. Close client gracefully in the finally block.
        questions = client.collections.get("Question2")

        response = questions.query.near_text(
            query="thai food",
            limit=2
        )

        result = response.objects[0].properties
    except Exception as e:
        return make_response(jsonify({'message': e}), 500)
    finally:
        client.close()  
    return make_response(jsonify({'message': "hello"}), 200)